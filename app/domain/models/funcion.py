"""Domain model for Funcion (Función)."""
from typing import Optional


class Funcion:
    """Representa una función (proyección de película en una sede)."""

    def __init__(
        self,
        id: Optional[int] = None,
        fecha: Optional[str] = None,
        hora: Optional[str] = None,
        precio_entrada: Optional[float] = None,
        estado_funcion: Optional[str] = None,
        observaciones: Optional[str] = None,
        id_sede: Optional[int] = None,
    ):
        self.id = id
        self.fecha = fecha
        self.hora = hora
        self.precio_entrada = precio_entrada
        self.estado_funcion = estado_funcion
        self.observaciones = observaciones
        self.id_sede = id_sede

    def __repr__(self) -> str:
        return (
            f"Funcion(id={self.id}, fecha={self.fecha}, hora={self.hora}, "
            f"precio_entrada={self.precio_entrada}, estado={self.estado_funcion}, "
            f"id_sede={self.id_sede})"
        )
