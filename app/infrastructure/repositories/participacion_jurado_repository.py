from typing import List

from app.domain.models.participacion_jurado import ParticipacionJurado
from app.infrastructure.database.oracle_connection import OracleConnection


class ParticipacionJuradoRepository:
    """CRUD operations for participacion_jurado table."""

    def __init__(self, connection_factory: OracleConnection) -> None:
        self._connection_factory = connection_factory

    def get_all(self) -> List[ParticipacionJurado]:
        """Retrieve all participacion_jurado records from the database."""
        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id_jurado, id_funcion, rol_participacion, comentarios
                    FROM participacion_jurado
                    ORDER BY id_jurado, id_funcion
                    """
                )
                rows = cursor.fetchall()
        return [self._map_row(row) for row in rows]

    def get_by_id(self, id_jurado: int, id_funcion: int) -> ParticipacionJurado | None:
        """Retrieve a single participacion_jurado by composite ID."""
        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id_jurado, id_funcion, rol_participacion, comentarios
                    FROM participacion_jurado
                    WHERE id_jurado = :id_jurado AND id_funcion = :id_funcion
                    """,
                    {"id_jurado": id_jurado, "id_funcion": id_funcion},
                )
                row = cursor.fetchone()
        return self._map_row(row) if row else None

    def add(self, participacion: ParticipacionJurado) -> bool:
        """Insert a new participacion_jurado record."""
        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO participacion_jurado (id_jurado, id_funcion, rol_participacion, comentarios)
                    VALUES (:id_jurado, :id_funcion, :rol_participacion, :comentarios)
                    """,
                    {
                        "id_jurado": participacion.id_jurado,
                        "id_funcion": participacion.id_funcion,
                        "rol_participacion": participacion.rol_participacion,
                        "comentarios": participacion.comentarios,
                    },
                )
                conn.commit()
        return True

    def update(self, participacion: ParticipacionJurado) -> bool:
        """Update an existing participacion_jurado record."""
        try:
            with self._connection_factory.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE participacion_jurado
                        SET rol_participacion = :rol_participacion,
                            comentarios = :comentarios
                        WHERE id_jurado = :id_jurado AND id_funcion = :id_funcion
                        """,
                        {
                            "rol_participacion": participacion.rol_participacion,
                            "comentarios": participacion.comentarios,
                            "id_jurado": participacion.id_jurado,
                            "id_funcion": participacion.id_funcion,
                        },
                    )
                conn.commit()
            return True
        except Exception:
            return False

    def delete(self, id_jurado: int, id_funcion: int) -> bool:
        """Delete a participacion_jurado record by composite ID."""
        try:
            with self._connection_factory.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM participacion_jurado WHERE id_jurado = :id_jurado AND id_funcion = :id_funcion",
                        {"id_jurado": id_jurado, "id_funcion": id_funcion},
                    )
                conn.commit()
            return True
        except Exception:
            return False

    def delete_many(self, ids: List[tuple]) -> bool:
        """Delete multiple participacion_jurado records by composite IDs."""
        if not ids:
            return False
        try:
            for id_jurado, id_funcion in ids:
                self.delete(id_jurado, id_funcion)
            return True
        except Exception:
            return False

    def _map_row(self, row: tuple) -> ParticipacionJurado:
        """Map a database row to a ParticipacionJurado object."""
        return ParticipacionJurado(
            id_jurado=row[0],
            id_funcion=row[1],
            rol_participacion=row[2],
            comentarios=row[3],
        )
