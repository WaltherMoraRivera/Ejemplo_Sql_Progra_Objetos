from typing import List
from datetime import date

from app.domain.models.evaluacion import Evaluacion
from app.infrastructure.database.oracle_connection import OracleConnection


class EvaluacionRepository:
    """CRUD operations for evaluacion table."""

    def __init__(self, connection_factory: OracleConnection) -> None:
        self._connection_factory = connection_factory
        # cached resolved fecha column name for this repository (None if no date column)
        self._fecha_column_name: str | None = None
        # cached resolved foreign-key column name for the related function/película
        self._fk_column_name: str | None = None

    def get_all(self) -> List[Evaluacion]:
        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                # ensure we know which FK and fecha columns exist
                self._ensure_fk_column(cursor)
                self._ensure_fecha_column(cursor)
                fk_col = self._fk_column_name or 'id_pelicula'
                if self._fecha_column_name:
                    cursor.execute(
                        f"""
                        SELECT id_jurado, {fk_col}, puntuacion, comentario, {self._fecha_column_name}, categoria_evaluada
                        FROM evaluacion
                        ORDER BY id_jurado, {fk_col}
                        """
                    )
                else:
                    cursor.execute(
                        f"""
                        SELECT id_jurado, {fk_col}, puntuacion, comentario, categoria_evaluada
                        FROM evaluacion
                        ORDER BY id_jurado, {fk_col}
                        """
                    )
                rows = cursor.fetchall()
        results: List[Evaluacion] = []
        for r in rows:
            if len(r) == 6:
                results.append(self._map_row_with_fecha(r))
            else:
                results.append(self._map_row_without_fecha(r))
        return results

    def get_by_id(self, id_: int) -> Evaluacion | None:
        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                self._ensure_fk_column(cursor)
                self._ensure_fecha_column(cursor)
                # Expect id_ to be a tuple/list (id_jurado, id_pelicula)
                if not (isinstance(id_, (list, tuple)) and len(id_) == 2):
                    raise ValueError("get_by_id for Evaluacion expects (id_jurado, id_pelicula) tuple")
                id_jurado_val, id_pelicula_val = id_[0], id_[1]
                fk_col = self._fk_column_name or 'id_pelicula'
                if self._fecha_column_name:
                    cursor.execute(
                        f"SELECT id_jurado, {fk_col}, puntuacion, comentario, {self._fecha_column_name}, categoria_evaluada FROM evaluacion WHERE id_jurado = :id_jurado AND {fk_col} = :id_pelicula",
                        {"id_jurado": id_jurado_val, "id_pelicula": id_pelicula_val},
                    )
                else:
                    cursor.execute(
                        f"SELECT id_jurado, {fk_col}, puntuacion, comentario, categoria_evaluada FROM evaluacion WHERE id_jurado = :id_jurado AND {fk_col} = :id_pelicula",
                        {"id_jurado": id_jurado_val, "id_pelicula": id_pelicula_val},
                    )
                row = cursor.fetchone()
        if not row:
            return None
        if len(row) == 6:
            return self._map_row_with_fecha(row)
        return self._map_row_without_fecha(row)

    def add(self, evaluacion: Evaluacion) -> bool:
        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                self._ensure_fk_column(cursor)
                self._ensure_fecha_column(cursor)
                fk_col = self._fk_column_name or 'id_pelicula'
                if self._fecha_column_name:
                    cursor.execute(
                        f"""
                        INSERT INTO evaluacion (id_jurado, {fk_col}, puntuacion, comentario, {self._fecha_column_name}, categoria_evaluada)
                        VALUES (:id_jurado, :id_pelicula, :puntuacion, :comentario, :fecha, :categoria)
                        """,
                        {
                            "id_jurado": evaluacion.id_jurado,
                            "id_pelicula": evaluacion.id_pelicula,
                            "puntuacion": evaluacion.puntuacion,
                            "comentario": evaluacion.comentario,
                            "fecha": evaluacion.fecha,
                            "categoria": getattr(evaluacion, 'categoria_evaluada', 'General'),
                        },
                    )
                else:
                    cursor.execute(
                        f"""
                        INSERT INTO evaluacion (id_jurado, {fk_col}, puntuacion, comentario, categoria_evaluada)
                        VALUES (:id_jurado, :id_pelicula, :puntuacion, :comentario, :categoria)
                        """,
                        {
                            "id_jurado": evaluacion.id_jurado,
                            "id_pelicula": evaluacion.id_pelicula,
                            "puntuacion": evaluacion.puntuacion,
                            "comentario": evaluacion.comentario,
                            "categoria": getattr(evaluacion, 'categoria_evaluada', 'General'),
                        },
                    )
                conn.commit()
        return True

    def update(self, evaluacion: Evaluacion) -> bool:
        try:
            with self._connection_factory.get_connection() as conn:
                with conn.cursor() as cursor:
                    self._ensure_fk_column(cursor)
                    self._ensure_fecha_column(cursor)
                    fk_col = self._fk_column_name or 'id_pelicula'
                    if self._fecha_column_name:
                        cursor.execute(
                            f"""
                            UPDATE evaluacion
                            SET puntuacion = :puntuacion,
                                comentario = :comentario,
                                {self._fecha_column_name} = :fecha,
                                categoria_evaluada = :categoria
                            WHERE id_jurado = :id_jurado AND {fk_col} = :id_pelicula
                            """,
                            {
                                "puntuacion": evaluacion.puntuacion,
                                "comentario": evaluacion.comentario,
                                "fecha": evaluacion.fecha,
                                "categoria": getattr(evaluacion, 'categoria_evaluada', 'General'),
                                "id_jurado": evaluacion.id_jurado,
                                "id_pelicula": evaluacion.id_pelicula,
                            },
                        )
                    else:
                        cursor.execute(
                            f"""
                            UPDATE evaluacion
                            SET puntuacion = :puntuacion,
                                comentario = :comentario,
                                categoria_evaluada = :categoria
                            WHERE id_jurado = :id_jurado AND {fk_col} = :id_pelicula
                            """,
                            {
                                "puntuacion": evaluacion.puntuacion,
                                "comentario": evaluacion.comentario,
                                "categoria": getattr(evaluacion, 'categoria_evaluada', 'General'),
                                "id_jurado": evaluacion.id_jurado,
                                "id_pelicula": evaluacion.id_pelicula,
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
                    # Expect id_ to be a tuple/list (id_jurado, id_pelicula) or an Evaluacion object
                    if isinstance(id_, Evaluacion):
                        id_jurado_val = id_.id_jurado
                        id_pelicula_val = id_.id_pelicula
                    elif isinstance(id_, (list, tuple)) and len(id_) == 2:
                        id_jurado_val, id_pelicula_val = id_[0], id_[1]
                    else:
                        raise ValueError("delete for Evaluacion expects (id_jurado, id_pelicula) tuple or Evaluacion object")
                    fk_col = self._fk_column_name or 'id_pelicula'
                    cursor.execute(f"DELETE FROM evaluacion WHERE id_jurado = :id_jurado AND {fk_col} = :id_pelicula",
                                   {"id_jurado": id_jurado_val, "id_pelicula": id_pelicula_val})
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

    # legacy compat wrapper
    def _map_row(self, row: tuple) -> Evaluacion:
        return self._map_row_with_fecha(row)

    def _map_row_with_fecha(self, row: tuple) -> Evaluacion:
        if row is None:
            return None
        # row: id_jurado, id_pelicula (or fk), puntuacion, comentario, fecha, categoria_evaluada
        return Evaluacion(
            id_jurado=row[0],
            id_pelicula=row[1],
            puntuacion=row[2],
            comentario=row[3] or "",
            fecha=row[4],
            categoria_evaluada=row[5] or "General",
        )

    def _map_row_without_fecha(self, row: tuple) -> Evaluacion:
        if row is None:
            return None
        # row: id_jurado, id_pelicula (or fk), puntuacion, comentario, categoria_evaluada
        return Evaluacion(
            id_jurado=row[0],
            id_pelicula=row[1],
            puntuacion=row[2],
            comentario=row[3] or "",
            fecha=None,
            categoria_evaluada=row[4] or "General",
        )

    def _has_column(self, cursor, column_name: str) -> bool:
        """Check whether the given column exists for the `evaluacion` table in the connected schema."""
        try:
            cursor.execute(
                "SELECT COUNT(*) FROM user_tab_columns WHERE table_name = :table AND column_name = :col",
                {"table": "EVALUACION", "col": column_name.upper()},
            )
            row = cursor.fetchone()
            return bool(row and row[0] > 0)
        except Exception:
            # If metadata query fails, assume column exists to preserve behavior
            return True

    def _ensure_fecha_column(self, cursor) -> None:
        """Resolve and cache the fecha column name for `evaluacion`.

        It checks a list of known candidates and sets `self._fecha_column_name`
        to the first match (upper-case). If none found, sets to None.
        """
        # If already resolved, nothing to do
        if getattr(self, "_fecha_column_name", None) is not None:
            return

        candidates = ["FECHA", "FECHA_EVALUACION", "FECHA_REGISTRO"]
        for cand in candidates:
            try:
                cursor.execute(
                    "SELECT COUNT(*) FROM user_tab_columns WHERE table_name = :table AND column_name = :col",
                    {"table": "EVALUACION", "col": cand},
                )
                row = cursor.fetchone()
                if row and row[0] > 0:
                    self._fecha_column_name = cand
                    return
            except Exception:
                # try next candidate
                continue

        # no candidate found
        self._fecha_column_name = None

    def _ensure_fk_column(self, cursor) -> None:
        """Resolve and cache the FK column name for `evaluacion` (either ID_FUNCION or ID_PELICULA).

        Sets `self._fk_column_name` to the first matching upper-case column name, or None if none found.
        """
        if getattr(self, "_fk_column_name", None) is not None:
            return

        candidates = ["ID_FUNCION", "ID_PELICULA"]
        for cand in candidates:
            try:
                cursor.execute(
                    "SELECT COUNT(*) FROM user_tab_columns WHERE table_name = :table AND column_name = :col",
                    {"table": "EVALUACION", "col": cand},
                )
                row = cursor.fetchone()
                if row and row[0] > 0:
                    self._fk_column_name = cand
                    return
            except Exception:
                continue

        # no candidate found
        self._fk_column_name = None
