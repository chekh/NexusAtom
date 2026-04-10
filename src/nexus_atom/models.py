"""Pydantic v2 strict models for atom specifications."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class AtomState(str, Enum):
    """Lifecycle states for an atom."""

    DRAFT = "draft"
    APPROVED = "approved"
    ARCHIVED = "archived"


class AtomSpec(BaseModel):
    """Immutable schema for an atom specification."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(..., description="Unique atom identifier (slug format)")
    name: str = Field(..., description="Human-readable atom name")
    state: AtomState = Field(default=AtomState.DRAFT, description="Lifecycle state")
    version: str = Field(..., description="SemVer string")
    depends_on: list[str] = Field(
        default_factory=list, description="IDs of dependency atoms"
    )
    tags: list[str] = Field(default_factory=list, description="Taxonomy tags")
    description: str = Field(
        default="", description="Short summary of the atom's contract"
    )
