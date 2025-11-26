from PyQt6.QtCore import QObject, pyqtSignal
from typing import List

from app.domain.models.premiacion import Premiacion
from app.infrastructure.repositories.premiacion_repository import PremiacionRepository


class PremiacionViewModel(QObject):
    premiaciones_changed = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, repository: PremiacionRepository):
        super().__init__()
        self.repository = repository
        self.premiaciones: List[Premiacion] = []

    def load_premiaciones(self):
        try:
            self.premiaciones = self.repository.get_all()
            self.premiaciones_changed.emit(self.premiaciones)
        except Exception as e:
            self.error_occurred.emit(f"Error loading premiaciones: {str(e)}")

    def add_premiacion(self, premiacion: Premiacion):
        try:
            if self.repository.add(premiacion):
                self.load_premiaciones()
        except Exception as e:
            self.error_occurred.emit(f"Error adding premiacion: {str(e)}")

    def update_premiacion(self, premiacion: Premiacion):
        try:
            if self.repository.update(premiacion):
                self.load_premiaciones()
        except Exception as e:
            self.error_occurred.emit(f"Error updating premiacion: {str(e)}")

    def delete_premiaciones(self, ids: List[int]):
        try:
            if self.repository.delete_many(ids):
                self.load_premiaciones()
        except Exception as e:
            self.error_occurred.emit(f"Error deleting premiaciones: {str(e)}")
