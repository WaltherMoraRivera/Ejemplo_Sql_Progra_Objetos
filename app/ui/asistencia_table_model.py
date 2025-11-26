from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt6.QtGui import QColor
from app.domain.models.asistencia import Asistencia


class AsistenciaTableModel(QAbstractTableModel):
    """Modelo de tabla para mostrar asistencias."""

    SELECT_COLUMN = 0
    ID_FUNCION_COLUMN = 1
    ID_ASISTENTE_COLUMN = 2
    ENTRADAS_COLUMN = 3
    FECHA_COMPRA_COLUMN = 4
    METODO_PAGO_COLUMN = 5
    COMENTARIOS_COLUMN = 6
    ACTION_COLUMN = 7

    def __init__(self):
        super().__init__()
        self.asistencias = []
        self.selected_rows = set()

    def rowCount(self, parent=QModelIndex()):
        return len(self.asistencias)

    def columnCount(self, parent=QModelIndex()):
        return 8  # checkbox + 6 campos + botón detalle

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            headers = ["", "ID Función", "ID Asistente", "Entradas", "Fecha Compra", "Método Pago", "Comentarios", ""]
            return headers[section]
        return None

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        asistencia = self.asistencias[index.row()]

        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == self.SELECT_COLUMN:
                return ""
            elif index.column() == self.ID_FUNCION_COLUMN:
                return str(asistencia.id_funcion)
            elif index.column() == self.ID_ASISTENTE_COLUMN:
                return str(asistencia.id_asistente)
            elif index.column() == self.ENTRADAS_COLUMN:
                return str(asistencia.entradas)
            elif index.column() == self.FECHA_COMPRA_COLUMN:
                return str(asistencia.fecha_compra)
            elif index.column() == self.METODO_PAGO_COLUMN:
                return asistencia.metodo_pago
            elif index.column() == self.COMENTARIOS_COLUMN:
                return asistencia.comentarios
            elif index.column() == self.ACTION_COLUMN:
                return "Detalle"
        elif role == Qt.ItemDataRole.BackgroundRole and index.row() in self.selected_rows:
            return QColor(200, 220, 255)

        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if index.column() == self.SELECT_COLUMN and role == Qt.ItemDataRole.EditRole:
            if value:
                self.selected_rows.add(index.row())
            else:
                self.selected_rows.discard(index.row())
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index):
        if index.column() == self.SELECT_COLUMN:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def update_asistencias(self, asistencias: list):
        """Actualiza la lista de asistencias en la tabla."""
        self.beginResetModel()
        self.asistencias = asistencias
        self.selected_rows.clear()
        self.endResetModel()

    def get_selected_ids(self) -> list:
        """Retorna lista de tuplas (id_funcion, id_asistente) seleccionadas."""
        return [(self.asistencias[row].id_funcion, self.asistencias[row].id_asistente) for row in self.selected_rows]

    def asistencia_at(self, row: int) -> Asistencia:
        """Obtiene la asistencia en una fila específica."""
        if 0 <= row < len(self.asistencias):
            return self.asistencias[row]
        return None
