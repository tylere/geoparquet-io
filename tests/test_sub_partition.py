"""Tests for sub-partition functionality."""

import shutil
import tempfile

import pytest
from click.testing import CliRunner

from geoparquet_io.cli.main import partition


@pytest.fixture
def cli_runner():
    return CliRunner()


@pytest.fixture
def temp_partition_dir():
    """Create a temp directory with parquet files of varying sizes."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


class TestMinSizeOption:
    """Test --min-size option parsing."""

    def test_min_size_option_exists(self, cli_runner):
        """Verify --min-size option is recognized."""
        result = cli_runner.invoke(partition, ["h3", "--help"])
        assert result.exit_code == 0
        assert "--min-size" in result.output

    def test_in_place_option_exists(self, cli_runner):
        """Verify --in-place option is recognized."""
        result = cli_runner.invoke(partition, ["h3", "--help"])
        assert result.exit_code == 0
        assert "--in-place" in result.output
