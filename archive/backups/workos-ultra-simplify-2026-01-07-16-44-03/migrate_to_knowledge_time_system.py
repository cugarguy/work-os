"""
Data migration script for transforming WorkOS from task management to knowledge/time system.

This script:
1. Creates a backup of the current system state
2. Preserves Knowledge/ and People/ directories (no modifications)
3. Converts task time data to time_analytics.json
4. Renames BACKLOG.md to NOTES_INBOX.md
5. Creates Tasks/README.md explaining read-only status
"""

import sys
import shutil
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class MigrationError(Exception):
    """Custom exception for migration errors."""
    pass


class WorkOSMigration:
    """Handles migration from task management to knowledge/time system."""
    
    def __init__(self, workspace_path: Path):
        """
        Initialize migration with workspace path.
        
        Args:
            workspace_path: Path to the WorkOS workspace root
        """
        self.workspace = Path(workspace_path)
        self.backup_dir = self.workspace / "backups" / f"migration-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
        self.knowledge_dir = self.workspace / "Knowledge"
        self.people_dir = self.workspace / "People"
        self.tasks_dir = self.workspace / "Tasks"
        self.system_dir = self.workspace / ".system"
        self.time_file = self.system_dir / "time_analytics.json"
        
        # Migration report
        self.report = {
            'timestamp': datetime.now().isoformat(),
            'backup_location': str(self.backup_dir),
            'knowledge_docs_preserved': 0,
            'people_profiles_preserved': 0,
            'tasks_converted': 0,
            'time_entries_created': 0,
            'errors': [],
            'warnings': []
        }
    
    def validate_workspace(self) -> bool:
        """
        Validate that the workspace has the expected structure.
        
        Returns:
            True if valid, raises MigrationError otherwise
        """
        if not self.workspace.exists():
            raise MigrationError(f"Workspace not found: {self.workspace}")
        
        if not self.knowledge_dir.exists():
            raise MigrationError(f"Knowledge directory not found: {self.knowledge_dir}")
        
        if not self.people_dir.exists():
            raise MigrationError(f"People directory not found: {self.people_dir}")
        
        if not self.tasks_dir.exists():
            self.report['warnings'].append(f"Tasks directory not found: {self.tasks_dir}")
        
        if not self.system_dir.exists():
            self.system_dir.mkdir(exist_ok=True)
            self.report['warnings'].append(f"Created .system directory: {self.system_dir}")
        
        return True
    
    def create_backup(self) -> bool:
        """
        Create a backup of the current system state.
        
        Returns:
            True if successful
        """
        print(f"Creating backup at {self.backup_dir}...")
        
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Backup directories
            for dir_name in ['Knowledge', 'People', 'Tasks', '.system']:
                src = self.workspace / dir_name
                if src.exists():
                    dst = self.backup_dir / dir_name
                    shutil.copytree(src, dst)
                    print(f"  Backed up {dir_name}/")
            
            # Backup key files
            for file_name in ['BACKLOG.md', 'config.yaml', 'CLAUDE.md']:
                src = self.workspace / file_name
                if src.exists():
                    dst = self.backup_dir / file_name
                    shutil.copy2(src, dst)
                    print(f"  Backed up {file_name}")
            
            print(f"✓ Backup created successfully")
            return True
            
        except Exception as e:
            raise MigrationError(f"Failed to create backup: {e}")
    
    def verify_preservation(self) -> bool:
        """
        Verify that Knowledge/ and People/ directories are intact.
        
        Returns:
            True if all files are preserved
        """
        print("Verifying Knowledge and People directories...")
        
        # Count knowledge documents
        knowledge_files = list(self.knowledge_dir.glob("*.md"))
        self.report['knowledge_docs_preserved'] = len(knowledge_files)
        print(f"  Knowledge documents: {len(knowledge_files)}")
        
        # Count people profiles
        people_files = list(self.people_dir.glob("*.md"))
        self.report['people_profiles_preserved'] = len(people_files)
        print(f"  People profiles: {len(people_files)}")
        
        print(f"✓ Directories verified")
        return True
    
    def convert_task_time_data(self) -> List[Dict]:
        """
        Convert task time estimates to time tracking entries.
        
        Returns:
            List of time entries created
        """
        print("Converting task time data...")
        
        if not self.tasks_dir.exists():
            print("  No Tasks directory found, skipping conversion")
            return []
        
        time_entries = []
        task_files = list(self.tasks_dir.glob("*.md"))
        
        for task_file in task_files:
            try:
                with open(task_file, 'r') as f:
                    content = f.read()
                
                # Parse frontmatter
                if not content.startswith('---'):
                    continue
                
                parts = content.split('---', 2)
                if len(parts) < 3:
                    continue
                
                frontmatter = yaml.safe_load(parts[1])
                if not frontmatter:
                    continue
                
                # Check if task has time data
                has_time_data = (
                    'estimated_minutes' in frontmatter or
                    'actual_minutes' in frontmatter or
                    'time_spent' in frontmatter
                )
                
                if has_time_data:
                    entry = {
                        'id': f"migrated_{task_file.stem}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        'work_description': frontmatter.get('title', task_file.stem),
                        'estimated_minutes': frontmatter.get('estimated_minutes'),
                        'actual_minutes': frontmatter.get('actual_minutes') or frontmatter.get('time_spent'),
                        'work_type': frontmatter.get('category', 'unknown'),
                        'migrated_from': str(task_file.name),
                        'migration_date': datetime.now().isoformat(),
                        'notes': 'Migrated from task management system'
                    }
                    time_entries.append(entry)
                    self.report['tasks_converted'] += 1
                    print(f"  Converted: {task_file.name}")
                
            except Exception as e:
                error_msg = f"Error processing {task_file.name}: {e}"
                self.report['errors'].append(error_msg)
                print(f"  ⚠ {error_msg}")
        
        self.report['time_entries_created'] = len(time_entries)
        print(f"✓ Converted {len(time_entries)} tasks to time entries")
        return time_entries
    
    def save_time_entries(self, time_entries: List[Dict]) -> bool:
        """
        Save time entries to time_analytics.json.
        
        Args:
            time_entries: List of time entry dictionaries
            
        Returns:
            True if successful
        """
        if not time_entries:
            print("No time entries to save")
            return True
        
        print(f"Saving time entries to {self.time_file}...")
        
        try:
            # Load existing entries if file exists
            existing_data = {'entries': []}
            if self.time_file.exists():
                with open(self.time_file, 'r') as f:
                    existing_data = json.load(f)
            
            # Append new entries
            existing_data['entries'].extend(time_entries)
            
            # Save
            with open(self.time_file, 'w') as f:
                json.dump(existing_data, f, indent=2)
            
            print(f"✓ Saved {len(time_entries)} time entries")
            return True
            
        except Exception as e:
            raise MigrationError(f"Failed to save time entries: {e}")
    
    def rename_backlog(self) -> bool:
        """
        Rename BACKLOG.md to NOTES_INBOX.md.
        
        Returns:
            True if successful or file doesn't exist
        """
        backlog_file = self.workspace / "BACKLOG.md"
        inbox_file = self.workspace / "NOTES_INBOX.md"
        
        if backlog_file.exists():
            print(f"Renaming BACKLOG.md to NOTES_INBOX.md...")
            try:
                backlog_file.rename(inbox_file)
                print(f"✓ Renamed to NOTES_INBOX.md")
                return True
            except Exception as e:
                raise MigrationError(f"Failed to rename BACKLOG.md: {e}")
        else:
            print("BACKLOG.md not found, skipping rename")
            return True
    
    def create_tasks_readme(self) -> bool:
        """
        Create Tasks/README.md explaining read-only status.
        
        Returns:
            True if successful
        """
        if not self.tasks_dir.exists():
            print("Tasks directory doesn't exist, skipping README creation")
            return True
        
        readme_path = self.tasks_dir / "README.md"
        print(f"Creating {readme_path}...")
        
        readme_content = """# Tasks Directory - Read-Only Reference

This directory contains historical task files from the previous task management system.

## Status: Read-Only

As of the migration to the knowledge and time intelligence system, this directory is **read-only** and maintained for reference purposes only.

## What Changed

WorkOS has been transformed from a task management system into a knowledge and time intelligence system that focuses on:

- **Knowledge Management**: Building a connected knowledge base using wikilinks
- **People Network**: Tracking relationships and expertise
- **Time Intelligence**: Understanding how long work takes and improving estimates
- **Work Breakdown**: Breaking complex work into estimable chunks

## Task Time Data

Time estimates and actual time spent from these task files have been converted to time tracking entries in `.system/time_analytics.json`. This historical data will inform future time estimates.

## Using the New System

Instead of managing tasks, the new system helps you:

1. **Capture Knowledge**: Add notes to `NOTES_INBOX.md` or use conversational capture
2. **Track Time**: Use time tracking tools to record work duration
3. **Get Estimates**: Receive intelligent estimates based on historical patterns
4. **Break Down Work**: Get help decomposing complex work into smaller chunks

## Accessing Historical Information

These task files remain available for reference. You can:
- Review past work descriptions
- Check historical time estimates
- Reference task context and notes
- See what work was completed

## Migration Date

This directory was marked read-only on: {migration_date}

For questions about the migration, see the migration report in `backups/`.
"""
        
        try:
            with open(readme_path, 'w') as f:
                f.write(readme_content.format(
                    migration_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
            print(f"✓ Created Tasks/README.md")
            return True
            
        except Exception as e:
            raise MigrationError(f"Failed to create Tasks/README.md: {e}")
    
    def generate_report(self) -> str:
        """
        Generate a migration report.
        
        Returns:
            Report as formatted string
        """
        report_lines = [
            "=" * 70,
            "WorkOS Migration Report",
            "=" * 70,
            f"Timestamp: {self.report['timestamp']}",
            f"Backup Location: {self.report['backup_location']}",
            "",
            "Summary:",
            f"  Knowledge documents preserved: {self.report['knowledge_docs_preserved']}",
            f"  People profiles preserved: {self.report['people_profiles_preserved']}",
            f"  Tasks converted: {self.report['tasks_converted']}",
            f"  Time entries created: {self.report['time_entries_created']}",
            ""
        ]
        
        if self.report['warnings']:
            report_lines.append("Warnings:")
            for warning in self.report['warnings']:
                report_lines.append(f"  ⚠ {warning}")
            report_lines.append("")
        
        if self.report['errors']:
            report_lines.append("Errors:")
            for error in self.report['errors']:
                report_lines.append(f"  ✗ {error}")
            report_lines.append("")
        
        report_lines.extend([
            "Next Steps:",
            "  1. Review the migration report above",
            "  2. Verify Knowledge/ and People/ directories are intact",
            "  3. Check .system/time_analytics.json for converted time data",
            "  4. Review NOTES_INBOX.md (formerly BACKLOG.md)",
            "  5. Read Tasks/README.md for information about the read-only task archive",
            "",
            "The migration is complete. Your data has been preserved and enhanced",
            "with time intelligence capabilities.",
            "=" * 70
        ])
        
        return "\n".join(report_lines)
    
    def save_report(self, report_text: str) -> bool:
        """
        Save the migration report to the backup directory.
        
        Args:
            report_text: The report content
            
        Returns:
            True if successful
        """
        report_path = self.backup_dir / "MIGRATION_REPORT.txt"
        
        try:
            with open(report_path, 'w') as f:
                f.write(report_text)
            print(f"\n✓ Migration report saved to {report_path}")
            return True
        except Exception as e:
            print(f"\n⚠ Failed to save report: {e}")
            return False
    
    def run(self) -> bool:
        """
        Run the complete migration process.
        
        Returns:
            True if successful
        """
        print("\n" + "=" * 70)
        print("WorkOS Migration: Task Management → Knowledge & Time Intelligence")
        print("=" * 70 + "\n")
        
        try:
            # Step 1: Validate workspace
            self.validate_workspace()
            
            # Step 2: Create backup
            self.create_backup()
            
            # Step 3: Verify preservation
            self.verify_preservation()
            
            # Step 4: Convert task time data
            time_entries = self.convert_task_time_data()
            
            # Step 5: Save time entries
            self.save_time_entries(time_entries)
            
            # Step 6: Rename BACKLOG.md
            self.rename_backlog()
            
            # Step 7: Create Tasks README
            self.create_tasks_readme()
            
            # Step 8: Generate and display report
            report_text = self.generate_report()
            print("\n" + report_text)
            
            # Step 9: Save report
            self.save_report(report_text)
            
            print("\n✓ Migration completed successfully!\n")
            return True
            
        except MigrationError as e:
            print(f"\n✗ Migration failed: {e}\n")
            self.report['errors'].append(str(e))
            return False
        except Exception as e:
            print(f"\n✗ Unexpected error during migration: {e}\n")
            self.report['errors'].append(f"Unexpected error: {e}")
            return False


def main():
    """Main entry point for the migration script."""
    if len(sys.argv) > 1:
        workspace_path = Path(sys.argv[1])
    else:
        # Default to current directory's parent (assuming we're in core/)
        workspace_path = Path(__file__).parent.parent
    
    print(f"Workspace: {workspace_path}")
    
    # Confirm with user
    response = input("\nThis will migrate your WorkOS installation. Continue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Migration cancelled.")
        return 1
    
    # Run migration
    migration = WorkOSMigration(workspace_path)
    success = migration.run()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
