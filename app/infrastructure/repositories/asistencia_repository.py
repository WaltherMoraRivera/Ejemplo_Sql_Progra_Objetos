from typing import List
from datetime import date
from app.domain.models.asistencia import Asistencia
from app.infrastructure.database.oracle_connection import OracleConnection


class AsistenciaRepository:
    """Repository for gestionar operaciones de Asistencia en la BD."""

    def __init__(self, connection_factory: OracleConnection):
        self._connection_factory = connection_factory

    def get_all(self) -> List[Asistencia]:
        """Obtiene todas las asistencias."""
        try:
            with self._connection_factory.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT id_funcion, id_asistente, entradas, fecha_compra, 
                               metodo_pago, comentarios
                        FROM asistencia
                        ORDER BY fecha_compra DESC
                    """)
                    rows = cursor.fetchall()
            return [self._map_row(row) for row in rows]
        except Exception as e:
            raise Exception(f"Error al obtener asistencias: {str(e)}")

    def get_by_id(self, id_funcion: int, id_asistente: int) -> Asistencia:
        """Obtiene una asistencia por su clave compuesta."""
        try:
            with self._connection_factory.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT id_funcion, id_asistente, entradas, fecha_compra, 
                               metodo_pago, comentarios
                        FROM asistencia
                        WHERE id_funcion = :id_funcion AND id_asistente = :id_asistente
                    """, {"id_funcion": id_funcion, "id_asistente": id_asistente})
                    row = cursor.fetchone()
            return self._map_row(row) if row else None
        except Exception as e:
            raise Exception(f"Error al obtener asistencia: {str(e)}")

    def add(self, asistencia: Asistencia) -> bool:
        """Inserta una nueva asistencia."""
        try:
            with self._connection_factory.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO asistencia 
                        (id_funcion, id_asistente, entradas, fecha_compra, metodo_pago, comentarios)
                        VALUES (:id_funcion, :id_asistente, :entradas, :fecha_compra, :metodo_pago, :comentarios)
                    """, {
                        "id_funcion": asistencia.id_funcion,
                        "id_asistente": asistencia.id_asistente,
                        "entradas": asistencia.entradas,
                        "fecha_compra": asistencia.fecha_compra,
                        "metodo_pago": asistencia.metodo_pago,
                        "comentarios": asistencia.comentarios
                    })
                conn.commit()
            return True
        except Exception as e:
            raise Exception(f"Error al insertar asistencia: {str(e)}")

    def update(self, asistencia: Asistencia) -> bool:
        """Actualiza una asistencia existente."""
        try:
            with self._connection_factory.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE asistencia
                        SET entradas = :entradas, fecha_compra = :fecha_compra, 
                            metodo_pago = :metodo_pago, comentarios = :comentarios
                        WHERE id_funcion = :id_funcion AND id_asistente = :id_asistente
                    """, {
                        "entradas": asistencia.entradas,
                        "fecha_compra": asistencia.fecha_compra,
                        "metodo_pago": asistencia.metodo_pago,
                        "comentarios": asistencia.comentarios,
                        "id_funcion": asistencia.id_funcion,
                        "id_asistente": asistencia.id_asistente
                    })
                conn.commit()
            return True
        except Exception as e:
            raise Exception(f"Error al actualizar asistencia: {str(e)}")

    def delete(self, id_funcion: int, id_asistente: int) -> bool:
        """Elimina una asistencia."""
        try:
            with self._connection_factory.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM asistencia WHERE id_funcion = :id_funcion AND id_asistente = :id_asistente",
                        {"id_funcion": id_funcion, "id_asistente": id_asistente}
                    )
                conn.commit()
            return True
        except Exception as e:
            raise Exception(f"Error al eliminar asistencia: {str(e)}")

    def delete_many(self, ids: List[tuple]) -> bool:
        """Elimina múltiples asistencias (lista de tuplas (id_funcion, id_asistente))."""
        try:
            for id_funcion, id_asistente in ids:
                self.delete(id_funcion, id_asistente)
            return True
        except Exception as e:
            raise Exception(f"Error al eliminar asistencias: {str(e)}")

    def _map_row(self, row: tuple) -> Asistencia:
        """Map a database row to an Asistencia object."""
        return Asistencia(
            id_funcion=row[0],
            id_asistente=row[1],
            entradas=row[2],
            fecha_compra=row[3],
            metodo_pago=row[4],
            comentarios=row[5]
        )
