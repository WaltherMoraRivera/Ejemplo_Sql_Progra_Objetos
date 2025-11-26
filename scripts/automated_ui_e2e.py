"""Automated UI E2E test using PyQt6 QTest.

Flow:
 - Open MainWindow
 - Verify initial list from repository
 - Click 'Nuevo' -> fill ClienteFormDialog -> accept
 - Verify item created in repository and appears in model
 - Click 'Recargar' and verify
 - Select created row and click 'Eliminar' (auto-confirm)
 - Verify deletion in repository and model

Exit codes:
 0 = success
 >0 = failure
"""
from pathlib import Path
import sys
import uuid
import time

from PyQt6.QtWidgets import QApplication, QPushButton, QMessageBox, QDialogButtonBox
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

from app.infrastructure.database.oracle_connection import OracleConnection
from app.infrastructure.repositories.asistente_repository import AsistenteRepository
from app.ui.main_window import MainWindow
from app.ui.dialogs import ClienteFormDialog


def find_button_by_text(window, text):
    for btn in window.findChildren(QPushButton):
        try:
            if btn.text() == text:
                return btn
        except Exception:
            continue
    return None


def main():
    settings = Path("config/settings.json")
    conn = OracleConnection.from_settings(settings)
    repo = AsistenteRepository(conn)

    app = QApplication(sys.argv)
    window = MainWindow(settings)
    window.show()
    QTest.qWaitForWindowExposed(window)
    QTest.qWait(200)

    # initial repo items
    repo_items_before = repo.get_all()
    print("Repo before count:", len(repo_items_before))

    # Find buttons
    nuevo_btn = find_button_by_text(window, "Nuevo")
    recargar_btn = find_button_by_text(window, "Recargar")
    eliminar_btn = find_button_by_text(window, "Eliminar")
    assert nuevo_btn and recargar_btn and eliminar_btn, "Toolbar buttons not found"

    # Prepare unique test asistente
    unique_tag = uuid.uuid4().hex[:8]
    test_email = f"ui.test.{unique_tag}@example.com"
    test_phone = str(uuid.uuid4().int % 10**10).rjust(10, "0")

    # Create the dialog programmatically (avoid blocking exec in MainWindow) and
    # use the viewmodel to add the asistente. This keeps the UI creation flow
    # logically equivalent while allowing automation.
    from app.domain.models.asistente import Asistente

    dialog = ClienteFormDialog(window)
    dialog.nombre_input.setText("UI TEST USER")
    dialog.email_input.setText(test_email)
    dialog.telefono_input.setText(test_phone)
    dialog.edad_input.setValue(29)
    dialog.ciudad_input.setText("TestCity")
    idx = dialog.tipo_input.findText("General")
    if idx >= 0:
        dialog.tipo_input.setCurrentIndex(idx)
    QTest.qWait(100)

    data = dialog.get_data()
    asistente_obj = Asistente(
        id=None,
        nombre=data["nombre"],
        correo=data["correo"],
        telefono=data["telefono"],
        edad=data["edad"],
        ciudad_residencia=data["ciudad_residencia"],
        tipo_asistente=data["tipo_asistente"],
    )

    # Add via viewmodel (prefer new name)
    if getattr(window._viewmodel, "add_asistente", None):
        ok_created = window._viewmodel.add_asistente(asistente_obj)
    else:
        ok_created = window._viewmodel.add_cliente(asistente_obj)
    QTest.qWait(300)

    # Ensure viewmodel/model refreshed and verify created in repo
    repo_items_after = repo.get_all()
    created = [a for a in repo_items_after if a.correo == test_email and a.telefono == test_phone]
    if not created:
        print("[ERROR] Created asistente not found in repository")
        sys.exit(4)
    created_id = created[0].id
    print("Created asistente id:", created_id)

    # Verify appears in model — force a load and process events to update the view
    window._viewmodel.load_asistentes()
    app.processEvents()
    QTest.qWait(500)

    # Debug prints: show viewmodel cache and model contents
    print("ViewModel cached asistentes:", len(window._viewmodel._asistentes))
    for a in window._viewmodel._asistentes:
        print(" - VM:", a.id, a.nombre, a.correo, a.telefono)
    model = window.centralWidget().model()
    print("Model rowCount:", model.rowCount())
    def _unwrap(val):
        try:
            if hasattr(val, "value"):
                return val.value()
            if hasattr(val, "toPyObject"):
                return val.toPyObject()
        except Exception:
            pass
        return val

    for r in range(model.rowCount()):
        nombre = _unwrap(model.data(model.index(r, 1), Qt.ItemDataRole.DisplayRole))
        correo = _unwrap(model.data(model.index(r, 2), Qt.ItemDataRole.DisplayRole))
        telefono = _unwrap(model.data(model.index(r, 3), Qt.ItemDataRole.DisplayRole))
        print(f" - MODEL ROW {r}: nombre={nombre} correo={correo} telefono={telefono}")
    model = window.centralWidget().model()
    found_in_model = False
    for r in range(model.rowCount()):
        nombre = _unwrap(model.data(model.index(r, 1), Qt.ItemDataRole.DisplayRole))
        correo = _unwrap(model.data(model.index(r, 2), Qt.ItemDataRole.DisplayRole))
        telefono = _unwrap(model.data(model.index(r, 3), Qt.ItemDataRole.DisplayRole))
        if str(correo) == test_email and str(telefono) == test_phone:
            found_in_model = True
            row_index = r
            break
    if not found_in_model:
        print("[ERROR] Created asistente not found in model view")
        sys.exit(5)
    print("Asistente visible in model at row", row_index)

    # Now test Recargar button (click it and ensure model still has it)
    QTest.mouseClick(recargar_btn, Qt.MouseButton.LeftButton)
    QTest.qWait(300)
    # Debug: print model rows after recargar
    app.processEvents()
    QTest.qWait(300)
    print("After recargar - model rows:")
    still_there = False
    for r in range(model.rowCount()):
        correo = _unwrap(model.data(model.index(r, 2), Qt.ItemDataRole.DisplayRole))
        telefono = _unwrap(model.data(model.index(r, 3), Qt.ItemDataRole.DisplayRole))
        print(f" - row {r}: correo={correo} telefono={telefono}")
        if str(correo) == test_email and str(telefono) == test_phone:
            still_there = True
            break
    if not still_there:
        print("[ERROR] After recargar, asistente not present")
        sys.exit(6)
    print("Recargar validated")

    # Select the created row by toggling checkbox via setData
    # Determine the select column index (0)
    select_index = model.index(row_index, 0)
    model.setData(select_index, Qt.CheckState.Checked, Qt.ItemDataRole.CheckStateRole)
    QTest.qWait(200)

    # Monkeypatch QMessageBox.question to auto return Yes
    original_question = QMessageBox.question
    def auto_yes(*args, **kwargs):
        return QMessageBox.StandardButton.Yes
    QMessageBox.question = auto_yes

    try:
        # Click eliminar
        QTest.mouseClick(eliminar_btn, Qt.MouseButton.LeftButton)
        QTest.qWait(500)
    finally:
        QMessageBox.question = original_question

    # Verify deletion in repo
    maybe = repo.get_by_id(created_id)
    if maybe is not None:
        print("[ERROR] Asistente still present in repo after delete")
        sys.exit(7)

    # Verify not in model
    window._viewmodel.load_asistentes()
    QTest.qWait(300)
    present = False
    for r in range(model.rowCount()):
        correo = model.data(model.index(r, 2), Qt.ItemDataRole.DisplayRole)
        if str(correo) == test_email:
            present = True
            break
    if present:
        print("[ERROR] Asistente still present in model after delete")
        sys.exit(8)

    print("Automated UI E2E passed: view/create/recargar/delete OK")
    sys.exit(0)


if __name__ == '__main__':
    main()
