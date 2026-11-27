"""Detección de temas y reincidencia en anotaciones (sistema basado en reglas).

1. Etiqueta cada anotación con los temas de services/lexico_temas.py (puntualidad, seguridad, trato...).
2. Determina el tono de cada tema (negativo / positivo / neutro).
3. Con el historial real del empleado, avisa cuando un tema NEGATIVO se repite dentro de una ventana
   de tiempo (por defecto 90 días): 2 veces = "se repite", 3 o más = "reincidente".

No hay modelo entrenado: no necesita datos de entrenamiento, es determinista y cada etiqueta
indica las palabras que la activaron.
"""
from __future__ import annotations

import re
from datetime import date, timedelta

from ..metrics import IA_REINCIDENCIAS, IA_TEMAS
from .lexico_temas import TEMAS
from .revisor import NEGADORES, Previa, clave_tipo, normalizar
from . import lexico as L
from .revisor import _compilar

VENTANA_DIAS = 90
TIPOS_NEGATIVOS = {"llamado"}
TIPOS_POSITIVOS = {"felicitacion", "reconocimiento"}

_PATRONES = {k: _compilar(v["patrones"]) for k, v in TEMAS.items()}
_POS = _compilar(L.POSITIVOS)
_NEG = _compilar(L.NEGATIVOS)


def _coincidencias(norm: str, patron: re.Pattern) -> list[str]:
    """Fragmentos que coinciden, ignorando los precedidos por una negación ('sin tardanzas')."""
    vistos: list[str] = []
    for m in patron.finditer(norm):
        previas = norm[: m.start()].split()[-2:]
        if any(p in NEGADORES for p in previas):
            continue
        if m.group(0) not in vistos:
            vistos.append(m.group(0))
    return vistos


def tono_general(norm: str, tipo: str | None) -> str:
    """negativo / positivo / neutro, según el tipo elegido y, si no es concluyente, según el texto."""
    if tipo in TIPOS_NEGATIVOS:
        return "negativo"
    if tipo in TIPOS_POSITIVOS:
        return "positivo"
    pos, neg = bool(_POS.search(norm)), bool(_NEG.search(norm))
    if neg and not pos:
        return "negativo"
    if pos and not neg:
        return "positivo"
    return "neutro"


def detectar(texto: str, tipo: str | None = None) -> list[dict]:
    """Temas de una anotación, ordenados por cantidad de coincidencias."""
    norm = normalizar(texto or "")
    tipo = tipo if tipo in ("llamado", "felicitacion", "observacion", "reconocimiento", "otro") else clave_tipo(tipo)
    general = tono_general(norm, tipo)
    encontrados = []
    for clave, patron in _PATRONES.items():
        ev = _coincidencias(norm, patron)
        if not ev:
            continue
        tono = "positivo" if TEMAS[clave].get("positivo") else general
        encontrados.append({"tema": clave, "nombre": TEMAS[clave]["nombre"], "tono": tono, "evidencia": ev[:4], "_n": len(ev)})
    encontrados.sort(key=lambda t: (-t["_n"], t["tema"]))
    for t in encontrados:
        del t["_n"]
    return encontrados


def _fecha(p: Previa, hoy: date) -> date:
    return p.fecha or hoy


def analizar(texto: str, tipo: str | None, fecha: date | None, historial: list[Previa],
             hoy: date | None = None, anotacion_id: int | None = None,
             dias: int = VENTANA_DIAS, registrar_metricas: bool = True) -> dict:
    """Temas de la anotación + alertas de reincidencia contra el historial del empleado."""
    hoy = hoy or date.today()
    k = clave_tipo(tipo)
    temas = detectar(texto, k)
    base = fecha or hoy
    desde = base - timedelta(days=dias)
    previas = [p for p in historial if p.id is None or p.id != anotacion_id]
    reincidencias = []
    for t in temas:
        if t["tono"] != "negativo":
            continue
        fechas = []
        for p in previas:
            f = _fecha(p, hoy)
            if not (desde <= f <= base):
                continue
            for pt in detectar(p.texto, p.tipo):
                if pt["tema"] == t["tema"] and pt["tono"] == "negativo":
                    fechas.append(f)
                    break
        if fechas:
            n = len(fechas) + 1
            reincidencias.append({
                "tema": t["tema"], "nombre": t["nombre"], "ocurrencias": n, "ventana_dias": dias,
                "fechas_previas": sorted(f.isoformat() for f in fechas),
                "nivel": "reincidente" if n >= 3 else "se_repite",
                "mensaje": (f"'{t['nombre']}' aparece por {n}.ª vez en los últimos {dias} días"
                            + (": es un patrón, no un hecho aislado." if n >= 3 else ".")),
            })
    if registrar_metricas:
        for t in temas:
            IA_TEMAS.labels(t["tema"], t["tono"]).inc()
        for r in reincidencias:
            IA_REINCIDENCIAS.labels(r["tema"], r["nivel"]).inc()
    return {"temas": temas, "reincidencias": reincidencias}


def perfil_empleado(historial: list[Previa], hoy: date | None = None, dias: int = VENTANA_DIAS,
                    minimo: int = 2) -> dict:
    """Resumen de temas de un empleado y alertas de reincidencia sobre toda su historia reciente."""
    hoy = hoy or date.today()
    desde = hoy - timedelta(days=dias)
    conteo: dict[str, dict] = {}
    for p in historial:
        f = _fecha(p, hoy)
        for t in detectar(p.texto, p.tipo):
            c = conteo.setdefault(t["tema"], {"tema": t["tema"], "nombre": t["nombre"], "negativas": 0,
                                              "positivas": 0, "neutras": 0, "recientes_negativas": [], "ultima_fecha": None})
            c[{"negativo": "negativas", "positivo": "positivas", "neutro": "neutras"}[t["tono"]]] += 1
            if t["tono"] == "negativo" and f >= desde:
                c["recientes_negativas"].append(f.isoformat())
            if c["ultima_fecha"] is None or f.isoformat() > c["ultima_fecha"]:
                c["ultima_fecha"] = f.isoformat()
    temas = sorted(conteo.values(), key=lambda c: (-(c["negativas"] + c["positivas"] + c["neutras"]), c["tema"]))
    alertas = []
    for c in temas:
        n = len(c["recientes_negativas"])
        if n >= minimo:
            alertas.append({"tema": c["tema"], "nombre": c["nombre"], "ocurrencias": n, "ventana_dias": dias,
                            "fechas": sorted(c["recientes_negativas"]),
                            "nivel": "reincidente" if n >= 3 else "se_repite"})
    for c in temas:
        del c["recientes_negativas"]
    alertas.sort(key=lambda a: (-a["ocurrencias"], a["tema"]))
    return {"anotaciones": len(historial), "ventana_dias": dias, "temas": temas, "alertas": alertas}
