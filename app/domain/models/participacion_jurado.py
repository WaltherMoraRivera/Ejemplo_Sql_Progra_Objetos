from dataclasses import dataclass


@dataclass
class ParticipacionJurado:
    """Modelo de dominio para Participacion_Jurado."""
    id_jurado: int
    id_funcion: int
    rol_participacion: str = "Evaluador"
    comentarios: str = "Sin comentarios"
