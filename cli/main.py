"""Typer CLI for NexusAtom spec-driven engine."""

from __future__ import annotations

import re
from pathlib import Path

import typer
import yaml

from nexus_atom.models import AtomState
from nexus_atom.orchestrator import Orchestrator

app = typer.Typer(
    name="nexus-atom",
    help="Spec-driven engine CLI: manage atom lifecycle and dependency graph.",
    no_args_is_help=True,
)

_DEFAULT_SPECS_DIR = Path("specs/atoms")


def _orchestrator() -> Orchestrator:
    return Orchestrator()


@app.command()
def create(
    atom_id: str = typer.Argument(..., help="Unique atom identifier (slug)"),
    name: str = typer.Option(..., "--name", "-n", help="Human-readable atom name"),
    version: str = typer.Option("0.1.0", "--version", "-v", help="SemVer version"),
    description: str = typer.Option(
        "", "--description", "-d", help="Short description"
    ),
    specs_dir: Path = typer.Option(
        _DEFAULT_SPECS_DIR, "--specs-dir", help="Atoms spec directory"
    ),
) -> None:
    """Scaffold a new atom spec file in DRAFT state."""
    specs_dir.mkdir(parents=True, exist_ok=True)
    output_path = specs_dir / f"{atom_id}.md"
    if output_path.exists():
        typer.echo(f"Error: spec already exists at {output_path}", err=True)
        raise typer.Exit(code=1)
    metadata = {
        "id": atom_id,
        "name": name,
        "state": "draft",
        "version": version,
        "depends_on": [],
        "tags": [],
        "description": description,
    }
    frontmatter = yaml.dump(metadata, default_flow_style=False, sort_keys=False)
    content = (
        f"---\n{frontmatter}---\n\n"
        "## Contract\n\n"
        "<!-- Describe the formal contract of this atom here -->\n"
    )
    output_path.write_text(content)
    typer.echo(f"Created: {output_path}")


@app.command()
def approve(
    atom_id: str = typer.Argument(..., help="Atom identifier to approve"),
    specs_dir: Path = typer.Option(
        _DEFAULT_SPECS_DIR, "--specs-dir", help="Atoms spec directory"
    ),
) -> None:
    """Transition an atom from DRAFT to APPROVED."""
    _transition_atom(atom_id, AtomState.APPROVED, specs_dir)


@app.command()
def archive(
    atom_id: str = typer.Argument(..., help="Atom identifier to archive"),
    specs_dir: Path = typer.Option(
        _DEFAULT_SPECS_DIR, "--specs-dir", help="Atoms spec directory"
    ),
) -> None:
    """Transition an atom from APPROVED to ARCHIVED."""
    _transition_atom(atom_id, AtomState.ARCHIVED, specs_dir)


@app.command()
def scan(
    specs_dir: Path = typer.Option(
        _DEFAULT_SPECS_DIR, "--specs-dir", help="Atoms spec directory"
    ),
    check_dag: bool = typer.Option(
        True, "--check-dag/--no-check-dag", help="Validate dependency DAG"
    ),
) -> None:
    """Scan the specs directory, validate all atoms, and optionally check the DAG."""
    if not specs_dir.exists():
        typer.echo(f"Error: specs directory not found: {specs_dir}", err=True)
        raise typer.Exit(code=1)
    orch = _orchestrator()
    atoms = orch.load_specs(specs_dir)
    if not atoms:
        typer.echo("No atom specs found.")
        return
    typer.echo(f"Found {len(atoms)} atom(s):")
    for atom in atoms:
        typer.echo(f"  [{atom.state.value}] {atom.id} v{atom.version}")
    if check_dag:
        try:
            order = orch.resolve_graph(atoms)
            typer.echo(f"\nResolution order: {' -> '.join(order)}")
        except Exception as exc:
            typer.echo(f"DAG error: {exc}", err=True)
            raise typer.Exit(code=1)


def _transition_atom(atom_id: str, target: AtomState, specs_dir: Path) -> None:
    """Load, transition, and rewrite an atom spec file."""
    spec_path = specs_dir / f"{atom_id}.md"
    if not spec_path.exists():
        typer.echo(f"Error: spec not found: {spec_path}", err=True)
        raise typer.Exit(code=1)
    orch = _orchestrator()
    atom = orch.load_spec(spec_path)
    try:
        updated = orch.transition(atom, target)
    except Exception as exc:
        typer.echo(f"Transition error: {exc}", err=True)
        raise typer.Exit(code=1)
    content = spec_path.read_text()
    content = re.sub(
        r"^state:\s*\S+",
        f"state: {updated.state.value}",
        content,
        count=1,
        flags=re.MULTILINE,
    )
    spec_path.write_text(content)
    typer.echo(f"Updated {spec_path}: {atom.state.value} -> {updated.state.value}")


if __name__ == "__main__":
    app()
