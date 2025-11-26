from PyQt6.QtCore import QObject, pyqtSignal
from typing import List

from app.domain.models.proyeccion import Proyeccion
from app.infrastructure.repositories.proyeccion_repository import ProyeccionRepository


class ProyeccionViewModel(QObject):
    proyecciones_changed = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, repository: ProyeccionRepository):
        super().__init__()
        self.repository = repository
        self.proyecciones: List[Proyeccion] = []

    def load_proyecciones(self):
        try:
            self.proyecciones = self.repository.get_all()
            self.proyecciones_changed.emit(self.proyecciones)
        except Exception as e:
            self.error_occurred.emit(f"Error loading proyecciones: {str(e)}")

    def add_proyeccion(self, p: Proyeccion):
        try:
            if self.repository.add(p):
                self.load_proyecciones()
        except Exception as e:
            self.error_occurred.emit(f"Error adding proyeccion: {str(e)}")

    def update_proyeccion(self, p: Proyeccion):
        try:
            if self.repository.update(p):
                self.load_proyecciones()
        except Exception as e:
            self.error_occurred.emit(f"Error updating proyeccion: {str(e)}")

    def delete_proyecciones(self, ids: List[tuple]):
        try:
            if self.repository.delete_many(ids):
                self.load_proyecciones()
        except Exception as e:
            self.error_occurred.emit(f"Error deleting proyecciones: {str(e)}")
