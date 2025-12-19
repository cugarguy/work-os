#!/usr/bin/env python3
"""
Knowledge Graph Manager for Knowledge Base Management

This module provides functionality to manage knowledge documents with YAML
frontmatter, wikilinks, and graph traversal capabilities.
"""

import yaml
import re
import logging
from pathlib import Path
from typing import List, Dict, Optional, Set
from datetime import datetime
from dataclasses import dataclass, asdict
from wikilink_resolver import WikilinkResolver, WikiLink

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeDocument:
    """Represents a knowledge document with metadata"""
    title: str
    path: Path
    created_date: str
    updated_date: str
    tags: List[str]
    related_people: List[str]
    time_invested: int  # minutes
    content: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['path'] = str(self.path)
        return result


class KnowledgeManager:
    """
    Manage knowledge documents and wikilink relationships.
    
    Provides CRUD operations for knowledge documents, wikilink management,
    graph traversal, and full-text search capabilities.
    """
    
    def __init__(self, base_dir: Path):
        """
        Initialize the knowledge manager.
        
        Args:
            base_dir: Base directory containing the knowledge base
        """
        self.base_dir = Path(base_dir)
        self.knowledge_dir = self.base_dir / 'Knowledge'
        self.wikilink_resolver = WikilinkResolver(base_dir)
        
        # Ensure knowledge directory exists
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
    
    def create_knowledge(self, title: str, content: str, links: List[str], 
                        tags: Optional[List[str]] = None,
                        related_people: Optional[List[str]] = None) -> Path:
        """
        Create a new knowledge document with YAML frontmatter.
        
        Args:
            title: Document title
            content: Document content (markdown)
            links: List of wikilinks to include in content
            tags: Optional list of tags
            related_people: Optional list of related people (as wikilinks)
            
        Returns:
            Path to the created document
        """
        # Sanitize title for filename
        filename = self._sanitize_filename(title)
        doc_path = self.knowledge_dir / f"{filename}.md"
        
        # Check if document already exists
        if doc_path.exists():
            logger.warning(f"Document already exists: {doc_path}")
            return doc_path
        
        # Prepare metadata
        now = datetime.now().strftime('%Y-%m-%d')
        metadata = {
            'title': title,
            'created_date': now,
            'updated_date': now,
            'tags': tags or [],
            'related_people': related_people or [],
            'time_invested': 0
        }
        
        # Build document content with frontmatter
        doc_content = self._build_document(metadata, content)
        
        # Write document
        doc_path.write_text(doc_content, encoding='utf-8')
        logger.info(f"Created knowledge document: {doc_path}")
        
        return doc_path
    
    def update_knowledge(self, doc_id: str, updates: Dict) -> bool:
        """
        Update an existing knowledge document.
        
        Args:
            doc_id: Document identifier (filename without .md)
            updates: Dictionary of updates to apply
                    Can include: content, tags, related_people, time_invested
            
        Returns:
            True if update successful, False otherwise
        """
        # Resolve document path
        doc_path = self.wikilink_resolver.resolve_link(doc_id)
        if not doc_path or not doc_path.exists():
            logger.error(f"Document not found: {doc_id}")
            return False
        
        try:
            # Read existing document
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse frontmatter and content
            metadata, body = self._parse_document(content)
            
            # Apply updates
            if 'content' in updates:
                body = updates['content']
            if 'tags' in updates:
                metadata['tags'] = updates['tags']
            if 'related_people' in updates:
                metadata['related_people'] = updates['related_people']
            if 'time_invested' in updates:
                metadata['time_invested'] = updates['time_invested']
            
            # Update timestamp
            metadata['updated_date'] = datetime.now().strftime('%Y-%m-%d')
            
            # Rebuild document
            updated_content = self._build_document(metadata, body)
            
            # Write back
            doc_path.write_text(updated_content, encoding='utf-8')
            logger.info(f"Updated knowledge document: {doc_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating document {doc_id}: {e}")
            return False
    
    def add_wikilink(self, source: str, target: str, context: str = "") -> bool:
        """
        Add a wikilink from source document to target document.
        
        Args:
            source: Source document identifier
            target: Target document identifier
            context: Optional context text around the link
            
        Returns:
            True if link added successfully, False otherwise
        """
        # Resolve source document
        source_path = self.wikilink_resolver.resolve_link(source)
        if not source_path or not source_path.exists():
            logger.error(f"Source document not found: {source}")
            return False
        
        try:
            # Read source document
            with open(source_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if link already exists
            existing_links = self.wikilink_resolver.parse_wikilinks(content)
            if any(link.target.lower() == target.lower() for link in existing_links):
                logger.info(f"Link to {target} already exists in {source}")
                return True
            
            # Add the wikilink
            wikilink = f"[[{target}]]"
            if context:
                new_content = f"{content}\n\n{context} {wikilink}\n"
            else:
                new_content = f"{content}\n\n{wikilink}\n"
            
            # Write back
            source_path.write_text(new_content, encoding='utf-8')
            logger.info(f"Added wikilink from {source} to {target}")
            
            # Clear cache to ensure backlinks are updated
            self.wikilink_resolver.rebuild_backlink_index()
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding wikilink: {e}")
            return False
    
    def get_related_knowledge(self, doc_id: str, depth: int = 1) -> List[Dict]:
        """
        Get related knowledge documents by traversing the wikilink graph.
        
        Args:
            doc_id: Document identifier
            depth: How many levels deep to traverse (default 1)
            
        Returns:
            List of related documents with metadata
        """
        # Resolve document
        doc_path = self.wikilink_resolver.resolve_link(doc_id)
        if not doc_path or not doc_path.exists():
            logger.error(f"Document not found: {doc_id}")
            return []
        
        # Track visited documents to avoid cycles
        visited: Set[str] = set()
        related: List[Dict] = []
        
        # BFS traversal
        current_level = [(doc_id, 0)]
        
        while current_level:
            current_doc, current_depth = current_level.pop(0)
            
            # Skip if already visited or depth exceeded
            if current_doc.lower() in visited or current_depth > depth:
                continue
            
            visited.add(current_doc.lower())
            
            # Get document path
            current_path = self.wikilink_resolver.resolve_link(current_doc)
            if not current_path or not current_path.exists():
                continue
            
            # Skip the original document in results
            if current_depth > 0:
                try:
                    with open(current_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    metadata, _ = self._parse_document(content)
                    related.append({
                        'id': current_path.stem,
                        'title': metadata.get('title', current_path.stem),
                        'path': str(current_path),
                        'depth': current_depth,
                        'tags': metadata.get('tags', [])
                    })
                except Exception as e:
                    logger.error(f"Error reading {current_path}: {e}")
                    continue
            
            # Get outgoing links for next level
            if current_depth < depth:
                try:
                    with open(current_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    links = self.wikilink_resolver.parse_wikilinks(content)
                    for link in links:
                        if link.target.lower() not in visited:
                            current_level.append((link.target, current_depth + 1))
                except Exception as e:
                    logger.error(f"Error processing links in {current_path}: {e}")
        
        return related
    
    def search_knowledge(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search knowledge base using full-text search and connection ranking.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of matching documents ranked by relevance
        """
        results = []
        query_lower = query.lower()
        
        # Search all markdown files in knowledge directory
        for doc_path in self.knowledge_dir.glob('*.md'):
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse document
                metadata, body = self._parse_document(content)
                
                # Calculate relevance score
                score = 0
                
                # Title match (highest weight)
                title = metadata.get('title', doc_path.stem)
                if query_lower in title.lower():
                    score += 10
                
                # Tag match
                tags = metadata.get('tags', [])
                if any(query_lower in tag.lower() for tag in tags):
                    score += 5
                
                # Content match
                if query_lower in body.lower():
                    # Count occurrences
                    occurrences = body.lower().count(query_lower)
                    score += min(occurrences, 5)  # Cap at 5 points
                
                # Connection strength (number of links)
                links = self.wikilink_resolver.parse_wikilinks(content)
                backlinks = self.wikilink_resolver.get_backlinks(doc_path.stem)
                connection_count = len(links) + len(backlinks)
                score += min(connection_count, 3)  # Cap at 3 points
                
                # Only include if there's a match
                if score > 0:
                    results.append({
                        'id': doc_path.stem,
                        'title': title,
                        'path': str(doc_path),
                        'score': score,
                        'tags': tags,
                        'snippet': self._extract_snippet(body, query_lower)
                    })
                    
            except Exception as e:
                logger.error(f"Error searching {doc_path}: {e}")
                continue
        
        # Sort by score (descending) and limit results
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:max_results]
    
    def get_backlinks(self, doc_id: str) -> List[Dict]:
        """
        Get all documents that link to the specified document.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            List of backlink information
        """
        backlinks = self.wikilink_resolver.get_backlinks(doc_id)
        return [
            {
                'source': bl.source,
                'source_path': str(bl.source_path),
                'context': bl.context
            }
            for bl in backlinks
        ]
    
    def _sanitize_filename(self, title: str) -> str:
        """
        Sanitize title for use as filename.
        
        Args:
            title: Document title
            
        Returns:
            Sanitized filename (without extension)
        """
        # Replace invalid characters with spaces
        sanitized = re.sub(r'[<>:"/\\|?*]', ' ', title)
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
        # Sanitize tags to avoid YAML parsing issues
        if 'tags' in metadata and isinstance(metadata['tags'], list):
            metadata['tags'] = [self._sanitize_tag(tag) for tag in metadata['tags']]
        
        # Build YAML frontmatter
        yaml_str = yaml.dump(metadata, default_flow_style=False, allow_unicode=True)
        
        # Normalize content line endings
        normalized_content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        # Combine frontmatter and content
        return f"---\n{yaml_str}---\n\n{normalized_content}"
    
    def _sanitize_tag(self, tag: str) -> str:
        """
        Sanitize a tag to avoid YAML parsing issues.
        
        Args:
            tag: Tag string
            
        Returns:
            Sanitized tag
        """
        # Remove problematic characters that break YAML
        sanitized = tag.replace('---', '-').replace("'", '').replace('"', '')
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
    
    def _extract_snippet(self, text: str, query: str, context_chars: int = 100) -> str:
        """
        Extract a snippet of text around the query match.
        
        Args:
            text: Full text content
            query: Query string to find
            context_chars: Number of characters to include on each side
            
        Returns:
            Snippet with query highlighted
        """
        pos = text.lower().find(query)
        if pos == -1:
            # Return first N characters if no match
            return text[:context_chars * 2].strip() + "..."
        
        start = max(0, pos - context_chars)
        end = min(len(text), pos + len(query) + context_chars)
        
        snippet = text[start:end].strip()
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."
        
        return snippet
    
    def update_time_investment(self, doc_id: str, additional_minutes: int) -> bool:
        """
        Update the time_invested field in a knowledge document.
        
        This adds to the existing time investment rather than replacing it.
        
        Args:
            doc_id: Document identifier (filename without .md)
            additional_minutes: Minutes to add to time_invested
            
        Returns:
            True if update successful, False otherwise
        """
        # Resolve document path
        doc_path = self.wikilink_resolver.resolve_link(doc_id)
        if not doc_path or not doc_path.exists():
            logger.error(f"Document not found: {doc_id}")
            return False
        
        try:
            # Read existing document
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse frontmatter and content
            metadata, body = self._parse_document(content)
            
            # Update time_invested
            current_time = metadata.get('time_invested', 0)
            metadata['time_invested'] = current_time + additional_minutes
            
            # Update timestamp
            metadata['updated_date'] = datetime.now().strftime('%Y-%m-%d')
            
            # Rebuild document
            updated_content = self._build_document(metadata, body)
            
            # Write back
            doc_path.write_text(updated_content, encoding='utf-8')
            logger.info(f"Updated time investment for {doc_id}: +{additional_minutes} minutes")
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating time investment for {doc_id}: {e}")
            return False
    
    def get_time_investment(self, doc_id: str) -> Optional[int]:
        """
        Get the current time_invested value for a knowledge document.
        
        Args:
            doc_id: Document identifier (filename without .md)
            
        Returns:
            Time invested in minutes, or None if document not found
        """
        # Resolve document path
        doc_path = self.wikilink_resolver.resolve_link(doc_id)
        if not doc_path or not doc_path.exists():
            logger.error(f"Document not found: {doc_id}")
            return None
        
        try:
            # Read document
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse frontmatter
            metadata, _ = self._parse_document(content)
            
            return metadata.get('time_invested', 0)
            
        except Exception as e:
            logger.error(f"Error reading time investment for {doc_id}: {e}")
            return None
