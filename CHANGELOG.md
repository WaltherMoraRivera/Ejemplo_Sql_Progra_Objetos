# Changelog

All notable changes to this project are documented in this file.

## Unreleased - 2025-11-26

### Added
- `Premiacion` entity: domain model (`app/domain/models/premiacion.py`), repository (`app/infrastructure/repositories/premiacion_repository.py`), viewmodel (`app/viewmodels/premiacion_viewmodel.py`), UI table model (`app/ui/premiacion_table_model.py`), and dialogs (`app/ui/dialogs.py`).
- Integration of `premiacion` into the main UI (`app/ui/main_window.py`) with CRUD flows (create, list, detail, delete).

### Changed
- Adapted `Evaluacion` and its repository to handle the real database schema (composite primary key and date column variations). See `app/domain/models/evaluacion.py` and `app/infrastructure/repositories/evaluacion_repository.py`.
- UI wiring updated across table models and viewmodels to follow the project's MVVM pattern.

### Fixed
- Handled ORA-00904 issues by detecting/using the correct column names for `EVALUACION` in the repository layer when necessary.

### Notes
- Performed quick syntax checks and a manual CRUD flow against the Oracle DB for `premiacion` (insert → fetch → delete). The test required using an existing `id_pelicula` to satisfy the FK constraint.

---

If you want a different changelog format (Keep a Changelog, semantic-release, or lightweight release notes), tell me which style and I will adapt this file.
