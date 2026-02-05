from typing import Optional

from pydantic import BaseModel


class DocumentoTipoOut(BaseModel):
    documentotipoid: int
    codigo: Optional[str] = None
    descripcion: Optional[str] = None


class ClienteDocumentoIn(BaseModel):
    documentotipoid: int
    url: str
    observaciones: Optional[str] = None


class ClienteDocumentoOut(BaseModel):
    cliente_documentoid: int
    documentotipoid: int
    url: str
    observaciones: Optional[str] = None
    created_at: Optional[str] = None
