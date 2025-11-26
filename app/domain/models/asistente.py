"""Domain model for Asistente (attendee) entity."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class Asistente:
    """Represents an attendee stored in the `asistente` table."""

    id: Optional[int]
    nombre: str
    correo: str
    telefono: str
    edad: Optional[int]
    ciudad_residencia: str
    tipo_asistente: str
