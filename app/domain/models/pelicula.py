"""Domain model for Pelicula entity."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Pelicula:
    """Represents a movie in the festival database."""

    titulo: str
    pais_origen: str
    director: str
    duracion_minutos: int
    genero: str = "Drama"
    clasificacion: str = "TE"
    sinopsis: str = "Sin sinopsis disponible"
    id: int | None = None

    def __repr__(self) -> str:
        return f"Pelicula(id={self.id}, titulo={self.titulo}, director={self.director}, duracion={self.duracion_minutos})"
