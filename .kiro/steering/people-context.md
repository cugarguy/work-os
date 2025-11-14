---
inclusion: fileMatch
fileMatchPattern: "People/*.md"
---

# People File Context

When working with person files in the People/ directory:

## File Naming Convention

Use format: `[FirstName LastName].md`

Examples:
- `John Smith.md`
- `Sarah Chen.md`

## File Structure

Person files should include:
- **Contact Info**: Email, phone, role, organization
- **Relationship Context**: How you know them, their role in your work
- **Meeting History**: Date-stamped notes from interactions
- **Topics & Interests**: Key themes, projects, areas of expertise
- **Notes & Insights**: Observations, communication preferences
- **Related Tasks/Projects**: Links to Tasks/ files

## Integration with Tasks

- Reference people in task files using `People/[Name].md` in resource_refs
- Link tasks to people for stakeholder context
- Use people files to track follow-ups and action items from meetings

## Best Practices

1. **Update after meetings** - Add notes while context is fresh
2. **Link bidirectionally** - Reference tasks in person files and people in task files
3. **Track action items** - Note commitments and follow-ups
4. **Maintain context** - Record key decisions and discussion points
5. **Respect privacy** - These files contain personal interaction data

## When Creating Person Files

- Use the template from `core/templates/person.md`
- Fill in known contact information
- Add initial relationship context
- Link to any existing related tasks

## When Updating Person Files

- Add meeting notes with dates
- Update relationship context as it evolves
- Link new tasks or projects
- Note any changes in role or contact info
