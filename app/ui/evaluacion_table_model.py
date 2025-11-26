from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt6.QtGui import QColor

from app.domain.models.evaluacion import Evaluacion


class EvaluacionTableModel(QAbstractTableModel):
    SELECT_COLUMN = 0
    ID_JURADO_COLUMN = 1
    ID_PELICULA_COLUMN = 2
    PUNTUACION_COLUMN = 3
    COMENTARIO_COLUMN = 4
    FECHA_COLUMN = 5
    CATEGORIA_COLUMN = 6
    ACTION_COLUMN = 7

    def __init__(self):
        super().__init__()
        self.evaluaciones: list[Evaluacion] = []
        self.selected_rows = set()

    def rowCount(self, parent=QModelIndex()):
        return len(self.evaluaciones)

    def columnCount(self, parent=QModelIndex()):
        return 8

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            headers = ["", "ID Jurado", "ID Película", "Puntuación", "Comentario", "Fecha", "Categoría", ""]
            return headers[section]
        return None

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        ev = self.evaluaciones[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == self.SELECT_COLUMN:
                return ""
            elif index.column() == self.ID_JURADO_COLUMN:
                return str(ev.id_jurado)
            elif index.column() == self.ID_PELICULA_COLUMN:
                return str(ev.id_pelicula)
            elif index.column() == self.PUNTUACION_COLUMN:
                return str(ev.puntuacion)
            elif index.column() == self.COMENTARIO_COLUMN:
                return ev.comentario
            elif index.column() == self.FECHA_COLUMN:
                return str(ev.fecha or "")
            elif index.column() == self.CATEGORIA_COLUMN:
                return getattr(ev, 'categoria_evaluada', "")
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

    def update_evaluaciones(self, evaluaciones: list[Evaluacion]):
        self.beginResetModel()
        self.evaluaciones = evaluaciones
        self.selected_rows.clear()
        self.endResetModel()

    def get_selected_ids(self) -> list:
        # return list of composite keys as tuples (id_jurado, id_pelicula)
        return [(self.evaluaciones[row].id_jurado, self.evaluaciones[row].id_pelicula) for row in self.selected_rows]

    def evaluacion_at(self, row: int) -> Evaluacion:
        if 0 <= row < len(self.evaluaciones):
            return self.evaluaciones[row]
        return None

    def clear_selection(self):
        if self.selected_rows:
            self.selected_rows.clear()
            self.dataChanged.emit(self.index(0, 0), self.index(len(self.evaluaciones) - 1, self.columnCount() - 1))
