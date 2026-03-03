"""Tests for FileGDB CRS detection.

DuckDB's ST_Read_Meta returns empty for FileGDB directories (a known limitation).
These tests verify our workaround that iterates through internal .gdbtable files.
"""

import os
import shutil
import tempfile

import pytest

from geoparquet_io.core.common import (
    detect_crs_from_spatial_file,
    get_duckdb_connection,
)


@pytest.fixture
def filegdb_path():
    """Create a test FileGDB using ogr2ogr.

    We use ogr2ogr because DuckDB's COPY TO with OpenFileGDB driver
    has issues with required parameters.
    """
    import subprocess
    import uuid

    # Create unique paths to avoid conflicts
    unique_id = uuid.uuid4().hex[:8]
    gdb_path = os.path.join(tempfile.gettempdir(), f"test_filegdb_{unique_id}.gdb")
    geojson_path = os.path.join(tempfile.gettempdir(), f"test_filegdb_source_{unique_id}.geojson")

    # Clean up any existing files
    if os.path.exists(gdb_path):
        shutil.rmtree(gdb_path)

    # Create a GeoJSON source file
    geojson_content = """{
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::4326"}},
        "features": [
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-75.1, 39.9]}, "properties": {"id": 1, "name": "Philadelphia"}},
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-73.9, 40.7]}, "properties": {"id": 2, "name": "New York"}}
        ]
    }"""

    with open(geojson_path, "w") as f:
        f.write(geojson_content)

    # Convert to FileGDB using ogr2ogr
    result = subprocess.run(
        ["ogr2ogr", "-f", "OpenFileGDB", gdb_path, geojson_path, "-a_srs", "EPSG:4326"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        # Cleanup on failure
        if os.path.exists(geojson_path):
            os.remove(geojson_path)
        pytest.skip(f"ogr2ogr failed to create FileGDB: {result.stderr}")

    yield gdb_path

    # Cleanup
    if os.path.exists(gdb_path):
        shutil.rmtree(gdb_path)
    if os.path.exists(geojson_path):
        os.remove(geojson_path)


class TestFileGDBCrsDetection:
    """Tests for FileGDB CRS detection workaround."""

    def test_detect_crs_from_filegdb_returns_crs(self, filegdb_path):
        """Test that CRS is detected from a FileGDB directory."""
        con = get_duckdb_connection(load_spatial=True)

        crs = detect_crs_from_spatial_file(filegdb_path, con, verbose=False)

        assert crs is not None, "CRS should be detected from FileGDB"
        # Check it's EPSG:4326
        if "id" in crs:
            assert crs["id"]["authority"] == "EPSG"
            assert crs["id"]["code"] == 4326
        elif "name" in crs:
            assert "4326" in str(crs) or "WGS 84" in str(crs)

    def test_detect_crs_from_filegdb_with_trailing_slash(self, filegdb_path):
        """Test that CRS detection works with trailing slash in path."""
        con = get_duckdb_connection(load_spatial=True)

        crs = detect_crs_from_spatial_file(filegdb_path + "/", con, verbose=False)

        assert crs is not None, "CRS should be detected even with trailing slash"

    def test_st_read_meta_returns_empty_for_filegdb_directory(self, filegdb_path):
        """Verify that ST_Read_Meta returns empty for FileGDB directories.

        This documents the underlying DuckDB limitation that our workaround fixes.
        """
        con = get_duckdb_connection(load_spatial=True)

        result = con.execute(f"SELECT * FROM ST_Read_Meta('{filegdb_path}')").fetchall()

        # This should be empty - that's the bug we're working around
        assert len(result) == 0, "ST_Read_Meta should return empty for FileGDB directories"

    def test_st_read_works_for_filegdb_directory(self, filegdb_path):
        """Verify that ST_Read works for FileGDB directories.

        This confirms the data itself is readable, just not the metadata.
        """
        con = get_duckdb_connection(load_spatial=True)

        result = con.execute(f"SELECT COUNT(*) FROM ST_Read('{filegdb_path}')").fetchone()

        assert result[0] > 0, "ST_Read should be able to read FileGDB data"

    def test_detect_crs_returns_none_for_nonexistent_path(self):
        """Test that non-existent paths return None gracefully."""
        con = get_duckdb_connection(load_spatial=True)

        crs = detect_crs_from_spatial_file("/nonexistent/path.gdb", con, verbose=False)

        assert crs is None

    def test_detect_crs_handles_non_gdb_directory(self):
        """Test that non-.gdb directories don't trigger FileGDB workaround."""
        con = get_duckdb_connection(load_spatial=True)

        # Use a regular directory
        crs = detect_crs_from_spatial_file("/tmp", con, verbose=False)

        # Should return None (not crash)
        assert crs is None
