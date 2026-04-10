# NexusAtom

Deterministic spec-driven engine. Atomic contracts, explicit DAG, manifest tracking, FSM lifecycle. Zero contract drift for multi-agent systems.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     CLI  (Typer)                        │
│         create │ approve │ archive │ scan               │
└───────────────────────────┬─────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────┐
│                    Orchestrator                         │
└──────────┬────────────────────────────┬─────────────────┘
           │                            │
┌──────────▼──────────┐    ┌────────────▼────────────────┐
│   ManifestParser    │    │        DAGResolver           │
│  (YAML frontmatter) │    │    (networkx DiGraph)        │
└──────────┬──────────┘    └────────────┬────────────────┘
           │                            │
┌──────────▼──────────┐    ┌────────────▼────────────────┐
│      AtomSpec       │    │       FSMValidator           │
│   (Pydantic v2)     │    │    (lifecycle states)        │
└─────────────────────┘    └─────────────────────────────┘

Atom lifecycle FSM:
  DRAFT ──► APPROVED ──► ARCHIVED
```

## Project Structure

```
NexusAtom/
├── src/nexus_atom/        # Core engine
│   ├── models.py          # Pydantic v2 AtomSpec + AtomState
│   ├── fsm.py             # FSM lifecycle validator
│   ├── dag.py             # DAG resolver (networkx)
│   ├── manifest.py        # YAML-frontmatter parser
│   └── orchestrator.py    # Coordinates all components
├── cli/
│   └── main.py            # Typer CLI (create/approve/archive/scan)
├── specs/atoms/
│   └── _template.md       # Atom spec template
├── tests/
│   ├── test_models.py
│   ├── test_fsm.py
│   ├── test_dag.py
│   └── test_manifest.py
└── pyproject.toml
```

## Quick Start

```bash
# Install
pip install -e ".[dev]"

# Scaffold a new atom spec
nexus-atom create my-atom --name "My Atom" --description "Does X"

# Approve and archive
nexus-atom approve my-atom
nexus-atom archive my-atom

# Scan and validate all specs + DAG
nexus-atom scan
```

## Development

```bash
# Run tests
pytest

# Type-check (strict)
mypy src cli tests

# Lint
ruff check src cli tests
```
