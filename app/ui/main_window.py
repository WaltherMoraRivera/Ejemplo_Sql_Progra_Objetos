"""Main window for the Cliente management UI."""
from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableView,
    QToolBar,
)

from app.domain.models.cliente import Cliente
from app.infrastructure.database.oracle_connection import OracleConnection
from app.infrastructure.repositories.cliente_repository import ClienteRepository
from app.ui.cliente_table_model import ClienteTableModel
from app.ui.delegates import DetailButtonDelegate
from app.ui.dialogs import ClienteDetailDialog, ClienteFormDialog
from app.viewmodels.cliente_viewmodel import ClienteViewModel


class MainWindow(QMainWindow):
    """Application's main window."""

    def __init__(self, settings_path: Path) -> None:
        super().__init__()
        self.setWindowTitle("Gestión de Clientes")
        self.resize(1100, 550)

        connection = OracleConnection.from_settings(settings_path)
        repository = ClienteRepository(connection)
        self._viewmodel = ClienteViewModel(repository)
        self._model = ClienteTableModel()
        self._detail_delegate = DetailButtonDelegate(self)

        self._setup_ui()
        self._connect_signals()
        self._viewmodel.load_clientes()

    def _setup_ui(self) -> None:
        table = QTableView(self)
        table.setModel(self._model)
        table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        table.setEditTriggers(QAbstractItemView.EditTrigger.AllEditTriggers)
        table.setAlternatingRowColors(True)
        table.horizontalHeader().setStretchLastSection(True)
        table.setItemDelegateForColumn(ClienteTableModel.ACTION_COLUMN, self._detail_delegate)
        self.setCentralWidget(table)

        toolbar = QToolBar("Acciones", self)
        toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        refresh_button = QPushButton("Recargar", self)
        refresh_button.clicked.connect(self._viewmodel.load_clientes)
        toolbar.addWidget(refresh_button)

        new_button = QPushButton("Nuevo", self)
        new_button.clicked.connect(self._open_create_dialog)
        toolbar.addWidget(new_button)

        delete_button = QPushButton("Eliminar", self)
        delete_button.clicked.connect(self._handle_delete_selected)
        toolbar.addWidget(delete_button)

        self.statusBar().showMessage("Listo")

    def _connect_signals(self) -> None:
        self._viewmodel.clientes_changed.connect(self._model.update_clientes)
        self._viewmodel.error_occurred.connect(self._show_error)
        self._detail_delegate.clicked.connect(self._show_detail_for_row)

    def _show_error(self, message: str) -> None:
        QMessageBox.critical(self, "Error", message)

    def _open_create_dialog(self) -> None:
        dialog = ClienteFormDialog(self)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return
        data = dialog.get_data()
        cliente = Cliente(
            id=None,
            rut=data["rut"],
            dv=data["dv"],
            nombre=data["nombre"],
            apellido=data["apellido"],
            fecha_nac=data["fecha_nac"],
            email=data["email"],
            telefono=data["telefono"],
            direccion=data["direccion"],
            estado_cliente=data["estado_cliente"],
            limite_credito=data["limite_credito"],
        )
        if self._viewmodel.add_cliente(cliente):
            self._model.clear_selection()
            self.statusBar().showMessage("Cliente creado correctamente", 5000)

    def _handle_delete_selected(self) -> None:
        selected_ids = self._model.get_selected_ids()
        if not selected_ids:
            QMessageBox.information(self, "Eliminar", "Debe seleccionar al menos un cliente.")
            return

        confirm = QMessageBox.question(
            self,
            "Eliminar clientes",
            f"¿Eliminar {len(selected_ids)} cliente(s) seleccionados?",
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        if self._viewmodel.delete_clientes(selected_ids):
            self._model.clear_selection()
            self.statusBar().showMessage("Clientes eliminados", 5000)

    def _show_detail_for_row(self, row: int) -> None:
        cliente = self._model.cliente_at(row)
        if not cliente:
            return
        dialog = ClienteDetailDialog(cliente, self)
        dialog.exec()
