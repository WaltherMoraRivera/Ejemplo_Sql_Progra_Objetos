"""Insert sample CIUDAD data from the images provided by the user."""
from pathlib import Path
import sys

from app.infrastructure.database.oracle_connection import OracleConnection
from app.infrastructure.repositories.ciudad_repository import CiudadRepository
from app.domain.models.ciudad import Ciudad


def main():
    settings = Path("config/settings.json")
    print(f"Using settings: {settings.resolve()}")
    
    try:
        conn = OracleConnection.from_settings(settings)
        print("[OK] Connection created")
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        sys.exit(1)
    
    repo = CiudadRepository(conn)
    
    # Data from the user's screenshot (id_ciudad, nombre, region, pais, observaciones)
    ciudades_data = [
        ("Santiago", "Metropolitana", "Chile", "Sin observaciones"),
        ("Valparaíso", "Valparaiso", "Chile", "Sin observaciones"),
        ("Concepción", "Bíobío", "Chile", "Sin observaciones"),
        ("Buenos Aires", "CABA", "Argentina", "Sin observaciones"),
        ("Lima", "Lima Metropolitana", "Perú", "Sin observaciones"),
    ]
    
    for nombre, region, pais, obs in ciudades_data:
        ciudad = Ciudad(
            id=None,
            nombre=nombre,
            region=region,
            pais=pais,
            observaciones=obs,
        )
        try:
            new_id = repo.add(ciudad)
            print(f"[OK] Inserted: id={new_id}, nombre={nombre}, region={region}, pais={pais}")
        except Exception as e:
            print(f"[WARN] Insert failed for {nombre}: {e}")
    
    # Verify insertion
    print("\nVerifying insertion:")
    ciudades = repo.get_all()
    print(f"[OK] Total ciudades in DB: {len(ciudades)}")
    for c in ciudades:
        print(f"  - id={c.id}, nombre={c.nombre}, region={c.region}, pais={c.pais}")


if __name__ == '__main__':
    main()
