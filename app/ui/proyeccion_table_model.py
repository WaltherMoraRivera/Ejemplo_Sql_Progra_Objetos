from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt6.QtGui import QColor

from app.domain.models.proyeccion import Proyeccion


class ProyeccionTableModel(QAbstractTableModel):
    SELECT_COLUMN = 0
    ID_FUNCION_COLUMN = 1
    ID_PELICULA_COLUMN = 2
    ORDEN_COLUMN = 3
    COMENTARIOS_COLUMN = 4
    ACTION_COLUMN = 5

    def __init__(self):
        super().__init__()
        self.proyecciones: list[Proyeccion] = []
        self.selected_rows = set()

    def rowCount(self, parent=QModelIndex()):
        return len(self.proyecciones)

    def columnCount(self, parent=QModelIndex()):
        return 6

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            headers = ["", "ID Función", "ID Película", "Orden", "Comentarios", ""]
            return headers[section]
        return None

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        p = self.proyecciones[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == self.SELECT_COLUMN:
                return ""
            elif index.column() == self.ID_FUNCION_COLUMN:
                return str(p.id_funcion)
            elif index.column() == self.ID_PELICULA_COLUMN:
                return str(p.id_pelicula)
            elif index.column() == self.ORDEN_COLUMN:
                return str(p.orden_proyeccion)
            elif index.column() == self.COMENTARIOS_COLUMN:
                return p.comentarios
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

    def update_proyecciones(self, proyecciones: list[Proyeccion]):
        self.beginResetModel()
        self.proyecciones = proyecciones
        self.selected_rows.clear()
        self.endResetModel()

    def get_selected_ids(self) -> list:
        return [(self.proyecciones[row].id_funcion, self.proyecciones[row].id_pelicula) for row in self.selected_rows]

    def proyeccion_at(self, row: int) -> Proyeccion:
        if 0 <= row < len(self.proyecciones):
            return self.proyecciones[row]
        return None

    def clear_selection(self):
        if self.selected_rows:
            self.selected_rows.clear()
            self.dataChanged.emit(self.index(0, 0), self.index(len(self.proyecciones) - 1, self.columnCount() - 1))
