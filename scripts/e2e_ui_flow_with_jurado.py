#!/usr/bin/env python3
"""E2E test validating JURADO integration in UI flow without database access."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add workspace root to path
workspace_root = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_root))

from PyQt6.QtWidgets import QApplication


def run_e2e_test():
    """Test JURADO entity in menu, table selection, and back navigation."""
    
    # Mock OracleConnection to avoid DB access
    mock_connection = MagicMock()
    
    with patch('app.infrastructure.database.oracle_connection.OracleConnection.from_settings', return_value=mock_connection):
        with patch('app.infrastructure.repositories.jurado_repository.JuradoRepository.get_all', return_value=[]):
            from app.ui.main_window import MainWindow
            
            app = QApplication.instance() or QApplication(sys.argv)
            
            settings_path = workspace_root / "config" / "settings.json"
            window = MainWindow(settings_path)
            window.show()
            
            # Step 1: Verify initial state (menu, no entity)
            step1_entity = window._entity
            step1_title = window.windowTitle()
            
            # Step 2: Select JURADO from menu
            window._set_entity('jurado')
            step2_entity = window._entity
            step2_title = window.windowTitle()
            step2_actions_visible = (window._refresh_action.isVisible() if hasattr(window, '_refresh_action') else False)
            step2_table_visible = window._table.isVisible()
            
            # Step 3: Back to menu
            window._show_table_selection_menu()
            step3_entity = window._entity
            step3_title = window.windowTitle()
            step3_actions_visible = (window._refresh_action.isVisible() if hasattr(window, '_refresh_action') else False)
            
            # Step 4: Select another entity (ASISTENCIA) to test widget reusability
            window._set_entity('asistencia')
            step4_entity = window._entity
            step4_title = window.windowTitle()
            
            # Step 5: Back to menu again
            window._show_table_selection_menu()
            step5_entity = window._entity
            step5_title = window.windowTitle()
            
            # Step 6: Select JURADO again (widget must not be deleted)
            window._set_entity('jurado')
            step6_entity = window._entity
            step6_title = window.windowTitle()
            step6_table_still_visible = window._table.isVisible()
            
            # Validate results
            print(f"step1_entity: {step1_entity}")
            print(f"step1_title: {step1_title}")
            print(f"step2_entity: {step2_entity}")
            print(f"step2_title: {step2_title}")
            print(f"step2_actions_visible: {step2_actions_visible}")
            print(f"step2_table_visible: {step2_table_visible}")
            print(f"step3_entity: {step3_entity}")
            print(f"step3_title: {step3_title}")
            print(f"step3_actions_visible: {step3_actions_visible}")
            print(f"step4_entity: {step4_entity}")
            print(f"step4_title: {step4_title}")
            print(f"step5_entity: {step5_entity}")
            print(f"step5_title: {step5_title}")
            print(f"step6_entity: {step6_entity}")
            print(f"step6_title: {step6_title}")
            print(f"step6_table_still_visible: {step6_table_still_visible}")
            
            # Assert all steps pass
            assert step1_entity is None, "Initial entity should be None"
            assert step1_title == "Gestor de Festival de Cine", "Initial title incorrect"
            assert step2_entity == 'jurado', "Should select jurado entity"
            assert "Jurados" in step2_title, "Title should indicate Jurados"
            assert step2_actions_visible, "Actions should be visible in table view"
            assert step2_table_visible, "Table should be visible after selecting JURADO"
            assert step3_entity is None, "Entity should be None after back to menu"
            assert step3_actions_visible is False, "Actions should be hidden in menu"
            assert step4_entity == 'asistencia', "Should switch to asistencia entity"
            assert step5_entity is None, "Entity should be None after back to menu again"
            assert step6_entity == 'jurado', "Should select jurado again"
            assert "Jurados" in step6_title, "Final title should indicate Jurados"
            assert step6_table_still_visible, "Table should still be usable after multiple transitions"
            
            print("✅ E2E UI Flow Test with JURADO PASSED: All transitions completed without errors.")
            window.close()
            return True


if __name__ == "__main__":
    try:
        run_e2e_test()
        sys.exit(0)
    except AssertionError as e:
        print(f"❌ Test Failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
