from pathlib import Path
from app.infrastructure.database.oracle_connection import OracleConnection
conn = OracleConnection.from_settings(Path('config/settings.json'))
with conn.get_connection() as c:
    with c.cursor() as cur:
        cur.execute("SELECT owner, synonym_name, table_owner, table_name FROM all_synonyms WHERE table_name = 'ASISTENTE'")
        rows = cur.fetchall()
        if not rows:
            print('No synonyms found for ASISTENTE')
        else:
            for r in rows:
                print('Synonym:', r)
