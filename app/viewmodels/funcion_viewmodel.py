"""ViewModel for Funcion (Función)."""
from PyQt6.QtCore import pyqtSignal, QObject

from app.domain.models.funcion import Funcion
from app.infrastructure.repositories.funcion_repository import FuncionRepository


class FuncionViewModel(QObject):
    """ViewModel for Funcion entity."""

    funciones_changed = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, repository: FuncionRepository):
        """Initialize FuncionViewModel.

        Args:
            repository: FuncionRepository instance.
        """
        super().__init__()
        self.repository = repository

    def load_funciones(self) -> None:
        """Load all funciones from the repository."""
        try:
            funciones = self.repository.get_all()
            self.funciones_changed.emit(funciones)
        except Exception as e:
            self.error_occurred.emit(f"Error loading funciones: {str(e)}")

    def add_funcion(self, funcion: Funcion) -> bool:
        """Add a new funcion.

        Args:
            funcion: Funcion object to add.

        Returns:
            True if successful, False otherwise.
        """
        try:
            if self.repository.add(funcion):
                self.load_funciones()
                return True
            return False
        except Exception as e:
            self.error_occurred.emit(f"Error adding funcion: {str(e)}")
            return False

    def update_funcion(self, funcion: Funcion) -> bool:
        """Update an existing funcion.

        Args:
            funcion: Funcion object to update.

        Returns:
            True if successful, False otherwise.
        """
        try:
            if self.repository.update(funcion):
                self.load_funciones()
                return True
            return False
        except Exception as e:
            self.error_occurred.emit(f"Error updating funcion: {str(e)}")
            return False

    def delete_funciones(self, funcion_ids: list) -> bool:
        """Delete multiple funciones.

        Args:
            funcion_ids: List of function IDs to delete.

        Returns:
            True if successful, False otherwise.
        """
        try:
            if self.repository.delete_many(funcion_ids):
                self.load_funciones()
                return True
            return False
        except Exception as e:
            self.error_occurred.emit(f"Error deleting funciones: {str(e)}")
            return False
