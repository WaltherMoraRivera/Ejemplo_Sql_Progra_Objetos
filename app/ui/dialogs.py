"""Dialog windows adapted to `asistente` entity."""
from __future__ import annotations

import re
from typing import Dict, Optional

from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QSpinBox,
    QVBoxLayout,
)

from app.domain.models.asistente import Asistente
from app.domain.models.ciudad import Ciudad
from app.domain.models.sede import Sede
from app.domain.models.pelicula import Pelicula
from app.domain.models.funcion import Funcion
from app.domain.models.asistencia import Asistencia
from app.domain.models.jurado import Jurado
from app.domain.models.participacion_jurado import ParticipacionJurado
from app.domain.models.premiacion import Premiacion

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ClienteFormDialog(QDialog):
    """Dialog to capture a new asistente entry (keeps class name for compatibility)."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Nuevo Asistente")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.nombre_input = QLineEdit()
        form_layout.addRow("Nombre", self.nombre_input)

        self.email_input = QLineEdit()
        form_layout.addRow("Correo", self.email_input)

        self.telefono_input = QLineEdit()
        self.telefono_input.setPlaceholderText("Teléfono")
        form_layout.addRow("Teléfono", self.telefono_input)

        self.edad_input = QSpinBox()
        self.edad_input.setRange(0, 120)
        form_layout.addRow("Edad", self.edad_input)

        self.ciudad_input = QLineEdit()
        form_layout.addRow("Ciudad residencia", self.ciudad_input)

        self.tipo_input = QComboBox()
        self.tipo_input.addItems(["General", "Estudiante", "Profesional", "Prensa"])
        form_layout.addRow("Tipo", self.tipo_input)

        layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self._on_accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def _on_accept(self) -> None:
        error = self._validate_inputs()
        if error:
            QMessageBox.warning(self, "Validación", error)
            return
        self.accept()

    def _validate_inputs(self) -> Optional[str]:
        nombre = self.nombre_input.text().strip()
        correo = self.email_input.text().strip()
        telefono = self.telefono_input.text().strip()
        if not nombre:
            return "El nombre es obligatorio."
        if not EMAIL_REGEX.match(correo):
            return "El correo no tiene un formato válido."
        if not telefono:
            return "El teléfono es obligatorio."
        return None

    def get_data(self) -> Dict[str, object]:
        """Return the sanitized values for an asistente."""

        return {
            "nombre": self.nombre_input.text().strip(),
            "correo": self.email_input.text().strip(),
            "telefono": self.telefono_input.text().strip(),
            "edad": int(self.edad_input.value()),
            "ciudad_residencia": self.ciudad_input.text().strip() or "No especificada",
            "tipo_asistente": self.tipo_input.currentText(),
        }


class ClienteDetailDialog(QDialog):
    """Displays all persisted information for an asistente.

    Keeps the dialog class name for backwards compatibility with existing imports,
    but accepts an `Asistente` instance.
    """

    def __init__(self, asistente: Asistente, parent=None) -> None:
        super().__init__(parent)
        self._asistente = asistente
        self.setWindowTitle("Detalle de Asistente")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        def add_row(label: str, value: str) -> None:
            form_layout.addRow(label, QLabel(value))

        add_row("ID", str(self._asistente.id or ""))
        add_row("Nombre", self._asistente.nombre)
        add_row("Correo", self._asistente.correo)
        add_row("Teléfono", self._asistente.telefono)
        add_row("Edad", str(self._asistente.edad or ""))
        add_row("Ciudad residencia", self._asistente.ciudad_residencia)
        add_row("Tipo", self._asistente.tipo_asistente)

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        button_box.accepted.connect(self.accept)
        button_box.button(QDialogButtonBox.StandardButton.Close).clicked.connect(self.accept)
        layout.addWidget(button_box)


class EvaluacionFormDialog(QDialog):
    """Dialog to capture a new evaluacion entry."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Nueva Evaluación")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.id_jurado_input = QSpinBox()
        self.id_jurado_input.setRange(1, 999999)
        form_layout.addRow("ID Jurado", self.id_jurado_input)

        self.id_pelicula_input = QSpinBox()
        self.id_pelicula_input.setRange(1, 999999)
        form_layout.addRow("ID Película", self.id_pelicula_input)

        self.puntuacion_input = QSpinBox()
        self.puntuacion_input.setRange(1, 10)
        form_layout.addRow("Puntuación", self.puntuacion_input)

        self.comentario_input = QLineEdit()
        self.comentario_input.setPlaceholderText("Comentario")
        form_layout.addRow("Comentario", self.comentario_input)

        self.fecha_input = QLineEdit()
        self.fecha_input.setPlaceholderText("YYYY-MM-DD (opcional)")
        form_layout.addRow("Fecha Evaluación", self.fecha_input)

        self.categoria_input = QComboBox()
        self.categoria_input.addItems(["General", "Direccion", "Actuacion", "Guion", "Fotografia", "Sonido"])
        form_layout.addRow("Categoría evaluada", self.categoria_input)

        layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self._on_accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def _on_accept(self) -> None:
        error = self._validate_inputs()
        if error:
            QMessageBox.warning(self, "Validación", error)
            return
        self.accept()

    def _validate_inputs(self) -> Optional[str]:
        if self.id_jurado_input.value() < 1:
            return "ID Jurado debe ser mayor a 0."
        if self.id_pelicula_input.value() < 1:
            return "ID Película debe ser mayor a 0."
        fecha = self.fecha_input.text().strip()
        if fecha and not self._is_valid_date(fecha):
            return "Formato de fecha inválido (use YYYY-MM-DD)."
        return None

    def get_data(self) -> Dict[str, object]:
        from datetime import datetime, date
        fecha_str = self.fecha_input.text().strip()
        fecha_val = datetime.strptime(fecha_str, "%Y-%m-%d").date() if fecha_str else None
        return {
            "id_jurado": int(self.id_jurado_input.value()),
            "id_pelicula": int(self.id_pelicula_input.value()),
            "puntuacion": int(self.puntuacion_input.value()),
            "comentario": self.comentario_input.text().strip() or "",
            "fecha": fecha_val,
            "categoria_evaluada": self.categoria_input.currentText(),
        }


