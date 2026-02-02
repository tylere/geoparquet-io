# Update PMTiles Tippecanoe Settings

## Overview
Update the gpio-pmtiles plugin to use enhanced tippecanoe settings based on FieldMaps production configuration, improving tile quality and processing efficiency.

## Current State
The plugin uses basic tippecanoe settings:
- `-P` (parallel mode)
- `-o` (output file)
- `-l` (layer name)
- `-zg` or explicit zoom levels
- `--drop-densest-as-needed` (simple dropping strategy)

## Target State
Enhanced tippecanoe settings from FieldMaps:
- `--layer=<name>` (existing, keep as is)
- `--attribution=<html>` (new, with default)
- `--maximum-zoom=<N>` (existing as --max-zoom)
- `--simplify-only-low-zooms` (new)
- `--no-simplification-of-shared-nodes` (new)
- `--read-parallel` (new, replaces `-P`)
- `--no-tile-size-limit` (new)
- `--force` (new, for overwriting existing files)

## Implementation Steps

### 1. Write Tests First (TDD)
**File**: `plugins/gpio-pmtiles/tests/test_pmtiles.py`

Add test cases for:
- Default attribution value
- Custom attribution via CLI
- New flags in tippecanoe command: `--simplify-only-low-zooms`, `--no-simplification-of-shared-nodes`, `--read-parallel`, `--no-tile-size-limit`, `--force`
- Verify `-P` is replaced by `--read-parallel`

### 2. Update Core Function
**File**: `plugins/gpio-pmtiles/gpio_pmtiles/core.py`

Update `_build_tippecanoe_command()`:
- Add `attribution` parameter with default: `'<a href="https://geoparquet.io/" target="_blank">geoparquet-io</a>'`
- Replace `-P` with `--read-parallel`
- Add `--simplify-only-low-zooms`
- Add `--no-simplification-of-shared-nodes`
- Add `--no-tile-size-limit`
- Add `--force`
- Add `--attribution=<value>`
- Keep existing logic for layer name, zoom levels, and `--drop-densest-as-needed`

Update `create_pmtiles_from_geoparquet()`:
- Add `attribution` parameter
- Pass through to `_build_tippecanoe_command()`

### 3. Update CLI
**File**: `plugins/gpio-pmtiles/gpio_pmtiles/cli.py`

Add `--attribution` option to `create` command:
```python
@click.option(
    "--attribution",
    help='Attribution HTML (default: geoparquet-io link)',
    default=None,
)
```

Pass through to `create_pmtiles_from_geoparquet()`.

### 4. Update Documentation
**File**: `plugins/gpio-pmtiles/README.md`

Add new option to Options section:
- `--attribution`: Attribution HTML for the tiles (default: geoparquet-io link)

Update "How It Works" section to reflect new tippecanoe flags.

Add example showing custom attribution:
```bash
gpio pmtiles create data.parquet tiles.pmtiles \
  --attribution '<a href="https://example.com">My Data</a>'
```

### 5. Test Execution
Run tests:
```bash
cd plugins/gpio-pmtiles
uv run pytest -v
```

Verify all tests pass.

### 6. Integration Testing
Test manually with real data:
```bash
# Test default attribution
gpio pmtiles create test.parquet test.pmtiles -v

# Test custom attribution
gpio pmtiles create test.parquet test2.pmtiles \
  --attribution '<a href="https://example.com">Example</a>' -v
```

## Success Criteria
- [ ] All existing tests pass
- [ ] New tests for attribution and flags pass
- [ ] Command builds correctly with new flags
- [ ] Attribution appears in generated PMTiles metadata
- [ ] Documentation updated with examples
- [ ] Code complexity remains at grade A
- [ ] PR opened with all changes

## Breaking Changes
None - all changes are additive with sensible defaults.

## Risks & Mitigations
- **Risk**: Tippecanoe version compatibility
  - **Mitigation**: These flags are in tippecanoe v2.0+ (widely available)

- **Risk**: `--force` might overwrite files unexpectedly
  - **Mitigation**: This is expected behavior for tile generation workflows

## Dependencies
- tippecanoe >= 2.0 (already required)
- No new Python dependencies
