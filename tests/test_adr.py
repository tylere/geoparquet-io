"""Tests for ADR directory structure."""

from pathlib import Path

import pytest


class TestADRDirectory:
    """Test ADR directory is properly structured."""

    @pytest.fixture
    def adr_dir(self):
        return Path(__file__).parent.parent / "context" / "shared" / "adr"

    def test_adr_directory_exists(self, adr_dir):
        """Verify ADR directory exists."""
        assert adr_dir.exists(), "ADR directory missing"
        assert adr_dir.is_dir()

    def test_readme_exists(self, adr_dir):
        """Verify README exists."""
        readme = adr_dir / "README.md"
        assert readme.exists(), "ADR README missing"

    def test_template_exists(self, adr_dir):
        """Verify template exists."""
        template = adr_dir / "template.md"
        assert template.exists(), "ADR template missing"

    def test_at_least_3_adrs_exist(self, adr_dir):
        """Verify at least 3 ADRs are documented."""
        adrs = list(adr_dir.glob("0*.md"))
        assert len(adrs) >= 3, f"Expected at least 3 ADRs, found {len(adrs)}"

    def test_adrs_have_required_sections(self, adr_dir):
        """Verify each ADR has required sections."""
        required_sections = [
            "## Status",
            "## Context",
            "## Decision",
            "## Consequences",
        ]

        for adr_file in adr_dir.glob("0*.md"):
            content = adr_file.read_text()
            for section in required_sections:
                assert section in content, f"{adr_file.name} missing {section}"

    def test_adrs_are_numbered_sequentially(self, adr_dir):
        """Verify ADRs are numbered sequentially."""
        adrs = sorted(adr_dir.glob("0*.md"))

        for i, adr in enumerate(adrs, start=1):
            expected_prefix = f"{i:04d}-"
            assert adr.name.startswith(expected_prefix), (
                f"Expected {adr.name} to start with {expected_prefix}"
            )

    def test_readme_index_matches_files(self, adr_dir):
        """Verify README index matches actual ADR files."""
        readme = adr_dir / "README.md"
        content = readme.read_text()

        for adr_file in adr_dir.glob("0*.md"):
            assert adr_file.name in content, f"README missing link to {adr_file.name}"
