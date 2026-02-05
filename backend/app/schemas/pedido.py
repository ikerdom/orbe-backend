from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class PedidoOut(BaseModel):
    pedido_id: int
    empresa_id: Optional[int] = None
    clienteid: Optional[int] = None
    cliente: Optional[str] = None
    cif_cliente: Optional[str] = None
    fecha_pedido: Optional[datetime] = None
    pedido_estadoid: Optional[int] = None
    pedido_estado_nombre: Optional[str] = None
    forma_pagoid: Optional[int] = None
    referencia_cliente: Optional[str] = None
    pedido_procedencia: Optional[str] = None
    tipodoc: Optional[str] = None
    pedido_tipo_documentoid: Optional[int] = None
    total: Optional[float] = None


class PedidoListResponse(BaseModel):
    data: List[PedidoOut]
    total: int
    total_pages: int
    page: int
    page_size: int


class PedidoDetalleOut(PedidoOut):
    fecha_completado: Optional[datetime] = None
    total_descuentos: Optional[float] = None
    total_base_gastos_envios: Optional[float] = None
    total_base_imponible: Optional[float] = None
    total_impuestos: Optional[float] = None
    total_recargos: Optional[float] = None
    observaciones: Optional[str] = None
    obs_logistica: Optional[str] = None
    created_on: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_on: Optional[datetime] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PedidoCreateIn(BaseModel):
    empresa_id: Optional[int] = None
    clienteid: Optional[int] = None
    cliente: Optional[str] = None
    cif_cliente: Optional[str] = None
    fecha_pedido: Optional[datetime] = None
    pedido_estadoid: Optional[int] = None
    forma_pagoid: Optional[int] = None
    agente_comercial_origen_id: Optional[int] = None
    referencia_cliente: Optional[str] = None
    pedido_procedencia: Optional[str] = None
    tipodoc: Optional[str] = None
    pedido_tipo_documentoid: Optional[int] = None
    observaciones: Optional[str] = None
    obs_logistica: Optional[str] = None


class PedidoUpdateIn(BaseModel):
    empresa_id: Optional[int] = None
    clienteid: Optional[int] = None
    cliente: Optional[str] = None
    cif_cliente: Optional[str] = None
    fecha_pedido: Optional[datetime] = None
    pedido_estadoid: Optional[int] = None
    forma_pagoid: Optional[int] = None
    agente_comercial_origen_id: Optional[int] = None
    referencia_cliente: Optional[str] = None
    pedido_procedencia: Optional[str] = None
    tipodoc: Optional[str] = None
    pedido_tipo_documentoid: Optional[int] = None
    observaciones: Optional[str] = None
    obs_logistica: Optional[str] = None


class PedidoLineaOut(BaseModel):
    pedido_linea_id: int
    pedido_id: int
    producto_id: Optional[int] = None
    referencia: Optional[str] = None
    nombre_producto: Optional[str] = None
    cantidad: Optional[float] = None
    precio: Optional[float] = None
    descuento_pct: Optional[float] = None
    precio_tras_dto: Optional[float] = None
    subtotal: Optional[float] = None
    tasa_impuesto: Optional[float] = None
    cuota_impuesto: Optional[float] = None
    tasa_recargo: Optional[float] = None
    cuota_recargo: Optional[float] = None
    tasa_gastosenvio: Optional[float] = None
    cuota_gastosenvio: Optional[float] = None
    fecha_limite: Optional[datetime] = None
    fecha_completado: Optional[datetime] = None
    producto_externo: Optional[bool] = None
    producto_observacion: Optional[str] = None
    pedido_estadoid: Optional[int] = None


class PedidoLineaCreate(BaseModel):
    producto_id: Optional[int] = None
    referencia: Optional[str] = None
    nombre_producto: Optional[str] = None
    cantidad: float = 1.0
    precio: float = 0.0
    descuento_pct: Optional[float] = 0.0
    producto_externo: Optional[bool] = None
    producto_observacion: Optional[str] = None


class PedidoTotalesOut(BaseModel):
    pedido_id: int
    total_base_imponible: Optional[float] = None
    total_impuestos: Optional[float] = None
    total_recargos: Optional[float] = None
    total_base_gastos_envios: Optional[float] = None
    total_descuentos: Optional[float] = None
    total: Optional[float] = None


class PedidoObservacionIn(BaseModel):
    tipo: str
    comentario: str
    usuario: str


class PedidoIncidenciaIn(BaseModel):
    tipo: str
    descripcion: str
    responsableid: Optional[int] = None
    estado: Optional[str] = None
    resolucion: Optional[str] = None


class CatalogoItem(BaseModel):
    id: int
    label: str


class PedidoCatalogos(BaseModel):
    clientes: list[CatalogoItem]
    estados: list[CatalogoItem]
    formas_pago: list[CatalogoItem]
    tipos_documento: list[CatalogoItem]
