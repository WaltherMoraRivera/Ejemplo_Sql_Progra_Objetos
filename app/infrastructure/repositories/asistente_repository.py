"""Repository layer for Asistente entity (wraps `asistente` table)."""
from __future__ import annotations

from typing import Iterable, List, Optional, Sequence

import oracledb

from app.domain.models.asistente import Asistente
from app.infrastructure.database.oracle_connection import OracleConnection


class AsistenteRepository:
    """Handles CRUD operations over `asistente` table."""

    def __init__(self, connection_factory: OracleConnection) -> None:
        self._connection_factory = connection_factory

    def get_all(self) -> List[Asistente]:
        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id_asistente, nombre, correo, telefono, edad, ciudad_residencia, tipo_asistente "
                    "FROM asistente ORDER BY id_asistente"
                )
                rows = cursor.fetchall()

        return [self._map_row(row) for row in rows]

    def get_by_id(self, asistente_id: int) -> Optional[Asistente]:
        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id_asistente, nombre, correo, telefono, edad, ciudad_residencia, tipo_asistente "
                    "FROM asistente WHERE id_asistente = :id",
                    {"id": asistente_id},
                )
                row = cursor.fetchone()

        return self._map_row(row) if row else None

    def add(self, asistente: Asistente) -> int:
        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                id_var = cursor.var(int)
                cursor.execute(
                    "INSERT INTO asistente (nombre, correo, telefono, edad, ciudad_residencia, tipo_asistente) "
                    "VALUES (:nombre, :correo, :telefono, :edad, :ciudad_residencia, :tipo_asistente) "
                    "RETURNING id_asistente INTO :new_id",
                    {
                        "nombre": asistente.nombre,
                        "correo": asistente.correo,
                        "telefono": asistente.telefono,
                        "edad": asistente.edad,
                        "ciudad_residencia": asistente.ciudad_residencia,
                        "tipo_asistente": asistente.tipo_asistente,
                        "new_id": id_var,
                    },
                )
                conn.commit()
                # `id_var.getvalue()` can return a single value or a sequence
                raw = id_var.getvalue()
                if isinstance(raw, (list, tuple)):
                    raw = raw[0]
                return int(raw)

    def update(self, asistente: Asistente) -> None:
        if asistente.id is None:
            raise ValueError("El asistente debe tener ID para ser actualizado")

        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE asistente SET nombre = :nombre, correo = :correo, telefono = :telefono, "
                    "edad = :edad, ciudad_residencia = :ciudad_residencia, tipo_asistente = :tipo_asistente "
                    "WHERE id_asistente = :id",
                    {
                        "id": asistente.id,
                        "nombre": asistente.nombre,
                        "correo": asistente.correo,
                        "telefono": asistente.telefono,
                        "edad": asistente.edad,
                        "ciudad_residencia": asistente.ciudad_residencia,
                        "tipo_asistente": asistente.tipo_asistente,
                    },
                )
                conn.commit()

    def delete_many(self, asistente_ids: Iterable[int]) -> None:
        ids = [aid for aid in asistente_ids if aid is not None]
        if not ids:
            return

        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                for asistente_id in ids:
                    cursor.execute("DELETE FROM asistente WHERE id_asistente = :id", {"id": asistente_id})
                conn.commit()

    @staticmethod
    def _map_row(row: Sequence) -> Asistente:
        return Asistente(
            id=row[0],
            nombre=row[1],
            correo=row[2],
            telefono=row[3],
            edad=row[4],
            ciudad_residencia=row[5],
            tipo_asistente=row[6],
        )
