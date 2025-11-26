from pathlib import Path
from app.infrastructure.database.oracle_connection import OracleConnection

settings = Path('config/settings.json')
print('Using settings', settings.resolve())
conn = OracleConnection.from_settings(settings)
with conn.get_connection() as c:
    with c.cursor() as cur:
        print('Querying ALL_TABLES for ASISTENTE')
        cur.execute("SELECT owner, table_name FROM all_tables WHERE table_name = 'ASISTENTE'")
        rows = cur.fetchall()
        if not rows:
            print('No entries in ALL_TABLES for ASISTENTE')
        else:
            for owner, tbl in rows:
                print('Owner:', owner, 'Table:', tbl)
                try:
                    cur.execute(f"SELECT COUNT(*) FROM {owner}.ASISTENTE")
                    cnt = cur.fetchone()[0]
                    print(f' Row count for {owner}.ASISTENTE =', cnt)
                    cur.execute(f"SELECT id_asistente, nombre, correo, telefono FROM {owner}.ASISTENTE ORDER BY id_asistente")
                    sample = cur.fetchmany(10)
                    for r in sample:
                        print('  ->', r)
                except Exception as e:
                    print('  Could not query', owner, '.ASISTENTE:', e)
