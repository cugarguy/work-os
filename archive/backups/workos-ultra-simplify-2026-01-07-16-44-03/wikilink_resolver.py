#!/usr/bin/env python3
"""
Wikilink Parser and Resolver for Knowledge Base Management

This module provides functionality to parse, resolve, and validate wikilink
references in markdown documents. It supports bidirectional linking and
backlink tracking.
"""

import re
import logging
from pathlib import Path
from typing import List, Optional, Dict, Set
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class WikiLink:
    """Represents a parsed wikilink"""
    target: str  # The target document name
    display_text: Optional[str] = None  # Optional display text (for [[target|display]] syntax)
    source_file: Optional[Path] = None  # The file containing this link
    
    def __str__(self):
        if self.display_text:
            return f"[[{self.target}|{self.display_text}]]"
        return f"[[{self.target}]]"


@dataclass
class BackLink:
    """Represents a backlink from one document to another"""
    source: str  # The document containing the link
    source_path: Path  # Full path to source document
    context: str  # Surrounding text context
    

class WikilinkResolver:
    """
    Parse, validate, and resolve wikilink references in markdown documents.
    
    Supports:
    - [[simple links]]
    - [[target|display text]]
    - Bidirectional link tracking
    - Broken link detection
    """
    
    # Regex pattern for wikilinks: [[target]] or [[target|display]]
    WIKILINK_PATTERN = re.compile(r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]')
    
    def __init__(self, base_dir: Path):
        """
        Initialize the wikilink resolver.
        
        Args:
            base_dir: Base directory containing markdown files
        """
        self.base_dir = Path(base_dir)
        self._backlink_index: Dict[str, List[BackLink]] = {}
        self._link_cache: Dict[str, Optional[Path]] = {}
        
    def parse_wikilinks(self, content: str, source_file: Optional[Path] = None) -> List[WikiLink]:
        """
        Extract all wikilinks from markdown content.
        
        Args:
            content: Markdown content to parse
            source_file: Optional path to the source file
            
        Returns:
            List of WikiLink objects found in the content
        """
        links = []
        for match in self.WIKILINK_PATTERN.finditer(content):
            target = match.group(1).strip()
            display_text = match.group(2).strip() if match.group(2) else None
            links.append(WikiLink(
                target=target,
                display_text=display_text,
                source_file=source_file
            ))
        return links
    
    def resolve_link(self, link_text: str) -> Optional[Path]:
        """
        Resolve a wikilink to an actual file path.
        
        Searches for the target file in:
        1. Knowledge/ directory
        2. People/ directory
        3. Base directory
        
        Args:
            link_text: The target text from the wikilink (without brackets)
            
        Returns:
            Path to the resolved file, or None if not found
        """
        # Check cache first
        if link_text in self._link_cache:
            return self._link_cache[link_text]
        
        # Normalize the link text
        normalized = link_text.strip()
        
        # Search paths in order of priority
        search_dirs = [
            self.base_dir / 'Knowledge',
            self.base_dir / 'People',
            self.base_dir
        ]
        
        # Try exact match with .md extension
        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
                
            # Try exact filename match
            target_path = search_dir / f"{normalized}.md"
            if target_path.exists():
                self._link_cache[link_text] = target_path
                return target_path
            
            # Try case-insensitive match
            for file_path in search_dir.glob('*.md'):
                if file_path.stem.lower() == normalized.lower():
                    self._link_cache[link_text] = file_path
                    return file_path
        
        # Not found
        self._link_cache[link_text] = None
        return None
    
    def validate_links(self, doc_path: Path) -> List[Dict[str, str]]:
        """
        Validate all wikilinks in a document.
        
        Args:
            doc_path: Path to the document to validate
            
        Returns:
            List of broken links with details
        """
        if not doc_path.exists():
            return [{'error': f'Document not found: {doc_path}'}]
        
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Error reading {doc_path}: {e}")
            return [{'error': f'Could not read document: {e}'}]
        
        broken_links = []
        links = self.parse_wikilinks(content, doc_path)
        
        for link in links:
            resolved_path = self.resolve_link(link.target)
            if resolved_path is None:
                broken_links.append({
                    'link': str(link),
                    'target': link.target,
                    'source': str(doc_path),
                    'reason': 'Target document not found'
                })
        
        return broken_links
    
    def get_backlinks(self, target: str) -> List[BackLink]:
        """
        Get all documents that link to the target document.
        
        Args:
            target: The target document name (without .md extension)
            
        Returns:
            List of BackLink objects
        """
        # Check if we have cached backlinks
        if target in self._backlink_index:
            return self._backlink_index[target]
        
        # Build backlink index for this target
        backlinks = []
        
        # Search all markdown files - use consolidated knowledgebase
        for search_dir in [
            self.base_dir / 'knowledgebase' / '-common' / 'Topics',
            self.base_dir / 'knowledgebase' / '-common' / 'People', 
            self.base_dir / 'knowledgebase' / '-common' / 'Tasks',
            self.base_dir / 'knowledgebase' / '-common',
            self.base_dir
        ]:
            if not search_dir.exists():
                continue
                
            for file_path in search_dir.glob('*.md'):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    links = self.parse_wikilinks(content, file_path)
                    for link in links:
                        # Check if this link points to our target
                        if link.target.lower() == target.lower():
                            # Extract context around the link
                            context = self._extract_context(content, str(link))
                            backlinks.append(BackLink(
                                source=file_path.stem,
                                source_path=file_path,
                                context=context
                            ))
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
                    continue
        
        # Cache the results
        self._backlink_index[target] = backlinks
        return backlinks
    
    def _extract_context(self, content: str, link_str: str, context_chars: int = 100) -> str:
        """
        Extract surrounding context for a link.
        
        Args:
            content: Full document content
            link_str: The link string to find
            context_chars: Number of characters to include on each side
            
        Returns:
            Context string with the link highlighted
        """
        try:
            pos = content.find(link_str)
            if pos == -1:
                return ""
            
            start = max(0, pos - context_chars)
            end = min(len(content), pos + len(link_str) + context_chars)
            
            context = content[start:end]
            # Clean up context
            context = context.replace('\n', ' ').strip()
            
            return f"...{context}..."
        except Exception:
            return ""
    
    def rebuild_backlink_index(self):
        """
        Rebuild the entire backlink index by scanning all documents.
        
        This is useful after bulk changes to the knowledge base.
        """
        self._backlink_index.clear()
        self._link_cache.clear()
        
        # We'll rebuild lazily as backlinks are requested
        logger.info("Backlink index cleared, will rebuild on demand")
    
    def get_all_links_in_document(self, doc_path: Path) -> Dict[str, List[WikiLink]]:
        """
        Get all outgoing and incoming links for a document.
        
        Args:
            doc_path: Path to the document
            
        Returns:
            Dictionary with 'outgoing' and 'incoming' link lists
        """
        result = {
            'outgoing': [],
            'incoming': []
        }
        
        if not doc_path.exists():
            return result
        
        # Get outgoing links
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            result['outgoing'] = self.parse_wikilinks(content, doc_path)
        except Exception as e:
            logger.error(f"Error reading {doc_path}: {e}")
        
        # Get incoming links (backlinks)
        doc_name = doc_path.stem
        backlinks = self.get_backlinks(doc_name)
        result['incoming'] = backlinks
        
        return result
