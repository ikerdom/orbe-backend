from typing import Optional

from fastapi import APIRouter, Depends, Query

from backend.app.core.database import get_supabase

router = APIRouter(prefix="/api", tags=["Albaranes"])


@router.get("/clientes/{clienteid}/albaranes")
def listar_albaranes(
    clienteid: int,
    q: Optional[str] = Query(None),
    fecha_desde: Optional[str] = Query(None),
    fecha_hasta: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    tipo_documento: Optional[str] = Query(None),
    ordenar_por: str = Query("fecha_albaran"),
    page: int = Query(1, ge=1),
    page_size: int = Query(30, ge=1, le=200),
    supabase=Depends(get_supabase),
):
    query = (
        supabase.table("albaran")
        .select(
            "albaran_id, numero, serie, estado, fecha_albaran, total_general, "
            "empresa_id, empresa(empresa_nombre), forma_pagoid, forma_pago(forma_pago_nombre), "
            "albaran_estadoid, albaran_estado(estado), tipo_documento, cliente, cif_cliente, "
            "cuenta_cliente_proveedor",
            count="exact",
        )
        .eq("clienteid", int(clienteid))
        .order(ordenar_por, desc=True)
    )

    if q:
        q_safe = q.replace(",", " ")
        if q_safe.isdigit():
            query = query.or_(
                f"numero.eq.{q_safe},serie.ilike.%{q_safe}%,"
                f"estado.ilike.%{q_safe}%,forma_de_pago.ilike.%{q_safe}%,"
                f"cliente.ilike.%{q_safe}%,cif_cliente.ilike.%{q_safe}%,"
                f"cuenta_cliente_proveedor.ilike.%{q_safe}%"
            )
        else:
            query = query.or_(
                f"serie.ilike.%{q_safe}%,estado.ilike.%{q_safe}%,"
                f"forma_de_pago.ilike.%{q_safe}%,cliente.ilike.%{q_safe}%,"
                f"cif_cliente.ilike.%{q_safe}%,cuenta_cliente_proveedor.ilike.%{q_safe}%"
            )

    if fecha_desde:
        query = query.gte("fecha_albaran", str(fecha_desde))
    if fecha_hasta:
        query = query.lte("fecha_albaran", str(fecha_hasta))
    if estado:
        query = query.ilike("estado", f"%{estado}%")
    if tipo_documento:
        query = query.ilike("tipo_documento", f"%{tipo_documento}%")

    start = (page - 1) * page_size
    end = start + page_size - 1
    res = query.range(start, end).execute()
    return {"data": res.data or [], "total": res.count or 0, "page": page, "page_size": page_size}


@router.get("/albaranes/{albaran_id}/lineas")
def listar_albaran_lineas(
    albaran_id: int,
    q: Optional[str] = Query(None),
    supabase=Depends(get_supabase),
):
    res = (
        supabase.table("albaran_linea")
        .select(
            "linea_id, albaran_id, descripcion, cantidad, precio, descuento_pct, "
            "precio_tras_dto, subtotal, tasa_impuesto, cuota_impuesto, tasa_recargo, "
            "cuota_recargo, producto_id_origen, producto_ref_origen, idproducto, producto_id"
        )
        .eq("albaran_id", albaran_id)
        .order("linea_id")
        .execute()
    )
    lineas = res.data or []
    if q:
        q_low = q.lower()

        def _match(linea):
            for k in ["descripcion", "producto_ref_origen", "producto_id_origen", "idproducto", "producto_id"]:
                if q_low in str(linea.get(k, "")).lower():
                    return True
            return False

        lineas = [l for l in lineas if _match(l)]
    return lineas
