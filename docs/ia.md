# Funcionalidad de inteligencia artificial: detección de temas, reincidencia y revisión de calidad

> Historias de usuario: **HU-C9, HU-C10 y HU-C11** (ver [historias-proyecto3.md](historias-proyecto3.md)).
> Código: `backend/app/services/lexico_temas.py` y `temas.py` (temas y reincidencia), `lexico.py` y `revisor.py` (calidad de redacción),
> `backend/app/api/ia.py` (endpoints) y `frontend/src/App.js` (componentes `RevisarAnotacion` y `TemasEmpleado`).

## 1. Problema y valor para el usuario

Las anotaciones de un empleado se leen una por una, y así es difícil ver lo importante: **si el mismo problema se repite**. Elegir el tipo
("Llamado de atención", "Felicitación"...) tampoco ayuda, porque es lo más fácil de hacer a mano. La IA aporta en dos cosas:

1. **Temas y reincidencia (función principal).** Cada anotación se etiqueta con temas (puntualidad, asistencia, seguridad, trato,
   desempeño, normas, recursos, comunicación, trabajo en equipo, atención al cliente, liderazgo, capacitación, trámites administrativos).
   Si un empleado repite un tema **negativo** dentro de 90 días, el sistema avisa: 2 veces = *se repite*, 3 o más = *reincidente*.
   - Al revisar una anotación nueva: etiquetas del texto + alerta si ese tema ya aparece en su historial.
   - En el detalle del empleado: tarjeta «Temas y reincidencia» con el perfil de temas y las alertas.
   - `GET /api/ia/reincidencias`: lista de todos los empleados con temas repetidos (la más grave primero).
2. **Revisión de calidad de redacción.** Antes de guardar, un puntaje de 0 a 100, los problemas detectados (insultos, juicios de valor,
   falta de fecha o de compromiso, datos sensibles, duplicados...) y cómo corregirlos.

La IA **asiste, no decide**: nunca guarda, sanciona ni clasifica por su cuenta; una alerta de reincidencia es un aviso para que una persona revise.

## 2. Enfoque: sistemas basados en reglas (IA simbólica)

| Aspecto | Decisión |
|---|---|
| Tipo | Sistema experto: base de conocimiento (léxico + 26 reglas) y motor de inferencia que las aplica |
| Tecnología | Python estándar (expresiones regulares, sin librerías de IA ni modelos entrenados) |
| Resultado | Determinista y explicable: cada conclusión indica qué regla la produjo y qué texto la activó |

**Por qué reglas y no un modelo entrenado o un LLM:**

- **Costo cero y sin claves.** No hay API de pago ni dependencia de servicios externos.
- **Privacidad.** Las anotaciones son datos laborales sensibles (Ley 1581 de 2012); el texto nunca sale del clúster.
- **Despliegue simple.** No hay archivo de modelo, entrenamiento ni librerías pesadas: la imagen Docker solo lleva código.
- **Auditable.** Una regla se puede leer, discutir con recursos humanos y corregir en minutos. Un clasificador entrenado con datos
  sintéticos nos falló en la práctica (confundía tipos), por eso se descartó.
- **Reglas que vienen del dominio**: buenas prácticas de redacción disciplinaria (hechos, fecha, frecuencia, compromiso, notificación,
  descargos, norma aplicable).

### Cómo decide
1. **Normaliza** el texto (minúsculas, sin tildes).
2. Cada regla aplica a ciertos tipos (por ejemplo, "notificación al empleado" solo a llamados de atención).
3. **Negaciones**: "no cumplió las metas" cuenta como negativo y "sin ausencias" como positivo.
4. **Historial real**: con `empleado_id` consulta las anotaciones anteriores del empleado para detectar duplicados y reincidencia.
5. **Puntaje** = 100 − penalizaciones (error 25, advertencia 10, sugerencia 4, informativo 0). Cualquier error implica
   *Requiere corrección*; ≥ 85 es *Lista*; < 60 es *Requiere corrección*.

## 3. Base de conocimiento (26 reglas)

| Id | Categoría | Severidad | Criterio que verifica | Aplica a |
|---|---|---|---|---|
| F01 | Forma | advertencia | Tiene la extensión suficiente para entenderse | todos |
| F02 | Forma | sugerencia | Es concisa | todos |
| F03 | Forma | error | Es legible | todos |
| F04 | Forma | sugerencia | Mantiene un tono sereno | todos |
| F05 | Forma | error | La fecha del registro es válida | todos |
| F06 | Forma | advertencia | Se registra sin demora | llamado |
| L01 | Lenguaje | error | No usa insultos ni lenguaje ofensivo | todos |
| L02 | Lenguaje | advertencia | Describe hechos observables, no juicios sobre la persona | todos |
| L03 | Lenguaje | sugerencia | Evita absolutos (siempre, nunca...) | todos |
| L04 | Lenguaje | advertencia | Se limita a lo comprobado, sin suposiciones | todos |
| L05 | Lenguaje | advertencia | Se basa en hechos directos, no en rumores | todos |
| L06 | Lenguaje | advertencia | No incluye datos sensibles innecesarios | todos |
| L07 | Lenguaje | advertencia | No expone datos personales de terceros | todos |
| C01 | Contenido | advertencia | Indica cuándo ocurrió el hecho | llamado, observacion |
| C02 | Contenido | sugerencia | Indica la frecuencia o la cantidad | llamado |
| C03 | Contenido | advertencia | Deja claro el compromiso o la consecuencia | llamado |
| C04 | Contenido | sugerencia | Deja constancia de que se notificó al empleado | llamado |
| C05 | Contenido | sugerencia | Registra la versión o los descargos del empleado | llamado |
| C06 | Contenido | advertencia | Cita la norma cuando habla de faltas graves o sanciones | llamado |
| C07 | Contenido | sugerencia | Dice qué hizo o logró la persona | felicitacion, reconocimiento |
| C08 | Contenido | sugerencia | Indica el periodo o motivo del reconocimiento | reconocimiento |
| C09 | Contenido | sugerencia | Define la acción o el seguimiento | observacion |
| T01 | Coherencia | advertencia | El texto corresponde al tipo elegido | felicitacion, llamado, reconocimiento |
| T02 | Coherencia | sugerencia | Trata un solo tema (no mezcla elogios con faltas) | felicitacion, llamado, observacion, reconocimiento |
| H01 | Historial | advertencia | No repite una anotación existente | todos |
| H02 | Historial | info | Considera los antecedentes del empleado | llamado |

