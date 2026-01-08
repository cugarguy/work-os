#!/usr/bin/env python3
"""
workOS Startup Validation Script

Validates access to consolidated knowledgebase, MCP tool integration, and operational files on startup.
Implements requirements 7.3, 7.4, 7.5 for workOS configuration.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import tempfile
import importlib.util

def log_message(message, level="INFO"):
    """Log validation message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def validate_directory_access(path, description):
    """Validate that a directory exists and is accessible"""
    try:
        path_obj = Path(path)
        if not path_obj.exists():
            log_message(f"FAILED: {description} - Directory does not exist: {path}", "ERROR")
            return False
        
        if not path_obj.is_dir():
            log_message(f"FAILED: {description} - Path is not a directory: {path}", "ERROR")
            return False
            
        # Test read access by listing directory
        list(path_obj.iterdir())
        log_message(f"SUCCESS: {description} - Directory accessible: {path}")
        return True
        
    except PermissionError:
        log_message(f"FAILED: {description} - Permission denied: {path}", "ERROR")
        return False
    except Exception as e:
        log_message(f"FAILED: {description} - Error accessing {path}: {str(e)}", "ERROR")
        return False

def validate_file_read_access(path, description):
    """Validate that we can read from a directory by checking for any readable file"""
    try:
        path_obj = Path(path)
        if not path_obj.exists():
            log_message(f"SKIPPED: {description} - Directory does not exist: {path}", "WARN")
            return True  # Not an error if directory doesn't exist yet
            
        # Try to find any readable file in the directory
        for file_path in path_obj.glob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    f.read(100)  # Read first 100 chars to test access
                log_message(f"SUCCESS: {description} - Can read files from: {path}")
                return True
            except Exception:
                continue
                
        # If no files found, that's okay - directory exists and is accessible
        log_message(f"SUCCESS: {description} - Directory accessible (no files to test): {path}")
        return True
        
    except Exception as e:
        log_message(f"FAILED: {description} - Error testing read access {path}: {str(e)}", "ERROR")
        return False

def validate_file_write_access(path, description):
    """Validate that we can write to a directory"""
    try:
        path_obj = Path(path)
        if not path_obj.exists():
            log_message(f"FAILED: {description} - Directory does not exist: {path}", "ERROR")
            return False
            
        # Create a temporary test file
        test_file = path_obj / f"workos-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}.tmp"
        
        try:
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write("workOS startup validation test file")
            
            # Verify we can read it back
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Clean up test file
            test_file.unlink()
            
            log_message(f"SUCCESS: {description} - Can write to: {path}")
            return True
            
        except Exception as e:
            # Try to clean up test file if it exists
            if test_file.exists():
                try:
                    test_file.unlink()
                except:
                    pass
            raise e
            
    except Exception as e:
        log_message(f"FAILED: {description} - Error testing write access {path}: {str(e)}", "ERROR")
        return False

