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
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QSizePolicy,
)
try:
    from PyQt6.QtWidgets import QAction
except Exception:
    # Some PyQt6 installations expose QAction in QtGui
    from PyQt6.QtGui import QAction

from app.domain.models.asistente import Asistente
from app.domain.models.ciudad import Ciudad
from app.domain.models.sede import Sede
from app.domain.models.pelicula import Pelicula
from app.domain.models.funcion import Funcion
from app.domain.models.asistencia import Asistencia
from app.domain.models.jurado import Jurado
from app.domain.models.participacion_jurado import ParticipacionJurado
from app.domain.models.evaluacion import Evaluacion
from app.domain.models.premiacion import Premiacion
from app.domain.models.proyeccion import Proyeccion
from app.infrastructure.database.oracle_connection import OracleConnection
from app.infrastructure.repositories.asistente_repository import AsistenteRepository
from app.infrastructure.repositories.ciudad_repository import CiudadRepository
from app.infrastructure.repositories.sede_repository import SedeRepository
from app.infrastructure.repositories.pelicula_repository import PeliculaRepository
from app.infrastructure.repositories.funcion_repository import FuncionRepository
from app.infrastructure.repositories.asistencia_repository import AsistenciaRepository
from app.infrastructure.repositories.jurado_repository import JuradoRepository
from app.infrastructure.repositories.participacion_jurado_repository import ParticipacionJuradoRepository
from app.infrastructure.repositories.evaluacion_repository import EvaluacionRepository
from app.infrastructure.repositories.premiacion_repository import PremiacionRepository
from app.infrastructure.repositories.proyeccion_repository import ProyeccionRepository
from app.ui.asistente_table_model import AsistenteTableModel
from app.ui.ciudad_table_model import CiudadTableModel
from app.ui.sede_table_model import SedeTableModel
from app.ui.pelicula_table_model import PeliculaTableModel
from app.ui.funcion_table_model import FuncionTableModel
from app.ui.asistencia_table_model import AsistenciaTableModel
from app.ui.jurado_table_model import JuradoTableModel
from app.ui.participacion_jurado_table_model import ParticipacionJuradoTableModel
from app.ui.evaluacion_table_model import EvaluacionTableModel
from app.ui.premiacion_table_model import PremiacionTableModel
from app.ui.proyeccion_table_model import ProyeccionTableModel
from app.ui.delegates import DetailButtonDelegate
from app.ui.dialogs import (
    ClienteDetailDialog,
    ClienteFormDialog,
    CiudadFormDialog,
    CiudadDetailDialog,
    SedeFormDialog,
    SedeDetailDialog,
    PeliculaFormDialog,
    PeliculaDetailDialog,
    FuncionFormDialog,
    FuncionDetailDialog,
    AsistenciaFormDialog,
    AsistenciaDetailDialog,
    JuradoFormDialog,
    JuradoDetailDialog,
    ParticipacionJuradoFormDialog,
    ParticipacionJuradoDetailDialog,
    EvaluacionFormDialog,
    EvaluacionDetailDialog,
    PremiacionFormDialog,
    PremiacionDetailDialog,
    ProyeccionFormDialog,
    ProyeccionDetailDialog,
)
from app.viewmodels.asistente_viewmodel import AsistenteViewModel
from app.viewmodels.ciudad_viewmodel import CiudadViewModel
from app.viewmodels.sede_viewmodel import SedeViewModel
from app.viewmodels.pelicula_viewmodel import PeliculaViewModel
from app.viewmodels.funcion_viewmodel import FuncionViewModel
from app.viewmodels.asistencia_viewmodel import AsistenciaViewModel
from app.viewmodels.jurado_viewmodel import JuradoViewModel
from app.viewmodels.participacion_jurado_viewmodel import ParticipacionJuradoViewModel
from app.viewmodels.evaluacion_viewmodel import EvaluacionViewModel
from app.viewmodels.premiacion_viewmodel import PremiacionViewModel
from app.viewmodels.proyeccion_viewmodel import ProyeccionViewModel


