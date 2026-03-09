"""Tests for CLAUDE.md section generation."""

import subprocess
import sys
from pathlib import Path

import pytest

# Project root for import resolution
PROJECT_ROOT = Path(__file__).parent.parent
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "generate_claude_md_sections.py"


class TestScriptExists:
    """Verify script infrastructure."""

    def test_script_exists(self):
        """Verify generation script exists."""
        assert SCRIPT_PATH.exists(), f"Expected script at {SCRIPT_PATH}"

    def test_script_runs_without_update(self):
        """Verify script runs in default (diff) mode without error."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH)],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        # Should succeed (exit 0) in default mode
        assert result.returncode in [0, 1], (
            f"Script error (rc={result.returncode}):\n{result.stderr}"
        )

    def test_script_check_mode(self):
        """Verify --check flag works."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--check"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        # Exit 0 if current, 1 if outdated
        assert result.returncode in [0, 1], (
            f"Script error (rc={result.returncode}):\n{result.stderr}"
        )


class TestCliCommandGeneration:
    """Unit tests for CLI command generation."""

    @pytest.fixture(autouse=True)
    def _import_module(self):
        """Import the generation module for unit tests."""
        # Add scripts to path for import
        if str(PROJECT_ROOT / "scripts") not in sys.path:
            sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        import generate_claude_md_sections

        self.mod = generate_claude_md_sections

    def test_get_cli_commands_returns_dict(self):
        """Test CLI introspection returns a dict of commands."""
        commands = self.mod.get_cli_commands()
        assert isinstance(commands, dict)
        assert len(commands) > 0

    def test_get_cli_commands_known_groups(self):
        """Test that known command groups are present."""
        commands = self.mod.get_cli_commands()
        expected = ["add", "convert", "inspect", "extract", "partition", "sort", "check", "publish"]
        for group in expected:
            assert group in commands, f"Expected command group '{group}' not found"

    def test_get_cli_commands_has_subcommands(self):
        """Test that groups have subcommands."""
        commands = self.mod.get_cli_commands()
        # 'add' group should have subcommands
        assert len(commands["add"]["subcommands"]) > 0
        assert "bbox" in commands["add"]["subcommands"]

    def test_get_cli_commands_has_help_text(self):
        """Test that commands have help text."""
        commands = self.mod.get_cli_commands()
        for name, info in commands.items():
            assert "help" in info, f"Command '{name}' missing help key"

    def test_generate_cli_section_format(self):
        """Test CLI section has correct markdown format."""
        section = self.mod.generate_cli_section()
        assert "<!-- BEGIN GENERATED: cli-commands -->" in section
        assert "<!-- END GENERATED: cli-commands -->" in section
        assert "| Command Group |" in section
        assert "| Subcommands |" in section

    def test_generate_cli_section_contains_commands(self):
        """Test CLI section contains actual command names."""
        section = self.mod.generate_cli_section()
        assert "`gpio add`" in section
        assert "`gpio convert`" in section
        assert "`gpio inspect`" in section


class TestMarkerGeneration:
    """Unit tests for test marker generation."""

    @pytest.fixture(autouse=True)
    def _import_module(self):
        """Import the generation module for unit tests."""
        if str(PROJECT_ROOT / "scripts") not in sys.path:
            sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        import generate_claude_md_sections

        self.mod = generate_claude_md_sections

    def test_get_test_markers_returns_list(self):
        """Test marker parsing returns a list."""
        markers = self.mod.get_test_markers(PROJECT_ROOT / "pyproject.toml")
        assert isinstance(markers, list)
        assert len(markers) > 0

    def test_get_test_markers_known_markers(self):
        """Test that known markers are present."""
        markers = self.mod.get_test_markers(PROJECT_ROOT / "pyproject.toml")
        marker_names = [m["name"] for m in markers]
        assert "slow" in marker_names
        assert "network" in marker_names

    def test_get_test_markers_have_descriptions(self):
        """Test that markers have descriptions."""
        markers = self.mod.get_test_markers(PROJECT_ROOT / "pyproject.toml")
        for marker in markers:
            assert "name" in marker
            assert "description" in marker
            assert len(marker["description"]) > 0

    def test_generate_markers_section_format(self):
        """Test markers section has correct markdown format."""
        section = self.mod.generate_markers_section(PROJECT_ROOT / "pyproject.toml")
        assert "<!-- BEGIN GENERATED: test-markers -->" in section
        assert "<!-- END GENERATED: test-markers -->" in section
        assert "| Marker |" in section
        assert "@pytest.mark." in section


