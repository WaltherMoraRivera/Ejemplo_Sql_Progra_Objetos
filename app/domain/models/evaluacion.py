from dataclasses import dataclass
from datetime import date


@dataclass
class Evaluacion:
    # Table uses a composite primary key: (id_jurado, id_pelicula)
    id_jurado: int = 0
    id_pelicula: int = 0
    puntuacion: int = 0
    comentario: str = ""
    fecha: date | None = None
    categoria_evaluada: str = "General"
