"""Oracle Autonomous Database connection helper."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

import oracledb


class OracleConnection:
    """Encapsulates connection management to Oracle Autonomous Database."""

    def __init__(
        self,
        user: str,
        password: str,
        dsn: str,
        config_dir: Optional[str] = None,
        wallet_password: Optional[str] = None,
    ) -> None:
        self._user = user
        self._password = password
        self._dsn = dsn
        self._config_dir = config_dir
        self._wallet_password = wallet_password

    def get_connection(self) -> oracledb.Connection:
        """Return a new Oracle connection instance.

        Raises:
            oracledb.Error: If the connection cannot be established.
        """

        connection_kwargs: Dict[str, Optional[str]] = {
            "user": self._user,
            "password": self._password,
            "dsn": self._dsn,
        }
        if self._config_dir:
            connection_kwargs["config_dir"] = self._config_dir
            connection_kwargs["wallet_location"] = self._config_dir
        if self._wallet_password:
            connection_kwargs["wallet_password"] = self._wallet_password

        try:
            db = oracledb.connect(**connection_kwargs)
            return db
        except oracledb.Error as exc:  # pragma: no cover - requires DB
            print(f"Error connecting to Oracle DB: {exc}")
            raise ConnectionError("No se pudo conectar a Oracle Autonomous Database") from exc
        
    @classmethod
    def from_settings(cls, settings_path: Path) -> "OracleConnection":
        """Create an instance from a JSON settings file."""

        with settings_path.open("r", encoding="utf-8") as file:
            data: Dict[str, Any] = json.load(file)

        db_conf: Dict[str, Optional[str]] = data.get("database", {})
        user = db_conf.get("user") or ""
        password = db_conf.get("password") or ""
        dsn = db_conf.get("dsn") or ""
        wallet_dir = db_conf.get("wallet_dir")
        wallet_password = db_conf.get("wallet_password")

        resolved_wallet_dir: Optional[str] = None
        if wallet_dir:
            wallet_path = Path(wallet_dir)
            if not wallet_path.is_absolute():
                config_relative = (settings_path.parent / wallet_path).resolve()
                project_relative = (settings_path.parent.parent / wallet_path).resolve()
                for candidate in (config_relative, project_relative):
                    if candidate.exists():
                        wallet_path = candidate
                        break
                else:
                    wallet_path = config_relative
            if not wallet_path.exists():
                raise FileNotFoundError(
                    f"La ruta del wallet configurada no existe: {wallet_path}"
                )
            resolved_wallet_dir = str(wallet_path)

        return cls(
            user=user,
            password=password,
            dsn=dsn,
            config_dir=resolved_wallet_dir,
            wallet_password=wallet_password or None,
        )
