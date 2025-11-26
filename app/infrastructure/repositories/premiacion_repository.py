from typing import List
from datetime import date

from app.domain.models.premiacion import Premiacion
from app.infrastructure.database.oracle_connection import OracleConnection


class PremiacionRepository:
    """CRUD operations for premiacion table."""

    def __init__(self, connection_factory: OracleConnection) -> None:
        self._connection_factory = connection_factory

    def get_all(self) -> List[Premiacion]:
        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id_premio, id_pelicula, categoria, edicion, posicion, descripcion, fecha_premiacion
                    FROM premiacion
                    ORDER BY id_premio
                    """
                )
                rows = cursor.fetchall()

        results: List[Premiacion] = []
        for r in rows:
            results.append(self._map_row(r))
        return results

    def get_by_id(self, id_: int) -> Premiacion | None:
        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id_premio, id_pelicula, categoria, edicion, posicion, descripcion, fecha_premiacion FROM premiacion WHERE id_premio = :id",
                    {"id": id_},
                )
                row = cursor.fetchone()
        if not row:
            return None
        return self._map_row(row)

    def add(self, premiacion: Premiacion) -> bool:
        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO premiacion (id_pelicula, categoria, edicion, posicion, descripcion, fecha_premiacion)
                    VALUES (:id_pelicula, :categoria, :edicion, :posicion, :descripcion, :fecha_premiacion)
                    """,
                    {
                        "id_pelicula": premiacion.id_pelicula,
                        "categoria": premiacion.categoria,
                        "edicion": premiacion.edicion,
                        "posicion": premiacion.posicion,
                        "descripcion": premiacion.descripcion,
                        "fecha_premiacion": premiacion.fecha_premiacion,
                    },
                )
                conn.commit()
        return True

    def update(self, premiacion: Premiacion) -> bool:
        try:
            with self._connection_factory.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE premiacion
                        SET id_pelicula = :id_pelicula,
                            categoria = :categoria,
                            edicion = :edicion,
                            posicion = :posicion,
                            descripcion = :descripcion,
                            fecha_premiacion = :fecha_premiacion
                        WHERE id_premio = :id_premio
                        """,
                        {
                            "id_pelicula": premiacion.id_pelicula,
                            "categoria": premiacion.categoria,
                            "edicion": premiacion.edicion,
                            "posicion": premiacion.posicion,
                            "descripcion": premiacion.descripcion,
                            "fecha_premiacion": premiacion.fecha_premiacion,
                            "id_premio": premiacion.id_premio,
                        },
                    )
                conn.commit()
            return True
        except Exception:
            return False

    def delete(self, id_: int) -> bool:
        try:
            with self._connection_factory.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM premiacion WHERE id_premio = :id", {"id": id_})
                conn.commit()
            return True
        except Exception:
            return False

    def delete_many(self, ids: List[int]) -> bool:
        if not ids:
            return False
        try:
            for _id in ids:
                self.delete(_id)
            return True
        except Exception:
            return False

    def _map_row(self, row: tuple) -> Premiacion:
        if row is None:
            return None
        return Premiacion(
            id_premio=row[0],
            id_pelicula=row[1],
            categoria=row[2] or "",
            edicion=row[3],
            posicion=row[4],
            descripcion=row[5] or "",
            fecha_premiacion=row[6],
        )
