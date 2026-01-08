#!/usr/bin/env python3
"""
People Network Manager for People Profile Management

This module provides functionality to manage person profiles with YAML
frontmatter, wikilinks to knowledge, and person-to-person relationships.
"""

import yaml
import re
import logging
from pathlib import Path
from typing import List, Dict, Optional, Set
from datetime import datetime
from dataclasses import dataclass, asdict
from wikilink_resolver import WikilinkResolver

logger = logging.getLogger(__name__)


@dataclass
class PersonProfile:
    """Represents a person profile with metadata"""
    name: str
    path: Path
    role: Optional[str]
    team: Optional[str]
    created_date: str
    updated_date: str
    expertise_areas: List[str]
    relationships: List[Dict[str, str]]
    total_collaboration_time: int  # minutes
    content: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['path'] = str(self.path)
        return result


class PeopleManager:
    """
    Manage person profiles and relationship connections.
    
    Provides CRUD operations for person profiles, person-to-knowledge linking,
    person-to-person relationships, and expertise discovery.
    """
    
    def __init__(self, base_dir: Path):
        """
        Initialize the people manager.
        
        Args:
            base_dir: Base directory containing the people network
        """
        self.base_dir = Path(base_dir)
        self.people_dir = self.base_dir / 'People'
        self.wikilink_resolver = WikilinkResolver(base_dir)
        
        # Ensure people directory exists
        self.people_dir.mkdir(parents=True, exist_ok=True)
    
    def create_person(self, name: str, metadata: Optional[Dict] = None) -> Path:
        """
        Create a new person profile with structured metadata.
        
        Args:
            name: Person's name
            metadata: Optional metadata dictionary containing:
                     - role: Job role/title
                     - team: Team name
                     - expertise_areas: List of knowledge area wikilinks
                     - relationships: List of relationship dicts
                     - content: Profile content (markdown)
            
        Returns:
            Path to the created profile
        """
        # Sanitize name for filename
        filename = self._sanitize_filename(name)
        person_path = self.people_dir / f"{filename}.md"
        
        # Check if profile already exists
        if person_path.exists():
            logger.warning(f"Person profile already exists: {person_path}")
            return person_path
        
        # Prepare metadata with defaults
        now = datetime.now().strftime('%Y-%m-%d')
        profile_metadata = {
            'name': name,
            'role': metadata.get('role') if metadata else None,
            'team': metadata.get('team') if metadata else None,
            'created_date': now,
            'updated_date': now,
            'expertise_areas': metadata.get('expertise_areas', []) if metadata else [],
            'relationships': metadata.get('relationships', []) if metadata else [],
            'total_collaboration_time': 0
        }
        
        # Get content
        content = metadata.get('content', f"# {name}\n\n## Overview\n\n") if metadata else f"# {name}\n\n## Overview\n\n"
        
        # Build document content with frontmatter
        doc_content = self._build_document(profile_metadata, content)
        
        # Write document
        person_path.write_text(doc_content, encoding='utf-8')
        logger.info(f"Created person profile: {person_path}")
        
        return person_path
    
    def update_person(self, person_id: str, updates: Dict) -> bool:
        """
        Update an existing person profile.
        
        Args:
            person_id: Person identifier (filename without .md)
            updates: Dictionary of updates to apply
                    Can include: content, role, team, expertise_areas,
                                relationships, total_collaboration_time
            
        Returns:
            True if update successful, False otherwise
        """
        # Resolve person path
        person_path = self.wikilink_resolver.resolve_link(person_id)
        if not person_path or not person_path.exists():
            logger.error(f"Person profile not found: {person_id}")
            return False
        
        try:
            # Read existing profile
            with open(person_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse frontmatter and content
            metadata, body = self._parse_document(content)
            
            # Apply updates
            if 'content' in updates:
                body = updates['content']
            if 'role' in updates:
                metadata['role'] = updates['role']
            if 'team' in updates:
                metadata['team'] = updates['team']
            if 'expertise_areas' in updates:
                metadata['expertise_areas'] = updates['expertise_areas']
            if 'relationships' in updates:
                metadata['relationships'] = updates['relationships']
            if 'total_collaboration_time' in updates:
                metadata['total_collaboration_time'] = updates['total_collaboration_time']
            
            # Update timestamp
            metadata['updated_date'] = datetime.now().strftime('%Y-%m-%d')
            
            # Rebuild document
            updated_content = self._build_document(metadata, body)
            
            # Write back
            person_path.write_text(updated_content, encoding='utf-8')
            logger.info(f"Updated person profile: {person_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating person profile {person_id}: {e}")
            return False
    
    def link_to_knowledge(self, person_id: str, knowledge_id: str, context: str = "") -> bool:
        """
        Link a person to a knowledge document (bidirectional).
        
        Args:
            person_id: Person identifier
            knowledge_id: Knowledge document identifier
            context: Optional context for the link
            
        Returns:
            True if link created successfully, False otherwise
        """
        # Resolve person path
        person_path = self.wikilink_resolver.resolve_link(person_id)
        if not person_path or not person_path.exists():
            logger.error(f"Person profile not found: {person_id}")
            return False
        
        # Resolve knowledge path
        knowledge_path = self.wikilink_resolver.resolve_link(knowledge_id)
        if not knowledge_path or not knowledge_path.exists():
            logger.error(f"Knowledge document not found: {knowledge_id}")
            return False
        
        try:
            # Update person profile - add to expertise_areas
            with open(person_path, 'r', encoding='utf-8') as f:
                person_content = f.read()
            
            person_metadata, person_body = self._parse_document(person_content)
            expertise_areas = person_metadata.get('expertise_areas', [])
            
            # Add knowledge link if not already present
            knowledge_link = f"[[{knowledge_id}]]"
            if knowledge_link not in expertise_areas:
                expertise_areas.append(knowledge_link)
                person_metadata['expertise_areas'] = expertise_areas
                person_metadata['updated_date'] = datetime.now().strftime('%Y-%m-%d')
                
                # Rebuild and save person profile
                updated_person = self._build_document(person_metadata, person_body)
                person_path.write_text(updated_person, encoding='utf-8')
                logger.info(f"Added {knowledge_id} to {person_id}'s expertise areas")
            
            # Update knowledge document - add to related_people
            with open(knowledge_path, 'r', encoding='utf-8') as f:
                knowledge_content = f.read()
            
            knowledge_metadata, knowledge_body = self._parse_document(knowledge_content)
            related_people = knowledge_metadata.get('related_people', [])
            
            # Add person link if not already present
            person_link = f"[[{person_id}]]"
            if person_link not in related_people:
                related_people.append(person_link)
                knowledge_metadata['related_people'] = related_people
                knowledge_metadata['updated_date'] = datetime.now().strftime('%Y-%m-%d')
                
                # Rebuild and save knowledge document
                updated_knowledge = self._build_document(knowledge_metadata, knowledge_body)
                knowledge_path.write_text(updated_knowledge, encoding='utf-8')
                logger.info(f"Added {person_id} to {knowledge_id}'s related people")
            
            # Clear cache to ensure backlinks are updated
            self.wikilink_resolver.rebuild_backlink_index()
            
            return True
            
        except Exception as e:
            logger.error(f"Error linking person to knowledge: {e}")
            return False
    
    def link_people(self, person1_id: str, person2_id: str, relationship: str, context: str = "") -> bool:
        """
        Create a relationship link between two people.
        
        Args:
            person1_id: First person identifier
            person2_id: Second person identifier
            relationship: Type of relationship (e.g., "collaborator", "reports_to", "manager")
            context: Optional context describing the relationship
            
        Returns:
            True if relationship created successfully, False otherwise
        """
        # Resolve both person paths
        person1_path = self.wikilink_resolver.resolve_link(person1_id)
        person2_path = self.wikilink_resolver.resolve_link(person2_id)
        
        if not person1_path or not person1_path.exists():
            logger.error(f"Person profile not found: {person1_id}")
            return False
        if not person2_path or not person2_path.exists():
            logger.error(f"Person profile not found: {person2_id}")
            return False
        
        try:
            # Update person1's relationships
            with open(person1_path, 'r', encoding='utf-8') as f:
                person1_content = f.read()
            
            person1_metadata, person1_body = self._parse_document(person1_content)
            relationships = person1_metadata.get('relationships', [])
            
            # Check if relationship already exists
            existing = any(
                r.get('person') == f"[[{person2_id}]]" and r.get('type') == relationship
                for r in relationships
            )
            
            if not existing:
                # Add new relationship
                new_relationship = {
                    'person': f"[[{person2_id}]]",
                    'type': relationship,
                    'context': context
                }
                relationships.append(new_relationship)
                person1_metadata['relationships'] = relationships
                person1_metadata['updated_date'] = datetime.now().strftime('%Y-%m-%d')
                
                # Rebuild and save
                updated_person1 = self._build_document(person1_metadata, person1_body)
                person1_path.write_text(updated_person1, encoding='utf-8')
                logger.info(f"Added relationship from {person1_id} to {person2_id}: {relationship}")
            
            # Clear cache
            self.wikilink_resolver.rebuild_backlink_index()
            
            return True
            
        except Exception as e:
            logger.error(f"Error linking people: {e}")
            return False
    
    def get_person_network(self, person_id: str) -> Dict:
        """
        Get a person's complete network including knowledge and people connections.
        
        Args:
            person_id: Person identifier
            
        Returns:
            Dictionary containing person metadata, expertise areas, and relationships
        """
        # Resolve person path
        person_path = self.wikilink_resolver.resolve_link(person_id)
        if not person_path or not person_path.exists():
            logger.error(f"Person profile not found: {person_id}")
            return {}
        
        try:
            with open(person_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            metadata, body = self._parse_document(content)
            
            # Build network information
            network = {
                'id': person_id,
                'name': metadata.get('name', person_id),
                'role': metadata.get('role'),
                'team': metadata.get('team'),
                'expertise_areas': metadata.get('expertise_areas', []),
                'relationships': metadata.get('relationships', []),
                'total_collaboration_time': metadata.get('total_collaboration_time', 0),
                'created_date': metadata.get('created_date'),
                'updated_date': metadata.get('updated_date')
            }
            
            return network
            
        except Exception as e:
            logger.error(f"Error getting person network for {person_id}: {e}")
            return {}
    
    def find_expertise(self, topic: str) -> List[Dict]:
        """
        Find people with expertise in a given topic.
        
        Searches for people connected to knowledge documents matching the topic.
        
        Args:
            topic: Topic or knowledge area to search for
            
        Returns:
            List of people with expertise in the topic, ranked by connection strength
        """
        results = []
        topic_lower = topic.lower()
        
        # Search all person profiles
        for person_path in self.people_dir.glob('*.md'):
            try:
                with open(person_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                metadata, body = self._parse_document(content)
                
                # Check expertise areas for topic match
                expertise_areas = metadata.get('expertise_areas', [])
                
                # Count matches
                match_count = 0
                for area in expertise_areas:
                    # Extract knowledge ID from wikilink
                    area_clean = area.replace('[[', '').replace(']]', '')
                    if topic_lower in area_clean.lower():
                        match_count += 1
                
                # Also check body content for topic mentions
                if topic_lower in body.lower():
                    match_count += 1
                
                if match_count > 0:
                    results.append({
                        'id': person_path.stem,
                        'name': metadata.get('name', person_path.stem),
                        'role': metadata.get('role'),
                        'team': metadata.get('team'),
                        'expertise_areas': expertise_areas,
                        'match_count': match_count
                    })
                    
            except Exception as e:
                logger.error(f"Error searching {person_path}: {e}")
                continue
        
        # Sort by match count (descending)
        results.sort(key=lambda x: x['match_count'], reverse=True)
        return results
    
    def _sanitize_filename(self, name: str) -> str:
        """
        Sanitize name for use as filename.
        
        Args:
            name: Person's name
            
        Returns:
            Sanitized filename (without extension)
        """
        # Replace invalid characters with spaces
        sanitized = re.sub(r'[<>:"/\\|?*]', ' ', name)
        # Collapse multiple spaces
        sanitized = re.sub(r'\s+', ' ', sanitized)
        # Trim and limit length
        sanitized = sanitized.strip()[:200]
        return sanitized
    
    def _build_document(self, metadata: Dict, content: str) -> str:
        """
        Build a complete markdown document with YAML frontmatter.
        
        Args:
            metadata: Document metadata dictionary
            content: Document body content
            
        Returns:
            Complete document string
        """
        # Sanitize name to avoid YAML parsing issues
        if 'name' in metadata and isinstance(metadata['name'], str):
            metadata['name'] = self._sanitize_yaml_string(metadata['name'])
        
        # Build YAML frontmatter
        yaml_str = yaml.dump(metadata, default_flow_style=False, allow_unicode=True)
        
        # Normalize content line endings
        normalized_content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        # Combine frontmatter and content
        return f"---\n{yaml_str}---\n\n{normalized_content}"
    
    def _sanitize_yaml_string(self, value: str) -> str:
        """
        Sanitize a string to avoid YAML parsing issues.
        
        Args:
            value: String to sanitize
            
        Returns:
            Sanitized string
        """
        # Replace problematic characters that break YAML
        sanitized = value.replace('---', '-').replace("'", '').replace('"', '')
        return sanitized.strip()
    
    def _parse_document(self, content: str) -> tuple[Dict, str]:
        """
        Parse a markdown document with YAML frontmatter.
        
        Args:
            content: Full document content
            
        Returns:
            Tuple of (metadata dict, body content)
        """
        # Check for frontmatter
        if not content.startswith('---'):
            return {}, content
        
        # Find end of frontmatter
        parts = content.split('---', 2)
        if len(parts) < 3:
            return {}, content
        
        # Parse YAML
        try:
            metadata = yaml.safe_load(parts[1])
            if metadata is None:
                metadata = {}
            body = parts[2].strip()
            return metadata, body
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML frontmatter: {e}")
            return {}, content