class EvaluacionDetailDialog(QDialog):
    """Displays persisted information for an evaluacion."""

    def __init__(self, evaluacion: 'Evaluacion', parent=None) -> None:
        super().__init__(parent)
        self._evaluacion = evaluacion
        self.setWindowTitle(f"Detalle de Evaluación ({evaluacion.id_jurado}, {evaluacion.id_pelicula})")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        def add_row(label: str, value: str) -> None:
            form_layout.addRow(label, QLabel(value))

        add_row("ID Jurado", str(self._evaluacion.id_jurado or ""))
        add_row("ID Película", str(self._evaluacion.id_pelicula or ""))
        add_row("Puntuación", str(self._evaluacion.puntuacion or ""))
        add_row("Comentario", self._evaluacion.comentario or "")
        add_row("Fecha Evaluación", str(self._evaluacion.fecha or ""))
        add_row("Categoría evaluada", getattr(self._evaluacion, 'categoria_evaluada', ""))

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        button_box.accepted.connect(self.accept)
        button_box.button(QDialogButtonBox.StandardButton.Close).clicked.connect(self.accept)
        layout.addWidget(button_box)


class CiudadFormDialog(QDialog):
    """Dialog to capture a new ciudad entry."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Nueva Ciudad")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.nombre_input = QLineEdit()
        form_layout.addRow("Nombre", self.nombre_input)

        self.region_input = QLineEdit()
        form_layout.addRow("Región", self.region_input)

        self.pais_input = QLineEdit()
        form_layout.addRow("País", self.pais_input)

        self.observaciones_input = QLineEdit()
        form_layout.addRow("Observaciones", self.observaciones_input)

        layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self._on_accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def _on_accept(self) -> None:
        if not self.nombre_input.text().strip():
            QMessageBox.warning(self, "Validación", "El nombre es obligatorio.")
            return
        if not self.pais_input.text().strip():
            QMessageBox.warning(self, "Validación", "El país es obligatorio.")
            return
        self.accept()

    def get_data(self) -> Dict[str, object]:
        return {
            "nombre": self.nombre_input.text().strip(),
            "region": self.region_input.text().strip(),
            "pais": self.pais_input.text().strip(),
            "observaciones": self.observaciones_input.text().strip() or "",
        }


class CiudadDetailDialog(QDialog):
    """Displays persisted information for a ciudad."""

    def __init__(self, ciudad: Ciudad, parent=None) -> None:
        super().__init__(parent)
        self._ciudad = ciudad
        self.setWindowTitle("Detalle de Ciudad")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        def add_row(label: str, value: str) -> None:
            form_layout.addRow(label, QLabel(value))

        add_row("ID", str(self._ciudad.id or ""))
        add_row("Nombre", self._ciudad.nombre)
        add_row("Región", self._ciudad.region)
        add_row("País", self._ciudad.pais)
        add_row("Observaciones", self._ciudad.observaciones or "")

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        button_box.accepted.connect(self.accept)
        button_box.button(QDialogButtonBox.StandardButton.Close).clicked.connect(self.accept)
        layout.addWidget(button_box)


class SedeFormDialog(QDialog):
    """Dialog to capture a new sede entry."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Nueva Sede")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.nombre_input = QLineEdit()
        form_layout.addRow("Nombre", self.nombre_input)

        self.direccion_input = QLineEdit()
        form_layout.addRow("Dirección", self.direccion_input)

        self.capacidad_input = QSpinBox()
        self.capacidad_input.setRange(1, 10000)
        form_layout.addRow("Capacidad máxima", self.capacidad_input)

        self.tipo_input = QComboBox()
        self.tipo_input.addItems(["Cine convencional", "Anfiteatro", "Sala de exhibición", "Otra"])
        form_layout.addRow("Tipo de sede", self.tipo_input)

        self.ciudad_id_input = QSpinBox()
        self.ciudad_id_input.setRange(1, 10000)
        form_layout.addRow("Ciudad ID", self.ciudad_id_input)

        self.estado_input = QComboBox()
        self.estado_input.addItems(["Activa", "Inactiva", "Mantenimiento"])
        form_layout.addRow("Estado", self.estado_input)

        layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self._on_accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def _on_accept(self) -> None:
        if not self.nombre_input.text().strip():
            QMessageBox.warning(self, "Validación", "El nombre es obligatorio.")
            return
        if not self.direccion_input.text().strip():
            QMessageBox.warning(self, "Validación", "La dirección es obligatoria.")
            return
        self.accept()

    def get_data(self) -> Dict[str, object]:
        return {
            "nombre": self.nombre_input.text().strip(),
            "direccion": self.direccion_input.text().strip(),
            "capacidad_maxima": int(self.capacidad_input.value()),
            "tipo_sede": self.tipo_input.currentText(),
            "id_ciudad": int(self.ciudad_id_input.value()),
            "estado": self.estado_input.currentText(),
        }


