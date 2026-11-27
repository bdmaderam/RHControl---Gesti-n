"""Revisor de calidad de anotaciones: un sistema experto basado en reglas.

Es IA simbólica clásica: una base de conocimiento (el léxico en lexico.py más las reglas de este
archivo) y un motor de inferencia que las aplica a la anotación y explica cada conclusión.
No hay modelo entrenado: el resultado es determinista, se puede auditar regla por regla y no
depende de datos, de claves ni de servicios externos.

Qué evalúa una anotación laboral:
  - Forma: extensión, legibilidad, fecha, tono.
  - Lenguaje: insultos, juicios de valor, absolutos, suposiciones, rumores, datos sensibles.
  - Contenido según el tipo: un llamado de atención debe decir cuándo, cuántas veces, qué se
    acordó y si se notificó al empleado; una felicitación debe decir qué se logró; etc.
  - Coherencia: que el texto corresponda al tipo elegido (con manejo de negaciones).
  - Historial (datos reales): duplicados y reincidencia del mismo empleado.

Para agregar una regla: escribir una función decorada con @regla(...) más abajo.
"""
from __future__ import annotations

import re
import time
import unicodedata
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Callable

from . import lexico as L
from ..metrics import IA_DURACION, IA_HALLAZGOS, IA_PUNTAJE, IA_REGLAS_CARGADAS, IA_REVISIONES

PENALIZACION = {"error": 25, "advertencia": 10, "sugerencia": 4, "info": 0}
UMBRAL_LISTA = 85
UMBRAL_MEJORABLE = 60
DIAS_REINCIDENCIA = 90
DIAS_REGISTRO_TARDIO = 90
NEGADORES = {"no", "nunca", "jamas", "sin", "ni", "tampoco"}

CLAVES_TIPO = {
    "llamado de atencion": "llamado", "felicitacion": "felicitacion",
    "observacion": "observacion", "reconocimiento": "reconocimiento",
}
ETIQUETAS = {
    "lista": "Lista para guardar",
    "mejorable": "Mejorable",
    "requiere_correccion": "Requiere corrección",
}


