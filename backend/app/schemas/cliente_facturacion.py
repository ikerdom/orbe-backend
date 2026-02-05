from typing import Optional

from pydantic import BaseModel


class FormaPagoOut(BaseModel):
    formapagoid: int
    nombre: Optional[str] = None


class ClienteBancoIn(BaseModel):
    iban: Optional[str] = None
    banco: Optional[str] = None
    sucursal: Optional[str] = None
    observaciones: Optional[str] = None


class ClienteTarjetaIn(BaseModel):
    numero_tarjeta: Optional[str] = None
    caducidad: Optional[str] = None
    cvv: Optional[str] = None
    titular: Optional[str] = None


class ClienteFacturacionIn(BaseModel):
    formapagoid: Optional[int] = None
    banco: Optional[ClienteBancoIn] = None
    tarjeta: Optional[ClienteTarjetaIn] = None


class ClienteFacturacionOut(BaseModel):
    clienteid: int
    formapagoid: Optional[int] = None
    perfil_completo: Optional[bool] = None
    banco: Optional[dict] = None
    tarjeta: Optional[dict] = None
