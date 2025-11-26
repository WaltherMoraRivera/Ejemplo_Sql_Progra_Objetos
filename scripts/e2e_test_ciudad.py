"""E2E test for Ciudad repository.

Creates a Ciudad, lists ciudades, deletes the created record and verifies deletion.
Exits with non-zero codes on failures for easier CI inspection.
"""
from pathlib import Path
import sys
import traceback
import uuid

from app.infrastructure.database.oracle_connection import OracleConnection
from app.infrastructure.repositories.ciudad_repository import CiudadRepository
from app.domain.models.ciudad import Ciudad


def main() -> None:
    settings = Path("config/settings.json")
    print(f"Using settings file: {settings.resolve()}")

    try:
        conn = OracleConnection.from_settings(settings)
        print("OracleConnection created from settings.")
        with conn.get_connection() as c:
            ver = getattr(c, "version", None)
            print("Connection opened. Connection object:", type(c).__name__, "version=", ver)
    except Exception as exc:
        print("[ERROR] DB connection failed:", exc)
        traceback.print_exc()
        sys.exit(2)

    repo = CiudadRepository(conn)

    unique_tag = uuid.uuid4().hex[:8]
    test_ciudad = Ciudad(
        id=None,
        nombre=f"TEST_CIUDAD_{unique_tag}",
        region="RegionTest",
        pais="TestLand",
        observaciones="Creado por prueba E2E",
    )

    try:
        new_id = repo.add(test_ciudad)
        print("[OK] Inserted Ciudad with id:", new_id)
    except Exception as exc:
        print("[ERROR] Insert failed:", exc)
        traceback.print_exc()
        sys.exit(3)

    try:
        all_items = repo.get_all()
        print(f"[OK] Retrieved {len(all_items)} ciudades (sample up to 5):")
        for item in all_items[:5]:
            print(" -", item)
        exists = any(getattr(x, "id", None) == new_id for x in all_items)
        print(f"[OK] Inserted ciudad present in list: {exists}")
    except Exception as exc:
        print("[ERROR] Listing failed:", exc)
        traceback.print_exc()
        sys.exit(4)

    try:
        repo.delete_many([new_id])
        print("[OK] Deleted ciudad id:", new_id)
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

    print("E2E Ciudad test completed successfully.")


if __name__ == "__main__":
    main()
