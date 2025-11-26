"""Repository for Funcion (Función)."""
from typing import List, Optional

from app.domain.models.funcion import Funcion
from app.infrastructure.database.oracle_connection import OracleConnection


class FuncionRepository:
    """Repository for FUNCION table."""

    def __init__(self, connection: Optional[OracleConnection] = None):
        """Initialize FuncionRepository.

        Args:
            connection: OracleConnection instance. If None, a new one is created.
        """
        self.connection = connection

    def get_all(self) -> List[Funcion]:
        """Retrieve all functions from FUNCION table.

        Returns:
            List of Funcion objects.
        """
        if not self.connection:
            return []

        query = """
            SELECT id_funcion, fecha, hora, precio_entrada, estado_funcion, observaciones, id_sede
            FROM funcion
            ORDER BY fecha DESC, hora ASC
        """
        try:
            cursor = self.connection.get_connection().cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            cursor.close()

            return [
                Funcion(
                    id=row[0],
                    fecha=str(row[1]) if row[1] else None,
                    hora=row[2],
                    precio_entrada=float(row[3]) if row[3] else None,
                    estado_funcion=row[4],
                    observaciones=row[5],
                    id_sede=row[6],
                )
                for row in rows
            ]
        except Exception as e:
            print(f"Error fetching funciones: {e}")
            return []

    def get_by_id(self, funcion_id: int) -> Optional[Funcion]:
        """Retrieve a single function by ID.

        Args:
            funcion_id: ID of the function.

        Returns:
            Funcion object or None if not found.
        """
        if not self.connection:
            return None

        query = """
            SELECT id_funcion, fecha, hora, precio_entrada, estado_funcion, observaciones, id_sede
            FROM funcion
            WHERE id_funcion = :id
        """
        try:
            cursor = self.connection.get_connection().cursor()
            cursor.execute(query, {"id": funcion_id})
            row = cursor.fetchone()
            cursor.close()

            if row:
                return Funcion(
                    id=row[0],
                    fecha=str(row[1]) if row[1] else None,
                    hora=row[2],
                    precio_entrada=float(row[3]) if row[3] else None,
                    estado_funcion=row[4],
                    observaciones=row[5],
                    id_sede=row[6],
                )
            return None
        except Exception as e:
            print(f"Error fetching funcion by id: {e}")
            return None

    def add(self, funcion: Funcion) -> bool:
        """Add a new function to the database.

        Args:
            funcion: Funcion object to insert.

        Returns:
            True if successful, False otherwise.
        """
        if not self.connection or funcion.id is not None:
            return False

        query = """
            INSERT INTO funcion (fecha, hora, precio_entrada, estado_funcion, observaciones, id_sede)
            VALUES (:fecha, :hora, :precio_entrada, :estado_funcion, :observaciones, :id_sede)
        """
        try:
            conn = self.connection.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                query,
                {
                    "fecha": funcion.fecha,
                    "hora": funcion.hora,
                    "precio_entrada": funcion.precio_entrada,
                    "estado_funcion": funcion.estado_funcion,
                    "observaciones": funcion.observaciones,
                    "id_sede": funcion.id_sede,
                },
            )
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Error adding funcion: {e}")
            return False

    def update(self, funcion: Funcion) -> bool:
        """Update an existing function.

        Args:
            funcion: Funcion object with id set.

        Returns:
            True if successful, False otherwise.
        """
        if not self.connection or funcion.id is None:
            return False

        query = """
            UPDATE funcion
            SET fecha = :fecha, hora = :hora, precio_entrada = :precio_entrada,
                estado_funcion = :estado_funcion, observaciones = :observaciones,
                id_sede = :id_sede
            WHERE id_funcion = :id
        """
        try:
            conn = self.connection.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                query,
                {
                    "fecha": funcion.fecha,
                    "hora": funcion.hora,
                    "precio_entrada": funcion.precio_entrada,
                    "estado_funcion": funcion.estado_funcion,
                    "observaciones": funcion.observaciones,
                    "id_sede": funcion.id_sede,
                    "id": funcion.id,
                },
            )
            conn.commit()
            cursor.close()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating funcion: {e}")
            return False

    def delete(self, funcion_id: int) -> bool:
        """Delete a function by ID.

        Args:
            funcion_id: ID of the function to delete.

        Returns:
            True if successful, False otherwise.
        """
        if not self.connection:
            return False

        query = "DELETE FROM funcion WHERE id_funcion = :id"
        try:
            conn = self.connection.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, {"id": funcion_id})
            conn.commit()
            result = cursor.rowcount > 0
            cursor.close()
            return result
        except Exception as e:
            print(f"Error deleting funcion: {e}")
            return False

    def delete_many(self, funcion_ids: List[int]) -> bool:
        """Delete multiple functions by ID.

        Args:
            funcion_ids: List of function IDs to delete.

        Returns:
            True if all deletions successful, False otherwise.
        """
        if not self.connection or not funcion_ids:
            return False

        try:
            conn = self.connection.get_connection()
            cursor = conn.cursor()
            for funcion_id in funcion_ids:
                cursor.execute("DELETE FROM funcion WHERE id_funcion = :id", {"id": funcion_id})
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Error deleting multiple funciones: {e}")
            return False
