"""E2E test for Asistente repository.

Creates an Asistente, lists asistentes, deletes the created record and verifies deletion.
Exits with non-zero codes on failures for easier CI inspection.
"""
from pathlib import Path
import sys
import traceback

from app.infrastructure.database.oracle_connection import OracleConnection
from app.infrastructure.repositories.asistente_repository import AsistenteRepository
from app.domain.models.asistente import Asistente
import uuid


def main() -> None:
    settings = Path("config/settings.json")
    print(f"Using settings file: {settings.resolve()}")

    try:
        conn = OracleConnection.from_settings(settings)
        print("OracleConnection created from settings.")
        with conn.get_connection() as c:
            # print a minimal connection detail
            ver = getattr(c, "version", None)
            print("Connection opened. Connection object:", type(c).__name__, "version=" , ver)
    except Exception as exc:
        print("[ERROR] DB connection failed:", exc)
        traceback.print_exc()
        sys.exit(2)

    repo = AsistenteRepository(conn)

    # Prepare a test asistente
    unique_tag = uuid.uuid4().hex[:8]
    telefono_value = str(uuid.uuid4().int % 10**10).rjust(10, "0")
    test_asistente = Asistente(
        id=None,
        nombre="TEST_AUTOM",
        correo=f"test.autom.{unique_tag}@example.com",
        telefono=telefono_value,
        edad=30,
        ciudad_residencia="TestCity",
        tipo_asistente="General",
    )

    try:
        new_id = repo.add(test_asistente)
        print("[OK] Inserted Asistente with id:", new_id)
    except Exception as exc:
        print("[ERROR] Insert failed:", exc)
        traceback.print_exc()
        sys.exit(3)

    try:
        all_items = repo.get_all()
        print(f"[OK] Retrieved {len(all_items)} asistentes (sample up to 5):")
        for item in all_items[:5]:
            print(" -", item)
        exists = any(getattr(x, "id", None) == new_id for x in all_items)
        print(f"[OK] Inserted asistente present in list: {exists}")
    except Exception as exc:
        print("[ERROR] Listing failed:", exc)
        traceback.print_exc()
        sys.exit(4)

    try:
        repo.delete_many([new_id])
        print("[OK] Deleted asistente id:", new_id)
    except Exception as exc:
        print("[ERROR] Delete failed:", exc)
        traceback.print_exc()
        sys.exit(5)

    try:
        maybe = repo.get_by_id(new_id)
        print("[OK] After delete, get_by_id returned:", maybe)
        if maybe is not None:
            print("[ERROR] Record still present after delete")
            sys.exit(6)
    except Exception as exc:
        print("[ERROR] Final get_by_id failed:", exc)
        traceback.print_exc()
        sys.exit(7)

    print("E2E test completed successfully.")


if __name__ == "__main__":
    main()
