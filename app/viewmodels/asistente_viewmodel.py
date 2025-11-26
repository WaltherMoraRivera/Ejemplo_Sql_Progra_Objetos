"""ViewModel for Asistente listing."""
from __future__ import annotations

from typing import List, Sequence

from PyQt6.QtCore import QObject, pyqtSignal

from app.domain.models.asistente import Asistente
from app.infrastructure.repositories.asistente_repository import AsistenteRepository


class AsistenteViewModel(QObject):
    """Coordinates UI updates for asistente data."""

    asistentes_changed = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, repository: AsistenteRepository) -> None:
        super().__init__()
        self._repository = repository
        self._asistentes: List[Asistente] = []

    def load_asistentes(self) -> None:
        try:
            self._asistentes = self._repository.get_all()
            self.asistentes_changed.emit(self._asistentes)
        except Exception as exc:  # pragma: no cover - interacts with DB
            self.error_occurred.emit(str(exc))

    def add_asistente(self, asistente: Asistente) -> bool:
        try:
            self._repository.add(asistente)
            self.load_asistentes()
            return True
        except Exception as exc:  # pragma: no cover - interacts with DB
            self.error_occurred.emit(str(exc))
            return False

    def delete_asistentes(self, asistente_ids: Sequence[int]) -> bool:
        try:
            self._repository.delete_many(asistente_ids)
            self.load_asistentes()
            return True
        except Exception as exc:  # pragma: no cover - interacts with DB
            self.error_occurred.emit(str(exc))
            return False

    @property
    def asistentes(self) -> List[Asistente]:
        return self._asistentes
