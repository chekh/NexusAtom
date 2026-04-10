"""Tests for manifest parser and directory scanner."""

from __future__ import annotations

from pathlib import Path

import pytest

from nexus_atom.manifest import ManifestParseError, ManifestParser
from nexus_atom.models import AtomState


@pytest.fixture
def parser() -> ManifestParser:
    return ManifestParser()


@pytest.fixture
def sample_spec(tmp_path: Path) -> Path:
    spec = tmp_path / "test-atom.md"
    spec.write_text(
        "---\n"
        "id: test-atom\n"
        "name: Test Atom\n"
        "state: draft\n"
        "version: 1.0.0\n"
        "depends_on: []\n"
        "tags: []\n"
        "description: A test atom.\n"
        "---\n\n"
        "## Contract\n\n"
        "Nothing here.\n"
    )
    return spec


def test_parse_file_valid(parser: ManifestParser, sample_spec: Path) -> None:
    atom = parser.parse_file(sample_spec)
    assert atom.id == "test-atom"
    assert atom.state == AtomState.DRAFT
    assert atom.version == "1.0.0"
    assert atom.description == "A test atom."


def test_parse_file_nonexistent_raises(parser: ManifestParser, tmp_path: Path) -> None:
    with pytest.raises(ManifestParseError):
        parser.parse_file(tmp_path / "nonexistent.md")


def test_parse_file_invalid_state_raises(
    parser: ManifestParser, tmp_path: Path
) -> None:
    spec = tmp_path / "bad-state.md"
    spec.write_text(
        "---\nid: bad\nname: Bad\nstate: not-valid\nversion: 1.0.0\n---\n"
    )
    with pytest.raises(ManifestParseError):
        parser.parse_file(spec)


def test_parse_file_missing_required_raises(
    parser: ManifestParser, tmp_path: Path
) -> None:
    spec = tmp_path / "incomplete.md"
    spec.write_text("---\nid: no-version\nname: No Version\nstate: draft\n---\n")
    with pytest.raises(ManifestParseError):
        parser.parse_file(spec)


def test_scan_directory_finds_specs(parser: ManifestParser, tmp_path: Path) -> None:
    (tmp_path / "atom-a.md").write_text(
        "---\nid: atom-a\nname: A\nstate: draft\nversion: 1.0.0\n---\n"
    )
    (tmp_path / "atom-b.md").write_text(
        "---\nid: atom-b\nname: B\nstate: approved\nversion: 1.0.0\n---\n"
    )
    atoms = parser.scan_directory(tmp_path)
    ids = [a.id for a in atoms]
    assert "atom-a" in ids
    assert "atom-b" in ids


def test_scan_directory_skips_template(parser: ManifestParser, tmp_path: Path) -> None:
    (tmp_path / "_template.md").write_text(
        "---\nid: template\nname: T\nstate: draft\nversion: 0.1.0\n---\n"
    )
    (tmp_path / "real-atom.md").write_text(
        "---\nid: real-atom\nname: Real\nstate: draft\nversion: 1.0.0\n---\n"
    )
    atoms = parser.scan_directory(tmp_path)
    ids = [a.id for a in atoms]
    assert "real-atom" in ids
    assert "template" not in ids


def test_scan_directory_empty(parser: ManifestParser, tmp_path: Path) -> None:
    atoms = parser.scan_directory(tmp_path)
    assert atoms == []


def test_scan_directory_recursive(parser: ManifestParser, tmp_path: Path) -> None:
    subdir = tmp_path / "sub"
    subdir.mkdir()
    (subdir / "nested.md").write_text(
        "---\nid: nested\nname: Nested\nstate: draft\nversion: 1.0.0\n---\n"
    )
    atoms = parser.scan_directory(tmp_path)
    assert any(a.id == "nested" for a in atoms)
