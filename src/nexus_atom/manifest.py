"""YAML-frontmatter manifest parser for atom spec files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import frontmatter  # type: ignore[import-untyped]

from nexus_atom.models import AtomSpec


class ManifestParseError(Exception):
    """Raised when a spec file cannot be parsed into an AtomSpec."""


class ManifestParser:
    """Parses atom spec files with YAML frontmatter into AtomSpec models."""

    def parse_file(self, path: Path) -> AtomSpec:
        """Load and validate a single spec file."""
        try:
            post = frontmatter.load(str(path))
        except Exception as exc:
            raise ManifestParseError(f"Cannot read {path}: {exc}") from exc
        metadata: dict[str, Any] = dict(post.metadata)
        try:
            return AtomSpec.model_validate(metadata)
        except Exception as exc:
            raise ManifestParseError(f"Invalid spec in {path}: {exc}") from exc

    def scan_directory(self, directory: Path) -> list[AtomSpec]:
        """Recursively scan a directory and return all valid AtomSpecs.

        Files whose names start with ``_`` are treated as templates and skipped.
        """
        specs: list[AtomSpec] = []
        for path in sorted(directory.rglob("*.md")):
            if path.name.startswith("_"):
                continue
            specs.append(self.parse_file(path))
        return specs