class SedeDetailDialog(QDialog):
    """Displays persisted information for a sede."""

    def __init__(self, sede: Sede, parent=None) -> None:
        super().__init__(parent)
        self._sede = sede
        self.setWindowTitle("Detalle de Sede")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        def add_row(label: str, value: str) -> None:
            form_layout.addRow(label, QLabel(value))

        add_row("ID", str(self._sede.id or ""))
        add_row("Nombre", self._sede.nombre)
        add_row("Dirección", self._sede.direccion)
        add_row("Capacidad máxima", str(self._sede.capacidad_maxima or ""))
        add_row("Tipo de sede", self._sede.tipo_sede)
        add_row("Ciudad ID", str(self._sede.id_ciudad or ""))
        add_row("Estado", self._sede.estado)

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        button_box.accepted.connect(self.accept)
        button_box.button(QDialogButtonBox.StandardButton.Close).clicked.connect(self.accept)
        layout.addWidget(button_box)


class PeliculaFormDialog(QDialog):
    """Dialog to capture a new pelicula entry."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Nueva Película")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.titulo_input = QLineEdit()
        form_layout.addRow("Título", self.titulo_input)

        self.pais_input = QLineEdit()
        form_layout.addRow("País de origen", self.pais_input)

        self.director_input = QLineEdit()
        form_layout.addRow("Director", self.director_input)

        self.duracion_input = QSpinBox()
        self.duracion_input.setRange(1, 600)
        form_layout.addRow("Duración (minutos)", self.duracion_input)

        self.genero_input = QComboBox()
        self.genero_input.addItems(["Drama", "Acción", "Comedia", "Terror", "Ciencia Ficción", "Documental", "Otro"])
        form_layout.addRow("Género", self.genero_input)

        self.clasificacion_input = QComboBox()
        self.clasificacion_input.addItems(["TE", "+7", "+14", "+18"])
        form_layout.addRow("Clasificación", self.clasificacion_input)

        self.sinopsis_input = QLineEdit()
        self.sinopsis_input.setPlaceholderText("Resumen de la película")
        form_layout.addRow("Sinopsis", self.sinopsis_input)

        layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self._on_accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def _on_accept(self) -> None:
        if not self.titulo_input.text().strip():
            QMessageBox.warning(self, "Validación", "El título es obligatorio.")
            return
        if not self.director_input.text().strip():
            QMessageBox.warning(self, "Validación", "El director es obligatorio.")
            return
        if not self.pais_input.text().strip():
            QMessageBox.warning(self, "Validación", "El país de origen es obligatorio.")
            return
        self.accept()

    def get_data(self) -> Dict[str, object]:
        return {
            "titulo": self.titulo_input.text().strip(),
            "pais_origen": self.pais_input.text().strip(),
            "director": self.director_input.text().strip(),
            "duracion_minutos": int(self.duracion_input.value()),
            "genero": self.genero_input.currentText(),
            "clasificacion": self.clasificacion_input.currentText(),
            "sinopsis": self.sinopsis_input.text().strip() or "Sin sinopsis disponible",
        }


class PeliculaDetailDialog(QDialog):
    """Displays persisted information for a pelicula."""

    def __init__(self, pelicula: Pelicula, parent=None) -> None:
        super().__init__(parent)
        self._pelicula = pelicula
        self.setWindowTitle("Detalle de Película")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        def add_row(label: str, value: str) -> None:
            form_layout.addRow(label, QLabel(value))

        add_row("ID", str(self._pelicula.id or ""))
        add_row("Título", self._pelicula.titulo)
        add_row("País de origen", self._pelicula.pais_origen)
        add_row("Director", self._pelicula.director)
        add_row("Duración (minutos)", str(self._pelicula.duracion_minutos or ""))
        add_row("Género", self._pelicula.genero)
        add_row("Clasificación", self._pelicula.clasificacion)
        add_row("Sinopsis", self._pelicula.sinopsis)

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        button_box.accepted.connect(self.accept)
        button_box.button(QDialogButtonBox.StandardButton.Close).clicked.connect(self.accept)
        layout.addWidget(button_box)


class FuncionFormDialog(QDialog):
    """Dialog to capture a new función entry."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Nueva Función")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.fecha_input = QLineEdit()
        self.fecha_input.setPlaceholderText("YYYY-MM-DD")
        form_layout.addRow("Fecha", self.fecha_input)

        self.hora_input = QLineEdit()
        self.hora_input.setPlaceholderText("HH:MM")
        form_layout.addRow("Hora", self.hora_input)

        self.precio_input = QLineEdit()
        self.precio_input.setPlaceholderText("5000")
        form_layout.addRow("Precio Entrada", self.precio_input)

        self.estado_input = QComboBox()
        self.estado_input.addItems(["Programada", "En curso", "Finalizada", "Cancelada"])
        form_layout.addRow("Estado", self.estado_input)

        self.observaciones_input = QLineEdit()
        self.observaciones_input.setPlaceholderText("Sin observaciones")
        form_layout.addRow("Observaciones", self.observaciones_input)

        self.id_sede_input = QLineEdit()
        self.id_sede_input.setPlaceholderText("ID de la Sede")
        form_layout.addRow("ID Sede", self.id_sede_input)

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_data(self) -> Dict[str, any]:
        """Return form data as a dictionary."""
        return {
            "fecha": self.fecha_input.text().strip(),
            "hora": self.hora_input.text().strip(),
            "precio_entrada": float(self.precio_input.text() or "5000"),
            "estado_funcion": self.estado_input.currentText(),
            "observaciones": self.observaciones_input.text().strip() or "Sin observaciones",
            "id_sede": int(self.id_sede_input.text() or "0"),
        }


