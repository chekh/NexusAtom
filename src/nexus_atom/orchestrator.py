"""Orchestrator: coordinates manifest parsing, DAG resolution, and FSM validation."""

from __future__ import annotations

from pathlib import Path

from nexus_atom.dag import DAGResolver
from nexus_atom.fsm import FSMValidator
from nexus_atom.manifest import ManifestParser
from nexus_atom.models import AtomSpec, AtomState


class Orchestrator:
    """High-level coordinator for the NexusAtom engine."""

    def __init__(self) -> None:
        self._parser = ManifestParser()
        self._dag = DAGResolver()
        self._fsm = FSMValidator()

    def load_spec(self, path: Path) -> AtomSpec:
        """Parse a single atom spec file."""
        return self._parser.parse_file(path)

    def load_specs(self, directory: Path) -> list[AtomSpec]:
        """Scan a directory and return all parsed atom specs."""
        return self._parser.scan_directory(directory)

    def resolve_graph(self, atoms: list[AtomSpec]) -> list[str]:
        """Build the dependency DAG and return a valid execution order."""
        graph = self._dag.build(atoms)
        self._dag.validate(graph)
        return self._dag.resolve_order(graph)

    def transition(self, atom: AtomSpec, target: AtomState) -> AtomSpec:
        """Apply a lifecycle transition and return an updated AtomSpec."""
        new_state = self._fsm.apply(atom.state, target)
        return atom.model_copy(update={"state": new_state})
