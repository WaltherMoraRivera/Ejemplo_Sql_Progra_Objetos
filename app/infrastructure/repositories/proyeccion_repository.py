from typing import List

from app.domain.models.proyeccion import Proyeccion
from app.infrastructure.database.oracle_connection import OracleConnection


class ProyeccionRepository:
    """CRUD operations for proyeccion table (composite PK: id_funcion, id_pelicula)."""

    def __init__(self, connection_factory: OracleConnection) -> None:
        self._connection_factory = connection_factory

    def get_all(self) -> List[Proyeccion]:
        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id_funcion, id_pelicula, orden_proyeccion, comentarios
                    FROM proyeccion
                    ORDER BY id_funcion, id_pelicula
                    """
                )
                rows = cursor.fetchall()

        return [self._map_row(r) for r in rows]

    def get_by_id(self, id_) -> Proyeccion | None:
        # id_ expected to be (id_funcion, id_pelicula)
        if not (isinstance(id_, (list, tuple)) and len(id_) == 2):
            raise ValueError("get_by_id for Proyeccion expects (id_funcion, id_pelicula) tuple")
        id_func, id_pel = id_[0], id_[1]
        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id_funcion, id_pelicula, orden_proyeccion, comentarios FROM proyeccion WHERE id_funcion = :idf AND id_pelicula = :idp",
                    {"idf": id_func, "idp": id_pel},
                )
                row = cursor.fetchone()
        return self._map_row(row) if row else None

    def add(self, proyeccion: Proyeccion) -> bool:
        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO proyeccion (id_funcion, id_pelicula, orden_proyeccion, comentarios)
                    VALUES (:id_funcion, :id_pelicula, :orden_proyeccion, :comentarios)
                    """,
                    {
                        "id_funcion": proyeccion.id_funcion,
                        "id_pelicula": proyeccion.id_pelicula,
                        "orden_proyeccion": proyeccion.orden_proyeccion,
                        "comentarios": proyeccion.comentarios,
                    },
                )
                conn.commit()
        return True

    def update(self, proyeccion: Proyeccion) -> bool:
        try:
            with self._connection_factory.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE proyeccion
                        SET orden_proyeccion = :orden_proyeccion,
                            comentarios = :comentarios
                        WHERE id_funcion = :id_funcion AND id_pelicula = :id_pelicula
                        """,
                        {
                            "orden_proyeccion": proyeccion.orden_proyeccion,
                            "comentarios": proyeccion.comentarios,
                            "id_funcion": proyeccion.id_funcion,
                            "id_pelicula": proyeccion.id_pelicula,
                        },
                    )
                conn.commit()
            return True
        except Exception:
            return False

    def delete(self, id_) -> bool:
        try:
            # id_ may be a Proyeccion or tuple
            if isinstance(id_, Proyeccion):
                id_func = id_.id_funcion
                id_pel = id_.id_pelicula
            elif isinstance(id_, (list, tuple)) and len(id_) == 2:
                id_func, id_pel = id_[0], id_[1]
            else:
                raise ValueError("delete for Proyeccion expects (id_funcion, id_pelicula) tuple or Proyeccion object")
            with self._connection_factory.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM proyeccion WHERE id_funcion = :idf AND id_pelicula = :idp", {"idf": id_func, "idp": id_pel})
                conn.commit()
            return True
        except Exception:
            return False

    def delete_many(self, ids: List[tuple]) -> bool:
        if not ids:
            return False
        try:
            for _id in ids:
                self.delete(_id)
            return True
        except Exception:
            return False

    def _map_row(self, row: tuple) -> Proyeccion:
        if row is None:
            return None
        return Proyeccion(
            id_funcion=row[0],
            id_pelicula=row[1],
            orden_proyeccion=row[2] or 1,
            comentarios=row[3] or "",
        )
