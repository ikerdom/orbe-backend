# backend/app/repositories/crm_repo.py
from typing import List, Optional
from postgrest.exceptions import APIError


class CrmRepository:
    def __init__(self, supabase):
        self.supabase = supabase

    def listar(self, filtros: dict) -> List[dict]:
        select_full = (
            "crm_actuacionid,titulo,descripcion,observaciones,hora_inicio,hora_fin,duracion_segundos,"
            "fecha_accion,fecha_vencimiento,"
            "requiere_seguimiento,fecha_recordatorio,clienteid,trabajador_creadorid,"
            "trabajador_asignadoid,crm_actuacion_estadoid,crm_actuacion_tipoid,"
            "crm_actuacion_estado(estado),crm_actuacion_tipo(tipo),"
            "cliente (clienteid, razonsocial, nombre)"
        )
        q = self.supabase.table("crm_actuacion").select(select_full)
        if filtros.get("trabajador_asignadoid"):
            q = q.eq("trabajador_asignadoid", filtros["trabajador_asignadoid"])
        if filtros.get("clienteid"):
            q = q.eq("clienteid", filtros["clienteid"])
        if filtros.get("crm_actuacion_estadoid"):
            q = q.eq("crm_actuacion_estadoid", filtros["crm_actuacion_estadoid"])
        if filtros.get("crm_actuacion_tipoid"):
            q = q.eq("crm_actuacion_tipoid", filtros["crm_actuacion_tipoid"])
        q = q.order("fecha_vencimiento", desc=False)
        try:
            res = q.execute()
        except APIError as e:
            if getattr(e, "args", None) and isinstance(e.args[0], dict) and e.args[0].get("code") == "PGRST204":
                # fallback sin relaciones por si faltan FK/columnas
                q = self.supabase.table("crm_actuacion").select(
                    "crm_actuacionid,titulo,descripcion,observaciones,hora_inicio,hora_fin,duracion_segundos,"
                    "fecha_accion,fecha_vencimiento,requiere_seguimiento,fecha_recordatorio,clienteid,"
                    "trabajador_creadorid,trabajador_asignadoid,crm_actuacion_estadoid,crm_actuacion_tipoid"
                )
                res = q.execute()
            else:
                raise
        rows = res.data or []
        if filtros.get("buscar"):
            s = filtros["buscar"].lower()
            rows = [r for r in rows if s in (r.get("titulo") or "").lower()]
        for r in rows:
            r["estado"] = (r.get("crm_actuacion_estado") or {}).get("estado")
            r["tipo"] = (r.get("crm_actuacion_tipo") or {}).get("tipo")
            cli = r.get("cliente") or {}
            r["cliente_nombre"] = cli.get("razonsocial") or cli.get("nombre")
        return rows

    def crear(self, data: dict) -> dict:
        res = self.supabase.table("crm_actuacion").insert(data).execute()
        return (res.data or [None])[0]

    def actualizar(self, accionid: int, data: dict) -> dict:
        self.supabase.table("crm_actuacion").update(data).eq("crm_actuacionid", accionid).execute()
        res = (
            self.supabase.table("crm_actuacion")
            .select("*")
            .eq("crm_actuacionid", accionid)
            .maybe_single()
            .execute()
        )
        return res.data or {}

    def obtener(self, accionid: int) -> Optional[dict]:
        try:
            res = (
                self.supabase.table("crm_actuacion")
                .select(
                    "crm_actuacionid,titulo,descripcion,observaciones,hora_inicio,hora_fin,duracion_segundos,"
                    "fecha_accion,fecha_vencimiento,"
                    "requiere_seguimiento,fecha_recordatorio,clienteid,trabajador_creadorid,"
                    "trabajador_asignadoid,crm_actuacion_estadoid,crm_actuacion_tipoid,"
                    "crm_actuacion_estado(estado),crm_actuacion_tipo(tipo),"
                    "cliente (clienteid, razonsocial, nombre)"
                )
                .eq("crm_actuacionid", accionid)
                .maybe_single()
                .execute()
            )
        except APIError as e:
            if getattr(e, "args", None) and isinstance(e.args[0], dict) and e.args[0].get("code") == "PGRST204":
                res = (
                    self.supabase.table("crm_actuacion")
                    .select(
                        "crm_actuacionid,titulo,descripcion,observaciones,hora_inicio,hora_fin,duracion_segundos,"
                        "fecha_accion,fecha_vencimiento,requiere_seguimiento,fecha_recordatorio,clienteid,"
                        "trabajador_creadorid,trabajador_asignadoid,crm_actuacion_estadoid,crm_actuacion_tipoid"
                    )
                    .eq("crm_actuacionid", accionid)
                    .maybe_single()
                    .execute()
                )
            else:
                raise
        row = res.data or None
        if row:
            row["estado"] = (row.get("crm_actuacion_estado") or {}).get("estado")
            row["tipo"] = (row.get("crm_actuacion_tipo") or {}).get("tipo")
            cli = row.get("cliente") or {}
            row["cliente_nombre"] = cli.get("razonsocial") or cli.get("nombre")
        return row
