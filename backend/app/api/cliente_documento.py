from typing import List

from fastapi import APIRouter, Depends, HTTPException

from backend.app.core.database import get_supabase
from backend.app.schemas.cliente_documento import (
    ClienteDocumentoIn,
    ClienteDocumentoOut,
    DocumentoTipoOut,
)

router = APIRouter(
    prefix="/api/clientes",
    tags=["Clientes"],
)


@router.get("/documentos/tipos", response_model=List[DocumentoTipoOut])
def listar_tipos_documento(supabase=Depends(get_supabase)):
    try:
        rows = (
            supabase.table("documento_tipo")
            .select("documentotipoid, codigo, descripcion")
            .eq("habilitado", True)
            .order("codigo")
            .execute()
            .data
            or []
        )
        return rows
    except Exception:
        return []


@router.get("/{clienteid}/documentos", response_model=List[ClienteDocumentoOut])
def listar_documentos(clienteid: int, supabase=Depends(get_supabase)):
    try:
        rows = (
            supabase.table("cliente_documento")
            .select("cliente_documentoid, url, observaciones, documentotipoid, created_at")
            .eq("clienteid", clienteid)
            .order("cliente_documentoid", desc=True)
            .execute()
            .data
            or []
        )
        return rows
    except Exception:
        return []


@router.post("/{clienteid}/documentos", response_model=ClienteDocumentoOut)
def crear_documento(clienteid: int, data: ClienteDocumentoIn, supabase=Depends(get_supabase)):
    payload = data.dict(exclude_none=True)
    payload["clienteid"] = clienteid
    try:
        res = supabase.table("cliente_documento").insert(payload).execute()
        row = (res.data or [None])[0]
        if not row:
            raise HTTPException(status_code=400, detail="No se pudo crear el documento")
        return row
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
