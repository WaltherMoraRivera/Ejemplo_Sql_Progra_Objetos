"""End-to-end test for ParticipacionJurado entity UI flow."""
from unittest.mock import MagicMock, patch

from PyQt6.QtWidgets import QApplication
import sys

# Mock Oracle connection before importing the app
sys.modules['oracledb'] = MagicMock()

from app.domain.models.participacion_jurado import ParticipacionJurado
from app.ui.main_window import MainWindow


def test_participacion_jurado_ui_flow():
    """Test ParticipacionJurado entity selection, visibility, and detail view."""
    app = QApplication([])

    # Create a temporary settings file for testing
    import tempfile
    from pathlib import Path
    import json

    with tempfile.TemporaryDirectory() as tmpdir:
        settings_path = Path(tmpdir) / "settings.json"
        settings_path.write_text(json.dumps({
            "db": {"user": "test", "password": "test", "dsn": "test"}
        }))

        # Create main window
        window = MainWindow(settings_path)

        # Step 1: Verify menu is shown initially
        assert window._entity is None, "Initial entity should be None"
        print("✓ Step 1: Menu shown initially (entity is None)")

        # Step 2: Select ParticipacionJurado entity
        with patch('app.infrastructure.database.oracle_connection.OracleConnection.from_settings'):
            with patch('app.infrastructure.repositories.participacion_jurado_repository.ParticipacionJuradoRepository') as MockRepo:
                # Mock repository to return test data
                mock_repo_instance = MagicMock()
                mock_repo_instance.get_all.return_value = [
                    ParticipacionJurado(id_jurado=1, id_funcion=1, rol_participacion="Evaluador", comentarios="Test"),
                    ParticipacionJurado(id_jurado=2, id_funcion=2, rol_participacion="Moderador", comentarios="Test 2"),
                ]
                MockRepo.return_value = mock_repo_instance

                window._set_entity('participacion_jurado')

        assert window._entity == 'participacion_jurado', "Entity should be 'participacion_jurado'"
        assert window._viewmodel is not None, "ViewModel should be initialized"
        assert window._model is not None, "TableModel should be initialized"
        print("✓ Step 2: ParticipacionJurado entity selected (entity, viewmodel, model initialized)")

        # Step 3: Verify title updated
        expected_title = "Gestor de Festival de Cine - Participaciones de Jurado"
        assert window.windowTitle() == expected_title, f"Title should be '{expected_title}'"
        print(f"✓ Step 3: Window title updated to '{expected_title}'")

        # Step 4: Verify toolbar actions are visible
        assert window._new_action.isVisible(), "New action should be visible"
        assert window._delete_action.isVisible(), "Delete action should be visible"
        assert window._refresh_action.isVisible(), "Refresh action should be visible"
        assert window._back_button.isVisible(), "Back button should be visible"
        print("✓ Step 4: Toolbar actions are visible (new, delete, refresh, back)")

        # Step 5: Verify back button functionality
        window._back_to_menu()
        assert window._entity is None, "Entity should be None after back"
        assert window._viewmodel is None, "ViewModel should be None after back"
        assert window._model is None, "TableModel should be None after back"
        assert not window._new_action.isVisible(), "New action should be hidden in menu"
        print("✓ Step 5: Back button returns to menu (entity, viewmodel, model cleared)")

        # Step 6: Re-select ParticipacionJurado to verify reusability
        with patch('app.infrastructure.database.oracle_connection.OracleConnection.from_settings'):
            with patch('app.infrastructure.repositories.participacion_jurado_repository.ParticipacionJuradoRepository') as MockRepo:
                mock_repo_instance = MagicMock()
                mock_repo_instance.get_all.return_value = [
                    ParticipacionJurado(id_jurado=3, id_funcion=3, rol_participacion="Invitado especial", comentarios="Test 3"),
                ]
                MockRepo.return_value = mock_repo_instance

                window._set_entity('participacion_jurado')

        assert window._entity == 'participacion_jurado', "Entity should be 'participacion_jurado' again"
        print("✓ Step 6: ParticipacionJurado entity re-selected successfully (reusable)")

    print("\n✅ All E2E tests for ParticipacionJurado PASSED!")


if __name__ == '__main__':
    test_participacion_jurado_ui_flow()
