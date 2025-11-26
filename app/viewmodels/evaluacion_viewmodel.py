from PyQt6.QtCore import QObject, pyqtSignal
from typing import List

from app.domain.models.evaluacion import Evaluacion
from app.infrastructure.repositories.evaluacion_repository import EvaluacionRepository


class EvaluacionViewModel(QObject):
    """ViewModel for managing Evaluacion business logic."""

    evaluaciones_changed = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, repository: EvaluacionRepository):
        super().__init__()
        self.repository = repository
        self.evaluaciones: List[Evaluacion] = []

    def load_evaluaciones(self):
        try:
            self.evaluaciones = self.repository.get_all()
            self.evaluaciones_changed.emit(self.evaluaciones)
        except Exception as e:
            self.error_occurred.emit(f"Error loading evaluaciones: {str(e)}")

    def add_evaluacion(self, evaluacion: Evaluacion):
        try:
            if self.repository.add(evaluacion):
                self.load_evaluaciones()
        except Exception as e:
            self.error_occurred.emit(f"Error adding evaluacion: {str(e)}")

    def update_evaluacion(self, evaluacion: Evaluacion):
        try:
            if self.repository.update(evaluacion):
                self.load_evaluaciones()
        except Exception as e:
            self.error_occurred.emit(f"Error updating evaluacion: {str(e)}")

    def delete_evaluaciones(self, ids: List[tuple]):
        try:
            if self.repository.delete_many(ids):
                self.load_evaluaciones()
        except Exception as e:
            self.error_occurred.emit(f"Error deleting evaluaciones: {str(e)}")
