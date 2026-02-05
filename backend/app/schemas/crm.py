from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel


class CrmAccionBase(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    observaciones: Optional[str] = None
    resultado: Optional[str] = None
    hora_inicio: Optional[datetime] = None
    hora_fin: Optional[datetime] = None
    duracion_segundos: Optional[int] = None

    crm_actuacion_estadoid: Optional[int] = None
    crm_actuacion_tipoid: Optional[int] = None
    estado: Optional[str] = None
    tipo: Optional[str] = None

    fecha_accion: Optional[datetime] = None
    fecha_vencimiento: Optional[date] = None
    requiere_seguimiento: Optional[bool] = None
    fecha_recordatorio: Optional[datetime] = None

    clienteid: Optional[int] = None
    trabajador_creadorid: Optional[int] = None
    trabajador_asignadoid: Optional[int] = None


class CrmAccionCreate(CrmAccionBase):
    pass


class CrmAccionUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    observaciones: Optional[str] = None
    resultado: Optional[str] = None
    hora_inicio: Optional[datetime] = None
    hora_fin: Optional[datetime] = None
    duracion_segundos: Optional[int] = None

    crm_actuacion_estadoid: Optional[int] = None
    crm_actuacion_tipoid: Optional[int] = None
    estado: Optional[str] = None
    tipo: Optional[str] = None

    fecha_accion: Optional[datetime] = None
    fecha_vencimiento: Optional[date] = None
    requiere_seguimiento: Optional[bool] = None
    fecha_recordatorio: Optional[datetime] = None

    clienteid: Optional[int] = None
    trabajador_creadorid: Optional[int] = None
    trabajador_asignadoid: Optional[int] = None


class CrmAccionOut(CrmAccionBase):
    crm_actuacionid: int
    cliente_nombre: Optional[str] = None


class CrmAccionList(BaseModel):
    data: List[CrmAccionOut]
