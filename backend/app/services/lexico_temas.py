"""Catálogo de temas para etiquetar anotaciones (puntualidad, seguridad, trato...).

Cada tema tiene un nombre legible y una lista de fragmentos de expresión regular escritos SIN tildes
y en minúsculas (el texto se normaliza antes de compararlo). `positivo=True` marca temas que solo
pueden describir algo bueno (p. ej. liderazgo), y por eso nunca generan alerta de reincidencia.
Para agregar un tema o una palabra basta con editar este archivo.
"""

TEMAS = {
    "puntualidad": {
        "nombre": "Puntualidad",
        "patrones": [
            r"lleg\w*\s+tarde", r"tardanza\w*", r"retard\w*", r"impuntual\w*", r"puntualidad", r"puntual",
            r"hora\s+de\s+(?:entrada|ingreso|llegada)", r"minutos\s+tarde", r"ingreso\s+tarde", r"llegada\s+tarde",
            r"demor\w*\s+en\s+(?:llegar|ingresar)", r"salio\s+(?:antes|temprano)", r"salida\s+anticipada",
        ],
    },
    "asistencia": {
        "nombre": "Asistencia y ausentismo",
        "patrones": [
            r"ausen\w*", r"inasistencia\w*", r"no\s+asisti\w*", r"no\s+se\s+presento", r"falto\b", r"faltas?\s+injustificad\w*",
            r"faltas?\s+al\s+trabajo", r"sin\s+permiso", r"sin\s+avisar", r"abandon\w*\s+(?:el|su)\s+(?:puesto|turno)",
            r"permisos?\s+frecuentes", r"incapacidad\w*", r"ausentismo",
        ],
    },
    "seguridad": {
        "nombre": "Seguridad y salud en el trabajo",
        "patrones": [
            r"seguridad\s+(?:industrial|laboral|en\s+el\s+trabajo)", r"sst", r"epp", r"casco", r"guantes", r"gafas\s+de\s+seguridad",
            r"elementos\s+de\s+proteccion", r"equipo\s+de\s+proteccion", r"accidente\w*", r"incidente\w*", r"riesgo\w*", r"peligro\w*",
            r"arnes", r"extintor\w*", r"evacuacion", r"protocolo\s+de\s+seguridad", r"normas?\s+de\s+seguridad", r"bioseguridad",
            r"tapabocas", r"senalizacion",
        ],
    },
    "trato": {
        "nombre": "Trato y respeto",
        "patrones": [
            r"irrespet\w*", r"falt\w*\s+(?:de\s+)?respeto", r"grit\w*", r"discusion\w*", r"discuti\w*", r"pele\w*", r"conflicto\w*",
            r"maltrat\w*", r"trato\s+(?:inadecuado|grosero|irrespetuoso)", r"agresion\w*", r"agresiv\w*", r"acoso", r"groser\w*",
            r"ofensa\w*", r"insult\w*", r"amenaz\w*", r"mal\s+trato", r"burl\w*", r"respetuos\w*", r"cordial\w*", r"amable\w*",
            r"buen\s+trato", r"trato", r"convivencia",
        ],
    },
    "desempeno": {
        "nombre": "Calidad y cumplimiento del trabajo",
        "patrones": [
            r"incumpl\w*", r"no\s+entreg\w*", r"entrego\s+tarde", r"entrega\s+tardia", r"informe\w*", r"reporte\w*", r"meta\w*",
            r"objetivo\w*", r"errores?", r"error\w*", r"reproceso\w*", r"calidad\s+del\s+trabajo", r"tarea\w*\s+(?:pendiente|sin\s+terminar)",
            r"productividad", r"rendimiento", r"bajo\s+desempeno", r"desempeno", r"resultado\w*", r"plazo\w*", r"fecha\s+de\s+entrega",
            r"fecha\s+acordada", r"proyecto\w*",
        ],
    },
    "normas": {
        "nombre": "Cumplimiento de normas y procedimientos",
        "patrones": [
            r"reglamento\w*", r"procedimiento\w*", r"politica\w*\s+(?:de\s+la\s+empresa|interna)", r"norma\w*", r"protocolo\w*",
            r"incumpl\w*\s+(?:la|el|las|los)\s+(?:norma|reglamento|procedimiento|politica|protocolo)", r"desobedec\w*", r"insubordinacion",
            r"instruccion\w*", r"orden\w*\s+(?:del|de\s+su)\s+(?:jefe|superior)", r"uniforme", r"carnet", r"dotacion", r"codigo\s+de\s+conducta",
            r"infraccion\w*", r"violacion",
        ],
    },
    "recursos": {
        "nombre": "Uso de equipos y recursos de la empresa",
        "patrones": [
            r"uso\s+indebido", r"equipos?\s+de\s+(?:la\s+)?empresa", r"computador\w*", r"celular\w*", r"internet", r"redes\s+sociales",
            r"herramienta\w*", r"vehiculo\w*", r"inventario\w*", r"perdida\s+de", r"dano\s+(?:a|de|en)", r"extravi\w*", r"material\w*",
            r"combustible", r"caja\s+menor", r"dinero", r"faltante\w*",
        ],
    },
    "comunicacion": {
        "nombre": "Comunicación",
        "patrones": [
            r"comunicacion", r"comunic\w*", r"no\s+respond\w*", r"no\s+avis\w*", r"no\s+informo", r"no\s+reporto", r"correo\w*",
            r"mensaje\w*", r"reunion\w*", r"escucha", r"claridad", r"retroalimentacion", r"feedback",
        ],
    },
    "equipo": {
        "nombre": "Trabajo en equipo",
        "patrones": [
            r"trabajo\s+en\s+equipo", r"equipo", r"colabor\w*", r"compan\w*ros?", r"apoy\w*\s+a", r"coordin\w*", r"cooperacion", r"cooper\w*",
            r"no\s+colabor\w*", r"individualista", r"ayud\w*",
        ],
    },
    "cliente": {
        "nombre": "Atención al cliente",
        "patrones": [
            r"clientes?", r"atencion\s+al\s+(?:cliente|usuario|publico)", r"usuarios?", r"queja\w*\s+de(?:l)?\s+cliente", r"servicio\s+al\s+cliente",
            r"reclamo\w*", r"satisfaccion\s+del\s+cliente",
        ],
    },
    "liderazgo": {
        "nombre": "Liderazgo e iniciativa",
        "positivo": True,
        "patrones": [
            r"liderazgo", r"lider\w*", r"iniciativa\w*", r"propuso", r"propuesta\w*", r"mejora\s+(?:de\s+)?proceso\w*", r"innovaci\w*",
            r"proactiv\w*", r"mentor\w*", r"capacit\w*\s+a", r"guio",
        ],
    },
    "formacion": {
        "nombre": "Capacitación y desarrollo",
        "positivo": True,
        "patrones": [
            r"capacitacion\w*", r"curso\w*", r"certificacion\w*", r"certificad\w*", r"formacion", r"diplomado\w*", r"entrenamiento\w*",
            r"aprendizaje", r"taller\w*", r"ascenso", r"promocion",
        ],
    },
    "administrativo": {
        "nombre": "Datos y trámites administrativos",
        "patrones": [
            r"nomina", r"cuenta\s+bancaria", r"datos\s+de\s+contacto", r"actualizar\s+(?:los\s+)?datos", r"documentos?", r"contrato\w*",
            r"afiliacion\w*", r"eps", r"pension", r"cesantias", r"vacaciones", r"horario\w*", r"turno\w*", r"cambio\s+de\s+horario",
            r"licencia\w*", r"tramite\w*",
        ],
    },
}
