"""Base de conocimiento léxica del revisor de anotaciones.

Todos los patrones se escriben SIN tildes y en minúsculas, porque el texto se normaliza antes de
compararlo (ver revisor.normalizar). Cada entrada es un fragmento de expresión regular; los
patrones terminados en \\w* cubren la familia de la palabra (p. ej. "incumpl\\w*" = incumplió,
incumplimiento...). Para agregar conocimiento basta con sumar elementos a estas listas.
"""

# --- Lenguaje que debilita una anotación (juicios, absolutos, suposiciones, rumores) ---
SUBJETIVO = [
    "verguenza", "desastre", "torpe",
    "flojo", "floja", "vago", "vaga", r"perezos\w*", r"desinteresad\w*", r"irresponsable\w*",
    r"incompetente\w*", r"problematic\w*", r"conflictiv\w*", "mala actitud", "actitud negativa",
    "mal caracter", "no le importa", "le da igual", "no le interesa", "no tiene interes", "falta de compromiso",
    r"mediocre\w*", r"desordenad\w*", "grosero", "grosera", "altanero", "altanera", "insolente", r"negligente\w*",
    r"desmotivad\w*", r"apatic\w*", "conformista", "pesimista", r"malgeniad\w*", "mala persona", "mal empleado",
    "mala educacion", "se cree", "se hace el", "se hace la", r"actitud\s+de\s+(?:superioridad|rebeldia)",
]
ABSOLUTOS = [
    "siempre", "nunca", "jamas", "todo el tiempo", "todos los dias", "constantemente",
    "todas las veces", "en todo momento", "cada vez que",
]
OFENSIVO = [
    "idiota", r"estupid\w*", "imbecil", "bruto", "bruta", "tonto", "tonta", "inutil", "basura", "estorbo",
    r"malparid\w*", "gonorrea", r"pendej\w*", "huevon", "cabron", "mierda", "carajo", "porqueria",
    "payaso", "burro", "burra", "ridiculo", "ridicula", "marica",
]
SUPOSICION = [
    "seguramente", "probablemente", "supongo", "creo que", "me parece", "parece que", "pareciera",
    "debe de ser", "con mala intencion", "por pereza", "por flojera", "quiza", "quizas", "tal vez",
    "al parecer", "se nota que", "deduzco", "lo hace a proposito", "lo hizo a proposito", "intencionalmente",
]
RUMOR = [
    "dicen que", "me contaron", "me comentaron", "se rumora", "se dice que", "segun comentarios", "segun dicen",
    "escuche que", "se comenta", "radio bemba", r"chisme\w*", "alguien me dijo", "unos companeros dicen",
]

# --- Datos sensibles (Ley 1581 de 2012, protección de datos personales en Colombia) ---
SENSIBLE = [
    r"embaraz\w*", "gestacion", r"diagnostic\w*", "cancer", "vih", "sida", "depresion", "ansiedad", "bipolar",
    "esquizofrenia", "discapacidad", r"psiquiatr\w*", r"psicolog\w*", "tratamiento medico", r"medicamento\w*",
    r"religio\w*", r"evangelic\w*", r"catolic\w*", r"musulman\w*", "partido politico", "afiliacion politica", "opinion politica", "ideologia",
    r"sindicat\w*", "orientacion sexual", r"homosexual\w*", "lesbiana", "raza", "etnia", "indigena",
    r"enfermedad\w*", r"enferm[oa]s?", "diabetes", "diabetic[oa]s?", "hipertension", r"epilep\w*", "asma", "artritis",
    r"cirugia\w*", "quimioterapia", "covid", r"terapia\w*", "problemas de salud", "estado de salud",
]

# --- Polaridad: conductas negativas y positivas (se invierten si van precedidas de negación) ---
NEGATIVOS = [
    r"lleg\w*\s+tarde", r"tardanza\w*", r"retard\w*", r"impuntual\w*", r"ausen\w*", r"inasistencia\w*",
    r"falto\b", r"faltas?\s+injustificad\w*", r"no\s+asisti\w*", r"incumpl\w*", r"advert\w*", r"amonest\w*",
    r"sancion\w*", r"queja\w*", r"llamad[oa]s?\s+de\s+atencion", r"reincid\w*", r"indisciplin\w*", r"irrespet\w*",
    r"falto\s+al\s+respeto", r"grit\w*", r"discusion\w*", r"uso\s+indebido", r"abandon\w*", r"negligen\w*",
    r"error\s+grave", r"reproceso\w*", r"proceso\s+disciplinario", r"mal\s+comportamiento", r"desobedec\w*",
    r"desatend\w*", r"insubordinacion", r"descuid\w*", r"demora\w*", r"infraccion\w*", r"violacion",
    r"agresion\w*", r"agredi\w*", r"acoso", r"falta\s+grave", r"retiro\s+anticipado",
]
POSITIVOS = [
    r"felicit\w*", r"excelente\w*", "sobresaliente", r"destac\w*", "buen trabajo", "gran trabajo", "buen desempeno",
    "muy bien", "gracias", r"agradec\w*", r"reconocimiento\w*", r"reconoc\w*\s+(?:su|el|la|los)\s+(?:labor|trabajo|aporte|esfuerzo|desempeno)",
    r"premi\w*", r"logr\w*", r"cumplimiento\s+de\s+(?:metas|objetivos|indicadores)",
    r"cumpli\w*\s+(?:con\s+)?(?:las\s+|los\s+)?(?:metas|objetivos|indicadores|expectativas)", r"supero\s+(?:las\s+|los\s+)?(?:metas|objetivos|expectativas)",
    "admirable", "impecable", "ejemplar", r"proactiv\w*", "liderazgo", "bonificacion", "incentivo", "empleado del mes",
    "mencion de honor", "primer lugar", "magnifico", "fantastico", "estupendo", "brillante",
]

