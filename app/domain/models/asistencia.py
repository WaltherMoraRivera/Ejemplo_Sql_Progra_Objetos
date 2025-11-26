from dataclasses import dataclass
from datetime import date


@dataclass
class Asistencia:
    """Modelo de dominio para Asistencia."""
    id_funcion: int
    id_asistente: int
    entradas: int = 1
    fecha_compra: date = None
    metodo_pago: str = "Efectivo"
    comentarios: str = "Sin comentarios"

    def __post_init__(self):
        if self.fecha_compra is None:
            self.fecha_compra = date.today()
