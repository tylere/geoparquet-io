# Platform-Specific Issues

This document catalogs known platform-specific issues and their solutions. These are recurring problems that may surface again in similar contexts.

## Windows File Locking with PyArrow

### Problem

On Windows, when `pq.ParquetFile(path)` throws an exception (e.g., invalid Parquet file), the file handle may not be released immediately. Python's garbage collector doesn't clean up the `ParquetFile` object right away, which keeps the file locked.

This causes `PermissionError: [WinError 32]` when attempting to delete the file:

```
PermissionError: [WinError 32] The process cannot access the file because it
is being used by another process: 'C:\...\tmp123.parquet'
```

### Solution

Always use a `finally` block to explicitly delete the `ParquetFile` object:

```python
def read_parquet_metadata(parquet_file: str) -> dict:
    pf = None  # Initialize to None
    try:
        pf = pq.ParquetFile(parquet_file)
        return dict(pf.metadata.metadata) if pf.metadata.metadata else {}
    except Exception as e:
        raise SomeError(f"Cannot read: {parquet_file}") from e
    finally:
        # Explicitly delete to release file handle (Windows compatibility)
        del pf
```

### Files Affected

- `geoparquet_io/core/duckdb_metadata.py`:
  - `_pyarrow_get_kv_metadata()`
  - `_pyarrow_get_geo_metadata()`
  - `_pyarrow_get_schema_info()`

### References

- PR #233 (inspect metadata performance)
- Windows CI failures in `test_duckdb_metadata.py::TestGeoParquetErrorExceptions`

---

## DuckDB Connection Cleanup on Windows

### Problem

On Windows, DuckDB connections must be explicitly closed before temporary files can be deleted. Unlike Unix where files can be deleted while open, Windows enforces strict file locking.

### Solution

Always use try/finally or context managers for DuckDB connections:

```python
con = duckdb.connect()
try:
    # ... use connection
finally:
    con.close()
```

Or use UUID in temporary filenames to avoid collisions:

```python
temp_file = f"/tmp/geoparquet_{uuid.uuid4().hex}.parquet"
```

### References

- Multiple tests throughout the codebase
- CLAUDE.md mentions this under "Debugging"
