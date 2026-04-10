"""Tests for FSM lifecycle validator."""

from __future__ import annotations

import pytest

from nexus_atom.fsm import FSMError, FSMValidator
from nexus_atom.models import AtomState


@pytest.fixture
def fsm() -> FSMValidator:
    return FSMValidator()


def test_draft_to_approved(fsm: FSMValidator) -> None:
    result = fsm.apply(AtomState.DRAFT, AtomState.APPROVED)
    assert result == AtomState.APPROVED


def test_approved_to_archived(fsm: FSMValidator) -> None:
    result = fsm.apply(AtomState.APPROVED, AtomState.ARCHIVED)
    assert result == AtomState.ARCHIVED


def test_draft_to_archived_raises(fsm: FSMValidator) -> None:
    with pytest.raises(FSMError, match="draft"):
        fsm.apply(AtomState.DRAFT, AtomState.ARCHIVED)


def test_archived_to_approved_raises(fsm: FSMValidator) -> None:
    with pytest.raises(FSMError, match="archived"):
        fsm.apply(AtomState.ARCHIVED, AtomState.APPROVED)


def test_approved_to_draft_raises(fsm: FSMValidator) -> None:
    with pytest.raises(FSMError, match="approved"):
        fsm.apply(AtomState.APPROVED, AtomState.DRAFT)


def test_archived_is_terminal(fsm: FSMValidator) -> None:
    for target in AtomState:
        with pytest.raises(FSMError):
            fsm.apply(AtomState.ARCHIVED, target)


def test_validate_transition_valid(fsm: FSMValidator) -> None:
    fsm.validate_transition(AtomState.DRAFT, AtomState.APPROVED)  # no exception


def test_validate_transition_invalid(fsm: FSMValidator) -> None:
    with pytest.raises(FSMError):
        fsm.validate_transition(AtomState.APPROVED, AtomState.DRAFT)
