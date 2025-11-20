"""ViewModel for Cliente listing."""
from __future__ import annotations

from typing import List, Sequence

from PyQt6.QtCore import QObject, pyqtSignal

from app.domain.models.cliente import Cliente
from app.infrastructure.repositories.cliente_repository import ClienteRepository


class ClienteViewModel(QObject):
    """Coordinates UI updates for client data."""

    clientes_changed = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, repository: ClienteRepository) -> None:
        super().__init__()
        self._repository = repository
        self._clientes: List[Cliente] = []

    def load_clientes(self) -> None:
        """Fetch clients from repository and notify listeners."""

        try:
            self._clientes = self._repository.get_all()
            self.clientes_changed.emit(self._clientes)
        except Exception as exc:  # pragma: no cover - interacts with DB
            self.error_occurred.emit(str(exc))

    def add_cliente(self, cliente: Cliente) -> bool:
        """Persist a new client and refresh cache."""

        try:
            self._repository.add(cliente)
            self.load_clientes()
            return True
        except Exception as exc:  # pragma: no cover - interacts with DB
            self.error_occurred.emit(str(exc))
            return False

    def delete_clientes(self, cliente_ids: Sequence[int]) -> bool:
        """Delete multiple clients and refresh cache."""

        try:
            self._repository.delete_many(cliente_ids)
            self.load_clientes()
            return True
        except Exception as exc:  # pragma: no cover - interacts with DB
            self.error_occurred.emit(str(exc))
            return False

    @property
    def clientes(self) -> List[Cliente]:
        """Return cached clients."""

        return self._clientes

