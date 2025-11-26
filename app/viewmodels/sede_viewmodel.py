"""ViewModel for Sede listing."""
from __future__ import annotations

from typing import List, Sequence

from PyQt6.QtCore import QObject, pyqtSignal

from app.domain.models.sede import Sede
from app.infrastructure.repositories.sede_repository import SedeRepository


class SedeViewModel(QObject):
    """Coordinates UI updates for sede data."""

    sedes_changed = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, repository: SedeRepository) -> None:
        super().__init__()
        self._repository = repository
        self._sedes: List[Sede] = []

    def load_sedes(self) -> None:
        try:
            self._sedes = self._repository.get_all()
            self.sedes_changed.emit(self._sedes)
        except Exception as exc:
            self.error_occurred.emit(str(exc))

    def add_sede(self, sede: Sede) -> bool:
        try:
            self._repository.add(sede)
            self.load_sedes()
            return True
        except Exception as exc:
            self.error_occurred.emit(str(exc))
            return False

    def delete_sedes(self, sede_ids: Sequence[int]) -> bool:
        try:
            self._repository.delete_many(sede_ids)
            self.load_sedes()
            return True
        except Exception as exc:
            self.error_occurred.emit(str(exc))
            return False

    @property
    def sedes(self) -> List[Sede]:
        return self._sedes
