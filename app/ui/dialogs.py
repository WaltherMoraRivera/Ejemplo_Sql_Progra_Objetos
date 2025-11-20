"""Dialog windows for cliente workflows."""
from __future__ import annotations

import re
from datetime import date
from typing import Dict, Optional

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QVBoxLayout,
)

from app.domain.models.cliente import Cliente

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ClienteFormDialog(QDialog):
    """Dialog to capture a new cliente entry."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Nuevo Cliente")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.rut_input = QLineEdit()
        self.rut_input.setPlaceholderText("Ej. 12345678")
        self.rut_input.setMaxLength(12)
        form_layout.addRow("RUT", self.rut_input)

        self.dv_input = QLineEdit()
        self.dv_input.setPlaceholderText("K")
        self.dv_input.setMaxLength(1)
        form_layout.addRow("DV", self.dv_input)

        self.nombre_input = QLineEdit()
        form_layout.addRow("Nombre", self.nombre_input)

        self.apellido_input = QLineEdit()
        form_layout.addRow("Apellido", self.apellido_input)

        self.fecha_input = QDateEdit()
        self.fecha_input.setCalendarPopup(True)
        self.fecha_input.setDisplayFormat("dd/MM/yyyy")
        self.fecha_input.setDate(QDate.currentDate())
        form_layout.addRow("Fecha nacimiento", self.fecha_input)

        self.email_input = QLineEdit()
        form_layout.addRow("Email", self.email_input)

        self.telefono_input = QLineEdit()
        self.telefono_input.setPlaceholderText("+56912345678")
        form_layout.addRow("Teléfono", self.telefono_input)

        self.direccion_input = QPlainTextEdit()
        self.direccion_input.setFixedHeight(60)
        form_layout.addRow("Dirección", self.direccion_input)

        self.estado_input = QComboBox()
        self.estado_input.addItems(["A", "I", "M"])
        form_layout.addRow("Estado", self.estado_input)

        self.credito_input = QDoubleSpinBox()
        self.credito_input.setRange(0, 100_000_000)
        self.credito_input.setSuffix(" CLP")
        self.credito_input.setDecimals(2)
        self.credito_input.setSingleStep(10000)
        form_layout.addRow("Límite crédito", self.credito_input)

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
        rut = self.rut_input.text().strip()
        dv = self.dv_input.text().strip().upper()
        nombre = self.nombre_input.text().strip()
        apellido = self.apellido_input.text().strip()
        email = self.email_input.text().strip()
        telefono = self.telefono_input.text().strip()

        if not rut.isdigit():
            return "El RUT debe contener sólo números."
        if len(dv) != 1:
            return "El dígito verificador debe tener un carácter."
        if not nombre:
            return "El nombre es obligatorio."
        if not apellido:
            return "El apellido es obligatorio."
        if not EMAIL_REGEX.match(email):
            return "El email no tiene un formato válido."
        if not telefono:
            return "El teléfono es obligatorio."
        return None

    def get_data(self) -> Dict[str, object]:
        """Return the sanitized values."""

        return {
            "rut": self.rut_input.text().strip(),
            "dv": self.dv_input.text().strip().upper(),
            "nombre": self.nombre_input.text().strip(),
            "apellido": self.apellido_input.text().strip(),
            "fecha_nac": self.fecha_input.date().toPyDate(),
            "email": self.email_input.text().strip(),
            "telefono": self.telefono_input.text().strip(),
            "direccion": self.direccion_input.toPlainText().strip(),
            "estado_cliente": self.estado_input.currentText(),
            "limite_credito": float(self.credito_input.value()),
        }


class ClienteDetailDialog(QDialog):
    """Displays all persisted information for a cliente."""

    def __init__(self, cliente: Cliente, parent=None) -> None:
        super().__init__(parent)
        self._cliente = cliente
        self.setWindowTitle("Detalle de cliente")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        def add_row(label: str, value: str) -> None:
            form_layout.addRow(label, QLabel(value))

        fecha = self._cliente.fecha_nac.strftime("%d/%m/%Y") if self._cliente.fecha_nac else "Sin registro"
        add_row("ID", str(self._cliente.id or ""))
        add_row("RUT", self._cliente.rut)
        add_row("DV", self._cliente.dv)
        add_row("Nombre", self._cliente.nombre)
        add_row("Apellido", self._cliente.apellido)
        add_row("Fecha nacimiento", fecha)
        add_row("Email", self._cliente.email)
        add_row("Teléfono", self._cliente.telefono)
        add_row("Dirección", self._cliente.direccion)
        add_row("Estado", self._cliente.estado_cliente)
        add_row("Límite crédito", f"{self._cliente.limite_credito or 0:,.0f}")

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        button_box.accepted.connect(self.accept)
        button_box.button(QDialogButtonBox.StandardButton.Close).clicked.connect(self.accept)
        layout.addWidget(button_box)