class FuncionDetailDialog(QDialog):
    """Dialog to display función details (read-only)."""

    def __init__(self, funcion: Funcion, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Detalle de Función {funcion.id}")
        self._funcion = funcion
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        def add_row(label: str, value: str) -> None:
            form_layout.addRow(label, QLabel(value))

        add_row("ID", str(self._funcion.id or ""))
        add_row("Fecha", self._funcion.fecha or "")
        add_row("Hora", self._funcion.hora or "")
        add_row("Precio Entrada", f"${self._funcion.precio_entrada:,.0f}" if self._funcion.precio_entrada else "$0")
        add_row("Estado", self._funcion.estado_funcion or "")
        add_row("Observaciones", self._funcion.observaciones or "")
        add_row("ID Sede", str(self._funcion.id_sede or ""))

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        button_box.accepted.connect(self.accept)
        button_box.button(QDialogButtonBox.StandardButton.Close).clicked.connect(self.accept)
        layout.addWidget(button_box)


class AsistenciaFormDialog(QDialog):
    """Dialog to capture a new asistencia entry."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Nueva Asistencia")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.id_funcion_input = QSpinBox()
        self.id_funcion_input.setRange(1, 999999)
        form_layout.addRow("ID Función", self.id_funcion_input)

        self.id_asistente_input = QSpinBox()
        self.id_asistente_input.setRange(1, 999999)
        form_layout.addRow("ID Asistente", self.id_asistente_input)

        self.entradas_input = QSpinBox()
        self.entradas_input.setRange(1, 100)
        self.entradas_input.setValue(1)
        form_layout.addRow("Entradas", self.entradas_input)

        self.fecha_compra_input = QLineEdit()
        self.fecha_compra_input.setPlaceholderText("YYYY-MM-DD")
        form_layout.addRow("Fecha Compra", self.fecha_compra_input)

        self.metodo_pago_input = QComboBox()
        self.metodo_pago_input.addItems(["Efectivo", "Tarjeta", "Transferencia"])
        form_layout.addRow("Método Pago", self.metodo_pago_input)

        self.comentarios_input = QLineEdit()
        self.comentarios_input.setPlaceholderText("Comentarios")
        form_layout.addRow("Comentarios", self.comentarios_input)

        layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self._on_accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def _on_accept(self) -> None:
        error = self._validate_inputs()
        if error:
            QMessageBox.warning(self, "Validación", error)
            return
        self.accept()

    def _validate_inputs(self) -> Optional[str]:
        if self.id_funcion_input.value() < 1:
            return "ID Función debe ser mayor a 0."
        if self.id_asistente_input.value() < 1:
            return "ID Asistente debe ser mayor a 0."
        if self.entradas_input.value() < 1:
            return "Entradas debe ser mayor a 0."
        fecha = self.fecha_compra_input.text().strip()
        if fecha and not self._is_valid_date(fecha):
            return "Formato de fecha inválido (use YYYY-MM-DD)."
        return None

    @staticmethod
    def _is_valid_date(date_str: str) -> bool:
        try:
            from datetime import datetime
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def get_data(self) -> Dict[str, object]:
        """Return the sanitized values for an asistencia."""
        from datetime import datetime, date
        fecha_str = self.fecha_compra_input.text().strip()
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date() if fecha_str else date.today()

        return {
            "id_funcion": int(self.id_funcion_input.value()),
            "id_asistente": int(self.id_asistente_input.value()),
            "entradas": int(self.entradas_input.value()),
            "fecha_compra": fecha,
            "metodo_pago": self.metodo_pago_input.currentText(),
            "comentarios": self.comentarios_input.text().strip() or "Sin comentarios",
        }


class AsistenciaDetailDialog(QDialog):
    """Dialog to display asistencia details (read-only)."""

    def __init__(self, asistencia: Asistencia, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Detalle de Asistencia ({asistencia.id_funcion}, {asistencia.id_asistente})")
        self._asistencia = asistencia
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        def add_row(label: str, value: str) -> None:
            form_layout.addRow(label, QLabel(value))

        add_row("ID Función", str(self._asistencia.id_funcion or ""))
        add_row("ID Asistente", str(self._asistencia.id_asistente or ""))
        add_row("Entradas", str(self._asistencia.entradas or ""))
        add_row("Fecha Compra", str(self._asistencia.fecha_compra or ""))
        add_row("Método Pago", self._asistencia.metodo_pago or "")
        add_row("Comentarios", self._asistencia.comentarios or "")

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        button_box.accepted.connect(self.accept)
        button_box.button(QDialogButtonBox.StandardButton.Close).clicked.connect(self.accept)
        layout.addWidget(button_box)


class JuradoFormDialog(QDialog):
    """Dialog to capture a new jurado entry."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Nuevo Jurado")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.nombre_input = QLineEdit()
        form_layout.addRow("Nombre", self.nombre_input)

        self.correo_input = QLineEdit()
        self.correo_input.setPlaceholderText("correo@ejemplo.com")
        form_layout.addRow("Correo", self.correo_input)

        self.especialidad_input = QLineEdit()
        form_layout.addRow("Especialidad", self.especialidad_input)

        self.pais_input = QLineEdit()
        self.pais_input.setText("Chile")
        form_layout.addRow("País Origen", self.pais_input)

        self.experiencia_input = QSpinBox()
        self.experiencia_input.setRange(0, 200)
        form_layout.addRow("Experiencia (años)", self.experiencia_input)

        self.tipo_input = QComboBox()
        self.tipo_input.addItems(["Invitado", "Permanente", "Honorario"])
        form_layout.addRow("Tipo de Jurado", self.tipo_input)

        self.biografia_input = QLineEdit()
        self.biografia_input.setPlaceholderText("Biografía del jurado")
        form_layout.addRow("Biografía", self.biografia_input)

        layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self._on_accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def _on_accept(self) -> None:
        error = self._validate_inputs()
        if error:
            QMessageBox.warning(self, "Validación", error)
            return
        self.accept()

    def _validate_inputs(self) -> Optional[str]:
        nombre = self.nombre_input.text().strip()
        correo = self.correo_input.text().strip()
        especialidad = self.especialidad_input.text().strip()
        
        if not nombre:
            return "El nombre es obligatorio."
        if not EMAIL_REGEX.match(correo):
            return "El correo no tiene un formato válido."
        if not especialidad:
            return "La especialidad es obligatoria."
        return None

    def get_data(self) -> Dict[str, object]:
        """Return the sanitized values for a jurado."""
        return {
            "nombre": self.nombre_input.text().strip(),
            "correo": self.correo_input.text().strip(),
            "especialidad": self.especialidad_input.text().strip(),
            "pais_origen": self.pais_input.text().strip() or "Chile",
            "experiencia_anos": int(self.experiencia_input.value()),
            "tipo_jurado": self.tipo_input.currentText(),
            "biografia": self.biografia_input.text().strip() or "Sin biografia disponible",
        }


