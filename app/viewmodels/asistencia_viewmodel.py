from PyQt6.QtCore import QObject, pyqtSignal
from typing import List
from app.domain.models.asistencia import Asistencia
from app.infrastructure.repositories.asistencia_repository import AsistenciaRepository


class AsistenciaViewModel(QObject):
    """ViewModel para gestionar la lógica de negocio de Asistencia."""

    asistencias_changed = pyqtSignal(list)  # Emitido cuando cambian las asistencias
    error_occurred = pyqtSignal(str)  # Emitido cuando ocurre un error

    def __init__(self, repository: AsistenciaRepository):
        super().__init__()
        self.repository = repository
        self.asistencias: List[Asistencia] = []

    def load_asistencias(self):
        """Carga todas las asistencias desde la BD."""
        try:
            self.asistencias = self.repository.get_all()
            self.asistencias_changed.emit(self.asistencias)
        except Exception as e:
            self.error_occurred.emit(f"Error al cargar asistencias: {str(e)}")

    def add_asistencia(self, asistencia: Asistencia):
        """Añade una nueva asistencia."""
        try:
            if self.repository.add(asistencia):
                self.load_asistencias()
        except Exception as e:
            self.error_occurred.emit(f"Error al añadir asistencia: {str(e)}")

    def update_asistencia(self, asistencia: Asistencia):
        """Actualiza una asistencia existente."""
        try:
            if self.repository.update(asistencia):
                self.load_asistencias()
        except Exception as e:
            self.error_occurred.emit(f"Error al actualizar asistencia: {str(e)}")

    def delete_asistencias(self, ids: List[tuple]):
        """Elimina múltiples asistencias."""
        try:
            if self.repository.delete_many(ids):
                self.load_asistencias()
        except Exception as e:
            self.error_occurred.emit(f"Error al eliminar asistencias: {str(e)}")
