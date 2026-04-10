"""DAG resolver for atom dependency graphs."""

from __future__ import annotations

from collections.abc import Iterable

import networkx as nx

from nexus_atom.models import AtomSpec


class CycleError(Exception):
    """Raised when a cycle is detected in the dependency graph."""


class DAGResolver:
    """Builds and validates a directed acyclic graph of atom dependencies."""

    def build(self, atoms: Iterable[AtomSpec]) -> nx.DiGraph:
        """Build a directed graph from atom dependency declarations.

        An edge atom_id -> dep means atom_id depends on dep.
        """
        graph: nx.DiGraph = nx.DiGraph()
        for atom in atoms:
            graph.add_node(atom.id)
            for dep in atom.depends_on:
                graph.add_edge(atom.id, dep)
        return graph

    def validate(self, graph: nx.DiGraph) -> None:
        """Raise CycleError if the graph contains a cycle."""
        cycles = list(nx.simple_cycles(graph))
        if cycles:
            cycle_strs = [" -> ".join(c) for c in cycles]
            raise CycleError(f"Dependency cycle(s) detected: {cycle_strs}")

    def resolve_order(self, graph: nx.DiGraph) -> list[str]:
        """Return atoms in topological (dependency-first) order.

        Dependencies are listed before the atoms that require them.
        """
        self.validate(graph)
        return list(nx.topological_sort(graph))[::-1]
