from dataclasses import dataclass
from enum import StrEnum


class Permission(StrEnum):
    SECRET_LOGIN = "login:secret"
    QR_LOGIN = "login:qrcode"


@dataclass(kw_only=True)
class Device:
    ip_addr: str = None
    secret: str
    permissions: list[str]
    id: str = None
    token: str = None
