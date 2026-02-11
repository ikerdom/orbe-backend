import math
from datetime import datetime
from typing import Optional

from backend.app.repositories.pedidos_repo import PedidosRepository
from backend.app.schemas.pedido import (
    PedidoListResponse,
    PedidoOut,
    PedidoDetalleOut,
    PedidoLineaOut,
    PedidoTotalesOut,
    PedidoObservacionIn,
    PedidoCreateIn,
    PedidoUpdateIn,
    PedidoLineaCreate,
    PedidoCatalogos,
    CatalogoItem,
    PedidoIncidenciaIn,
)


class PedidosService:
    def __init__(self, repo: PedidosRepository):
        self.repo = repo

    # -----------------------------
    # Listar
    # -----------------------------
    def listar(
        self,
        filtros: dict,
        page: int,
        page_size: int,
    ) -> PedidoListResponse:
        rows, total = self.repo.listar(filtros, page, page_size)
        data = [PedidoOut(**r) for r in rows]
        total_pages = max(1, math.ceil((total or 0) / page_size))
        return PedidoListResponse(
            data=data,
            total=total,
            total_pages=total_pages,
            page=page,
            page_size=page_size,
        )

    # -----------------------------
    # Detalle
    # -----------------------------
    def detalle(self, pedidoid: int) -> PedidoDetalleOut:
        ped = self.repo.obtener(pedidoid)
        if not ped:
            raise ValueError("Pedido no encontrado")
        return PedidoDetalleOut(**ped)

    def crear(self, data: PedidoCreateIn) -> PedidoDetalleOut:
        payload = data.dict(exclude_none=True)
        payload.setdefault("fecha_pedido", datetime.now().isoformat())
        created = self.repo.crear(payload)
        if not created:
            raise RuntimeError("No se pudo crear el pedido")
        return PedidoDetalleOut(**created)

    def actualizar(self, pedidoid: int, data: PedidoUpdateIn) -> PedidoDetalleOut:
        if not self.repo.obtener(pedidoid):
            raise ValueError("Pedido no encontrado")
        self.repo.actualizar(pedidoid, data.dict(exclude_none=True))
        nuevo = self.repo.obtener(pedidoid)
        return PedidoDetalleOut(**nuevo)

    def borrar(self, pedidoid: int):
        self.repo.borrar(pedidoid)

    # -----------------------------
    # Líneas
    # -----------------------------
    def lineas(self, pedidoid: int):
        return [PedidoLineaOut(**l) for l in self.repo.lineas(pedidoid)]

    def agregar_linea(self, pedidoid: int, data: PedidoLineaCreate) -> int:
        payload = data.dict(exclude_none=True)
        payload["pedido_id"] = pedidoid

        cantidad = float(payload.get("cantidad") or 0.0)
        precio = float(payload.get("precio") or 0.0)
        descuento_pct = float(payload.get("descuento_pct") or 0.0)
        precio_tras_dto = precio * (1 - (descuento_pct / 100.0))
        subtotal = precio_tras_dto * cantidad

        payload["precio_tras_dto"] = round(precio_tras_dto, 4)
        payload["subtotal"] = round(subtotal, 4)
        return self.repo.insertar_linea(payload)

    def borrar_linea(self, pedidoid: int, detalleid: int):
        self.repo.borrar_linea(detalleid)

    # -----------------------------
    # Totales
    # -----------------------------
    def totales(self, pedidoid: int) -> Optional[PedidoTotalesOut]:
        t = self.repo.totales(pedidoid)
        if t:
            return PedidoTotalesOut(**t)
        return None

    def recalcular_totales(self, pedidoid: int, use_iva: bool = True, gastos_envio: float = 0.0, envio_sin_cargo: bool = False):
        ped = self.repo.obtener(pedidoid)
        if not ped:
            raise ValueError("Pedido no encontrado")

        lineas = self.repo.lineas(pedidoid)
        if not lineas:
            raise ValueError("No hay líneas en el pedido")

        base_total = 0.0
        impuesto_total = 0.0
        recargo_total = 0.0
        gastos_total = 0.0
        descuento_total = 0.0

        for l in lineas:
            cantidad = float(l.get("cantidad") or 0.0)
            precio = float(l.get("precio") or 0.0)
            descuento_pct = float(l.get("descuento_pct") or 0.0)
            precio_tras_dto = l.get("precio_tras_dto")
            if precio_tras_dto is None:
                precio_tras_dto = precio * (1 - (descuento_pct / 100.0))
            subtotal = l.get("subtotal")
            if subtotal is None:
                subtotal = float(precio_tras_dto) * cantidad

            base_total += float(subtotal)
            descuento_total += max((precio * cantidad) - float(subtotal), 0.0)

            if use_iva:
                impuesto_total += float(l.get("cuota_impuesto") or 0.0)
            recargo_total += float(l.get("cuota_recargo") or 0.0)
            gastos_total += float(l.get("cuota_gastosenvio") or 0.0)

        if gastos_envio and not envio_sin_cargo:
            gastos_total = float(gastos_envio)
        if envio_sin_cargo:
            gastos_total = 0.0

        total_importe = base_total + impuesto_total + recargo_total + gastos_total
        payload = {
            "total_base_imponible": round(base_total, 2),
            "total_impuestos": round(impuesto_total, 2),
            "total_recargos": round(recargo_total, 2),
            "total_base_gastos_envios": round(gastos_total, 2),
            "total_descuentos": round(descuento_total, 2),
            "total": round(total_importe, 2),
        }
        self.repo.actualizar_totales(pedidoid, payload)
        return PedidoTotalesOut(pedido_id=pedidoid, **payload)

    # -----------------------------
    # Observaciones
    # -----------------------------
    def observaciones(self, pedidoid: int):
        ped = self.repo.obtener(pedidoid)
        if not ped:
            return []
        items = []
        if ped.get("observaciones"):
            items.append(
                {
                    "tipo": "pedido",
                    "comentario": ped.get("observaciones"),
                    "fecha": ped.get("updated_on") or ped.get("created_on"),
                    "usuario": ped.get("updated_by") or ped.get("created_by"),
                }
            )
        if ped.get("obs_logistica"):
            items.append(
                {
                    "tipo": "logistica",
                    "comentario": ped.get("obs_logistica"),
                    "fecha": ped.get("updated_on") or ped.get("created_on"),
                    "usuario": ped.get("updated_by") or ped.get("created_by"),
                }
            )
        return items

    def crear_observacion(self, pedidoid: int, data: PedidoObservacionIn, usuario: str):
        ped = self.repo.obtener(pedidoid)
        if not ped:
            raise ValueError("Pedido no encontrado")

        field = "obs_logistica" if (data.tipo or "").lower().startswith("log") else "observaciones"
        existing = ped.get(field) or ""
        stamp = datetime.now().isoformat(timespec="seconds")
        entry = f"[{stamp}] {usuario}: {data.comentario}".strip()
        new_val = f"{existing}\n{entry}".strip() if existing else entry
        self.repo.crear_observacion(pedidoid, {field: new_val, "updated_on": stamp, "updated_by": usuario})

    # -----------------------------
    # Incidencias
    # -----------------------------
    def incidencias(self, pedidoid: int):
        return self.repo.incidencias(pedidoid)

    def crear_incidencia(self, pedidoid: int, data: PedidoIncidenciaIn) -> dict:
        if not self.repo.obtener(pedidoid):
            raise ValueError("Pedido no encontrado")
        payload = data.dict(exclude_none=True)
        return self.repo.crear_incidencia(pedidoid, payload)

    def top_clientes(self, limit: int = 5) -> list[dict]:
        return self.repo.top_clientes(limit=limit)

    # -----------------------------
    # Catálogos
    # -----------------------------
    def catalogos(self) -> PedidoCatalogos:
        def to_items(rows: list, id_field: str, label_field: str):
            return [
                CatalogoItem(id=int(r[id_field]), label=str(r[label_field]))
                for r in rows
                if r.get(id_field) is not None
            ]

        clientes = self.repo.catalogo("cliente", "clienteid", "razonsocial", order_field="razonsocial")
        if not clientes:
            clientes = self.repo.catalogo("cliente", "clienteid", "nombre", order_field="nombre")

        return PedidoCatalogos(
            clientes=to_items(clientes, "clienteid", "razonsocial") if clientes and "razonsocial" in (clientes[0] or {}) else to_items(clientes, "clienteid", "nombre"),
            estados=to_items(self.repo.catalogo("pedido_estado", "pedido_estadoid", "estado", order_field="estado"), "pedido_estadoid", "estado"),
            formas_pago=to_items(self.repo.catalogo("forma_pago", "forma_pagoid", "nombre", order_field="nombre"), "forma_pagoid", "nombre"),
            tipos_documento=to_items(self.repo.catalogo("pedido_tipo_documento", "pedido_tipo_documentoid", "nombre", order_field="nombre"), "pedido_tipo_documentoid", "nombre"),
        )
