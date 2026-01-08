# Wikilink Resolver

The Wikilink Resolver provides functionality for parsing, resolving, and validating wikilink references in markdown documents. It supports bidirectional linking and backlink tracking for the WorkOS knowledge base.

## Features

- **Parse wikilinks**: Extract `[[wikilink]]` and `[[target|display]]` syntax from markdown
- **Resolve links**: Find the actual file path for a wikilink target
- **Validate links**: Detect broken or missing links
- **Track backlinks**: Find all documents that link to a target document
- **Bidirectional linking**: Automatically maintain bidirectional relationships

## Usage

### Basic Usage

```python
from pathlib import Path
from wikilink_resolver import WikilinkResolver

# Initialize resolver with base directory
resolver = WikilinkResolver(Path('/path/to/workos'))

# Parse wikilinks from content
content = "This links to [[Knowledge Document]] and [[Person|John Smith]]."
links = resolver.parse_wikilinks(content)

for link in links:
    print(f"Target: {link.target}, Display: {link.display_text}")

# Resolve a link to a file path
path = resolver.resolve_link('Knowledge Document')
if path:
    print(f"Found at: {path}")

# Get backlinks for a document
backlinks = resolver.get_backlinks('Knowledge Document')
for backlink in backlinks:
    print(f"Linked from: {backlink.source}")
    print(f"Context: {backlink.context}")

# Validate all links in a document
broken = resolver.validate_links(Path('Knowledge/My Document.md'))
if broken:
    print(f"Found {len(broken)} broken links")
```

### Advanced Usage

```python
# Get all incoming and outgoing links for a document
doc_path = Path('Knowledge/My Document.md')
all_links = resolver.get_all_links_in_document(doc_path)

print(f"Outgoing links: {len(all_links['outgoing'])}")
for link in all_links['outgoing']:
    print(f"  -> {link.target}")

print(f"Incoming links: {len(all_links['incoming'])}")
for backlink in all_links['incoming']:
    print(f"  <- {backlink.source}")

# Rebuild the backlink index after bulk changes
resolver.rebuild_backlink_index()
```

## Wikilink Syntax

The resolver supports two wikilink formats:

1. **Simple link**: `[[Target Document]]`
   - Links to a document named "Target Document.md"
   - Display text is the same as the target

2. **Link with display text**: `[[Target Document|Custom Display]]`
   - Links to "Target Document.md"
   - Shows "Custom Display" as the link text

## Link Resolution

The resolver searches for target documents in the following order:

1. `Knowledge/` directory
2. `People/` directory  
3. Base directory

Link resolution is **case-insensitive** for better usability.

## Testing

The wikilink resolver includes comprehensive test coverage:

### Property-Based Tests (Hypothesis)

Property-based tests verify universal properties across randomly generated inputs:

- **Property 1: Wikilink Bidirectionality** - If document A links to B, then B's backlinks include A
- **Property 3: Complete Link Display** - All incoming and outgoing links are returned when viewing a document

Run property tests:
```bash
pytest test_wikilink_properties.py -v
```

### Unit Tests

Unit tests verify specific examples and edge cases:

- Parsing various wikilink formats
- Resolving links in different directories
- Case-insensitive resolution
- Broken link detection
- Backlink tracking

Run unit tests:
```bash
pytest test_wikilink_resolver.py -v
```

Run all tests:
```bash
pytest test_wikilink*.py -v
```

## Implementation Details

### Caching

The resolver caches:
- **Link resolution results**: Avoids repeated file system searches
- **Backlink index**: Builds on-demand and caches for performance

Clear caches with `rebuild_backlink_index()` after bulk changes.

### Performance

- Link resolution: O(1) after first lookup (cached)
- Backlink lookup: O(n) where n = number of markdown files (builds index on first request)
- Parsing: O(m) where m = content length

### Thread Safety

The current implementation is **not thread-safe**. If you need concurrent access, wrap operations in locks or use separate resolver instances per thread.

## Requirements

- Python 3.10+
- No external dependencies for core functionality
- `hypothesis` and `pytest` for testing

## Integration with WorkOS

The wikilink resolver is designed to integrate with the WorkOS knowledge and time intelligence system:

- Works with `Knowledge/` and `People/` directories
- Supports the knowledge graph manager
- Enables bidirectional linking between documents
- Provides foundation for related topic discovery

## Future Enhancements

Potential improvements:
- File system watchers for automatic cache invalidation
- Fuzzy matching for link suggestions
- Link suggestion based on content analysis
- Export to graph visualization formats
- Support for external link types (URLs, file paths)
