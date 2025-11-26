from PyQt6.QtCore import QObject, pyqtSignal
from typing import List

from app.domain.models.jurado import Jurado
from app.infrastructure.repositories.jurado_repository import JuradoRepository


class JuradoViewModel(QObject):
    """ViewModel for managing Jurado business logic."""

    jurados_changed = pyqtSignal(list)  # Emitted when jurados list changes
    error_occurred = pyqtSignal(str)    # Emitted when an error occurs

    def __init__(self, repository: JuradoRepository):
        super().__init__()
        self.repository = repository
        self.jurados: List[Jurado] = []

    def load_jurados(self):
        """Load all jurados from the database."""
        try:
            self.jurados = self.repository.get_all()
            self.jurados_changed.emit(self.jurados)
        except Exception as e:
            self.error_occurred.emit(f"Error al cargar jurados: {str(e)}")

    def add_jurado(self, jurado: Jurado):
        """Add a new jurado."""
        try:
            if self.repository.add(jurado):
                self.load_jurados()
        except Exception as e:
            self.error_occurred.emit(f"Error al añadir jurado: {str(e)}")

    def update_jurado(self, jurado: Jurado):
        """Update an existing jurado."""
        try:
            if self.repository.update(jurado):
                self.load_jurados()
        except Exception as e:
            self.error_occurred.emit(f"Error al actualizar jurado: {str(e)}")

    def delete_jurados(self, ids: List[int]):
        """Delete multiple jurados."""
        try:
            if self.repository.delete_many(ids):
                self.load_jurados()
        except Exception as e:
            self.error_occurred.emit(f"Error al eliminar jurados: {str(e)}")
