from typing import Optional, Dict

from fastapi import APIRouter, Depends, HTTPException

from backend.app.core.database import get_supabase
from backend.app.schemas.cliente_facturacion import (
    FormaPagoOut,
    ClienteBancoIn,
    ClienteTarjetaIn,
    ClienteFacturacionIn,
    ClienteFacturacionOut,
)

router = APIRouter(prefix="/api/clientes", tags=["Clientes"])


def _rpc_update_forma_pago(supabase, clienteid: int, formapagoid: int) -> bool:
    try:
        supabase.rpc("safe_update_cliente", {"p_clienteid": clienteid, "p_formapagoid": formapagoid}).execute()
        return True
    except Exception:
        return False


def _update_forma_pago(supabase, clienteid: int, formapagoid: int) -> None:
    if not _rpc_update_forma_pago(supabase, clienteid, formapagoid):
        supabase.table("cliente").update({"formapagoid": formapagoid}).eq("clienteid", clienteid).execute()


def _verificar_perfil_completo(supabase, clienteid: int) -> Optional[bool]:
    try:
        dir_ok = False
        # Tabla principal de direcciones
        try:
            rows = (
                supabase.table("clientes_direccion")
                .select("clientes_direccionid, direccionfiscal, direccion, codigopostal")
                .eq("idtercero", clienteid)
                .limit(1)
                .execute()
                .data
                or []
            )
        except Exception:
            rows = []
        if not rows:
            # Fallback a tabla alternativa
            try:
                rows = (
                    supabase.table("cliente_direccion")
                    .select("cliente_direccionid, direccionfiscal, direccion, codigopostal, cp")
                    .eq("clienteid", clienteid)
                    .limit(1)
                    .execute()
                    .data
                    or []
                )
            except Exception:
                rows = []
        if rows:
            r = rows[0]
            cp = r.get("codigopostal") or r.get("cp")
            dir_ok = bool(cp) and bool(r.get("direccionfiscal") or r.get("direccion"))

        cliente = supabase.table("cliente").select("formapagoid").eq("clienteid", clienteid).single().execute().data
        fpagoid = (cliente or {}).get("formapagoid")
        fpago_ok = bool(fpagoid)

        nombre_fp = ""
        if fpagoid:
            fpago = (
                supabase.table("forma_pago")
                .select("nombre")
                .eq("formapagoid", fpagoid)
                .single()
                .execute()
                .data
            )
            nombre_fp = (fpago or {}).get("nombre", "").lower()

        banco_ok = True
        if any(p in nombre_fp for p in ["banco", "transferencia", "domiciliacion", "domiciliación"]):
            banco_ok = bool(
                supabase.table("cliente_banco")
                .select("cliente_bancoid")
                .eq("clienteid", clienteid)
                .limit(1)
                .execute()
                .data
            )

        completo = bool(dir_ok and fpago_ok and banco_ok)
        try:
            supabase.table("cliente").update({"perfil_completo": completo}).eq("clienteid", clienteid).execute()
        except Exception:
            pass
        return completo
    except Exception:
        return None


@router.get("/facturacion/catalogos")
def catalogos_facturacion(supabase=Depends(get_supabase)):
    try:
        rows = (
            supabase.table("forma_pago")
            .select("formapagoid, nombre")
            .eq("habilitado", True)
            .order("formapagoid")
            .execute()
            .data
            or []
        )
    except Exception:
        rows = []
    return [FormaPagoOut(**r) for r in rows]


@router.get("/{clienteid}/facturacion", response_model=ClienteFacturacionOut)
def obtener_facturacion(clienteid: int, supabase=Depends(get_supabase)):
    try:
        cli = supabase.table("cliente").select("clienteid, formapagoid, perfil_completo").eq("clienteid", clienteid).single().execute().data
    except Exception:
        cli = {}

    try:
        banco = supabase.table("cliente_banco").select("*").eq("clienteid", clienteid).limit(1).execute().data
        banco = banco[0] if banco else None
    except Exception:
        banco = None

    try:
        tarjeta = supabase.table("cliente_tarjeta").select("*").eq("clienteid", clienteid).limit(1).execute().data
        tarjeta = tarjeta[0] if tarjeta else None
    except Exception:
        tarjeta = None

    return ClienteFacturacionOut(
        clienteid=clienteid,
        formapagoid=(cli or {}).get("formapagoid"),
        perfil_completo=(cli or {}).get("perfil_completo"),
        banco=banco,
        tarjeta=tarjeta,
    )


@router.post("/{clienteid}/facturacion", response_model=ClienteFacturacionOut)
def guardar_facturacion(clienteid: int, data: ClienteFacturacionIn, supabase=Depends(get_supabase)):
    try:
        if data.formapagoid is not None:
            _update_forma_pago(supabase, clienteid, data.formapagoid)

        if data.banco:
            payload = data.banco.dict(exclude_none=True)
            payload["clienteid"] = clienteid
            supabase.table("cliente_banco").upsert(payload, on_conflict="clienteid").execute()

        if data.tarjeta:
            payload = data.tarjeta.dict(exclude_none=True)
            payload["clienteid"] = clienteid
            supabase.table("cliente_tarjeta").upsert(payload, on_conflict="clienteid").execute()

        perfil = _verificar_perfil_completo(supabase, clienteid)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        cli = supabase.table("cliente").select("formapagoid, perfil_completo").eq("clienteid", clienteid).single().execute().data
    except Exception:
        cli = {}

    return ClienteFacturacionOut(
        clienteid=clienteid,
        formapagoid=(cli or {}).get("formapagoid"),
        perfil_completo=perfil if perfil is not None else (cli or {}).get("perfil_completo"),
        banco=data.banco.dict() if data.banco else None,
        tarjeta=data.tarjeta.dict() if data.tarjeta else None,
    )
