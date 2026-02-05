from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query

from backend.app.core.database import get_supabase

router = APIRouter(prefix="/api/crm/alertas", tags=["CRM"])


def _estado_id(supa, nombre: str):
    try:
        row = (
            supa.table("crm_actuacion_estado")
            .select("crm_actuacion_estadoid")
            .eq("estado", nombre)
            .single()
            .execute()
            .data
        )
    except Exception:
        row = None
    return row.get("crm_actuacion_estadoid") if row else None


def _get_alertas_trabajador(supa, trabajadorid: int) -> dict:
    if not trabajadorid:
        return {
            "total": 0,
            "criticas": [],
            "hoy": [],
            "proximas": [],
            "seguimiento": [],
        }

    hoy = date.today()
    maniana = hoy + timedelta(days=1)
    sem = hoy + timedelta(days=7)
    estado_id = _estado_id(supa, "Pendiente")
    if not estado_id:
        return {
            "total": 0,
            "criticas": [],
            "hoy": [],
            "proximas": [],
            "seguimiento": [],
        }

    try:
        criticas = (
            supa.table("crm_actuacion")
            .select(
                "crm_actuacionid, clienteid, crm_actuacion_estado(estado), fecha_vencimiento, "
                "fecha_accion, titulo, resultado, requiere_seguimiento, fecha_recordatorio, "
                "cliente (clienteid, razonsocial, nombre)"
            )
            .eq("trabajador_asignadoid", trabajadorid)
            .eq("crm_actuacion_estadoid", estado_id)
            .or_(
                f"fecha_vencimiento.lt.{hoy.isoformat()},"
                f"and(requiere_seguimiento.eq.true,fecha_recordatorio.lt.{hoy.isoformat()})"
            )
            .order("fecha_vencimiento")
            .limit(100)
            .execute()
            .data
            or []
        )
    except Exception:
        criticas = []

    try:
        hoy_list = (
            supa.table("crm_actuacion")
            .select(
                "crm_actuacionid, clienteid, crm_actuacion_estado(estado), fecha_vencimiento, "
                "fecha_accion, titulo, resultado, requiere_seguimiento, fecha_recordatorio, "
                "cliente (clienteid, razonsocial, nombre)"
            )
            .eq("trabajador_asignadoid", trabajadorid)
            .eq("crm_actuacion_estadoid", estado_id)
            .or_(
                f"fecha_vencimiento.eq.{hoy.isoformat()},"
                f"fecha_recordatorio.eq.{hoy.isoformat()}"
            )
            .order("fecha_vencimiento")
            .limit(100)
            .execute()
            .data
            or []
        )
    except Exception:
        hoy_list = []

    try:
        proximas = (
            supa.table("crm_actuacion")
            .select(
                "crm_actuacionid, clienteid, crm_actuacion_estado(estado), fecha_vencimiento, "
                "fecha_accion, titulo, resultado, requiere_seguimiento, fecha_recordatorio, "
                "cliente (clienteid, razonsocial, nombre)"
            )
            .eq("trabajador_asignadoid", trabajadorid)
            .eq("crm_actuacion_estadoid", estado_id)
            .gte("fecha_vencimiento", maniana.isoformat())
            .lte("fecha_vencimiento", sem.isoformat())
            .order("fecha_vencimiento")
            .limit(100)
            .execute()
            .data
            or []
        )
    except Exception:
        proximas = []

    try:
        seguimiento = (
            supa.table("crm_actuacion")
            .select(
                "crm_actuacionid, clienteid, crm_actuacion_estado(estado), fecha_vencimiento, "
                "fecha_accion, titulo, resultado, requiere_seguimiento, fecha_recordatorio, "
                "cliente (clienteid, razonsocial, nombre)"
            )
            .eq("trabajador_asignadoid", trabajadorid)
            .eq("crm_actuacion_estadoid", estado_id)
            .eq("requiere_seguimiento", True)
            .order("fecha_recordatorio")
            .limit(100)
            .execute()
            .data
            or []
        )
    except Exception:
        seguimiento = []

    ids_totales = set()
    for lista in (criticas, hoy_list, proximas, seguimiento):
        for a in lista:
            ids_totales.add(a.get("crm_actuacionid"))

    return {
        "total": len(ids_totales),
        "criticas": criticas,
        "hoy": hoy_list,
        "proximas": proximas,
        "seguimiento": seguimiento,
    }


def _get_alertas_globales(supa) -> dict:
    hoy = date.today()
    try:
        estado_id = _estado_id(supa, "Pendiente")
        criticas = (
            supa.table("crm_actuacion")
            .select(
                "crm_actuacionid, clienteid, trabajador_asignadoid, crm_actuacion_estado(estado), fecha_vencimiento, "
                "fecha_accion, titulo, resultado, requiere_seguimiento, fecha_recordatorio, "
                "cliente (clienteid, razonsocial, nombre), "
                "trabajador!crm_actuacion_trabajador_asignadoid_fkey (trabajadorid, nombre, apellidos)"
            )
            .eq("crm_actuacion_estadoid", estado_id)
            .or_(
                f"fecha_vencimiento.lt.{hoy.isoformat()},"
                f"and(requiere_seguimiento.eq.true,fecha_recordatorio.lt.{hoy.isoformat()})"
            )
            .order("fecha_vencimiento")
            .limit(200)
            .execute()
            .data
            or []
        )
    except Exception:
        criticas = []

    return {
        "total": len(criticas),
        "criticas": criticas,
    }


@router.get("")
def alertas_trabajador(
    trabajadorid: int = Query(..., ge=1),
    supabase=Depends(get_supabase),
):
    return _get_alertas_trabajador(supabase, trabajadorid)


@router.get("/globales")
def alertas_globales(supabase=Depends(get_supabase)):
    return _get_alertas_globales(supabase)
