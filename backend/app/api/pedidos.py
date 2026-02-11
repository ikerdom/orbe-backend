from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.app.core.database import get_supabase
from backend.app.repositories.pedidos_repo import PedidosRepository
from backend.app.schemas.pedido import (
    PedidoListResponse,
    PedidoDetalleOut,
    PedidoLineaOut,
    PedidoTotalesOut,
    PedidoObservacionIn,
    PedidoCreateIn,
    PedidoUpdateIn,
    PedidoLineaCreate,
    PedidoCatalogos,
    PedidoIncidenciaIn,
)
from backend.app.services.pedidos_service import PedidosService

router = APIRouter(prefix="/api/pedidos", tags=["Pedidos"])


def get_service(supabase=Depends(get_supabase)) -> PedidosService:
    repo = PedidosRepository(supabase)
    return PedidosService(repo)


@router.get("", response_model=PedidoListResponse)
def listar_pedidos(
    q: Optional[str] = Query(None),
    clienteid: Optional[int] = Query(None),
    estadoid: Optional[int] = Query(None),
    forma_pagoid: Optional[int] = Query(None),
    pedido_procedencia: Optional[str] = Query(None),
    pedido_estado_nombre: Optional[str] = Query(None),
    tipodoc: Optional[str] = Query(None),
    pedido_tipo_documentoid: Optional[int] = Query(None),
    referencia_cliente: Optional[str] = Query(None),
    cif_cliente: Optional[str] = Query(None),
    total_min: Optional[float] = Query(None),
    total_max: Optional[float] = Query(None),
    fecha_desde: Optional[str] = Query(None),
    fecha_hasta: Optional[str] = Query(None),
    fecha_completado_desde: Optional[str] = Query(None),
    fecha_completado_hasta: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(30, ge=1, le=100),
    service: PedidosService = Depends(get_service),
):
    filtros = {
        "q": q,
        "clienteid": clienteid,
        "estadoid": estadoid,
        "forma_pagoid": forma_pagoid,
        "pedido_procedencia": pedido_procedencia,
        "pedido_estado_nombre": pedido_estado_nombre,
        "tipodoc": tipodoc,
        "pedido_tipo_documentoid": pedido_tipo_documentoid,
        "referencia_cliente": referencia_cliente,
        "cif_cliente": cif_cliente,
        "total_min": total_min,
        "total_max": total_max,
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
        "fecha_completado_desde": fecha_completado_desde,
        "fecha_completado_hasta": fecha_completado_hasta,
    }
    return service.listar(filtros, page, page_size)


@router.get("/catalogos", response_model=PedidoCatalogos)
def catalogos_pedidos(service: PedidosService = Depends(get_service)):
    return service.catalogos()


@router.post("", response_model=PedidoDetalleOut)
def crear_pedido(body: PedidoCreateIn, service: PedidosService = Depends(get_service)):
    return service.crear(body)


@router.put("/{pedidoid}", response_model=PedidoDetalleOut)
def actualizar_pedido(pedidoid: int, body: PedidoUpdateIn, service: PedidosService = Depends(get_service)):
    try:
        return service.actualizar(pedidoid, body)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{pedidoid}")
def borrar_pedido(pedidoid: int, service: PedidosService = Depends(get_service)):
    service.borrar(pedidoid)
    return {"ok": True}


@router.get("/{pedidoid}", response_model=PedidoDetalleOut)
def obtener_pedido(pedidoid: int, service: PedidosService = Depends(get_service)):
    try:
        return service.detalle(pedidoid)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{pedidoid}/lineas", response_model=list[PedidoLineaOut])
def lineas_pedido(pedidoid: int, service: PedidosService = Depends(get_service)):
    return service.lineas(pedidoid)


@router.post("/{pedidoid}/lineas", response_model=int)
def agregar_linea_pedido(pedidoid: int, body: PedidoLineaCreate, service: PedidosService = Depends(get_service)):
    return service.agregar_linea(pedidoid, body)


@router.delete("/{pedidoid}/lineas/{detalleid}")
def borrar_linea_pedido(pedidoid: int, detalleid: int, service: PedidosService = Depends(get_service)):
    service.borrar_linea(pedidoid, detalleid)
    return {"ok": True}


@router.get("/{pedidoid}/totales", response_model=Optional[PedidoTotalesOut])
def totales_pedido(pedidoid: int, service: PedidosService = Depends(get_service)):
    return service.totales(pedidoid)


@router.post("/{pedidoid}/recalcular-totales", response_model=PedidoTotalesOut)
def recalcular_totales(
    pedidoid: int,
    use_iva: bool = Query(True),
    gastos_envio: float = Query(0.0),
    envio_sin_cargo: bool = Query(False),
    service: PedidosService = Depends(get_service),
):
    try:
        return service.recalcular_totales(pedidoid, use_iva=use_iva, gastos_envio=gastos_envio, envio_sin_cargo=envio_sin_cargo)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{pedidoid}/observaciones")
def listar_observaciones(pedidoid: int, service: PedidosService = Depends(get_service)):
    return service.observaciones(pedidoid)


@router.post("/{pedidoid}/observaciones")
def crear_observacion(
    pedidoid: int,
    body: PedidoObservacionIn,
    service: PedidosService = Depends(get_service),
):
    service.crear_observacion(pedidoid, body, usuario=body.usuario or "sistema")
    return {"ok": True}


@router.get("/{pedidoid}/incidencias")
def listar_incidencias(pedidoid: int, service: PedidosService = Depends(get_service)):
    return service.incidencias(pedidoid)


@router.post("/{pedidoid}/incidencias")
def crear_incidencia(
    pedidoid: int,
    body: PedidoIncidenciaIn,
    service: PedidosService = Depends(get_service),
):
    try:
        return service.crear_incidencia(pedidoid, body)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