# ---------------------------------------------------------------------------
# Utilidades de texto
# ---------------------------------------------------------------------------
def normalizar(texto: str) -> str:
    """Minúsculas, sin tildes ni ñ, con espacios simples (los patrones del léxico asumen esto)."""
    sin_marcas = "".join(c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", sin_marcas.lower()).strip()


def clave_tipo(tipo: str | None) -> str | None:
    """'Llamado de atención' -> 'llamado'. Tipos desconocidos (p. ej. 'Otro') -> 'otro'. Sin tipo -> None."""
    if not tipo or not tipo.strip():
        return None
    return CLAVES_TIPO.get(normalizar(tipo), "otro")


def _compilar(fragmentos: list[str]) -> re.Pattern:
    return re.compile(r"\b(?:" + "|".join(fragmentos) + r")\b")


PATRONES = {nombre: _compilar(lista) for nombre, lista in vars(L).items() if nombre.isupper()}
RE_CORREO = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
RE_TELEFONO = re.compile(r"(?<![\w-])(?:\+?57\s?)?3\d{9}(?![\w-])")
RE_NUMERO_LARGO = re.compile(r"(?<![\w-])\d{7,}(?![\w-])")
RE_REPETIDO = re.compile(r"(.)\1{4,}")
RE_TECLADO = re.compile(r"asdf|qwer|zxcv|sdfg|dfgh|jklñ|jkln|qaz|wsx")


@dataclass(frozen=True)
class Previa:
    """Anotación anterior del mismo empleado (la usan las reglas de historial)."""
    id: int | None
    tipo: str | None
    fecha: date | None
    texto: str

    @property
    def tokens(self) -> frozenset[str]:
        return frozenset(re.findall(r"[a-z0-9]+", normalizar(self.texto)))


@dataclass
class Ctx:
    """Lo que ven las reglas: el texto en varias formas, el tipo, la fecha y el historial."""
    texto: str
    tipo: str | None
    fecha: date | None
    hoy: date
    historial: list[Previa]
    anotacion_id: int | None = None
    norm: str = field(init=False)
    palabras: list[str] = field(init=False)
    _pol: tuple[list[str], list[str]] | None = field(default=None, init=False, repr=False)

    def __post_init__(self):
        self.norm = normalizar(self.texto)
        self.palabras = re.findall(r"[a-z0-9]+", self.norm)

    def buscar(self, nombre: str) -> list[str]:
        """Fragmentos del texto que coinciden con una lista del léxico (sin repetidos, en orden)."""
        vistos: list[str] = []
        for m in PATRONES[nombre].finditer(self.norm):
            if m.group(0) not in vistos:
                vistos.append(m.group(0))
        return vistos

    def tiene(self, nombre: str) -> bool:
        return PATRONES[nombre].search(self.norm) is not None

    def polaridad(self) -> tuple[list[str], list[str]]:
        """(positivos, negativos). Una negación invierte el término: 'no cumplió las metas' es negativo
        y 'sin ausencias' es positivo."""
        if self._pol is None:
            pos: list[str] = []
            neg: list[str] = []
            for nombre, destino_normal, destino_inverso in (("POSITIVOS", pos, neg), ("NEGATIVOS", neg, pos)):
                for m in PATRONES[nombre].finditer(self.norm):
                    previas = self.norm[: m.start()].split()[-3:]
                    negador = next((p for p in previas if p in NEGADORES), None)
                    if negador:
                        destino_inverso.append(f"{negador} {m.group(0)}")
                    else:
                        destino_normal.append(m.group(0))
            self._pol = (pos, neg)
        return self._pol


@dataclass
class Disparo:
    """Resultado de una regla que se cumplió (es decir, que encontró un problema)."""
    evidencia: list[str] = field(default_factory=list)
    severidad: str | None = None   # reemplaza la severidad por defecto de la regla
    mensaje: str | None = None     # reemplaza el mensaje por defecto


@dataclass(frozen=True)
class Regla:
    id: str
    categoria: str
    severidad: str
    criterio: str      # lo que se espera de una buena anotación (se muestra cuando se cumple)
    mensaje: str       # el problema (se muestra cuando falla)
    sugerencia: str
    aplica: frozenset[str] | None            # tipos a los que aplica; None = a todos
    detecta: Callable[[Ctx], Disparo | None]
    cuando: Callable[[Ctx], bool] | None = None   # condición extra para que la regla aplique

    def aplicable(self, ctx: Ctx) -> bool:
        if self.aplica is not None and ctx.tipo not in self.aplica:
            return False
        return self.cuando(ctx) if self.cuando else True


REGLAS: list[Regla] = []


def regla(id, categoria, severidad, criterio, mensaje, sugerencia, aplica=None, cuando=None):
    """Decorador que registra una regla en la base de conocimiento."""
    def registrar(fn):
        REGLAS.append(Regla(id, categoria, severidad, criterio, mensaje, sugerencia,
                            frozenset(aplica) if aplica else None, fn, cuando))
        return fn
    return registrar


LLAMADO = ("llamado",)
POSITIVOS_TIPO = ("felicitacion", "reconocimiento")


# ---------------------------------------------------------------------------
# FORMA
# ---------------------------------------------------------------------------
@regla("F01", "Forma", "advertencia", "Tiene la extensión suficiente para entenderse",
       "El texto es demasiado corto para entenderse.",
       "Describe qué ocurrió, cuándo y con qué consecuencia en al menos una o dos frases completas.")
def _longitud_minima(ctx):
    n = len(ctx.palabras)
    if n < 4:
        return Disparo([f"{n} palabra(s)"], severidad="error")
    if n < 8:
        return Disparo([f"{n} palabras"])


@regla("F02", "Forma", "sugerencia", "Es concisa",
       "El texto es muy largo.",
       "Resume los hechos principales o divide el texto en varias anotaciones.")
def _longitud_maxima(ctx):
    if len(ctx.palabras) > 120:
        return Disparo([f"{len(ctx.palabras)} palabras"])


@regla("F03", "Forma", "error", "Es legible",
       "El texto parece ilegible o escrito al azar.",
       "Escribe frases completas que otra persona pueda entender.")
def _ilegible(ctx):
    letras = [c for c in ctx.texto if c.isalpha()]
    evidencia = []
    if len(letras) < 3:
        evidencia.append("casi sin letras")
    if RE_REPETIDO.search(ctx.norm):
        evidencia.append("caracteres repetidos")
    if RE_TECLADO.search(ctx.norm):
        evidencia.append("secuencia de teclado")
    if any(len(p) >= 5 and not re.search(r"[aeiou]", p) and not p.isdigit() for p in ctx.palabras):
        evidencia.append("palabras sin vocales")
    return Disparo(evidencia) if evidencia else None


@regla("F04", "Forma", "sugerencia", "Mantiene un tono sereno",
       "El texto tiene un tono exaltado (mayúsculas sostenidas o varias exclamaciones).",
       "Usa un tono neutral: los hechos pesan más que el énfasis.")
def _tono_exaltado(ctx):
    letras = [c for c in ctx.texto if c.isalpha()]
    mayusculas = sum(1 for c in letras if c.isupper())
    evidencia = []
    if len(letras) >= 15 and mayusculas / len(letras) > 0.6:
        evidencia.append("mayúsculas sostenidas")
    if ctx.texto.count("!") >= 3 or "!!" in ctx.texto:
        evidencia.append("exclamaciones")
    return Disparo(evidencia) if evidencia else None


@regla("F05", "Forma", "error", "La fecha del registro es válida",
       "La fecha del registro es posterior a hoy.",
       "Corrige la fecha: una anotación no puede registrar hechos futuros.",
       cuando=lambda c: c.fecha is not None)
def _fecha_futura(ctx):
    if ctx.fecha > ctx.hoy:
        return Disparo([ctx.fecha.isoformat()])


@regla("F06", "Forma", "advertencia", "Se registra sin demora",
       f"La fecha del registro tiene más de {DIAS_REGISTRO_TARDIO} días de antigüedad.",
       "Deja constancia del motivo del registro tardío; un llamado de atención extemporáneo pierde fuerza.",
       aplica=LLAMADO, cuando=lambda c: c.fecha is not None)
def _registro_tardio(ctx):
    dias = (ctx.hoy - ctx.fecha).days
    if dias > DIAS_REGISTRO_TARDIO:
        return Disparo([f"{dias} días"])


# ---------------------------------------------------------------------------
# LENGUAJE
# ---------------------------------------------------------------------------
@regla("L01", "Lenguaje", "error", "No usa insultos ni lenguaje ofensivo",
       "El texto contiene lenguaje ofensivo.",
       "Elimina los insultos y describe objetivamente lo ocurrido: la anotación puede usarse en un proceso formal.")
def _ofensivo(ctx):
    h = ctx.buscar("OFENSIVO")
    return Disparo(h) if h else None


@regla("L02", "Lenguaje", "advertencia", "Describe hechos observables, no juicios sobre la persona",
       "El texto usa juicios de valor sobre la persona en lugar de describir hechos.",
       "Cambia el adjetivo por el hecho: en vez de 'es flojo', escribe qué tarea no entregó y cuándo.")
def _subjetivo(ctx):
    h = ctx.buscar("SUBJETIVO")
    return Disparo(h) if h else None


@regla("L03", "Lenguaje", "sugerencia", "Evita absolutos (siempre, nunca...)",
       "El texto usa absolutos que son difíciles de sustentar.",
       "Reemplaza 'siempre' o 'nunca' por la frecuencia real: 'tres veces en la última semana'.")
def _absolutos(ctx):
    h = ctx.buscar("ABSOLUTOS")
    return Disparo(h) if h else None


@regla("L04", "Lenguaje", "advertencia", "Se limita a lo comprobado, sin suposiciones",
       "El texto expresa suposiciones o intenciones que no están comprobadas.",
       "Registra solo lo que se vio o se documentó; evita adivinar la intención de la persona.")
def _suposicion(ctx):
    h = ctx.buscar("SUPOSICION")
    return Disparo(h) if h else None


@regla("L05", "Lenguaje", "advertencia", "Se basa en hechos directos, no en rumores",
       "El texto se apoya en comentarios o rumores de terceros.",
       "Anota solo lo que presenciaste o lo que consta en un documento, y cita la fuente si es indirecta.")
def _rumor(ctx):
    h = ctx.buscar("RUMOR")
    return Disparo(h) if h else None


@regla("L06", "Lenguaje", "advertencia", "No incluye datos sensibles innecesarios",
       "El texto menciona datos sensibles (salud, religión, política, orientación sexual...), protegidos por la Ley 1581.",
       "Quita el dato sensible salvo que sea indispensable; en un llamado de atención puede parecer discriminación.")
def _sensible(ctx):
    h = ctx.buscar("SENSIBLE")
    if not h:
        return None
    return Disparo(h, severidad="error" if ctx.tipo == "llamado" else None)


@regla("L07", "Lenguaje", "advertencia", "No expone datos personales de terceros",
       "El texto incluye correos, teléfonos o números de identificación.",
       "Quita esos datos; la anotación puede leerla más gente de la necesaria.")
def _datos_personales(ctx):
    evidencia = []
    if RE_CORREO.search(ctx.texto):
        evidencia.append("correo electrónico")
    if RE_TELEFONO.search(ctx.texto):
        evidencia.append("teléfono")
    elif RE_NUMERO_LARGO.search(ctx.texto):
        evidencia.append("número largo (¿documento?)")
    return Disparo(evidencia) if evidencia else None


# ---------------------------------------------------------------------------
# CONTENIDO SEGÚN EL TIPO
# ---------------------------------------------------------------------------
@regla("C01", "Contenido", "advertencia", "Indica cuándo ocurrió el hecho",
       "No se indica cuándo ocurrió el hecho (la fecha del formulario es la del registro, no la del hecho).",
       "Agrega el día o el periodo: 'el lunes 3 de noviembre', 'durante la última semana'.",
       aplica=("llamado", "observacion"))
def _sin_cuando(ctx):
    if not ctx.tiene("TEMPORAL"):
        return Disparo(severidad="advertencia" if ctx.tipo == "llamado" else "sugerencia")


@regla("C02", "Contenido", "sugerencia", "Indica la frecuencia o la cantidad",
       "No se indica cuántas veces o con qué frecuencia ocurrió.",
       "Agrega el número: 'en tres ocasiones', 'dos días seguidos', 'con 20 minutos de retraso'.",
       aplica=LLAMADO)
def _sin_frecuencia(ctx):
    if not ctx.tiene("CUANTIFICACION"):
        return Disparo()


@regla("C03", "Contenido", "advertencia", "Deja claro el compromiso o la consecuencia",
       "No se indica el compromiso acordado ni la consecuencia de que se repita.",
       "Agrega qué se acordó o qué pasaría si se repite: 'se acuerda llegar antes de las 8:00; de repetirse...'.",
       aplica=LLAMADO)
def _sin_consecuencia(ctx):
    if not ctx.tiene("CONSECUENCIA"):
        return Disparo()


@regla("C04", "Contenido", "sugerencia", "Deja constancia de que se notificó al empleado",
       "No consta que el empleado haya sido informado.",
       "Escribe cómo se le comunicó: 'se le informó verbalmente y por escrito el día...'.",
       aplica=LLAMADO)
def _sin_notificacion(ctx):
    if not ctx.tiene("NOTIFICACION"):
        return Disparo()


@regla("C05", "Contenido", "sugerencia", "Registra la versión o los descargos del empleado",
       "No se registra la versión del empleado (descargos).",
       "Anota qué explicó el empleado, o que no quiso dar explicación; es parte del debido proceso.",
       aplica=LLAMADO)
def _sin_descargos(ctx):
    if not ctx.tiene("DESCARGOS"):
        return Disparo()


@regla("C06", "Contenido", "advertencia", "Cita la norma cuando habla de faltas graves o sanciones",
       "Se mencionan faltas graves o sanciones sin citar el reglamento, el contrato o la norma.",
       "Cita la norma aplicable: 'según el artículo X del reglamento interno de trabajo'.",
       aplica=LLAMADO, cuando=lambda c: c.tiene("GRAVEDAD"))
def _sin_norma(ctx):
    if not ctx.tiene("NORMA"):
        return Disparo(ctx.buscar("GRAVEDAD"))


@regla("C07", "Contenido", "sugerencia", "Dice qué hizo o logró la persona",
       "No se indica qué hizo o logró la persona.",
       "Menciona el proyecto, la meta o el resultado concreto que motiva la felicitación o el reconocimiento.",
       aplica=POSITIVOS_TIPO)
def _sin_logro(ctx):
    if not ctx.tiene("LOGRO"):
        return Disparo()


@regla("C08", "Contenido", "sugerencia", "Indica el periodo o motivo del reconocimiento",
       "No se indica el periodo o el motivo del reconocimiento.",
       "Agrega el periodo evaluado: 'durante el segundo semestre', 'por cinco años de servicio'.",
       aplica=("reconocimiento",))
def _sin_periodo(ctx):
    if not ctx.tiene("PERIODO"):
        return Disparo()


@regla("C09", "Contenido", "sugerencia", "Define la acción o el seguimiento",
       "No se indica ninguna acción, pendiente o seguimiento.",
       "Agrega qué sigue y quién lo hará: 'se programa reunión de seguimiento el viernes'.",
       aplica=("observacion",))
def _sin_seguimiento(ctx):
    if not ctx.tiene("SEGUIMIENTO"):
        return Disparo()


# ---------------------------------------------------------------------------
# COHERENCIA ENTRE EL TIPO Y EL TEXTO
# ---------------------------------------------------------------------------
@regla("T01", "Coherencia", "advertencia", "El texto corresponde al tipo elegido",
       "El texto no parece corresponder al tipo elegido.",
       "Revisa el tipo: si el texto es disciplinario usa 'Llamado de atención'; si es positivo, 'Felicitación' o 'Reconocimiento'.",
       aplica=("llamado", "felicitacion", "reconocimiento"))
def _coherencia(ctx):
    pos, neg = ctx.polaridad()
    if pos and neg:
        return None  # texto mixto: lo cubre T02
    if ctx.tipo in POSITIVOS_TIPO and neg:
        return Disparo(neg, mensaje="El tipo es positivo, pero el texto describe conductas negativas.")
    if ctx.tipo == "llamado" and pos:
        return Disparo(pos, mensaje="El tipo es 'Llamado de atención', pero el texto describe aspectos positivos.")


@regla("T02", "Coherencia", "sugerencia", "Trata un solo tema (no mezcla elogios con faltas)",
       "El texto mezcla aspectos positivos y negativos.",
       "Separa en dos anotaciones: una para lo positivo y otra para lo que debe corregirse; así cada una conserva su valor.",
       aplica=("llamado", "felicitacion", "reconocimiento", "observacion"))
def _mezcla(ctx):
    pos, neg = ctx.polaridad()
    if pos and neg:
        return Disparo(pos[:2] + neg[:2])


# ---------------------------------------------------------------------------
# HISTORIAL (datos reales del empleado)
# ---------------------------------------------------------------------------
def _previas(ctx):
    return [p for p in ctx.historial if p.id is None or p.id != ctx.anotacion_id]


def _similitud(a: frozenset[str], b: frozenset[str]) -> float:
    return len(a & b) / len(a | b) if a and b else 0.0


@regla("H01", "Historial", "advertencia", "No repite una anotación existente",
       "El texto es casi idéntico a otra anotación de este empleado.",
       "Verifica que no sea un duplicado; si es un hecho nuevo, descríbelo con sus propios datos.",
       cuando=lambda c: bool(c.historial))
def _duplicada(ctx):
    mia = frozenset(ctx.palabras)
    if len(mia) < 4:
        return None
    for p in _previas(ctx):
        if _similitud(mia, p.tokens) >= 0.8:
            return Disparo([p.fecha.isoformat() if p.fecha else "otra anotación"])


@regla("H02", "Historial", "info", "Considera los antecedentes del empleado",
       "Hay antecedentes de llamados de atención recientes.",
       "Menciona los antecedentes y verifica en el reglamento el procedimiento de escalamiento.",
       aplica=LLAMADO, cuando=lambda c: bool(c.historial))
def _reincidencia(ctx):
    base = ctx.fecha or ctx.hoy
    desde = base - timedelta(days=DIAS_REINCIDENCIA)
    previos = [p for p in _previas(ctx) if p.tipo == "llamado" and p.fecha and desde <= p.fecha <= base]
    if not previos:
        return None
    n = len(previos) + 1
    return Disparo([f"{len(previos)} previo(s)"],
                   mensaje=f"Este sería el llamado de atención n.º {n} en los últimos {DIAS_REINCIDENCIA} días.")


# ---------------------------------------------------------------------------
# MOTOR DE INFERENCIA
# ---------------------------------------------------------------------------
IA_REGLAS_CARGADAS.set(len(REGLAS))


def catalogo() -> list[dict]:
    """La base de conocimiento en formato legible (para documentar y mostrar en la sustentación)."""
    return [{
        "id": r.id, "categoria": r.categoria, "severidad": r.severidad, "criterio": r.criterio,
        "aplica_a": sorted(r.aplica) if r.aplica else "todos los tipos",
    } for r in REGLAS]


def revisar(texto: str, tipo: str | None = None, fecha: date | None = None,
            historial: list[Previa] | None = None, hoy: date | None = None,
            anotacion_id: int | None = None, registrar_metricas: bool = True) -> dict:
    """Aplica todas las reglas a una anotación y devuelve el puntaje, los hallazgos y lo que sí cumple."""
    inicio = time.perf_counter()
    ctx = Ctx(texto=texto or "", tipo=clave_tipo(tipo), fecha=fecha, hoy=hoy or date.today(),
              historial=historial or [], anotacion_id=anotacion_id)
    hallazgos, cumplidas = [], []
    evaluadas = 0
    for r in REGLAS:
        if not r.aplicable(ctx):
            continue
        evaluadas += 1
        disparo = r.detecta(ctx)
        if disparo is None:
            cumplidas.append(r.criterio)
            continue
        hallazgos.append({
            "regla": r.id, "categoria": r.categoria, "severidad": disparo.severidad or r.severidad,
            "mensaje": disparo.mensaje or r.mensaje, "sugerencia": r.sugerencia,
            "evidencia": disparo.evidencia[:5],
        })
    orden = {"error": 0, "advertencia": 1, "sugerencia": 2, "info": 3}
    hallazgos.sort(key=lambda h: (orden[h["severidad"]], h["regla"]))

    puntaje = max(0, 100 - sum(PENALIZACION[h["severidad"]] for h in hallazgos))
    if any(h["severidad"] == "error" for h in hallazgos) or puntaje < UMBRAL_MEJORABLE:
        nivel = "requiere_correccion"
    elif puntaje >= UMBRAL_LISTA:
        nivel = "lista"
    else:
        nivel = "mejorable"

    previos_llamado = sum(1 for p in _previas(ctx) if p.tipo == "llamado")
    resultado = {
        "puntaje": puntaje, "nivel": nivel, "etiqueta": ETIQUETAS[nivel],
        "resumen": _resumen(nivel, hallazgos),
        "hallazgos": hallazgos, "cumplidas": cumplidas,
        "reglas_evaluadas": evaluadas,
        "contexto": {"tipo_evaluado": ctx.tipo, "palabras": len(ctx.palabras),
                     "anotaciones_previas": len(_previas(ctx)), "llamados_previos": previos_llamado},
    }
    if registrar_metricas:
        IA_REVISIONES.labels(nivel).inc()
        IA_PUNTAJE.observe(puntaje)
        for h in hallazgos:
            IA_HALLAZGOS.labels(h["regla"], h["severidad"]).inc()
        IA_DURACION.observe(time.perf_counter() - inicio)
    return resultado


def _resumen(nivel: str, hallazgos: list[dict]) -> str:
    n = {s: sum(1 for h in hallazgos if h["severidad"] == s) for s in PENALIZACION}
    if not hallazgos:
        return "No se encontraron problemas: la anotación cumple todos los criterios."
    partes = []
    if n["error"]:
        partes.append(f"{n['error']} error(es)")
    if n["advertencia"]:
        partes.append(f"{n['advertencia']} advertencia(s)")
    if n["sugerencia"]:
        partes.append(f"{n['sugerencia']} sugerencia(s)")
    if n["info"]:
        partes.append(f"{n['info']} dato(s) informativo(s)")
    return "Se encontraron " + ", ".join(partes) + "."
