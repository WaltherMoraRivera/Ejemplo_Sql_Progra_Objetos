"""Repository layer for Cliente entity."""
from __future__ import annotations

from typing import Iterable, List, Optional, Sequence

import oracledb

from app.domain.models.cliente import Cliente
from app.infrastructure.database.oracle_connection import OracleConnection


class ClienteRepository:
    """Handles CRUD operations over CLIENTE table."""

    def __init__(self, connection_factory: OracleConnection) -> None:
        self._connection_factory = connection_factory

    def get_all(self) -> List[Cliente]:
        """Retrieve every client from the database."""

        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                result_cursor_var = cursor.var(oracledb.DB_TYPE_CURSOR)
                cursor.callproc("SP_GET_CLIENTES", [result_cursor_var])
                result_cursor = result_cursor_var.getvalue()
                try:
                    rows = result_cursor.fetchall()
                finally:
                    result_cursor.close()

        return [self._map_row(row) for row in rows]

    def get_by_id(self, cliente_id: int) -> Optional[Cliente]:
        """Return a client by its identifier."""

        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                result_cursor_var = cursor.var(oracledb.DB_TYPE_CURSOR)
                cursor.callproc("SP_GET_CLIENTE_BY_ID", [cliente_id, result_cursor_var])
                result_cursor = result_cursor_var.getvalue()
                try:
                    row = result_cursor.fetchone()
                finally:
                    result_cursor.close()

        return self._map_row(row) if row else None

    def add(self, cliente: Cliente) -> int:
        """Insert a new client and return its generated ID."""

        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                id_var = cursor.var(int)
                cursor.callproc(
                    "SP_INSERT_CLIENTE",
                    [
                        cliente.rut,
                        cliente.dv,
                        cliente.nombre,
                        cliente.apellido,
                        cliente.fecha_nac,
                        cliente.email,
                        cliente.telefono,
                        cliente.direccion,
                        cliente.estado_cliente,
                        cliente.limite_credito,
                        id_var,
                    ],
                )
                conn.commit()
                return int(id_var.getvalue())

    def update(self, cliente: Cliente) -> None:
        """Update an existing client."""

        if cliente.id is None:
            raise ValueError("El cliente debe tener ID para ser actualizado")

        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.callproc(
                    "SP_UPDATE_CLIENTE",
                    [
                        cliente.id,
                        cliente.rut,
                        cliente.dv,
                        cliente.nombre,
                        cliente.apellido,
                        cliente.fecha_nac,
                        cliente.email,
                        cliente.telefono,
                        cliente.direccion,
                        cliente.estado_cliente,
                        cliente.limite_credito,
                    ],
                )
                conn.commit()

    def delete(self, cliente_id: int) -> None:
        """Delete a single client by ID using a stored procedure."""

        self.delete_many([cliente_id])

    def delete_many(self, cliente_ids: Iterable[int]) -> None:
        """Delete several clients via stored procedure."""

        ids = [cid for cid in cliente_ids if cid is not None]
        if not ids:
            return

        with self._connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                for cliente_id in ids:
                    cursor.callproc("SP_DELETE_CLIENTE", [cliente_id])
                conn.commit()

    @staticmethod
    def _map_row(row: Sequence) -> Cliente:
        """Map a DB row to the domain model."""

        return Cliente(
            id=row[0],
            rut=row[1],
            dv=row[2],
            nombre=row[3],
            apellido=row[4],
            fecha_nac=row[5],
            email=row[6],
            telefono=row[7],
            direccion=row[8],
            estado_cliente=row[9],
            limite_credito=row[10],
        )