class JuradoDetailDialog(QDialog):
    """Dialog to display jurado details (read-only)."""

    def __init__(self, jurado: Jurado, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Detalle de Jurado {jurado.id}")
        self._jurado = jurado
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        def add_row(label: str, value: str) -> None:
            form_layout.addRow(label, QLabel(value))

        add_row("ID", str(self._jurado.id or ""))
        add_row("Nombre", self._jurado.nombre or "")
        add_row("Correo", self._jurado.correo or "")
        add_row("Especialidad", self._jurado.especialidad or "")
        add_row("País Origen", self._jurado.pais_origen or "")
        add_row("Experiencia (años)", str(self._jurado.experiencia_anos or ""))
        add_row("Tipo de Jurado", self._jurado.tipo_jurado or "")
        add_row("Biografía", self._jurado.biografia or "")

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        button_box.accepted.connect(self.accept)
        button_box.button(QDialogButtonBox.StandardButton.Close).clicked.connect(self.accept)
        layout.addWidget(button_box)


class ParticipacionJuradoFormDialog(QDialog):
    """Dialog to capture a new participacion_jurado entry."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Nueva Participación de Jurado")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.id_jurado_input = QSpinBox()
        self.id_jurado_input.setRange(1, 999999)
        form_layout.addRow("ID Jurado", self.id_jurado_input)

        self.id_funcion_input = QSpinBox()
        self.id_funcion_input.setRange(1, 999999)
        form_layout.addRow("ID Función", self.id_funcion_input)

        self.rol_input = QComboBox()
        self.rol_input.addItems(["Evaluador", "Moderador", "Invitado especial"])
        form_layout.addRow("Rol de Participación", self.rol_input)

        self.comentarios_input = QLineEdit()
        self.comentarios_input.setPlaceholderText("Comentarios")
        form_layout.addRow("Comentarios", self.comentarios_input)

        layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self._on_accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def _on_accept(self) -> None:
        error = self._validate_inputs()
        if error:
            QMessageBox.warning(self, "Validación", error)
            return
        self.accept()

    def _validate_inputs(self) -> Optional[str]:
        if self.id_jurado_input.value() < 1:
            return "ID Jurado debe ser mayor a 0."
        if self.id_funcion_input.value() < 1:
            return "ID Función debe ser mayor a 0."
        return None

    def get_data(self) -> Dict[str, object]:
        """Return the sanitized values for a participacion_jurado."""
        return {
            "id_jurado": int(self.id_jurado_input.value()),
            "id_funcion": int(self.id_funcion_input.value()),
            "rol_participacion": self.rol_input.currentText(),
            "comentarios": self.comentarios_input.text().strip() or "Sin comentarios",
        }


class ParticipacionJuradoDetailDialog(QDialog):
    """Dialog to display participacion_jurado details (read-only)."""

    def __init__(self, participacion: ParticipacionJurado, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(
            f"Detalle de Participación ({participacion.id_jurado}, {participacion.id_funcion})"
        )
        self._participacion = participacion
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        def add_row(label: str, value: str) -> None:
            form_layout.addRow(label, QLabel(value))

        add_row("ID Jurado", str(self._participacion.id_jurado or ""))
        add_row("ID Función", str(self._participacion.id_funcion or ""))
        add_row("Rol de Participación", self._participacion.rol_participacion or "")
        add_row("Comentarios", self._participacion.comentarios or "")

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        button_box.accepted.connect(self.accept)
        button_box.button(QDialogButtonBox.StandardButton.Close).clicked.connect(self.accept)
        layout.addWidget(button_box)


class PremiacionFormDialog(QDialog):
    """Dialog to capture a new premiacion entry."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Nueva Premiación")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.id_pelicula_input = QSpinBox()
        self.id_pelicula_input.setRange(1, 999999)
        form_layout.addRow("ID Película", self.id_pelicula_input)

        self.categoria_input = QLineEdit()
        form_layout.addRow("Categoría", self.categoria_input)

        self.edicion_input = QSpinBox()
        self.edicion_input.setRange(1, 99999)
        form_layout.addRow("Edición", self.edicion_input)

        self.posicion_input = QSpinBox()
        self.posicion_input.setRange(1, 3)
        form_layout.addRow("Posición", self.posicion_input)

        self.descripcion_input = QLineEdit()
        form_layout.addRow("Descripción", self.descripcion_input)

        self.fecha_input = QLineEdit()
        self.fecha_input.setPlaceholderText("YYYY-MM-DD (opcional)")
        form_layout.addRow("Fecha Premiación", self.fecha_input)

        layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self._on_accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def _on_accept(self) -> None:
        error = self._validate_inputs()
        if error:
            QMessageBox.warning(self, "Validación", error)
            return
        self.accept()

    def _validate_inputs(self) -> Optional[str]:
        if self.id_pelicula_input.value() < 1:
            return "ID Película debe ser mayor a 0."
        if not self.categoria_input.text().strip():
            return "La categoría es obligatoria."
        if self.edicion_input.value() < 1:
            return "Edición debe ser mayor a 0."
        fecha = self.fecha_input.text().strip()
        if fecha and not self._is_valid_date(fecha):
            return "Formato de fecha inválido (use YYYY-MM-DD)."
        return None

    @staticmethod
    def _is_valid_date(date_str: str) -> bool:
        try:
            from datetime import datetime

            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def get_data(self) -> Dict[str, object]:
        from datetime import datetime, date

        fecha_str = self.fecha_input.text().strip()
        fecha_val = datetime.strptime(fecha_str, "%Y-%m-%d").date() if fecha_str else None
        return {
            "id_pelicula": int(self.id_pelicula_input.value()),
            "categoria": self.categoria_input.text().strip(),
            "edicion": int(self.edicion_input.value()),
            "posicion": int(self.posicion_input.value()),
            "descripcion": self.descripcion_input.text().strip() or "Sin descripcion",
            "fecha_premiacion": fecha_val,
        }


class PremiacionDetailDialog(QDialog):
    """Displays persisted information for a premiacion."""

    def __init__(self, premiacion: 'Premiacion', parent=None) -> None:
        super().__init__(parent)
        self._premiacion = premiacion
        self.setWindowTitle(f"Detalle de Premiación {premiacion.id_premio}")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        def add_row(label: str, value: str) -> None:
            form_layout.addRow(label, QLabel(value))

        add_row("ID Premio", str(self._premiacion.id_premio or ""))
        add_row("ID Película", str(self._premiacion.id_pelicula or ""))
        add_row("Categoría", self._premiacion.categoria or "")
        add_row("Edición", str(self._premiacion.edicion or ""))
        add_row("Posición", str(self._premiacion.posicion or ""))
        add_row("Descripción", self._premiacion.descripcion or "")
        add_row("Fecha Premiación", str(self._premiacion.fecha_premiacion or ""))

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        button_box.accepted.connect(self.accept)
        button_box.button(QDialogButtonBox.StandardButton.Close).clicked.connect(self.accept)
        layout.addWidget(button_box)

