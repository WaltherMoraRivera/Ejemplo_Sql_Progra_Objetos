"""Domain model for Ciudad entity."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class Ciudad:
    """Represents a city stored in the `ciudad` table.

    Fields match the DDL in `sql/script.sql`: id_ciudad, nombre, region, pais, observaciones.
    """

    id: Optional[int]
    nombre: str
    region: str
    pais: str
    observaciones: str