class MainWindow(QMainWindow):
    """Application's main window."""

    def __init__(self, settings_path: Path) -> None:
        super().__init__()
        self.setWindowTitle("Gestor de Festival de Cine")
        self.resize(1100, 550)
        self._settings_path = settings_path
        self._detail_delegate = DetailButtonDelegate(self)

        # current entity: None until user selects a table
        self._entity: str | None = None
        self._viewmodel = None
        self._model = None

        self._setup_ui()
        # Show table selection menu instead of loading a default table
        self._show_table_selection_menu()

    def _setup_ui(self) -> None:
        """Initialize UI containers but don't load a table yet."""
        self._main_container = QWidget(self)
        self.setCentralWidget(self._main_container)
        # Persistent layout for the central container to avoid repeated setLayout calls
        self._main_layout = QVBoxLayout()
        self._main_container.setLayout(self._main_layout)

        self._table = QTableView()
        self._table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.AllEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.horizontalHeader().setStretchLastSection(True)

        toolbar = QToolBar("Acciones", self)
        toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        # Primary actions implemented as QActions for reliable show/hide
        self._refresh_action = QAction("Recargar", self)
        toolbar.addAction(self._refresh_action)

        self._new_action = QAction("Nuevo", self)
        self._new_action.triggered.connect(self._open_create_dialog)
        toolbar.addAction(self._new_action)

        self._delete_action = QAction("Eliminar", self)
        self._delete_action.triggered.connect(self._handle_delete_selected)
        toolbar.addAction(self._delete_action)

        # Spacer to push the back button to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)

        # Back action to return to table selection (hidden until inside a table view)
        self._back_action = QAction("Volver al Menu", self)
        self._back_action.triggered.connect(self._back_to_menu)
        toolbar.addAction(self._back_action)
        # alias for backwards compatibility with existing code/tests
        self._back_button = self._back_action

        # Hide actions and back button until a table is selected
        self._refresh_action.setVisible(False)
        self._new_action.setVisible(False)
        self._delete_action.setVisible(False)
        self._back_action.setVisible(False)

        # We no longer show a top-level "Tabla" menu here — selection is via the visual menu
        self.statusBar().showMessage("Seleccione una tabla para comenzar")

    def _show_table_selection_menu(self) -> None:
        """Display a menu to select which table to manage."""
        # Clear current entity when returning to menu
        self._entity = None
        # Reset window title to base title
        self.setWindowTitle("Gestor de Festival de Cine")
        
        # Create menu widget
        menu_widget = QWidget()
        layout = QVBoxLayout()

        # Title
        title = QLabel("TABLAS DISPONIBLES")
        title_font = title.font()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(30)
        layout.addWidget(title)
        layout.addSpacing(30)

        # Button grid
        button_layout = QGridLayout()
        button_layout.setSpacing(20)

        # Define tables: (nombre, entity_key, row, col)
        # Layout: 6 rows x 2 cols = 12 buttons (11 tables + 1 close button)
        # Button order adjusted to user's required sequence:
        # 1 Ciudad, 2 Sede, 3 Pelicula, 4 Funcion, 5 Proyeccion,
        # 6 Asistente, 7 Asistencia, 8 Jurado, 9 Participacion_Jurado,
        # 10 Evaluacion, 11 Premiacion, 12 Cerrar App
        tables = [
            ("CIUDADES", "ciudad", 0, 0),
            ("SEDES", "sede", 0, 1),
            ("PELÍCULAS", "pelicula", 1, 0),
            ("FUNCIONES", "funcion", 1, 1),
            ("PROYECCIONES", "proyeccion", 2, 0),
            ("ASISTENTES", "asistente", 2, 1),
            ("ASISTENCIAS", "asistencia", 3, 0),
            ("JURADOS", "jurado", 3, 1),
            ("PARTICIPACIONES", "participacion_jurado", 4, 0),
            ("EVALUACIONES", "evaluacion", 4, 1),
            ("PREMIACIONES", "premiacion", 5, 0),
        ]

        # Smaller buttons so the 12-button grid fits nicely
        for tabla_nombre, entity_key, row, col in tables:
            btn = QPushButton(tabla_nombre)
            btn.setMinimumSize(180, 80)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            btn_font = btn.font()
            btn_font.setPointSize(11)
            btn_font.setBold(True)
            btn.setFont(btn_font)
            btn.clicked.connect(lambda checked, ek=entity_key: self._set_entity(ek))
            button_layout.addWidget(btn, row, col)

        # Add the symmetric 12th button: CERRAR APP (red background, white text)
        close_btn = QPushButton("CERRAR APP")
        close_btn.setMinimumSize(180, 80)
        close_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        close_font = close_btn.font()
        close_font.setPointSize(11)
        close_font.setBold(True)
        close_btn.setFont(close_font)
        # Red background, white text
        close_btn.setStyleSheet("background-color: #c0392b; color: white;")
        close_btn.clicked.connect(self.close)
        # place at final row, second column
        button_layout.addWidget(close_btn, 5, 1)

        layout.addLayout(button_layout)
        layout.addStretch()

        menu_widget.setLayout(layout)
        # Clear existing widgets, table is never deleted just hidden and removed from layout
        self._clear_main_container()
        self._main_layout.addWidget(menu_widget)

        # Hide primary actions when showing menu
        if hasattr(self, "_refresh_action"):
            self._refresh_action.setVisible(False)
        if hasattr(self, "_new_action"):
            self._new_action.setVisible(False)
        if hasattr(self, "_delete_action"):
            self._delete_action.setVisible(False)
        if hasattr(self, "_back_action"):
            self._back_action.setVisible(False)

    def _show_table_view(self) -> None:
        """Switch from menu view to table view."""
        # Clear the main container (table is never deleted, just hidden and removed)
        self._clear_main_container()

        # Add table view back to layout and show it
        self._main_layout.addWidget(self._table)
        self._table.show()

    def _clear_main_container(self) -> None:
        """Remove all widgets from the main layout.

        The `self._table` is never deleted, only removed and hidden so it can be reused.
        """
        while self._main_layout.count():
            item = self._main_layout.takeAt(0)
            w = item.widget()
            if not w:
                continue
            if w is self._table:
                # Never delete the table; just remove it from layout and hide
                self._main_layout.removeWidget(self._table)
                self._table.hide()
            else:
                w.setParent(None)
                w.deleteLater()

    def _connect_signals(self) -> None:
        # Connect appropriate signals depending on current entity
        try:
            if self._entity == 'asistente':
                self._viewmodel.asistentes_changed.connect(self._model.update_asistentes)
                refresh_action = getattr(self._viewmodel, 'load_asistentes', None)
            elif self._entity == 'ciudad':
                self._viewmodel.ciudades_changed.connect(self._model.update_ciudades)
                refresh_action = getattr(self._viewmodel, 'load_ciudades', None)
            elif self._entity == 'sede':
                self._viewmodel.sedes_changed.connect(self._model.update_sedes)
                refresh_action = getattr(self._viewmodel, 'load_sedes', None)
            elif self._entity == 'pelicula':
                self._viewmodel.peliculas_changed.connect(self._model.update_peliculas)
                refresh_action = getattr(self._viewmodel, 'load_peliculas', None)
            elif self._entity == 'funcion':
                self._viewmodel.funciones_changed.connect(self._model.update_funciones)
                refresh_action = getattr(self._viewmodel, 'load_funciones', None)
            elif self._entity == 'asistencia':
                self._viewmodel.asistencias_changed.connect(self._model.update_asistencias)
                refresh_action = getattr(self._viewmodel, 'load_asistencias', None)
            elif self._entity == 'jurado':
                self._viewmodel.jurados_changed.connect(self._model.update_jurados)
                refresh_action = getattr(self._viewmodel, 'load_jurados', None)
            elif self._entity == 'participacion_jurado':
                self._viewmodel.participaciones_changed.connect(self._model.update_participaciones)
                refresh_action = getattr(self._viewmodel, 'load_participaciones', None)
            elif self._entity == 'evaluacion':
                self._viewmodel.evaluaciones_changed.connect(self._model.update_evaluaciones)
                refresh_action = getattr(self._viewmodel, 'load_evaluaciones', None)
            elif self._entity == 'premiacion':
                self._viewmodel.premiaciones_changed.connect(self._model.update_premiaciones)
                refresh_action = getattr(self._viewmodel, 'load_premiaciones', None)
            elif self._entity == 'proyeccion':
                self._viewmodel.proyecciones_changed.connect(self._model.update_proyecciones)
                refresh_action = getattr(self._viewmodel, 'load_proyecciones', None)
            else:
                refresh_action = None
        except AttributeError:
            # fallback to legacy names
            try:
                self._viewmodel.clientes_changed.connect(self._model.update_clientes)
                refresh_action = getattr(self._viewmodel, 'load_clientes', None)
            except Exception:
                refresh_action = None

        # connect error and delegate
        self._viewmodel.error_occurred.connect(self._show_error)
        self._detail_delegate.clicked.connect(self._show_detail_for_row)

        # connect refresh button to the viewmodel loader
        if refresh_action:
            try:
                self._refresh_action.triggered.disconnect()
            except Exception:
                pass
            self._refresh_action.triggered.connect(refresh_action)

    def _show_error(self, message: str) -> None:
        QMessageBox.critical(self, "Error", message)

    def _open_create_dialog(self) -> None:
        if self._entity is None or self._viewmodel is None or self._model is None:
            QMessageBox.warning(self, "Información", "Seleccione una tabla primero.")
            return

        if self._entity == 'asistente':
            dialog = ClienteFormDialog(self)
            if dialog.exec() != dialog.DialogCode.Accepted:
                return
            data = dialog.get_data()
            obj = Asistente(
                id=None,
                nombre=data["nombre"],
                correo=data["correo"],
                telefono=data["telefono"],
                edad=data["edad"],
                ciudad_residencia=data["ciudad_residencia"],
                tipo_asistente=data["tipo_asistente"],
            )
            if getattr(self._viewmodel, "add_asistente", None):
                created = self._viewmodel.add_asistente(obj)
            else:
                created = self._viewmodel.add_cliente(obj)
            if created:
                self._model.clear_selection()
                self.statusBar().showMessage("Asistente creado correctamente", 5000)
        elif self._entity == 'ciudad':
            dialog = CiudadFormDialog(self)
            if dialog.exec() != dialog.DialogCode.Accepted:
                return
            data = dialog.get_data()
            ciudad = Ciudad(
                id=None,
                nombre=data["nombre"],
                region=data.get("region", ""),
                pais=data.get("pais", ""),
                observaciones=data.get("observaciones", ""),
            )
            if getattr(self._viewmodel, "add_ciudad", None):
                created = self._viewmodel.add_ciudad(ciudad)
            else:
                created = False
            if created:
                self._model.clear_selection()
                self.statusBar().showMessage("Ciudad creada correctamente", 5000)
        elif self._entity == 'sede':
            dialog = SedeFormDialog(self)
            if dialog.exec() != dialog.DialogCode.Accepted:
                return
            data = dialog.get_data()
            sede = Sede(
                id=None,
                nombre=data["nombre"],
                direccion=data["direccion"],
                capacidad_maxima=data["capacidad_maxima"],
                tipo_sede=data["tipo_sede"],
                id_ciudad=data["id_ciudad"],
                estado=data["estado"],
            )
            if getattr(self._viewmodel, "add_sede", None):
                created = self._viewmodel.add_sede(sede)
            else:
                created = False
            if created:
                self._model.clear_selection()
                self.statusBar().showMessage("Sede creada correctamente", 5000)
        elif self._entity == 'pelicula':
            dialog = PeliculaFormDialog(self)
            if dialog.exec() != dialog.DialogCode.Accepted:
                return
            data = dialog.get_data()
            pelicula = Pelicula(
                id=None,
                titulo=data["titulo"],
                pais_origen=data["pais_origen"],
                director=data["director"],
                duracion_minutos=data["duracion_minutos"],
                genero=data["genero"],
                clasificacion=data["clasificacion"],
                sinopsis=data["sinopsis"],
            )
            if getattr(self._viewmodel, "add_pelicula", None):
                created = self._viewmodel.add_pelicula(pelicula)
            else:
                created = False
            if created:
                self._model.clear_selection()
                self.statusBar().showMessage("Película creada correctamente", 5000)
        elif self._entity == 'funcion':
            dialog = FuncionFormDialog(self)
            if dialog.exec() != dialog.DialogCode.Accepted:
                return
            data = dialog.get_data()
            funcion = Funcion(
                id=None,
                fecha=data["fecha"],
                hora=data["hora"],
                precio_entrada=data["precio_entrada"],
                estado_funcion=data["estado_funcion"],
                observaciones=data["observaciones"],
                id_sede=data["id_sede"],
            )
            if getattr(self._viewmodel, "add_funcion", None):
                created = self._viewmodel.add_funcion(funcion)
            else:
                created = False
            if created:
                self._model.clear_selection()
                self.statusBar().showMessage("Función creada correctamente", 5000)
        elif self._entity == 'asistencia':
            dialog = AsistenciaFormDialog(self)
            if dialog.exec() != dialog.DialogCode.Accepted:
                return
            data = dialog.get_data()
            asistencia = Asistencia(
                id_funcion=data["id_funcion"],
                id_asistente=data["id_asistente"],
                entradas=data["entradas"],
                fecha_compra=data["fecha_compra"],
                metodo_pago=data["metodo_pago"],
                comentarios=data["comentarios"],
            )
            if getattr(self._viewmodel, "add_asistencia", None):
                created = self._viewmodel.add_asistencia(asistencia)
            else:
                created = False
            if created:
                self._model.clear_selection()
                self.statusBar().showMessage("Asistencia creada correctamente", 5000)
        elif self._entity == 'jurado':
            dialog = JuradoFormDialog(self)
            if dialog.exec() != dialog.DialogCode.Accepted:
                return
            data = dialog.get_data()
            jurado = Jurado(
                nombre=data["nombre"],
                correo=data["correo"],
                especialidad=data["especialidad"],
                pais_origen=data["pais_origen"],
                experiencia_anos=data["experiencia_anos"],
                tipo_jurado=data["tipo_jurado"],
                biografia=data["biografia"],
            )
            if getattr(self._viewmodel, "add_jurado", None):
                created = self._viewmodel.add_jurado(jurado)
            else:
                created = False
            if created:
                self._model.clear_selection()
                self.statusBar().showMessage("Jurado creado correctamente", 5000)
        elif self._entity == 'participacion_jurado':
            dialog = ParticipacionJuradoFormDialog(self)
            if dialog.exec() != dialog.DialogCode.Accepted:
                return
            data = dialog.get_data()
            participacion = ParticipacionJurado(
                id_jurado=data["id_jurado"],
                id_funcion=data["id_funcion"],
                rol_participacion=data["rol_participacion"],
                comentarios=data["comentarios"],
            )
            if getattr(self._viewmodel, "add_participacion", None):
                created = self._viewmodel.add_participacion(participacion)
            else:
                created = False
            if created:
                self._model.clear_selection()
                self.statusBar().showMessage("Participación creada correctamente", 5000)
        elif self._entity == 'evaluacion':
            dialog = EvaluacionFormDialog(self)
            if dialog.exec() != dialog.DialogCode.Accepted:
                return
            data = dialog.get_data()
            evaluacion = Evaluacion(
                id_jurado=data["id_jurado"],
                id_pelicula=data["id_pelicula"],
                puntuacion=data["puntuacion"],
                comentario=data["comentario"],
                fecha=data.get("fecha"),
                categoria_evaluada=data.get("categoria_evaluada", "General"),
            )
            if getattr(self._viewmodel, "add_evaluacion", None):
                created = self._viewmodel.add_evaluacion(evaluacion)
            else:
                created = False
            if created:
                self._model.clear_selection()
                self.statusBar().showMessage("Evaluación creada correctamente", 5000)
        elif self._entity == 'premiacion':
            dialog = PremiacionFormDialog(self)
            if dialog.exec() != dialog.DialogCode.Accepted:
                return
            data = dialog.get_data()
            premiacion = Premiacion(
                id_premio=None,
                id_pelicula=data["id_pelicula"],
                categoria=data["categoria"],
                edicion=data["edicion"],
                posicion=data["posicion"],
                descripcion=data.get("descripcion", "Sin descripcion"),
                fecha_premiacion=data.get("fecha_premiacion"),
            )
            if getattr(self._viewmodel, "add_premiacion", None):
                created = self._viewmodel.add_premiacion(premiacion)
            else:
                created = False
            if created:
                self._model.clear_selection()
                self.statusBar().showMessage("Premiación creada correctamente", 5000)
        elif self._entity == 'proyeccion':
            dialog = ProyeccionFormDialog(self)
            if dialog.exec() != dialog.DialogCode.Accepted:
                return
            data = dialog.get_data()
            proy = Proyeccion(
                id_funcion=data["id_funcion"],
                id_pelicula=data["id_pelicula"],
                orden_proyeccion=data.get("orden_proyeccion", 1),
                comentarios=data.get("comentarios", "Sin comentarios"),
            )
            if getattr(self._viewmodel, "add_proyeccion", None):
                created = self._viewmodel.add_proyeccion(proy)
            else:
                created = False
            if created:
                self._model.clear_selection()
                self.statusBar().showMessage("Proyección creada correctamente", 5000)

    def _handle_delete_selected(self) -> None:
        if self._entity is None or self._viewmodel is None or self._model is None:
            QMessageBox.warning(self, "Información", "Seleccione una tabla primero.")
            return

        selected_ids = self._model.get_selected_ids()
        if not selected_ids:
            QMessageBox.information(self, "Eliminar", "Debe seleccionar al menos un elemento.")
            return

        confirm = QMessageBox.question(
            self,
            "Eliminar",
            f"¿Eliminar {len(selected_ids)} elemento(s) seleccionados?",
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        if self._entity == 'asistente':
            if getattr(self._viewmodel, "delete_asistentes", None):
                ok = self._viewmodel.delete_asistentes(selected_ids)
            else:
                ok = self._viewmodel.delete_clientes(selected_ids)
            if ok:
                self._model.clear_selection()
                self.statusBar().showMessage("Asistentes eliminados", 5000)
        elif self._entity == 'ciudad':
            if getattr(self._viewmodel, "delete_ciudades", None):
                ok = self._viewmodel.delete_ciudades(selected_ids)
            else:
                ok = False
            if ok:
                self._model.clear_selection()
                self.statusBar().showMessage("Ciudades eliminadas", 5000)
        elif self._entity == 'sede':
            if getattr(self._viewmodel, "delete_sedes", None):
                ok = self._viewmodel.delete_sedes(selected_ids)
            else:
                ok = False
            if ok:
                self._model.clear_selection()
                self.statusBar().showMessage("Sedes eliminadas", 5000)
        elif self._entity == 'pelicula':
            if getattr(self._viewmodel, "delete_peliculas", None):
                ok = self._viewmodel.delete_peliculas(selected_ids)
            else:
                ok = False
            if ok:
                self._model.clear_selection()
                self.statusBar().showMessage("Películas eliminadas", 5000)
        elif self._entity == 'funcion':
            if getattr(self._viewmodel, "delete_funciones", None):
                ok = self._viewmodel.delete_funciones(selected_ids)
            else:
                ok = False
            if ok:
                self._model.clear_selection()
                self.statusBar().showMessage("Funciones eliminadas", 5000)
        elif self._entity == 'asistencia':
            if getattr(self._viewmodel, "delete_asistencias", None):
                ok = self._viewmodel.delete_asistencias(selected_ids)
            else:
                ok = False
            if ok:
                self._model.clear_selection()
                self.statusBar().showMessage("Asistencias eliminadas", 5000)
        elif self._entity == 'jurado':
            if getattr(self._viewmodel, "delete_jurados", None):
                ok = self._viewmodel.delete_jurados(selected_ids)
            else:
                ok = False
            if ok:
                self._model.clear_selection()
                self.statusBar().showMessage("Jurados eliminados", 5000)
        elif self._entity == 'participacion_jurado':
            if getattr(self._viewmodel, "delete_participaciones", None):
                ok = self._viewmodel.delete_participaciones(selected_ids)
            else:
                ok = False
            if ok:
                self._model.clear_selection()
                self.statusBar().showMessage("Participaciones eliminadas", 5000)
        elif self._entity == 'evaluacion':
            if getattr(self._viewmodel, "delete_evaluaciones", None):
                ok = self._viewmodel.delete_evaluaciones(selected_ids)
            else:
                ok = False
            if ok:
                self._model.clear_selection()
                self.statusBar().showMessage("Evaluaciones eliminadas", 5000)
        elif self._entity == 'premiacion':
            if getattr(self._viewmodel, "delete_premiaciones", None):
                ok = self._viewmodel.delete_premiaciones(selected_ids)
            else:
                ok = False
            if ok:
                self._model.clear_selection()
                self.statusBar().showMessage("Premiaciones eliminadas", 5000)
        elif self._entity == 'proyeccion':
            if getattr(self._viewmodel, "delete_proyecciones", None):
                ok = self._viewmodel.delete_proyecciones(selected_ids)
            else:
                ok = False
            if ok:
                self._model.clear_selection()
                self.statusBar().showMessage("Proyecciones eliminadas", 5000)

    def _show_detail_for_row(self, row: int) -> None:
        if self._entity is None or self._model is None:
            return

        if self._entity == 'asistente':
            cliente = self._model.asistente_at(row)
            if not cliente:
                return
            dialog = ClienteDetailDialog(cliente, self)
            dialog.exec()
        elif self._entity == 'ciudad':
            ciudad = self._model.ciudad_at(row)
            if not ciudad:
                return
            dialog = CiudadDetailDialog(ciudad, self)
            dialog.exec()
        elif self._entity == 'sede':
            sede = self._model.sede_at(row)
            if not sede:
                return
            dialog = SedeDetailDialog(sede, self)
            dialog.exec()
        elif self._entity == 'pelicula':
            pelicula = self._model.pelicula_at(row)
            if not pelicula:
                return
            dialog = PeliculaDetailDialog(pelicula, self)
            dialog.exec()
        elif self._entity == 'funcion':
            funcion = self._model.funcion_at(row)
            if not funcion:
                return
            dialog = FuncionDetailDialog(funcion, self)
            dialog.exec()
        elif self._entity == 'asistencia':
            asistencia = self._model.asistencia_at(row)
            if not asistencia:
                return
            dialog = AsistenciaDetailDialog(asistencia, self)
            dialog.exec()
        elif self._entity == 'jurado':
            jurado = self._model.jurado_at(row)
            if not jurado:
                return
            dialog = JuradoDetailDialog(jurado, self)
            dialog.exec()
        elif self._entity == 'participacion_jurado':
            participacion = self._model.participacion_at(row)
            if not participacion:
                return
            dialog = ParticipacionJuradoDetailDialog(participacion, self)
            dialog.exec()
        elif self._entity == 'evaluacion':
            evaluacion = self._model.evaluacion_at(row)
            if not evaluacion:
                return
            dialog = EvaluacionDetailDialog(evaluacion, self)
            dialog.exec()
        elif self._entity == 'premiacion':
            premiacion = self._model.premiacion_at(row)
            if not premiacion:
                return
            dialog = PremiacionDetailDialog(premiacion, self)
            dialog.exec()
        elif self._entity == 'proyeccion':
            proy = self._model.proyeccion_at(row)
            if not proy:
                return
            dialog = ProyeccionDetailDialog(proy, self)
            dialog.exec()

    def _set_entity(self, entity: str) -> None:
        """Switch current managed entity to 'asistente', 'ciudad', 'sede', 'pelicula', 'funcion', 'asistencia', or 'jurado'."""
        self._entity = entity
        connection = OracleConnection.from_settings(self._settings_path)
        if entity == 'asistente':
            repository = AsistenteRepository(connection)
            self._viewmodel = AsistenteViewModel(repository)
            self._model = AsistenteTableModel()
            title_suffix = "Asistentes"
        elif entity == 'ciudad':
            repository = CiudadRepository(connection)
            self._viewmodel = CiudadViewModel(repository)
            self._model = CiudadTableModel()
            title_suffix = "Ciudades"
        elif entity == 'sede':
            repository = SedeRepository(connection)
            self._viewmodel = SedeViewModel(repository)
            self._model = SedeTableModel()
            title_suffix = "Sedes"
        elif entity == 'pelicula':
            repository = PeliculaRepository(connection)
            self._viewmodel = PeliculaViewModel(repository)
            self._model = PeliculaTableModel()
            title_suffix = "Películas"
        elif entity == 'funcion':
            repository = FuncionRepository(connection)
            self._viewmodel = FuncionViewModel(repository)
            self._model = FuncionTableModel()
            title_suffix = "Funciones"
        elif entity == 'asistencia':
            repository = AsistenciaRepository(connection)
            self._viewmodel = AsistenciaViewModel(repository)
            self._model = AsistenciaTableModel()
            title_suffix = "Asistencias"
        elif entity == 'jurado':
            repository = JuradoRepository(connection)
            self._viewmodel = JuradoViewModel(repository)
            self._model = JuradoTableModel()
            title_suffix = "Jurados"
        elif entity == 'participacion_jurado':
            repository = ParticipacionJuradoRepository(connection)
            self._viewmodel = ParticipacionJuradoViewModel(repository)
            self._model = ParticipacionJuradoTableModel()
            title_suffix = "Participaciones de Jurado"
        elif entity == 'evaluacion':
            repository = EvaluacionRepository(connection)
            self._viewmodel = EvaluacionViewModel(repository)
            self._model = EvaluacionTableModel()
            title_suffix = "Evaluaciones"
        elif entity == 'premiacion':
            repository = PremiacionRepository(connection)
            self._viewmodel = PremiacionViewModel(repository)
            self._model = PremiacionTableModel()
            title_suffix = "Premiaciones"
        elif entity == 'proyeccion':
            repository = ProyeccionRepository(connection)
            self._viewmodel = ProyeccionViewModel(repository)
            self._model = ProyeccionTableModel()
            title_suffix = "Proyecciones"
        else:
            raise ValueError(f"Unknown entity: {entity}")

        # Update window title
        self.setWindowTitle(f"Gestor de Festival de Cine - {title_suffix}")

        # Switch to table view
        self._show_table_view()

        # attach model and delegate
        self._table.setModel(self._model)
        try:
            self._table.setItemDelegateForColumn(self._model.ACTION_COLUMN, self._detail_delegate)
        except Exception:
            pass

        # connect signals and load data
        self._connect_signals()
        # load via viewmodel
        if entity == 'asistente':
            try:
                self._viewmodel.load_asistentes()
            except AttributeError:
                try:
                    self._viewmodel.load_clientes()
                except Exception:
                    pass
        elif entity == 'ciudad':
            try:
                self._viewmodel.load_ciudades()
            except Exception:
                pass
        elif entity == 'sede':
            try:
                self._viewmodel.load_sedes()
            except Exception:
                pass
        elif entity == 'pelicula':
            try:
                self._viewmodel.load_peliculas()
            except Exception:
                pass
        elif entity == 'funcion':
            try:
                self._viewmodel.load_funciones()
            except Exception:
                pass
        elif entity == 'asistencia':
            try:
                self._viewmodel.load_asistencias()
            except Exception:
                pass
        elif entity == 'jurado':
            try:
                self._viewmodel.load_jurados()
            except Exception:
                pass
        elif entity == 'participacion_jurado':
            try:
                self._viewmodel.load_participaciones()
            except Exception:
                pass
        elif entity == 'evaluacion':
            try:
                self._viewmodel.load_evaluaciones()
            except Exception:
                pass
        elif entity == 'premiacion':
            try:
                self._viewmodel.load_premiaciones()
            except Exception:
                pass
        elif entity == 'proyeccion':
            try:
                self._viewmodel.load_proyecciones()
            except Exception:
                pass

        # Show primary actions now that a table is selected
        if hasattr(self, "_refresh_action"):
            self._refresh_action.setVisible(True)
        if hasattr(self, "_new_action"):
            self._new_action.setVisible(True)
        if hasattr(self, "_delete_action"):
            self._delete_action.setVisible(True)
        if hasattr(self, "_back_action"):
            try:
                self._back_action.setVisible(True)
            except Exception:
                pass

    def _back_to_menu(self) -> None:
        """Return to the initial table selection menu."""
        # Clear current entity and viewmodel/model references
        self._entity = None
        self._viewmodel = None
        self._model = None
        # Reset title
        self.setWindowTitle("Gestor de Festival de Cine")
        # Show selection menu and hide toolbar actions
        self._show_table_selection_menu()
