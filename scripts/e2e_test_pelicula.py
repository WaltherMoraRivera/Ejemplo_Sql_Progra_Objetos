"""End-to-end test for Pelicula CRUD operations."""
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.domain.models.pelicula import Pelicula
from app.infrastructure.database.oracle_connection import OracleConnection
from app.infrastructure.repositories.pelicula_repository import PeliculaRepository


def test_pelicula_crud():
    """Test create, read, list, and delete operations for Pelicula."""
    settings_path = Path(__file__).parent.parent / "config" / "settings.json"
    connection = OracleConnection.from_settings(settings_path)
    repo = PeliculaRepository(connection)

    # Use timestamp for unique titles
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("\n=== Testing Pelicula CRUD ===\n")

    # Test 1: Create a new pelicula
    print("Test 1: Creating new pelicula...")
    pelicula_data = Pelicula(
        titulo=f"La Persistencia de la Memoria ({timestamp})",
        pais_origen="España",
        director="Salvador Dalí",
        duracion_minutos=120,
        genero="Surrealismo",
        clasificacion="+14",
        sinopsis="Una exploración visual de los conceptos de tiempo y espacio.",
    )
    new_id = repo.add(pelicula_data)
    print(f"✓ Pelicula created with ID: {new_id}")
    assert new_id is not None, "Failed to create pelicula"

    # Test 2: Retrieve by ID
    print("\nTest 2: Retrieving pelicula by ID...")
    retrieved = repo.get_by_id(new_id)
    assert retrieved is not None, "Failed to retrieve pelicula"
    assert retrieved.titulo == pelicula_data.titulo, "Titulo mismatch"
    assert retrieved.director == pelicula_data.director, "Director mismatch"
    assert retrieved.duracion_minutos == pelicula_data.duracion_minutos, "Duracion mismatch"
    print(f"✓ Retrieved: {retrieved}")

    # Test 3: List all peliculas
    print("\nTest 3: Listing all peliculas...")
    all_peliculas = repo.get_all()
    print(f"✓ Found {len(all_peliculas)} peliculas total")
    assert len(all_peliculas) > 0, "No peliculas found"
    assert any(p.id == new_id for p in all_peliculas), "Created pelicula not in list"

    # Test 4: Create multiple peliculas for batch operations
    print("\nTest 4: Creating multiple peliculas...")
    pelicula_ids = [new_id]

    additional_peliculas = [
        Pelicula(
            titulo=f"Cien años de soledad ({timestamp})",
            pais_origen="Colombia",
            director="Gabriel García Márquez",
            duracion_minutos=180,
            genero="Drama",
            clasificacion="+18",
            sinopsis="La epopeya de la familia Buendía a través de generaciones.",
        ),
        Pelicula(
            titulo=f"Metamorfosis Visual ({timestamp})",
            pais_origen="Argentina",
            director="Jorge Luis Borges",
            duracion_minutos=95,
            genero="Documental",
            clasificacion="+7",
            sinopsis="Un viaje a través de transformaciones artísticas.",
        ),
    ]

    for pel in additional_peliculas:
        new_id_2 = repo.add(pel)
        pelicula_ids.append(new_id_2)
        print(f"  ✓ Created pelicula ID: {new_id_2}")

    # Test 5: Update a pelicula
    print("\nTest 5: Updating pelicula...")
    to_update = Pelicula(
        id=pelicula_ids[0],
        titulo=f"La Persistencia de la Memoria - Remasterizada ({timestamp})",
        pais_origen="España",
        director="Salvador Dalí",
        duracion_minutos=125,
        genero="Surrealismo",
        clasificacion="+14",
        sinopsis="Una exploración visual de los conceptos de tiempo y espacio (versión mejorada).",
    )
    update_ok = repo.update(to_update)
    assert update_ok, "Failed to update pelicula"
    verified = repo.get_by_id(pelicula_ids[0])
    assert verified.titulo == to_update.titulo, "Update verification failed"
    assert verified.duracion_minutos == 125, "Duration not updated"
    print(f"✓ Updated pelicula: {verified.titulo} (Duración: {verified.duracion_minutos} min)")

    # Test 6: Delete single pelicula
    print("\nTest 6: Deleting single pelicula...")
    id_to_delete = pelicula_ids[1]
    delete_ok = repo.delete_many([id_to_delete])
    assert delete_ok, "Failed to delete pelicula"
    deleted_check = repo.get_by_id(id_to_delete)
    assert deleted_check is None, "Pelicula still exists after deletion"
    print(f"✓ Deleted pelicula ID: {id_to_delete}")

    # Test 7: Delete multiple peliculas
    print("\nTest 7: Deleting multiple peliculas...")
    ids_to_delete = [pelicula_ids[0], pelicula_ids[2]]
    delete_ok = repo.delete_many(ids_to_delete)
    assert delete_ok, "Failed to delete multiple peliculas"
    for pid in ids_to_delete:
        check = repo.get_by_id(pid)
        assert check is None, f"Pelicula {pid} still exists after deletion"
    print(f"✓ Deleted {len(ids_to_delete)} peliculas")

    print("\n=== All Pelicula CRUD Tests Passed! ===\n")


if __name__ == "__main__":
    test_pelicula_crud()
    print("Exit code: 0")
