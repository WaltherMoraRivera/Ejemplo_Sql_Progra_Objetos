"""Repository for Pelicula entity."""
from __future__ import annotations

from typing import List

from app.domain.models.pelicula import Pelicula
from app.infrastructure.database.oracle_connection import OracleConnection


class PeliculaRepository:
    """CRUD operations for pelicula table."""

    def __init__(self, connection_factory: OracleConnection) -> None:
        self._connection_factory = connection_factory

    def get_all(self) -> List[Pelicula]:
        """Retrieve all peliculas from the database."""
        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id_pelicula, titulo, pais_origen, director, duracion_minutos,
                           genero, clasificacion, sinopsis
                    FROM pelicula
                    ORDER BY id_pelicula
                    """
                )
                rows = cursor.fetchall()
        return [self._map_row(row) for row in rows]

    def get_by_id(self, id_pelicula: int) -> Pelicula | None:
        """Retrieve a single pelicula by ID."""
        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id_pelicula, titulo, pais_origen, director, duracion_minutos,
                           genero, clasificacion, sinopsis
                    FROM pelicula
                    WHERE id_pelicula = :id
                    """,
                    {"id": id_pelicula},
                )
                row = cursor.fetchone()
        return self._map_row(row) if row else None

    def add(self, pelicula: Pelicula) -> int | None:
        """Insert a new pelicula and return its generated ID."""
        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO pelicula (titulo, pais_origen, director, duracion_minutos,
                                         genero, clasificacion, sinopsis)
                    VALUES (:titulo, :pais_origen, :director, :duracion_minutos,
                            :genero, :clasificacion, :sinopsis)
                    """,
                    {
                        "titulo": pelicula.titulo,
                        "pais_origen": pelicula.pais_origen,
                        "director": pelicula.director,
                        "duracion_minutos": pelicula.duracion_minutos,
                        "genero": pelicula.genero,
                        "clasificacion": pelicula.clasificacion,
                        "sinopsis": pelicula.sinopsis,
                    },
                )
                conn.commit()

            # Retrieve the generated ID
            with conn.cursor() as id_cursor:
                id_cursor.execute("SELECT MAX(id_pelicula) FROM pelicula")
                result = id_cursor.fetchone()
                # result may be (id,) or [id]
                new_id = result[0] if isinstance(result, (tuple, list)) else result
                return new_id if new_id is not None else None

    def update(self, pelicula: Pelicula) -> bool:
        """Update an existing pelicula."""
        if pelicula.id is None:
            return False
        try:
            with self._connection_factory.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE pelicula
                        SET titulo = :titulo,
                            pais_origen = :pais_origen,
                            director = :director,
                            duracion_minutos = :duracion_minutos,
                            genero = :genero,
                            clasificacion = :clasificacion,
                            sinopsis = :sinopsis
                        WHERE id_pelicula = :id
                        """,
                        {
                            "titulo": pelicula.titulo,
                            "pais_origen": pelicula.pais_origen,
                            "director": pelicula.director,
                            "duracion_minutos": pelicula.duracion_minutos,
                            "genero": pelicula.genero,
                            "clasificacion": pelicula.clasificacion,
                            "sinopsis": pelicula.sinopsis,
                            "id": pelicula.id,
                        },
                    )
                conn.commit()
            return True
        except Exception:
            return False

    def delete_many(self, ids: List[int]) -> bool:
        """Delete multiple peliculas by IDs."""
        if not ids:
            return False
        try:
            with self._connection_factory.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        f"DELETE FROM pelicula WHERE id_pelicula IN ({','.join([':id' + str(i) for i in range(len(ids))])})",
                        {f"id{i}": id_val for i, id_val in enumerate(ids)},
                    )
                conn.commit()
            return True
        except Exception:
            return False

    def _map_row(self, row: tuple) -> Pelicula:
        """Map a database row to a Pelicula object."""
        return Pelicula(
            id=row[0],
            titulo=row[1],
            pais_origen=row[2],
            director=row[3],
            duracion_minutos=row[4],
            genero=row[5],
            clasificacion=row[6],
            sinopsis=row[7],
        )
