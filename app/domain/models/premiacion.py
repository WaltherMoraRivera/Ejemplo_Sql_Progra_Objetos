"""Domain model for Premiacion entity."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass
class Premiacion:
    id_premio: int | None = None
    id_pelicula: int = 0
    categoria: str = ""
    edicion: int = 1
    posicion: int = 1
    descripcion: str = "Sin descripcion"
    fecha_premiacion: date | None = None

    def __repr__(self) -> str:
        return f"Premiacion(id_premio={self.id_premio}, id_pelicula={self.id_pelicula}, categoria={self.categoria})"
