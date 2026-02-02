# Documentation Cleanup Plan (PR7)

**Branch**: `cleanup/pr7-docs-audit`
**Status**: In Progress
**Date**: 2026-02-01

## Overview

Clean up documentation to reflect the current state of the codebase after PRs 1-6:
- Remove documentation for deprecated commands
- Update navigation and references
- Verify Python API documentation
- Ensure all examples work with current command structure

## Files to Remove

### Deprecated CLI Command Docs (5 files)
These commands were removed in PR1 (#174):

1. `docs/cli/meta.md` → Use `gpio inspect meta` instead
2. `docs/cli/stac.md` → Use `gpio publish stac` instead
3. `docs/cli/upload.md` → Use `gpio publish upload` instead
4. `docs/cli/validate.md` → Use `gpio check spec` instead

Note: `docs/cli/overview.md` mentions reproject but that was also removed.

### Deprecated Guide Docs (4 files)

1. `docs/guide/meta.md` → Redirect to inspect guide
2. `docs/guide/stac.md` → Content should be in publish guide (if exists, else remove)
3. `docs/guide/upload.md` → Content should be in publish guide (if exists, else remove)
4. `docs/guide/validate.md` → Redirect to check guide

## Files to Update

### Navigation and Index

1. **docs/index.md**
   - Remove references to deprecated commands
   - Update command list to current set (add, benchmark, check, convert, extract, inspect, partition, publish, sort)

2. **docs/cli/overview.md**
   - Remove `reproject`, `meta`, `stac`, `upload`, `validate`
   - Ensure only current commands listed
   - Update any command migration notes

### Python API Documentation

3. **docs/api/python-api.md**
   - Verify all API methods match current `geoparquet_io/api/table.py`
   - Verify all ops functions match `geoparquet_io/api/ops.py`
   - Check for references to deprecated functionality

### Guides That May Reference Deprecated Commands

4. **docs/guide/remote-files.md**
   - May reference old `upload` command → should reference `publish upload`

5. **docs/getting-started/quickstart.md**
   - Verify no references to deprecated commands

6. **docs/contributing.md**
   - Verify examples use current commands

## Verification Steps

### 1. Check for Broken Internal Links
```bash
# Find all markdown links
grep -r "\[.*\](.*\.md)" docs/ --include="*.md"

# Check if linked files exist
```

### 2. Verify Command References
```bash
# Find references to deprecated commands
grep -ri "gpio meta\|gpio stac\|gpio upload\|gpio validate\|gpio reproject" docs/ --include="*.md"
```

### 3. Test Code Examples
For each remaining guide, test the CLI and Python examples to ensure they work.

## Acceptance Criteria

- [ ] All deprecated command docs removed (8 files total)
- [ ] No broken internal links in documentation
- [ ] No references to removed commands (`meta`, `stac`, `upload`, `validate`, `reproject`)
- [ ] Navigation/index reflects current command structure
- [ ] Python API docs match actual API surface
- [ ] All quality checks pass (tests, linting)
- [ ] CHANGELOG.md updated if needed

## Implementation Order

1. Remove deprecated CLI docs (4 files)
2. Remove deprecated guide docs (4 files)
3. Update index.md and cli/overview.md
4. Search and replace deprecated command references
5. Verify Python API documentation
6. Test remaining examples
7. Run quality checks
8. Commit and push
9. Open PR

## Notes

- This is cleanup work, not new documentation
- Focus on removing outdated content and fixing references
- Preserve migration guidance in CHANGELOG.md (already done in PR1)
- Don't create new documentation unless fixing a gap
