"""Table model for Funcion (Función)."""
from PyQt6.QtCore import Qt, QAbstractTableModel, pyqtSignal

from app.domain.models.funcion import Funcion


class FuncionTableModel(QAbstractTableModel):
    """Table model for displaying Funcion objects in a QTableView."""

    SELECT_COLUMN = 0
    ACTION_COLUMN = 8  # Detalle button column

    def __init__(self):
        """Initialize FuncionTableModel."""
        super().__init__()
        self._funciones: list[Funcion] = []
        self._selected_ids: set = set()

    def rowCount(self, parent=None) -> int:
        """Return number of rows."""
        return len(self._funciones)

    def columnCount(self, parent=None) -> int:
        """Return number of columns (checkbox, fecha, hora, precio, estado, observaciones, id_sede, ..., detalle)."""
        return 9

    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.ItemDataRole.DisplayRole) -> str:
        """Return header text for columns."""
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            headers = [
                "Seleccionar",
                "Fecha",
                "Hora",
                "Precio",
                "Estado",
                "Observaciones",
                "Sede ID",
                "Detalles",
            ]
            return headers[section] if section < len(headers) else ""
        return None

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        """Return cell data."""
        if not index.isValid():
            return None

        funcion = self._funciones[index.row()]
        col = index.column()

        # Checkbox column
        if col == self.SELECT_COLUMN:
            if role == Qt.ItemDataRole.CheckStateRole and funcion.id:
                return Qt.CheckState.Checked if funcion.id in self._selected_ids else Qt.CheckState.Unchecked
            return None

        # Display columns
        if role == Qt.ItemDataRole.DisplayRole:
            if col == 1:
                return funcion.fecha or ""
            elif col == 2:
                return funcion.hora or ""
            elif col == 3:
                return f"${funcion.precio_entrada:,.0f}" if funcion.precio_entrada else "$0"
            elif col == 4:
                return funcion.estado_funcion or ""
            elif col == 5:
                return (funcion.observaciones[:30] + "...") if funcion.observaciones and len(funcion.observaciones) > 30 else funcion.observaciones or ""
            elif col == 6:
                return str(funcion.id_sede) if funcion.id_sede else ""
            elif col == 7:
                return "Detalle"

        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole) -> bool:
        """Handle checkbox state changes."""
        if not index.isValid():
            return False

        funcion = self._funciones[index.row()]
        col = index.column()

        if col == self.SELECT_COLUMN and role == Qt.ItemDataRole.CheckStateRole:
            if not funcion.id:
                return False

            if value == Qt.CheckState.Checked:
                self._selected_ids.add(funcion.id)
            else:
                self._selected_ids.discard(funcion.id)

            self.dataChanged.emit(index, index)
            return True

        return False

    def flags(self, index):
        """Set cell flags (selectable, editable for checkboxes)."""
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        col = index.column()
        if col == self.SELECT_COLUMN:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsUserCheckable
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def update_funciones(self, funciones: list[Funcion]) -> None:
        """Update the table with a new list of funciones.

        Args:
            funciones: List of Funcion objects.
        """
        # Preserve selected IDs that still exist in the new list
        new_ids = {f.id for f in funciones if f.id}
        self._selected_ids &= new_ids

        self.beginResetModel()
        self._funciones = funciones
        self.endResetModel()

    def clear_selection(self) -> None:
        """Clear all checkbox selections."""
        self._selected_ids.clear()
        # Emit dataChanged for all rows to refresh checkboxes visually
        if self.rowCount() > 0:
            self.dataChanged.emit(
                self.index(0, self.SELECT_COLUMN),
                self.index(self.rowCount() - 1, self.SELECT_COLUMN),
            )

    def get_selected_ids(self) -> list:
        """Get list of selected function IDs."""
        return list(self._selected_ids)

    def funcion_at(self, row: int) -> Funcion | None:
        """Get funcion at given row."""
        if 0 <= row < len(self._funciones):
            return self._funciones[row]
        return None
