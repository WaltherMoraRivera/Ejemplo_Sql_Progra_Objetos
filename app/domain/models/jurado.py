from dataclasses import dataclass


@dataclass
class Jurado:
    """Modelo de dominio para Jurado."""
    nombre: str
    correo: str
    especialidad: str
    pais_origen: str = "Chile"
    experiencia_anos: int = 0
    tipo_jurado: str = "Invitado"
    biografia: str = "Sin biografia disponible"
    id: int = None
