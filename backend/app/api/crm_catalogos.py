from fastapi import APIRouter, Depends

from backend.app.core.database import get_supabase

router = APIRouter(prefix="/api/crm", tags=["CRM"])


@router.get("/catalogos")
def catalogos_crm(supabase=Depends(get_supabase)):
    try:
        estados = (
            supabase.table("crm_actuacion_estado")
            .select("crm_actuacion_estadoid, estado")
            .order("crm_actuacion_estadoid")
            .execute()
            .data
            or []
        )
    except Exception:
        estados = []
    try:
        tipos = (
            supabase.table("crm_actuacion_tipo")
            .select("crm_actuacion_tipoid, tipo")
            .order("crm_actuacion_tipoid")
            .execute()
            .data
            or []
        )
    except Exception:
        tipos = []
    return {"estados": estados, "tipos": tipos}
