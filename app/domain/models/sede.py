"""Domain model for Sede entity."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class Sede:
    """Represents a sede (venue) stored in the `sede` table.

    Fields match DDL: id_sede, nombre, direccion, capacidad_maxima, tipo_sede, id_ciudad, estado.
    """

    id: Optional[int]
    nombre: str
    direccion: str
    capacidad_maxima: int
    tipo_sede: str
    id_ciudad: int
    estado: str