El catálogo también se puede consultar con `GET /api/ia/reglas`.

### Detección de temas y reincidencia
- **Catálogo de temas** en `lexico_temas.py` (13 temas, cada uno con sus palabras). Agregar una palabra o un tema es editar ese archivo.
- **Tono** de cada tema: negativo si el tipo es *Llamado de atención*; positivo si es *Felicitación* o *Reconocimiento*; en *Observación* u *Otro* se decide por las palabras del texto. Liderazgo y capacitación son siempre positivos.
- **Negaciones**: "sin tardanzas" o "no se ausentó" no activan el tema.
- **Reincidencia**: solo cuentan anotaciones con el mismo tema en tono negativo dentro de la ventana (90 días por defecto, configurable). Una felicitación nunca genera alerta.
- **Por qué reglas y no un modelo entrenado**: la base de datos real tiene muy pocas anotaciones para entrenar, y un modelo sobre datos sintéticos ya falló en este proyecto. Con reglas funciona desde la primera anotación, es gratis y cada etiqueta muestra las palabras que la activaron. Si algún día hay cientos de anotaciones reales etiquetadas, se podría entrenar un modelo y comparar contra estas reglas.

## 4. Endpoints (todos exigen JWT)

| Método y ruta | Uso |
|---|---|
| `POST /api/ia/revisar-anotacion` | Cuerpo: `descripcion`, y opcionalmente `tipo`, `fecha`, `empleado_id`, `anotacion_id` |
| `GET /api/ia/auditoria-anotaciones?nivel_maximo=70` | Anotaciones guardadas con puntaje ≤ umbral |
| `GET /api/ia/reglas` | Catálogo de reglas |
| `POST /api/ia/revisar-anotacion` (con `empleado_id`) | Además de la calidad, devuelve `temas` y `reincidencias` |
| `GET /api/ia/temas-empleado/{id}?dias=90` | Perfil de temas del empleado y alertas (404 si no existe) |
| `GET /api/ia/reincidencias?dias=90&minimo=2` | Empleados con un tema negativo repetido |

## 5. Métricas de monitoreo (Prometheus / Grafana)

| Métrica | Qué mide |
|---|---|
| `ia_revisiones_total{nivel}` | Revisiones realizadas por resultado |
| `ia_puntaje_calidad` (histograma) | Distribución de puntajes |
| `ia_hallazgos_total{regla,severidad}` | Qué problemas son más frecuentes |
| `ia_revision_duracion_seconds` (histograma) | Latencia de cada revisión (del orden de milisegundos) |
| `ia_reglas_cargadas` | Reglas activas por pod |
| `ia_temas_detectados_total{tema,tono}` | Temas detectados |
| `ia_reincidencias_total{tema,nivel}` | Alertas de reincidencia emitidas |

Se muestran en la fila "Funcionalidad de IA" del dashboard *RHControl - API e IA*.

## 6. Pruebas

`backend/tests/test_temas.py`: un caso positivo y uno negativo por tema, negaciones, tono, reincidencia (2.ª y 3.ª vez, ventana, otros temas, felicitaciones, edición) y endpoints. `backend/tests/test_ia.py`: una prueba positiva y una negativa por regla, textos bien escritos de cada tipo que deben salir
*Lista* (sin falsos positivos), negaciones, historial, validación de entrada, JWT y métricas. Frontend: pruebas de Jest del panel.

## 7. Limitaciones (importante para la sustentación)

- **Los temas dependen del vocabulario.** Una anotación con palabras que el catálogo no conoce queda sin tema y no cuenta para la reincidencia. Algunas palabras amplias (p. ej. «informe», «equipo») pueden etiquetar un tema de más.
- **La reincidencia se calcula por tema, no por la gravedad del hecho**; no distingue dos tardanzas de 5 minutos de dos de 3 horas.

- **No es perfecto ni "100 %".** El sistema detecta lo que su vocabulario conoce; una jerga nueva o una ofensa no listada pasará. Por eso
  se diseñó para ampliarse: basta agregar palabras a `lexico.py` o una función `@regla` en `revisor.py`.
- **No entiende significado, solo patrones.** Una ironía o un texto bien escrito con contenido falso no se detectan.
- **Español colombiano genérico.** Faltan modismos regionales.
- **No es asesoría legal.** Las reglas sobre debido proceso y datos sensibles son buenas prácticas; la validación final es de recursos humanos o un abogado.
- **El puntaje es orientativo**: las penalizaciones se escogieron por criterio, no se calibraron con datos reales.

## 8. Mejoras futuras

- Medir con anotaciones reales y ajustar el vocabulario según los falsos positivos y negativos que reporten los usuarios.
- Combinar las reglas con un LLM *autoalojado* solo para reescribir la redacción, manteniendo las reglas como control.
- Reglas configurables por empresa (según su reglamento interno).
