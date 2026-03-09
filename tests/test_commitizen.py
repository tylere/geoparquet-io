"""Tests for commitizen configuration."""

import subprocess
import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


class TestCommitizenConfig:
    """Test commitizen is properly configured."""

    def test_commitizen_installed(self):
        """Verify commitizen is installed."""
        result = subprocess.run(
            ["uv", "run", "cz", "version"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
        assert result.stdout.strip()

    def test_commitizen_config_exists(self):
        """Verify commitizen config in pyproject.toml."""
        pyproject = Path("pyproject.toml")
        with open(pyproject, "rb") as f:
            config = tomllib.load(f)

        assert "commitizen" in config.get("tool", {})
        cz_config = config["tool"]["commitizen"]
        assert cz_config.get("name") == "cz_conventional_commits"
        assert "version" in cz_config

    def test_commitizen_config_has_required_fields(self):
        """Verify all required commitizen config fields are present."""
        pyproject = Path("pyproject.toml")
        with open(pyproject, "rb") as f:
            config = tomllib.load(f)

        cz_config = config["tool"]["commitizen"]
        assert cz_config.get("tag_format") == "v$version"
        assert cz_config.get("changelog_file") == "CHANGELOG.md"
        assert cz_config.get("update_changelog_on_bump") is True
        assert cz_config.get("major_version_zero") is True

    def test_version_matches_pyproject(self):
        """Verify commitizen version matches pyproject.toml project version."""
        pyproject = Path("pyproject.toml")
        with open(pyproject, "rb") as f:
            config = tomllib.load(f)

        project_version = config["project"]["version"]
        cz_version = config["tool"]["commitizen"]["version"]
        assert project_version == cz_version, (
            f"Version mismatch: project={project_version}, commitizen={cz_version}"
        )


class TestCommitMessageValidation:
    """Test commit message validation."""

    def test_valid_feat_message(self):
        """Test that valid feat message passes."""
        result = subprocess.run(
            ["uv", "run", "cz", "check", "--message", "feat(cli): add new command"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0

    def test_valid_fix_message(self):
        """Test that valid fix message passes."""
        result = subprocess.run(
            ["uv", "run", "cz", "check", "--message", "fix: resolve null pointer issue"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0

    def test_valid_docs_message(self):
        """Test that valid docs message passes."""
        result = subprocess.run(
            ["uv", "run", "cz", "check", "--message", "docs: update Python API examples"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0

    def test_valid_chore_message(self):
        """Test that valid chore message passes."""
        result = subprocess.run(
            [
                "uv",
                "run",
                "cz",
                "check",
                "--message",
                "chore(ci): add security scanning",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0

    def test_invalid_message_fails(self):
        """Test that invalid message fails validation."""
        result = subprocess.run(
            ["uv", "run", "cz", "check", "--message", "Updated some stuff"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode != 0

    def test_bare_imperative_fails(self):
        """Test that bare imperative (no type prefix) fails validation."""
        result = subprocess.run(
            ["uv", "run", "cz", "check", "--message", "Add new feature"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode != 0

    def test_breaking_change_message(self):
        """Test breaking change format with ! suffix."""
        result = subprocess.run(
            ["uv", "run", "cz", "check", "--message", "feat!: remove deprecated API"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0

    def test_breaking_change_with_scope(self):
        """Test breaking change format with scope and ! suffix."""
        result = subprocess.run(
            [
                "uv",
                "run",
                "cz",
                "check",
                "--message",
                "feat(api)!: rename convert method",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0

    def test_valid_refactor_message(self):
        """Test that valid refactor message passes."""
        result = subprocess.run(
            [
                "uv",
                "run",
                "cz",
                "check",
                "--message",
                "refactor(core): extract geometry helpers",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0

    def test_valid_test_message(self):
        """Test that valid test message passes."""
        result = subprocess.run(
            [
                "uv",
                "run",
                "cz",
                "check",
                "--message",
                "test(api): add coverage for partition module",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0


class TestChangelogGeneration:
    """Test changelog generation capability."""

    def test_changelog_dry_run(self):
        """Test changelog generation in dry-run mode runs without crashing."""
        result = subprocess.run(
            ["uv", "run", "cz", "changelog", "--dry-run"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        # May return non-zero if no conventional commits exist yet in history,
        # but it must not produce unexpected error output indicating misconfiguration.
        assert "error" not in result.stderr.lower() or result.returncode == 0
