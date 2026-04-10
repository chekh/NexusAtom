"""Tests for Pydantic v2 AtomSpec model validation."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from nexus_atom.models import AtomSpec, AtomState


def test_valid_defaults() -> None:
    atom = AtomSpec(id="my-atom", name="My Atom", version="1.0.0")
    assert atom.state == AtomState.DRAFT
    assert atom.depends_on == []
    assert atom.tags == []
    assert atom.description == ""


def test_all_fields() -> None:
    atom = AtomSpec(
        id="auth-token",
        name="Auth Token",
        state=AtomState.APPROVED,
        version="2.1.0",
        depends_on=["user-identity"],
        tags=["auth", "security"],
        description="Issues JWT auth tokens.",
    )
    assert atom.id == "auth-token"
    assert atom.state == AtomState.APPROVED
    assert atom.depends_on == ["user-identity"]


def test_invalid_state_raises() -> None:
    with pytest.raises(ValidationError):
        AtomSpec(id="x", name="X", version="1.0.0", state="invalid")  # type: ignore[arg-type]


def test_missing_required_id_raises() -> None:
    with pytest.raises(ValidationError):
        AtomSpec(name="Missing ID", version="1.0.0")  # type: ignore[call-arg]


def test_missing_required_version_raises() -> None:
    with pytest.raises(ValidationError):
        AtomSpec(id="x", name="X")  # type: ignore[call-arg]


def test_extra_field_forbidden() -> None:
    with pytest.raises(ValidationError):
        AtomSpec(id="x", name="X", version="1.0.0", unknown_field="oops")  # type: ignore[call-arg]


def test_frozen_prevents_mutation() -> None:
    atom = AtomSpec(id="x", name="X", version="1.0.0")
    with pytest.raises(ValidationError):
        setattr(atom, "id", "y")


def test_model_validate_from_dict() -> None:
    data = {
        "id": "parsed-atom",
        "name": "Parsed Atom",
        "version": "0.2.0",
        "state": "draft",
    }
    atom = AtomSpec.model_validate(data)
    assert atom.id == "parsed-atom"
    assert atom.state == AtomState.DRAFT
