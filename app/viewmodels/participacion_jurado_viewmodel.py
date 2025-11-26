from PyQt6.QtCore import QObject, pyqtSignal

from app.domain.models.participacion_jurado import ParticipacionJurado
from app.infrastructure.repositories.participacion_jurado_repository import ParticipacionJuradoRepository


class ParticipacionJuradoViewModel(QObject):
    """ViewModel for participacion_jurado entity."""

    participaciones_changed = pyqtSignal(list)  # emit list of participaciones
    error_occurred = pyqtSignal(str)

    def __init__(self, repository: ParticipacionJuradoRepository) -> None:
        super().__init__()
        self._repository = repository
        self._participaciones: list[ParticipacionJurado] = []

    @property
    def participaciones(self) -> list[ParticipacionJurado]:
        return self._participaciones

    def load_participaciones(self) -> None:
        """Load all participaciones from repository and emit them."""
        try:
            self._participaciones = self._repository.get_all()
            self.participaciones_changed.emit(self._participaciones)
        except Exception as e:
            self.error_occurred.emit(f"Error loading participaciones: {str(e)}")

    def add_participacion(self, participacion: ParticipacionJurado) -> bool:
        """Add a new participacion."""
        try:
            success = self._repository.add(participacion)
            if success:
                self.load_participaciones()
            return success
        except Exception as e:
            self.error_occurred.emit(f"Error adding participacion: {str(e)}")
            return False

    def update_participacion(self, participacion: ParticipacionJurado) -> bool:
        """Update an existing participacion."""
        try:
            success = self._repository.update(participacion)
            if success:
                self.load_participaciones()
            return success
        except Exception as e:
            self.error_occurred.emit(f"Error updating participacion: {str(e)}")
            return False

    def delete_participaciones(self, ids: list[tuple]) -> bool:
        """Delete multiple participaciones by composite IDs."""
        try:
            success = self._repository.delete_many(ids)
            if success:
                self.load_participaciones()
            return success
        except Exception as e:
            self.error_occurred.emit(f"Error deleting participaciones: {str(e)}")
            return False
