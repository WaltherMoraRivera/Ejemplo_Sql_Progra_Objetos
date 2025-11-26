"""ViewModel for Ciudad listing."""
from __future__ import annotations

from typing import List, Sequence

from PyQt6.QtCore import QObject, pyqtSignal

from app.domain.models.ciudad import Ciudad
from app.infrastructure.repositories.ciudad_repository import CiudadRepository


class CiudadViewModel(QObject):
    """Coordinates UI updates for ciudad data."""

    ciudades_changed = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, repository: CiudadRepository) -> None:
        super().__init__()
        self._repository = repository
        self._ciudades: List[Ciudad] = []

    def load_ciudades(self) -> None:
        try:
            self._ciudades = self._repository.get_all()
            self.ciudades_changed.emit(self._ciudades)
        except Exception as exc:  # pragma: no cover - interacts with DB
            self.error_occurred.emit(str(exc))

    def add_ciudad(self, ciudad: Ciudad) -> bool:
        try:
            self._repository.add(ciudad)
            self.load_ciudades()
            return True
        except Exception as exc:  # pragma: no cover - interacts with DB
            self.error_occurred.emit(str(exc))
            return False

    def delete_ciudades(self, ciudad_ids: Sequence[int]) -> bool:
        try:
            self._repository.delete_many(ciudad_ids)
            self.load_ciudades()
            return True
        except Exception as exc:  # pragma: no cover - interacts with DB
            self.error_occurred.emit(str(exc))
            return False

    @property
    def ciudades(self) -> List[Ciudad]:
        return self._ciudades