class TestModuleGeneration:
    """Unit tests for core module generation."""

    @pytest.fixture(autouse=True)
    def _import_module(self):
        """Import the generation module for unit tests."""
        if str(PROJECT_ROOT / "scripts") not in sys.path:
            sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        import generate_claude_md_sections

        self.mod = generate_claude_md_sections

    def test_get_core_modules_returns_list(self):
        """Test core module scanning returns a list."""
        modules = self.mod.get_core_modules(PROJECT_ROOT / "geoparquet_io" / "core")
        assert isinstance(modules, list)
        assert len(modules) > 0

    def test_get_core_modules_includes_common(self):
        """Test that common.py is found."""
        modules = self.mod.get_core_modules(PROJECT_ROOT / "geoparquet_io" / "core")
        module_names = [m["name"] for m in modules]
        assert "common.py" in module_names

    def test_get_core_modules_skips_init(self):
        """Test that __init__.py is excluded."""
        modules = self.mod.get_core_modules(PROJECT_ROOT / "geoparquet_io" / "core")
        module_names = [m["name"] for m in modules]
        assert "__init__.py" not in module_names

    def test_get_core_modules_has_line_counts(self):
        """Test that modules have line counts."""
        modules = self.mod.get_core_modules(PROJECT_ROOT / "geoparquet_io" / "core")
        for mod in modules:
            assert "lines" in mod
            assert mod["lines"] > 0

    def test_generate_modules_section_format(self):
        """Test modules section has correct markdown format."""
        section = self.mod.generate_modules_section(PROJECT_ROOT / "geoparquet_io" / "core")
        assert "<!-- BEGIN GENERATED: core-modules -->" in section
        assert "<!-- END GENERATED: core-modules -->" in section
        assert "| Module |" in section
        assert "| Purpose |" in section
        assert "| Lines |" in section

    def test_generate_modules_section_limits_to_15(self):
        """Test that only top 15 modules are shown."""
        section = self.mod.generate_modules_section(PROJECT_ROOT / "geoparquet_io" / "core")
        # Count table rows (lines starting with | and not header/separator)
        table_rows = [
            line
            for line in section.split("\n")
            if line.startswith("|")
            and "Module" not in line
            and "---" not in line
            and "more modules" not in line
        ]
        assert len(table_rows) == 15

    def test_generate_modules_section_has_more_line(self):
        """Test that the '... more modules' line is present."""
        section = self.mod.generate_modules_section(PROJECT_ROOT / "geoparquet_io" / "core")
        assert "more modules" in section


class TestSectionUpdate:
    """Unit tests for section replacement logic."""

    @pytest.fixture(autouse=True)
    def _import_module(self):
        """Import the generation module for unit tests."""
        if str(PROJECT_ROOT / "scripts") not in sys.path:
            sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        import generate_claude_md_sections

        self.mod = generate_claude_md_sections

    def test_update_existing_section(self):
        """Test replacing an existing generated section."""
        content = """# Header
<!-- BEGIN GENERATED: test -->
old content
<!-- END GENERATED: test -->
# Footer"""

        new_section = """<!-- BEGIN GENERATED: test -->
new content
<!-- END GENERATED: test -->"""

        result = self.mod.update_section(content, "test", new_section)
        assert "new content" in result
        assert "old content" not in result
        assert "# Header" in result
        assert "# Footer" in result

    def test_update_preserves_surrounding_content(self):
        """Test that content before and after is preserved."""
        content = """Line 1
Line 2
<!-- BEGIN GENERATED: foo -->
old stuff
<!-- END GENERATED: foo -->
Line 3
Line 4"""

        new_section = """<!-- BEGIN GENERATED: foo -->
new stuff
<!-- END GENERATED: foo -->"""

        result = self.mod.update_section(content, "foo", new_section)
        assert "Line 1" in result
        assert "Line 2" in result
        assert "Line 3" in result
        assert "Line 4" in result
        assert "new stuff" in result

    def test_update_nonexistent_section_returns_unchanged(self):
        """Test that updating a missing section returns content unchanged."""
        content = "# No generated sections here"
        new_section = """<!-- BEGIN GENERATED: missing -->
stuff
<!-- END GENERATED: missing -->"""

        result = self.mod.update_section(content, "missing", new_section)
        assert result == content

    def test_update_multiple_sections_independently(self):
        """Test that multiple sections can be updated independently."""
        content = """# Doc
<!-- BEGIN GENERATED: alpha -->
old alpha
<!-- END GENERATED: alpha -->
Middle text
<!-- BEGIN GENERATED: beta -->
old beta
<!-- END GENERATED: beta -->
End"""

        new_alpha = """<!-- BEGIN GENERATED: alpha -->
new alpha
<!-- END GENERATED: alpha -->"""

        result = self.mod.update_section(content, "alpha", new_alpha)
        assert "new alpha" in result
        assert "old alpha" not in result
        # beta should be unchanged
        assert "old beta" in result


class TestUpdateMode:
    """Tests for --update mode on CLAUDE.md."""

    @pytest.fixture(autouse=True)
    def _import_module(self):
        if str(PROJECT_ROOT / "scripts") not in sys.path:
            sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        import generate_claude_md_sections

        self.mod = generate_claude_md_sections

    def test_claude_md_has_generated_markers(self):
        """Test that CLAUDE.md contains the generated section markers."""
        claude_md = PROJECT_ROOT / "CLAUDE.md"
        content = claude_md.read_text()
        for section_name in ["cli-commands", "test-markers", "core-modules"]:
            assert f"<!-- BEGIN GENERATED: {section_name} -->" in content, (
                f"CLAUDE.md missing BEGIN marker for '{section_name}'"
            )
            assert f"<!-- END GENERATED: {section_name} -->" in content, (
                f"CLAUDE.md missing END marker for '{section_name}'"
            )

    def test_update_produces_valid_markdown(self):
        """Test that updated CLAUDE.md still has valid structure."""
        claude_md = PROJECT_ROOT / "CLAUDE.md"
        content = claude_md.read_text()

        # Generate all sections and apply
        sections = {
            "cli-commands": self.mod.generate_cli_section(),
            "test-markers": self.mod.generate_markers_section(PROJECT_ROOT / "pyproject.toml"),
            "core-modules": self.mod.generate_modules_section(
                PROJECT_ROOT / "geoparquet_io" / "core"
            ),
        }

        updated = content
        for name, section_content in sections.items():
            updated = self.mod.update_section(updated, name, section_content)

        # Should still have the main title
        assert "# Claude Code Instructions for geoparquet-io" in updated
        # Should have all three generated sections
        for name in sections:
            assert f"<!-- BEGIN GENERATED: {name} -->" in updated
            assert f"<!-- END GENERATED: {name} -->" in updated
