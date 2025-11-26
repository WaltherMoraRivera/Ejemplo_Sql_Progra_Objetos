"""Diagnóstico: verifica si CiudadRepository obtiene datos de la BD."""
from pathlib import Path
import sys

from app.infrastructure.database.oracle_connection import OracleConnection
from app.infrastructure.repositories.ciudad_repository import CiudadRepository


def main():
    settings = Path("config/settings.json")
    print(f"Settings: {settings.resolve()}")
    
    try:
        conn = OracleConnection.from_settings(settings)
        print("[OK] Connection created")
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        sys.exit(1)
    
    repo = CiudadRepository(conn)
    
    try:
        ciudades = repo.get_all()
        print(f"[OK] Retrieved {len(ciudades)} ciudades from repository")
        for c in ciudades:
            print(f"  - id={c.id}, nombre={c.nombre}, region={c.region}, pais={c.pais}, obs={c.observaciones}")
    except Exception as e:
        print(f"[ERROR] get_all() failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)
    
    if len(ciudades) == 0:
        print("[WARN] No ciudades found in database")
    else:
        print("[OK] Data retrieval works correctly")


if __name__ == '__main__':
    main()
