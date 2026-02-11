from postgrest.exceptions import APIError
from typing import List, Optional, Tuple


class PedidosRepository:
    def __init__(self, supabase):
        self.supabase = supabase

    # -----------------------------
    # Listado
    # -----------------------------
    def listar(self, filtros: dict, page: int, page_size: int) -> Tuple[List[dict], int]:
        q = self.supabase.table("pedido").select("*", count="exact")

        if filtros.get("q"):
            term = str(filtros["q"]).strip()
            conds = [
                f"cliente.ilike.%{term}%",
                f"referencia_cliente.ilike.%{term}%",
                f"cif_cliente.ilike.%{term}%",
            ]
            if term.isdigit():
                conds.extend([f"pedido_id.eq.{term}", f"clienteid.eq.{term}"])
            q = q.or_(",".join(conds))
        if filtros.get("clienteid"):
            q = q.eq("clienteid", filtros["clienteid"])
        if filtros.get("estadoid"):
            q = q.eq("pedido_estadoid", filtros["estadoid"])
        if filtros.get("forma_pagoid"):
            q = q.eq("forma_pagoid", filtros["forma_pagoid"])
        if filtros.get("pedido_procedencia"):
            q = q.eq("pedido_procedencia", filtros["pedido_procedencia"])
        if filtros.get("pedido_estado_nombre"):
            q = q.ilike("pedido_estado_nombre", f"%{filtros['pedido_estado_nombre']}%")
        if filtros.get("tipodoc"):
            q = q.ilike("tipodoc", f"%{filtros['tipodoc']}%")
        if filtros.get("pedido_tipo_documentoid"):
            q = q.eq("pedido_tipo_documentoid", filtros["pedido_tipo_documentoid"])
        if filtros.get("referencia_cliente"):
            q = q.ilike("referencia_cliente", f"%{filtros['referencia_cliente']}%")
        if filtros.get("cif_cliente"):
            q = q.ilike("cif_cliente", f"%{filtros['cif_cliente']}%")
        if filtros.get("total_min") is not None:
            q = q.gte("total", filtros["total_min"])
        if filtros.get("total_max") is not None:
            q = q.lte("total", filtros["total_max"])
        if filtros.get("fecha_desde"):
            q = q.gte("fecha_pedido", filtros["fecha_desde"])
        if filtros.get("fecha_hasta"):
            q = q.lte("fecha_pedido", filtros["fecha_hasta"])
        if filtros.get("fecha_completado_desde"):
            q = q.gte("fecha_completado", filtros["fecha_completado_desde"])
        if filtros.get("fecha_completado_hasta"):
            q = q.lte("fecha_completado", filtros["fecha_completado_hasta"])

        start = (page - 1) * page_size
        end = start + page_size - 1
        try:
            res = q.order("created_at", desc=True).range(start, end).execute()
            return res.data or [], res.count or 0
        except APIError as e:
            if getattr(e, "args", None) and isinstance(e.args[0], dict) and e.args[0].get("code") == "PGRST205":
                return [], 0
            raise

    # -----------------------------
    # Cabecera / detalle
    # -----------------------------
    def obtener(self, pedidoid: int) -> Optional[dict]:
        res = (
            self.supabase.table("pedido")
            .select("*")
            .eq("pedido_id", pedidoid)
            .maybe_single()
            .execute()
        )
        return res.data or None

    def crear(self, data: dict) -> dict:
        res = self.supabase.table("pedido").insert(data).execute()
        return (res.data or [None])[0]

    def actualizar(self, pedidoid: int, data: dict):
        self.supabase.table("pedido").update(data).eq("pedido_id", pedidoid).execute()

    def borrar(self, pedidoid: int):
        self.supabase.table("pedido").delete().eq("pedido_id", pedidoid).execute()

    # -----------------------------
    # Líneas
    # -----------------------------
    def lineas(self, pedidoid: int) -> List[dict]:
        res = (
            self.supabase.table("pedido_linea")
            .select(
                "pedido_linea_id, pedido_id, pedido_estadoid, producto_id, referencia, nombre_producto, cantidad, "
                "precio, descuento_pct, precio_tras_dto, subtotal, tasa_impuesto, cuota_impuesto, "
                "tasa_recargo, cuota_recargo, tasa_gastosenvio, cuota_gastosenvio, fecha_limite, "
                "fecha_completado, producto_externo, producto_observacion"
            )
            .eq("pedido_id", pedidoid)
            .order("pedido_linea_id")
            .execute()
        )
        return res.data or []

    def insertar_linea(self, data: dict) -> int:
        res = self.supabase.table("pedido_linea").insert(data).execute()
        return res.data[0]["pedido_linea_id"]

    def borrar_linea(self, detalleid: int):
        self.supabase.table("pedido_linea").delete().eq("pedido_linea_id", detalleid).execute()

    # -----------------------------
    # Totales
    # -----------------------------
    def totales(self, pedidoid: int) -> Optional[dict]:
        res = (
            self.supabase.table("pedido")
            .select(
                "pedido_id,total_base_imponible,total_impuestos,total_recargos,total_base_gastos_envios,total_descuentos,total"
            )
            .eq("pedido_id", pedidoid)
            .maybe_single()
            .execute()
        )
        return res.data or None

    def actualizar_totales(self, pedidoid: int, payload: dict):
        self.supabase.table("pedido").update(payload).eq("pedido_id", pedidoid).execute()

    # -----------------------------
    # Observaciones
    # -----------------------------
    def observaciones(self, pedidoid: int) -> List[dict]:
        ped = self.obtener(pedidoid)
        if not ped:
            return []
        return [ped]

    def crear_observacion(self, pedidoid: int, data: dict):
        self.actualizar(pedidoid, data)

    # -----------------------------
    # Incidencias
    # -----------------------------
    def incidencias(self, pedidoid: int) -> List[dict]:
        for field in ("pedido_id", "pedidoid"):
            try:
                res = (
                    self.supabase.table("pedido_incidencia")
                    .select("*")
                    .eq(field, pedidoid)
                    .order("fecha", desc=True)
                    .execute()
                )
                return res.data or []
            except APIError as e:
                if getattr(e, "args", None) and isinstance(e.args[0], dict) and e.args[0].get("code") in ("PGRST204", "PGRST205"):
                    continue
                raise
            except Exception:
                continue
        return []

    def crear_incidencia(self, pedidoid: int, data: dict) -> dict:
        for field in ("pedido_id", "pedidoid"):
            try:
                payload = dict(data)
                payload[field] = pedidoid
                res = self.supabase.table("pedido_incidencia").insert(payload).execute()
                return (res.data or [None])[0] or {}
            except APIError as e:
                if getattr(e, "args", None) and isinstance(e.args[0], dict) and e.args[0].get("code") in ("PGRST204", "PGRST205"):
                    continue
                raise
            except Exception:
                continue
        return {}

    # -----------------------------
    # Catálogos
    # -----------------------------
    def catalogo(self, table: str, id_field: str, label_field: str, where_enabled: bool = False, order_field: Optional[str] = None) -> List[dict]:
        q = self.supabase.table(table).select(f"{id_field},{label_field}")
        if where_enabled:
            try:
                q = q.eq("habilitado", True)
            except Exception:
                pass
        if order_field:
            try:
                q = q.order(order_field)
            except Exception:
                pass
        try:
            res = q.execute()
            return res.data or []
        except Exception:
            return []

    def top_clientes(self, limit: int = 5) -> List[dict]:
        counts: dict[int, dict] = {}
        page_size = 1000
        page = 0
        while True:
            start = page * page_size
            end = start + page_size - 1
            res = (
                self.supabase.table("pedido")
                .select("clienteid, cliente")
                .range(start, end)
                .execute()
            )
            rows = res.data or []
            if not rows:
                break
            for r in rows:
                cid = r.get("clienteid")
                if not cid:
                    continue
                if cid not in counts:
                    label = r.get("cliente") or str(cid)
                    counts[cid] = {"clienteid": cid, "label": label, "count": 0}
                counts[cid]["count"] += 1
            page += 1
        top = sorted(counts.values(), key=lambda x: x["count"], reverse=True)
        return top[: max(1, int(limit))]
