"""Domain model for Proyeccion entity."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Proyeccion:
    id_funcion: int
    id_pelicula: int
    orden_proyeccion: int = 1
    comentarios: str = "Sin comentarios"

    def __repr__(self) -> str:
        return f"Proyeccion(id_funcion={self.id_funcion}, id_pelicula={self.id_pelicula}, orden={self.orden_proyeccion})"
