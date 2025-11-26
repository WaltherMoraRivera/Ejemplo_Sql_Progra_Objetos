"""Repository layer for Ciudad entity (wraps `ciudad` table)."""
from __future__ import annotations

from typing import Iterable, List, Optional, Sequence

import oracledb

from app.domain.models.ciudad import Ciudad
from app.infrastructure.database.oracle_connection import OracleConnection


class CiudadRepository:
    """Handles CRUD operations over `ciudad` table."""

    def __init__(self, connection_factory: OracleConnection) -> None:
        self._connection_factory = connection_factory

    def get_all(self) -> List[Ciudad]:
        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id_ciudad, nombre, region, pais, observaciones FROM ciudad ORDER BY id_ciudad"
                )
                rows = cursor.fetchall()

        return [self._map_row(row) for row in rows]

    def get_by_id(self, ciudad_id: int) -> Optional[Ciudad]:
        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id_ciudad, nombre, region, pais, observaciones FROM ciudad WHERE id_ciudad = :id",
                    {"id": ciudad_id},
                )
                row = cursor.fetchone()

        return self._map_row(row) if row else None

    def add(self, ciudad: Ciudad) -> int:
        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                id_var = cursor.var(int)
                cursor.execute(
                    "INSERT INTO ciudad (nombre, region, pais, observaciones) VALUES (:nombre, :region, :pais, :observaciones) RETURNING id_ciudad INTO :new_id",
                    {
                        "nombre": ciudad.nombre,
                        "region": ciudad.region,
                        "pais": ciudad.pais,
                        "observaciones": ciudad.observaciones,
                        "new_id": id_var,
                    },
                )
                conn.commit()
                raw = id_var.getvalue()
                if isinstance(raw, (list, tuple)):
                    raw = raw[0]
                return int(raw)

    def update(self, ciudad: Ciudad) -> None:
        if ciudad.id is None:
            raise ValueError("La ciudad debe tener ID para ser actualizada")

        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE ciudad SET nombre = :nombre, region = :region, pais = :pais, observaciones = :observaciones WHERE id_ciudad = :id",
                    {
                        "id": ciudad.id,
                        "nombre": ciudad.nombre,
                        "region": ciudad.region,
                        "pais": ciudad.pais,
                        "observaciones": ciudad.observaciones,
                    },
                )
                conn.commit()

    def delete_many(self, ciudad_ids: Iterable[int]) -> None:
        ids = [cid for cid in ciudad_ids if cid is not None]
        if not ids:
            return

        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                for ciudad_id in ids:
                    cursor.execute("DELETE FROM ciudad WHERE id_ciudad = :id", {"id": ciudad_id})
                conn.commit()

    @staticmethod
    def _map_row(row: Sequence) -> Ciudad:
        return Ciudad(
            id=row[0],
            nombre=row[1],
            region=row[2],
            pais=row[3],
            observaciones=row[4],
        )
