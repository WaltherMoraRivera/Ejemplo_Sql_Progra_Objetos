"""End-to-end test for Evaluacion entity UI flow."""
from unittest.mock import MagicMock, patch

from PyQt6.QtWidgets import QApplication
import sys

# Mock Oracle connection before importing the app
sys.modules['oracledb'] = MagicMock()

from app.domain.models.evaluacion import Evaluacion
from app.ui.main_window import MainWindow


def test_evaluacion_ui_flow():
    app = QApplication([])

    import tempfile
    from pathlib import Path
    import json

    with tempfile.TemporaryDirectory() as tmpdir:
        settings_path = Path(tmpdir) / "settings.json"
        settings_path.write_text(json.dumps({
            "db": {"user": "test", "password": "test", "dsn": "test"}
        }))

        window = MainWindow(settings_path)

        assert window._entity is None
        print("✓ Step 1: Menu shown initially (entity is None)")

        with patch('app.infrastructure.database.oracle_connection.OracleConnection.from_settings'):
            with patch('app.infrastructure.repositories.evaluacion_repository.EvaluacionRepository') as MockRepo:
                mock_repo = MagicMock()
                mock_repo.get_all.return_value = [
                    Evaluacion(id=1, id_jurado=1, id_funcion=1, puntuacion=85, comentario="Buen trabajo"),
                ]
                MockRepo.return_value = mock_repo

                window._set_entity('evaluacion')

        assert window._entity == 'evaluacion'
        assert window._viewmodel is not None
        assert window._model is not None
        print("✓ Step 2: Evaluacion entity selected (entity, viewmodel, model initialized)")

        expected_title = "Gestor de Festival de Cine - Evaluaciones"
        assert window.windowTitle() == expected_title
        print(f"✓ Step 3: Window title updated to '{expected_title}'")

        assert window._new_action.isVisible()
        assert window._delete_action.isVisible()
        assert window._refresh_action.isVisible()
        assert window._back_button.isVisible()
        print("✓ Step 4: Toolbar actions are visible (new, delete, refresh, back)")

        window._back_to_menu()
        assert window._entity is None
        assert window._viewmodel is None
        assert window._model is None
        assert not window._new_action.isVisible()
        print("✓ Step 5: Back button returns to menu (entity, viewmodel, model cleared)")

        with patch('app.infrastructure.database.oracle_connection.OracleConnection.from_settings'):
            with patch('app.infrastructure.repositories.evaluacion_repository.EvaluacionRepository') as MockRepo:
                mock_repo = MagicMock()
                mock_repo.get_all.return_value = [
                    Evaluacion(id=2, id_jurado=2, id_funcion=2, puntuacion=90, comentario="Excelente"),
                ]
                MockRepo.return_value = mock_repo

                window._set_entity('evaluacion')

        assert window._entity == 'evaluacion'
        print("✓ Step 6: Evaluacion entity re-selected successfully (reusable)")

    print("\n✅ All E2E tests for Evaluacion PASSED!")


if __name__ == '__main__':
    test_evaluacion_ui_flow()
