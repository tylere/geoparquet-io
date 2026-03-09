"""Tests for import-linter architecture contracts."""

import subprocess


class TestImportLinterContracts:
    """Test that import-linter is configured and passing."""

    def test_lint_imports_command_exists(self):
        """Verify lint-imports command is available."""
        result = subprocess.run(
            ["uv", "run", "lint-imports", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "lint-imports" in result.stdout or "Usage" in result.stdout

    def test_all_contracts_pass(self):
        """Verify all import-linter contracts pass."""
        result = subprocess.run(
            ["uv", "run", "lint-imports"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Import contracts failed:\n{result.stdout}\n{result.stderr}"

    def test_core_does_not_import_click(self):
        """Integration test: verify core modules don't import click (new violations).

        Note: Existing violations are tracked in pyproject.toml under
        [tool.importlinter.contracts] ignore_imports. New core code must not
        import click directly. Contract ID: core-no-click.
        """
        result = subprocess.run(
            ["uv", "run", "lint-imports", "--contract", "core-no-click"],
            capture_output=True,
            text=True,
        )
        # lint-imports returns 0 if contract passes
        assert result.returncode == 0, f"Core imports Click:\n{result.stdout}"

    def test_api_does_not_import_cli(self):
        """Verify API modules do not import CLI modules. Contract ID: api-no-cli."""
        result = subprocess.run(
            ["uv", "run", "lint-imports", "--contract", "api-no-cli"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"API imports CLI:\n{result.stdout}"
