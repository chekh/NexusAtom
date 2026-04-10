"""Finite State Machine validator for atom lifecycle transitions."""

from __future__ import annotations

from nexus_atom.models import AtomState

# Allowed state transitions: source -> list of valid targets
TRANSITIONS: dict[AtomState, list[AtomState]] = {
    AtomState.DRAFT: [AtomState.APPROVED],
    AtomState.APPROVED: [AtomState.ARCHIVED],
    AtomState.ARCHIVED: [],
}


class FSMError(Exception):
    """Raised when an invalid state transition is attempted."""


class FSMValidator:
    """Validates and applies atom lifecycle state transitions."""

    def validate_transition(self, current: AtomState, target: AtomState) -> None:
        """Raise FSMError if the transition current -> target is not allowed."""
        allowed = TRANSITIONS.get(current, [])
        if target not in allowed:
            raise FSMError(
                f"Invalid transition: {current.value!r} -> {target.value!r}. "
                f"Allowed: {[s.value for s in allowed]}"
            )

    def apply(self, current: AtomState, target: AtomState) -> AtomState:
        """Validate and return the new state after a transition."""
        self.validate_transition(current, target)
        return target
