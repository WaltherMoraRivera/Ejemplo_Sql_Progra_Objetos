"""ViewModel for Pelicula entity."""
from __future__ import annotations

from typing import List

from PyQt6.QtCore import QObject, pyqtSignal

from app.domain.models.pelicula import Pelicula
from app.infrastructure.repositories.pelicula_repository import PeliculaRepository


class PeliculaViewModel(QObject):
    """ViewModel for managing peliculas."""

    peliculas_changed = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, repository: PeliculaRepository) -> None:
        super().__init__()
        self._repository = repository
        self._peliculas: List[Pelicula] = []

    def load_peliculas(self) -> None:
        """Load all peliculas from repository and emit signal."""
        try:
            self._peliculas = self._repository.get_all()
            self.peliculas_changed.emit(self._peliculas)
        except Exception as e:
            self.error_occurred.emit(f"Error cargando peliculas: {str(e)}")

    def add_pelicula(self, pelicula: Pelicula) -> bool:
        """Add a new pelicula and reload data."""
        try:
            new_id = self._repository.add(pelicula)
            if new_id is not None:
                self.load_peliculas()
                return True
            return False
        except Exception as e:
            self.error_occurred.emit(f"Error creando pelicula: {str(e)}")
            return False

    def delete_peliculas(self, ids: List[int]) -> bool:
        """Delete peliculas by IDs and reload data."""
        try:
            ok = self._repository.delete_many(ids)
            if ok:
                self.load_peliculas()
            return ok
        except Exception as e:
            self.error_occurred.emit(f"Error eliminando peliculas: {str(e)}")
            return False
