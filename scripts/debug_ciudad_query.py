"""Debug: ejecuta la query SELECT directamente contra la BD."""
from pathlib import Path
import sys

from app.infrastructure.database.oracle_connection import OracleConnection


def main():
    settings = Path("config/settings.json")
    print(f"Settings: {settings.resolve()}")
    
    try:
        conn = OracleConnection.from_settings(settings)
        print("[OK] Connection created")
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        sys.exit(1)
    
    try:
        with conn.get_connection() as c:
            with c.cursor() as cursor:
                # Primero, enumera las tablas disponibles
                cursor.execute("SELECT table_name FROM user_tables ORDER BY table_name")
                tables = cursor.fetchall()
                print(f"[OK] Tables in current schema: {[t[0] for t in tables]}")
                
                # Intenta contar registros en ciudad
                if tables and any('CIUDAD' in str(t[0]).upper() for t in tables):
                    print("\n[OK] CIUDAD table exists. Executing SELECT...")
                    cursor.execute("SELECT id_ciudad, nombre, region, pais, observaciones FROM ciudad")
                    rows = cursor.fetchall()
                    print(f"[OK] Retrieved {len(rows)} rows from ciudad")
                    for row in rows:
                        print(f"  - {row}")
                else:
                    print("[WARN] CIUDAD table not found in current schema")
    except Exception as e:
        print(f"[ERROR] Query failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)


if __name__ == '__main__':
    main()
