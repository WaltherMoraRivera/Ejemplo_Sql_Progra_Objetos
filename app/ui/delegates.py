"""Custom delegates for table interactions."""
from __future__ import annotations

from PyQt6.QtCore import QEvent, QModelIndex, QPoint, pyqtSignal
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QApplication, QStyle, QStyleOptionButton, QStyledItemDelegate


class DetailButtonDelegate(QStyledItemDelegate):
    """Renders a push button on a table cell and emits clicks."""

    clicked = pyqtSignal(int)

    def paint(self, painter, option, index):  # type: ignore[override]
        button_option = QStyleOptionButton()
        button_option.rect = option.rect.adjusted(4, 4, -4, -4)
        button_option.text = "Detalle"
        button_option.state = QStyle.StateFlag.State_Enabled
        if option.state & QStyle.StateFlag.State_MouseOver:
            button_option.state |= QStyle.StateFlag.State_MouseOver
        QApplication.style().drawControl(QStyle.ControlElement.CE_PushButton, button_option, painter)

    def editorEvent(self, event: QEvent, model, option, index: QModelIndex) -> bool:  # type: ignore[override]
        if event.type() == QEvent.Type.MouseButtonRelease and isinstance(event, QMouseEvent):
            pos: QPoint = event.position().toPoint()
            if option.rect.contains(pos):
                self.clicked.emit(index.row())
                return True
        return super().editorEvent(event, model, option, index)
