"""Domain model for Cliente entity."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(slots=True)
class Cliente:
    """Represents a client record stored in Oracle DB."""

    id: Optional[int]
    rut: str
    dv: str
    nombre: str
    apellido: str
    fecha_nac: Optional[date]
    email: str
    telefono: str
    direccion: str
    estado_cliente: str
    limite_credito: Optional[float]

