# ADR-0004: Python API Mirrors CLI

## Status

Accepted

## Context

geoparquet-io started as a CLI tool, but users increasingly want to use its functionality from Python scripts, Jupyter notebooks, and data pipelines. Rather than forcing users to shell out to the CLI with `subprocess`, the project needs a first-class Python API that provides the same capabilities.

The question is how to structure this API: should it mirror the CLI surface, provide a completely different interface, or offer multiple paradigms?

## Decision

Every CLI command has a corresponding Python API exposed through two complementary interfaces:

1. **Method-based API** (`api/table.py`): A `Table` class that wraps a GeoParquet file and provides chainable methods. Created via `gpio.read("file.parquet")`, with methods like `.add_bbox()`, `.sort_hilbert()`, `.reproject()`.

2. **Functional API** (`api/ops.py`): Standalone functions like `gpio.add_bbox(input, output)` that mirror CLI semantics -- take input/output paths and options as arguments.

Both APIs delegate to the same `core/` module functions (the `*_table()` functions from ADR-0001), ensuring behavioral parity with the CLI.

```python
import geoparquet_io as gpio

# Method-based (chainable)
table = gpio.read("input.parquet")
table.add_bbox().sort_hilbert().write("output.parquet")

# Functional (mirrors CLI)
gpio.add_bbox("input.parquet", "output.parquet")
```

When a new CLI command is added, a corresponding method must be added to `Table` and a corresponding function to `ops.py`. This is enforced through code review and documented in the contributor checklist.

## Consequences

### Positive
- Users get full functionality from Python without subprocess calls.
- The `Table` class provides IDE autocomplete and method chaining for interactive use.
- The functional API provides a familiar interface for users who think in terms of CLI commands.
- Behavioral parity is guaranteed since both APIs and the CLI share core implementations.

### Negative
- Every new feature requires updating three locations: `core/*.py`, `cli/main.py`, and `api/` (both `table.py` and `ops.py`).
- The API surface must be maintained and documented alongside the CLI.
- Parameter naming must be kept consistent between CLI options and API arguments.

### Neutral
- The `Table` class currently has ~2400 lines, growing with each new operation. This is manageable since each method is self-contained.
- Some operations (like partitioning) produce directory output rather than a single file, which fits the functional API better than the method-based API.

## Alternatives Considered

### CLI-only (no Python API)
Requiring users to call the CLI via subprocess. Rejected because it provides poor developer experience -- no type hints, no autocomplete, string-based argument passing, and subprocess overhead.

### Auto-generated API from CLI
Automatically generating Python functions from Click command definitions. Rejected because the resulting API would expose Click-specific concepts (like parameter types) and would not support method chaining or a clean `Table` abstraction.

### Table class only (no functional API)
Providing only the method-based `Table` API. Rejected because some operations (batch processing, simple one-off transforms) are more naturally expressed as function calls than method chains.

## References

- `geoparquet_io/api/table.py` -- `Table` class with method-based API
- `geoparquet_io/api/ops.py` -- Functional API
- `geoparquet_io/api/__init__.py` -- Public API surface
- ADR-0001 -- CLI/Core separation that enables this pattern
