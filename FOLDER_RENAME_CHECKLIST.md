# Folder Rename Checklist: personal-os → work-os

## Current Situation
- **Current Path**: `/Users/bsteeger/Documents/1-projects/workOS/personal-os`
- **Target Path**: `/Users/bsteeger/Documents/1-projects/workOS/work-os`
- **Status**: MCP config already updated with new path ✅

## Step-by-Step Process

### 1. Close Kiro
- [x] Save any open files
- [x] Close Kiro completely (Cmd+Q)
- [x] Verify Kiro is fully closed

### 2. Rename the Folder
Open Terminal and run:
```bash
cd /Users/bsteeger/Documents/1-projects/workOS
mv personal-os work-os
```

### 3. Verify the Rename
```bash
ls -la /Users/bsteeger/Documents/1-projects/workOS/work-os
```
You should see all your files in the new location.

### 4. Reopen in Kiro
- [x] Open Kiro
- [x] File → Open Folder
- [x] Navigate to: `/Users/bsteeger/Documents/1-projects/workOS/work-os`
- [x] Open the folder

### 5. Verify MCP Server
- [x] Check MCP Server view in Kiro
- [ ] Verify `workos` server is connected
- [ ] If not connected, check `.kiro/settings/mcp.json` path is correct

### 6. Test Functionality
- [ ] Try a hook (e.g., "WorkOS Daily Focus")
- [ ] Verify tasks are accessible
- [ ] Check that all files load correctly

## If MCP Server Doesn't Connect

The path in `.kiro/settings/mcp.json` should be:
```json
"args": ["/Users/bsteeger/Documents/1-projects/workOS/work-os/core/mcp/server.py"]
```

And the env variable:
```json
"MANAGER_AI_BASE_DIR": "/Users/bsteeger/Documents/1-projects/workOS/work-os"
```

These are already updated, so it should work automatically!

## Optional: Update Git Remote (if pushing to GitHub)
```bash
cd /Users/bsteeger/Documents/1-projects/workOS/work-os
git remote set-url origin https://github.com/amanaiproduct/work-os.git
```

## Optional: Update Shell Alias
If you installed the `pos` alias, update it:
```bash
cd /Users/bsteeger/Documents/1-projects/workOS/work-os
./scripts/install-alias.sh
```

This will update the alias to point to the new location.

## Troubleshooting

### If files don't load:
- Check you opened the correct folder in Kiro
- Verify the folder was renamed successfully

### If MCP server fails:
- Open `.kiro/settings/mcp.json`
- Verify paths point to `work-os` not `personal-os`
- Restart Kiro

### If hooks don't work:
- They should work automatically after Kiro restart
- Check the MCP Server view to ensure `workos` is connected

## Expected Result
✅ Folder renamed to `work-os`
✅ Kiro opens the new location
✅ MCP server `workos` connects automatically
✅ All hooks work with new names
✅ All files and functionality intact

---

**Ready to proceed?** Start with Step 1: Close Kiro!
