"""Repository layer for Sede entity (wraps `sede` table)."""
from __future__ import annotations

from typing import Iterable, List, Optional, Sequence

from app.domain.models.sede import Sede
from app.infrastructure.database.oracle_connection import OracleConnection


class SedeRepository:
    """Handles CRUD operations over `sede` table."""

    def __init__(self, connection_factory: OracleConnection) -> None:
        self._connection_factory = connection_factory

    def get_all(self) -> List[Sede]:
        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id_sede, nombre, direccion, capacidad_maxima, tipo_sede, id_ciudad, estado "
                    "FROM sede ORDER BY id_sede"
                )
                rows = cursor.fetchall()

        return [self._map_row(row) for row in rows]

    def get_by_id(self, sede_id: int) -> Optional[Sede]:
        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id_sede, nombre, direccion, capacidad_maxima, tipo_sede, id_ciudad, estado "
                    "FROM sede WHERE id_sede = :id",
                    {"id": sede_id},
                )
                row = cursor.fetchone()

        return self._map_row(row) if row else None

    def add(self, sede: Sede) -> int:
        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                id_var = cursor.var(int)
                cursor.execute(
                    "INSERT INTO sede (nombre, direccion, capacidad_maxima, tipo_sede, id_ciudad, estado) "
                    "VALUES (:nombre, :direccion, :capacidad_maxima, :tipo_sede, :id_ciudad, :estado) "
                    "RETURNING id_sede INTO :new_id",
                    {
                        "nombre": sede.nombre,
                        "direccion": sede.direccion,
                        "capacidad_maxima": sede.capacidad_maxima,
                        "tipo_sede": sede.tipo_sede,
                        "id_ciudad": sede.id_ciudad,
                        "estado": sede.estado,
                        "new_id": id_var,
                    },
                )
                conn.commit()
                raw = id_var.getvalue()
                if isinstance(raw, (list, tuple)):
                    raw = raw[0]
                return int(raw)

    def update(self, sede: Sede) -> None:
        if sede.id is None:
            raise ValueError("La sede debe tener ID para ser actualizada")

        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE sede SET nombre = :nombre, direccion = :direccion, capacidad_maxima = :capacidad_maxima, "
                    "tipo_sede = :tipo_sede, id_ciudad = :id_ciudad, estado = :estado WHERE id_sede = :id",
                    {
                        "id": sede.id,
                        "nombre": sede.nombre,
                        "direccion": sede.direccion,
                        "capacidad_maxima": sede.capacidad_maxima,
                        "tipo_sede": sede.tipo_sede,
                        "id_ciudad": sede.id_ciudad,
                        "estado": sede.estado,
                    },
                )
                conn.commit()

    def delete_many(self, sede_ids: Iterable[int]) -> None:
        ids = [sid for sid in sede_ids if sid is not None]
        if not ids:
            return

        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                for sede_id in ids:
                    cursor.execute("DELETE FROM sede WHERE id_sede = :id", {"id": sede_id})
                conn.commit()

    @staticmethod
    def _map_row(row: Sequence) -> Sede:
        return Sede(
            id=row[0],
            nombre=row[1],
            direccion=row[2],
            capacidad_maxima=row[3],
            tipo_sede=row[4],
            id_ciudad=row[5],
            estado=row[6],
        )
