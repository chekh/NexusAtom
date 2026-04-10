"""Tests for DAG resolver including cycle detection."""

from __future__ import annotations

import pytest

from nexus_atom.dag import CycleError, DAGResolver
from nexus_atom.models import AtomSpec


def _atom(atom_id: str, depends_on: list[str] | None = None) -> AtomSpec:
    return AtomSpec(
        id=atom_id, name=atom_id, version="1.0.0", depends_on=depends_on or []
    )


@pytest.fixture
def resolver() -> DAGResolver:
    return DAGResolver()


def test_build_adds_nodes(resolver: DAGResolver) -> None:
    atoms = [_atom("a"), _atom("b", ["a"])]
    graph = resolver.build(atoms)
    assert "a" in graph.nodes
    assert "b" in graph.nodes


def test_build_adds_edges(resolver: DAGResolver) -> None:
    atoms = [_atom("a"), _atom("b", ["a"])]
    graph = resolver.build(atoms)
    assert graph.has_edge("b", "a")


def test_no_cycle_validates(resolver: DAGResolver) -> None:
    atoms = [_atom("a"), _atom("b", ["a"]), _atom("c", ["b"])]
    graph = resolver.build(atoms)
    resolver.validate(graph)  # must not raise


def test_direct_cycle_raises(resolver: DAGResolver) -> None:
    atoms = [_atom("a", ["b"]), _atom("b", ["a"])]
    graph = resolver.build(atoms)
    with pytest.raises(CycleError):
        resolver.validate(graph)


def test_indirect_cycle_raises(resolver: DAGResolver) -> None:
    atoms = [_atom("a", ["c"]), _atom("b", ["a"]), _atom("c", ["b"])]
    graph = resolver.build(atoms)
    with pytest.raises(CycleError):
        resolver.validate(graph)


def test_resolve_order_dependencies_first(resolver: DAGResolver) -> None:
    # c depends on b, b depends on a => order: a, b, c
    atoms = [_atom("a"), _atom("b", ["a"]), _atom("c", ["b"])]
    graph = resolver.build(atoms)
    order = resolver.resolve_order(graph)
    assert order.index("a") < order.index("b")
    assert order.index("b") < order.index("c")


def test_resolve_order_raises_on_cycle(resolver: DAGResolver) -> None:
    atoms = [_atom("a", ["b"]), _atom("b", ["a"])]
    graph = resolver.build(atoms)
    with pytest.raises(CycleError):
        resolver.resolve_order(graph)


def test_empty_graph_valid(resolver: DAGResolver) -> None:
    graph = resolver.build([])
    resolver.validate(graph)
    assert resolver.resolve_order(graph) == []


def test_isolated_nodes(resolver: DAGResolver) -> None:
    atoms = [_atom("x"), _atom("y")]
    graph = resolver.build(atoms)
    resolver.validate(graph)
    order = resolver.resolve_order(graph)
    assert set(order) == {"x", "y"}