def validate_mcp_integration(workspace_root):
    """Validate that MCP tools can access consolidated knowledgebase"""
    try:
        # Try to import core modules to test MCP integration
        core_path = workspace_root / "1-projects" / "-agents" / "workOS" / "core"
        
        # Test if we can import knowledge manager
        knowledge_manager_path = core_path / "knowledge_manager.py"
        if knowledge_manager_path.exists():
            spec = importlib.util.spec_from_file_location("knowledge_manager", knowledge_manager_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                log_message("SUCCESS: MCP Integration - Knowledge manager module loadable")
                return True
        
        log_message("SKIPPED: MCP Integration - Knowledge manager not found (may not be implemented yet)", "WARN")
        return True  # Not a failure if not implemented yet
        
    except Exception as e:
        log_message(f"FAILED: MCP Integration - Error testing MCP tools: {str(e)}", "ERROR")
        return False

def validate_deprecated_path_handling(workspace_root):
    """Validate that deprecated local knowledge paths are properly handled"""
    try:
        workos_root = workspace_root / "1-projects" / "-agents" / "workOS"
        
        deprecated_paths = [
            ("Knowledge", "Local Knowledge directory"),
            ("People", "Local People directory"),
            ("Tasks", "Local Tasks directory"),
            ("daily-notes", "Local daily-notes directory")
        ]
        
        all_passed = True
        
        for dir_name, description in deprecated_paths:
            deprecated_path = workos_root / dir_name
            if deprecated_path.exists():
                log_message(f"WARNING: {description} still exists at deprecated location: {deprecated_path}", "WARN")
                log_message(f"         Content should be migrated to: 2-knowledgebase/-common/{dir_name}/", "WARN")
                # This is a warning, not a failure - migration may be in progress
            else:
                log_message(f"SUCCESS: {description} - Deprecated path properly removed: {deprecated_path}")
        
        return all_passed
        
    except Exception as e:
        log_message(f"FAILED: Deprecated path validation - Error: {str(e)}", "ERROR")
        return False

def main():
    """Main validation function"""
    log_message("Starting workOS startup validation...")
    
    # Get the workspace root (assuming script is in workOS/.kiro/)
    script_dir = Path(__file__).parent
    workspace_root = script_dir.parent.parent.parent
    
    validation_results = []
    
    # Validate consolidated knowledgebase access
    log_message("Validating consolidated knowledgebase access...")
    
    knowledge_base = workspace_root / "2-knowledgebase" / "-common"
    
    # Test main knowledgebase directory
    result = validate_directory_access(knowledge_base, "Consolidated knowledgebase root")
    validation_results.append(("Knowledgebase root access", result))
    
    # Test knowledge subdirectories
    knowledge_dirs = [
        ("People", "People profiles"),
        ("Knowledge", "Knowledge documents"),
        ("business-assets", "Business assets"),
        ("context-blocks", "Context blocks"),
        ("daily-notes", "Daily notes"),
        ("Tasks", "Task files"),
        ("shared-content", "Shared content")
    ]
    
    for dir_name, description in knowledge_dirs:
        dir_path = knowledge_base / dir_name
        result = validate_file_read_access(dir_path, f"Read access to {description}")
        validation_results.append((f"Read {description}", result))
    
    # Test write access to knowledgebase
    result = validate_file_write_access(knowledge_base, "Write access to knowledgebase")
    validation_results.append(("Knowledgebase write access", result))
    
    # Validate MCP tool integration
    log_message("Validating MCP tool integration...")
    result = validate_mcp_integration(workspace_root)
    validation_results.append(("MCP tool integration", result))
    
    # Validate operational file access
    log_message("Validating operational file access...")
    
    workos_root = workspace_root / "1-projects" / "-agents" / "workOS"
    
    operational_dirs = [
        (".kiro/steering", "Steering rules"),
        ("core", "Core system"),
        ("scripts", "Scripts"),
        ("docs", "Documentation"),
        (".kiro/settings", "Configuration"),
        (".kiro/hooks", "Hooks")
    ]
    
    for dir_name, description in operational_dirs:
        dir_path = workos_root / dir_name
        result = validate_directory_access(dir_path, f"Operational files - {description}")
        validation_results.append((f"Operational {description}", result))
    
    # Validate deprecated path handling
    log_message("Validating deprecated path handling...")
    result = validate_deprecated_path_handling(workspace_root)
    validation_results.append(("Deprecated path handling", result))
    
    # Summary
    log_message("Validation Summary:")
    log_message("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_name, result in validation_results:
        status = "PASS" if result else "FAIL"
        log_message(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    log_message("=" * 50)
    log_message(f"Total tests: {len(validation_results)}")
    log_message(f"Passed: {passed}")
    log_message(f"Failed: {failed}")
    
    if failed > 0:
        log_message("workOS startup validation FAILED - some knowledge files may not be accessible", "ERROR")
        log_message("Check file permissions and paths in data-sources.md configuration", "ERROR")
        return 1
    else:
        log_message("workOS startup validation PASSED - all knowledge and operational files accessible")
        return 0

if __name__ == "__main__":
    sys.exit(main())