from typing import List

from app.domain.models.jurado import Jurado
from app.infrastructure.database.oracle_connection import OracleConnection


class JuradoRepository:
    """CRUD operations for jurado table."""

    def __init__(self, connection_factory: OracleConnection) -> None:
        self._connection_factory = connection_factory

    def get_all(self) -> List[Jurado]:
        """Retrieve all jurados from the database."""
        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id_jurado, nombre, correo, especialidad, pais_origen,
                           experiencia_anos, tipo_jurado, biografia
                    FROM jurado
                    ORDER BY id_jurado
                    """
                )
                rows = cursor.fetchall()
        return [self._map_row(row) for row in rows]

    def get_by_id(self, id_jurado: int) -> Jurado | None:
        """Retrieve a single jurado by ID."""
        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id_jurado, nombre, correo, especialidad, pais_origen,
                           experiencia_anos, tipo_jurado, biografia
                    FROM jurado
                    WHERE id_jurado = :id
                    """,
                    {"id": id_jurado},
                )
                row = cursor.fetchone()
        return self._map_row(row) if row else None

    def add(self, jurado: Jurado) -> int | None:
        """Insert a new jurado and return its generated ID."""
        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO jurado (nombre, correo, especialidad, pais_origen,
                                       experiencia_anos, tipo_jurado, biografia)
                    VALUES (:nombre, :correo, :especialidad, :pais_origen,
                            :experiencia_anos, :tipo_jurado, :biografia)
                    """,
                    {
                        "nombre": jurado.nombre,
                        "correo": jurado.correo,
                        "especialidad": jurado.especialidad,
                        "pais_origen": jurado.pais_origen,
                        "experiencia_anos": jurado.experiencia_anos,
                        "tipo_jurado": jurado.tipo_jurado,
                        "biografia": jurado.biografia,
                    },
                )
                conn.commit()

            # Retrieve the generated ID
            with conn.cursor() as id_cursor:
                id_cursor.execute("SELECT MAX(id_jurado) FROM jurado")
                result = id_cursor.fetchone()
                new_id = result[0] if isinstance(result, (tuple, list)) else result
                return new_id if new_id is not None else None

    def update(self, jurado: Jurado) -> bool:
        """Update an existing jurado."""
        if jurado.id is None:
            return False
        try:
            with self._connection_factory.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE jurado
                        SET nombre = :nombre,
                            correo = :correo,
                            especialidad = :especialidad,
                            pais_origen = :pais_origen,
                            experiencia_anos = :experiencia_anos,
                            tipo_jurado = :tipo_jurado,
                            biografia = :biografia
                        WHERE id_jurado = :id
                        """,
                        {
                            "nombre": jurado.nombre,
                            "correo": jurado.correo,
                            "especialidad": jurado.especialidad,
                            "pais_origen": jurado.pais_origen,
                            "experiencia_anos": jurado.experiencia_anos,
                            "tipo_jurado": jurado.tipo_jurado,
                            "biografia": jurado.biografia,
                            "id": jurado.id,
                        },
                    )
                conn.commit()
            return True
        except Exception:
            return False

    def delete_many(self, ids: List[int]) -> bool:
        """Delete multiple jurados by IDs."""
        if not ids:
            return False
        try:
            with self._connection_factory.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        f"DELETE FROM jurado WHERE id_jurado IN ({','.join([':id' + str(i) for i in range(len(ids))])})",
                        {f"id{i}": id_val for i, id_val in enumerate(ids)},
                    )
                conn.commit()
            return True
        except Exception:
            return False

    def _map_row(self, row: tuple) -> Jurado:
        """Map a database row to a Jurado object."""
        return Jurado(
            id=row[0],
            nombre=row[1],
            correo=row[2],
            especialidad=row[3],
            pais_origen=row[4],
            experiencia_anos=row[5],
            tipo_jurado=row[6],
            biografia=row[7],
        )
