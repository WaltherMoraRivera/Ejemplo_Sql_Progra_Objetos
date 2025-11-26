"""Qt table model for Pelicula data."""
from __future__ import annotations

from typing import List, Sequence, Set

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant

from app.domain.models.pelicula import Pelicula


class PeliculaTableModel(QAbstractTableModel):
    """Model that adapts Pelicula objects to a QTableView."""

    HEADERS: Sequence[str] = (
        "Seleccionar",
        "Título",
        "País",
        "Director",
        "Duración (min)",
        "Género",
        "Clasificación",
        "Sinopsis",
        "Detalle",
    )
    SELECT_COLUMN = 0
    ACTION_COLUMN = len(HEADERS) - 1

    def __init__(self, peliculas: List[Pelicula] | None = None) -> None:
        super().__init__()
        self._peliculas: List[Pelicula] = peliculas or []
        self._selected_ids: Set[int] = set()

    def rowCount(self, parent: QModelIndex | None = None) -> int:  # noqa: N802
        return len(self._peliculas)

    def columnCount(self, parent: QModelIndex | None = None) -> int:  # noqa: N802
        return len(self.HEADERS)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> QVariant:  # noqa: N802
        if not index.isValid():
            return QVariant()

        pelicula = self._peliculas[index.row()]
        column = index.column()

        if column == self.SELECT_COLUMN and role == Qt.ItemDataRole.CheckStateRole:
            if pelicula.id is None:
                return QVariant(Qt.CheckState.Unchecked)
            return QVariant(
                Qt.CheckState.Checked if pelicula.id in self._selected_ids else Qt.CheckState.Unchecked
            )

        if role not in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            return QVariant()

        values = {
            1: pelicula.titulo,
            2: pelicula.pais_origen,
            3: pelicula.director,
            4: pelicula.duracion_minutos,
            5: pelicula.genero,
            6: pelicula.clasificacion,
            7: pelicula.sinopsis[:50] + "..." if len(pelicula.sinopsis) > 50 else pelicula.sinopsis,
            self.ACTION_COLUMN: "Detalle",
        }
        value = values.get(column, "")
        return QVariant(value if value is not None else "")

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> QVariant:  # noqa: N802
        if role != Qt.ItemDataRole.DisplayRole:
            return QVariant()
        if orientation == Qt.Orientation.Horizontal:
            return QVariant(self.HEADERS[section])
        return QVariant(str(section + 1))

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:  # noqa: N802
        base_flags = super().flags(index)
        if not index.isValid():
            return base_flags

        if index.column() == self.SELECT_COLUMN:
            return (
                Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsEditable
                | Qt.ItemFlag.ItemIsUserCheckable
                | Qt.ItemFlag.ItemIsSelectable
            )
        if index.column() == self.ACTION_COLUMN:
            return Qt.ItemFlag.ItemIsEnabled
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def setData(self, index: QModelIndex, value: QVariant, role: int = Qt.ItemDataRole.EditRole) -> bool:  # noqa: N802
        if not index.isValid() or index.column() != self.SELECT_COLUMN:
            return False
        if role not in (Qt.ItemDataRole.CheckStateRole, Qt.ItemDataRole.EditRole):
            return False

        pelicula = self._peliculas[index.row()]
        if pelicula.id is None:
            return False

        state = Qt.CheckState(value)
        if state == Qt.CheckState.Checked:
            self._selected_ids.add(pelicula.id)
        else:
            self._selected_ids.discard(pelicula.id)

        self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole])
        return True

    def update_peliculas(self, peliculas: List[Pelicula]) -> None:
        """Replace the internal list and notify views."""

        self.beginResetModel()
        self._peliculas = peliculas
        current_ids = {pelicula.id for pelicula in peliculas if pelicula.id is not None}
        self._selected_ids.intersection_update(current_ids)
        self.endResetModel()

    def get_selected_ids(self) -> List[int]:
        """Return selected IDs."""

        return list(self._selected_ids)

    def clear_selection(self) -> None:
        """Clear any checkbox selections."""

        if not self._selected_ids:
            return
        self._selected_ids.clear()
        if self.rowCount() == 0:
            return
        top_left = self.index(0, self.SELECT_COLUMN)
        bottom_right = self.index(self.rowCount() - 1, self.SELECT_COLUMN)
        self.dataChanged.emit(top_left, bottom_right, [Qt.ItemDataRole.CheckStateRole])

    def pelicula_at(self, row: int) -> Pelicula | None:
        """Return pelicula for the provided row."""

        if 0 <= row < len(self._peliculas):
            return self._peliculas[row]
        return None
