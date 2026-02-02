# Convert CRS Validation Plan

**Related Issues:** #189 (FlatGeobuf missing CRS), #190 (Shapefile missing .prj)
**Branch:** `fix/convert-crs-validation-189-190`
**Date:** 2025-01-31

## Problem Statement

When exporting GeoParquet files with EPSG:4326 CRS to legacy formats (Shapefile, FlatGeobuf), the output files are missing CRS metadata because `_get_srs_parameter()` returns `None` for "default" CRS, assuming output formats default to WGS84. However:

1. **Shapefile**: No `.prj` file created → import fails
2. **FlatGeobuf**: No CRS metadata embedded → import fails

This breaks round-trip conversion workflows.

## Root Cause

In `core/format_writers.py`:
```python
def _get_srs_parameter(input_path, verbose=False):
    crs = extract_crs_from_parquet(input_path, verbose)
    if not crs or is_default_crs(crs):  # <-- BUG: Returns None for 4326
        return None
    # ...
```

GDAL formats don't have implicit defaults—CRS must always be explicit.

## Implementation Plan

### Step 1: Write Failing Tests (TDD)

**File:** `tests/test_convert_crs_roundtrip.py`

1. **Test Shapefile .prj exists for EPSG:4326**
   - Export 4326 GeoParquet → Shapefile
   - Assert `.prj` file exists
   - Assert `.prj` contains valid WKT

2. **Test FlatGeobuf CRS preserved for EPSG:4326**
   - Export 4326 GeoParquet → FlatGeobuf
   - Re-import → GeoParquet (should not fail)
   - Verify CRS is preserved

3. **Test round-trip CRS preservation** (all formats)
   - GeoParquet → Format → GeoParquet
   - Assert CRS matches original

4. **Test check_all passes on converted GeoParquet**
   - Convert legacy format → GeoParquet
   - Run `check_all()` on output
   - Assert all checks pass

### Step 2: Fix _get_srs_parameter

**Change:** Remove the `is_default_crs()` check—always return CRS for GDAL exports.

```python
def _get_srs_parameter(input_path, verbose=False):
    crs = extract_crs_from_parquet(input_path, verbose)
    if not crs:
        return None  # Only skip if truly no CRS

    # Always return CRS for GDAL formats (no implicit defaults)
    epsg_info = _extract_crs_identifier(crs)
    if epsg_info:
        authority, code = epsg_info
        if authority.isalnum() and isinstance(code, int):
            return f"{authority}:{code}"

    return json.dumps(crs)
```

### Step 3: Add check_all Validation to Conversion Tests

**Files:** `tests/test_convert.py`, `tests/test_conversion_end_to_end.py`

Add post-conversion validation:
```python
from geoparquet_io.core.check_parquet_structure import check_all

def test_convert_shapefile_to_geoparquet_passes_check_all(shapefile_input, tmp_path):
    output = tmp_path / "output.parquet"
    convert_to_geoparquet(shapefile_input, output)
    results = check_all(output, return_results=True)
    assert results["pass"], f"Output failed check_all: {results}"
```

### Step 4: Add Legacy Format CRS Validation

**File:** `tests/test_format_writers.py`

Enhance existing tests:
1. Parse `.prj` WKT and verify EPSG code
2. Verify GeoPackage `gpkg_spatial_ref_sys` table
3. Verify FlatGeobuf can be read back with correct CRS

### Step 5: Edge Case Tests

1. **Projected CRS** (EPSG:5070) → verify preserved
2. **No CRS** → verify appropriate handling
3. **Non-standard CRS** (PROJJSON only) → verify PROJJSON used

## Commit Plan

| # | Commit Message | Files |
|---|----------------|-------|
| 1 | Add failing tests for CRS export issues #189 #190 | `tests/test_convert_crs_roundtrip.py` |
| 2 | Fix _get_srs_parameter to always export CRS | `core/format_writers.py` |
| 3 | Add check_all validation to conversion tests | `tests/test_convert.py`, etc. |
| 4 | Add CRS validation for legacy format exports | `tests/test_format_writers.py` |
| 5 | Add edge case tests for CRS handling | `tests/test_convert_crs_roundtrip.py` |

## Success Criteria

- [ ] All new tests pass
- [ ] Existing tests still pass
- [ ] Round-trip conversion preserves CRS for all formats
- [ ] `check_all` passes on all converted GeoParquet files
- [ ] Issues #189 and #190 are resolved

## Testing Commands

```bash
# Run specific test file
uv run pytest tests/test_convert_crs_roundtrip.py -v

# Run all conversion tests
uv run pytest tests/test_convert*.py tests/test_format_writers.py -v

# Run with coverage
uv run pytest --cov=geoparquet_io.core.format_writers -v
```