# --- Criterios de estructura (lo que una buena anotación debe contener) ---
TEMPORAL = [
    r"\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?", r"\d{4}-\d{2}-\d{2}",
    r"\d{1,2}\s+de\s+(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre|diciembre)",
    r"(?:el\s+)?(?:lunes|martes|miercoles|jueves|viernes|sabado|domingo)", "hoy", "ayer", "anteayer", "anoche",
    "esta semana", "la semana pasada", "este mes", "el mes pasado",
    r"el\s+dia\s+\d+", r"a\s+las\s+\d{1,2}", r"durante\s+el\s+turno", "esta manana", "esta tarde",
    r"durante\s+(?:el|los)\s+(?:ultimo|ultimos|mes|meses|trimestre|semestre|ano)",
]
CUANTIFICACION = [
    r"\d+\s+(?:veces|vez|ocasion\w*|dias?|minutos?|horas?|semanas?)", r"(?:una|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|varias|primera|segunda|tercera|cuarta)\s+(?:veces|vez|ocasion\w*)",
    r"veces", r"ocasion\w*", r"reiterad\w*", r"repetid\w*",
]
CONSECUENCIA = [
    r"se\s+acuerd\w*", r"acuerd\w*", r"compromis\w*", r"comprometi\w*", "plan de mejora", "plan de accion", "seguimiento",
    "proxima vez", "de repetirse", "en caso de", "nueva falta", r"sancion\w*", "proceso disciplinario",
    r"se\s+(?:le\s+)?advierte", r"medidas?", r"correctiv\w*", "suspension", "se citara", r"reincidencia",
    r"se\s+(?:le\s+)?informa\s+que", r"podria\s+(?:derivar|generar|acarrear)", r"debera",
]
NOTIFICACION = [
    r"se\s+le\s+(?:informo|notifico|comunico|hizo\s+saber|dio\s+a\s+conocer|explico)", r"fue\s+notificad\w*",
    r"se\s+(?:informo|notifico|comunico)\s+(?:al|a)\s+(?:empleado|trabajador|colaborador)", "enterad[oa]",
    r"firm[oa]\w*", r"en\s+presencia", "verbalmente", "por escrito", "se dio a conocer", "se le informa",
    r"se\s+(?:le\s+)?comunica", r"se\s+(?:le\s+)?notifica",
]
DESCARGOS = [
    r"descargo\w*", "version del empleado", "su version", r"manifest\w*", r"explic\w*", r"argument\w*",
    r"respondi\w*", r"aclar\w*", "justificacion", "sin justificar", "sin justificacion", "no justifico",
    "dio su version", "sin explicacion",
]
LOGRO = [
    r"proyecto\w*", r"meta\w*", r"objetivo\w*", r"cliente\w*", r"entrega\w*", r"cierre", r"resultado\w*", r"venta\w*",
    r"informe\w*", r"reporte\w*", r"presentacion\w*", r"auditoria\w*", r"lanzamiento", r"certificacion", r"indicador\w*",
    r"incidente\w*", r"migracion", r"capacitacion\w*", r"evento\w*", r"propuesta\w*", r"licitacion", r"producto\w*",
    r"proceso\w*", r"equipo\w*", r"mejora\w*", r"ahorro", r"calidad", r"servicio", r"\d+",
]
PERIODO = [
    r"trimestre\w*", r"semestre\w*", "ano", "anos", r"mes(?:es)?", "periodo", "durante", "antiguedad",
    "de servicio", r"\d+\s+anos", "temporada", "esta semana", "ultimo",
]
SEGUIMIENTO = [
    "seguimiento", r"se\s+acuerd\w*", r"se\s+recomienda", r"se\s+sugiere", "pendiente", "queda", r"se\s+programa\w*",
    "proxima", "proximo", r"revisar", r"se\s+solicita", r"se\s+pide", "plazo", "fecha limite", r"se\s+debe",
    r"debe\w*", r"validar", r"verificar", r"actualizar", r"enviar", r"entregar",
]
GRAVEDAD = [
    "falta grave", "proceso disciplinario", "terminacion", "despido", "suspension", "justa causa", "sancion disciplinaria",
]
NORMA = [
    "reglamento", "articulo", "codigo sustantivo", "contrato", "manual", "politica", "clausula", r"\bley\b",
    "numeral", "literal", "protocolo", "estatuto",
]
