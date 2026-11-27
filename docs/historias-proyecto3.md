# Historias de usuario del Proyecto 3

Historias para registrar en el tablero de GitHub Projects, con el mismo formato de la plantilla `.github/ISSUE_TEMPLATE/historia-de-usuario.md`. Cada componente del enunciado tiene al menos una historia:

| Componente | Historias |
|---|---|
| Monitoreo y observabilidad | HU-C1, HU-C2, HU-C3 |
| Autenticación | HU-C4 |
| Kubernetes | HU-C5, HU-C6, HU-C7, HU-C8 |
| Inteligencia artificial | HU-C9, HU-C10, HU-C11 |
| Documentación | HU-C12 |

Los sprints (1 a 3) son una propuesta: renómbralos como corresponda en tu tablero (por ejemplo, Sprint 4 a 6). Los responsables son una propuesta de reparto para tres integrantes; reemplaza `@[tercer-integrante]` por el usuario de GitHub del tercer miembro.

**Crear los issues automáticamente:** con la CLI de GitHub autenticada (`gh auth login`), `./scripts/crear-historias.sh` crea los 12 issues en el repositorio. Si defines `PROYECTO=<número del tablero>`, también los agrega al GitHub Project.

Total: 12 historias, 45 puntos.


---

## HU-C1 — Exponer /metrics con métricas de la API

# Historia de Usuario: Exponer /metrics con métricas de la API

## Como desarrollador del equipo
Quiero que la API exponga un endpoint /metrics con contador de requests, latencia y un gauge
Para poder observar su comportamiento en tiempo real

## Criterios de Aceptación:
- [ ] GET /metrics responde en formato Prometheus sin autenticación y fuera del prefijo /api
- [ ] Existen http_requests_total, http_request_duration_seconds (histograma) y http_requests_in_progress (gauge)
- [ ] La etiqueta endpoint usa la ruta definida, no la URL real
- [ ] Las probes y /metrics no se cuentan a sí mismas
- [ ] Pruebas pytest de las métricas en verde

## Componente: Monitoreo
## Estimación: 3
## Sprint: 1
## Responsable: @bdmaderam


---

## HU-C2 — Prometheus y Grafana con dashboard de 3+ paneles

# Historia de Usuario: Prometheus y Grafana con dashboard de 3+ paneles

## Como desarrollador del equipo
Quiero un Prometheus y un Grafana con un dashboard cargado automáticamente
Para ver throughput, latencia y errores sin configurar nada a mano

## Criterios de Aceptación:
- [ ] docker-compose.monitoring.yml levanta Prometheus (9090) y Grafana (3001)
- [ ] El dashboard tiene throughput, latencia (p95/p99) y una métrica adicional (errores, requests en curso, empleados activos)
- [ ] El dashboard y el datasource se cargan por provisioning
- [ ] Documentado en el README

## Componente: Monitoreo
## Estimación: 3
## Sprint: 1
## Responsable: @Danielsuarez1-ops


---

## HU-C3 — Script de tráfico de prueba

# Historia de Usuario: Script de tráfico de prueba

## Como desarrollador del equipo
Quiero un script que genere tráfico hacia la API
Para llenar de datos los paneles y demostrar el autoescalado

## Criterios de Aceptación:
- [ ] scripts/generate-traffic.py inicia sesión y mezcla lecturas, escrituras, llamadas de IA y errores
- [ ] Parámetros --url, --duracion, --hilos y --pausa
- [ ] Los paneles de Grafana se mueven al ejecutarlo

## Componente: Monitoreo
## Estimación: 2
## Sprint: 1
## Responsable: @[tercer-integrante]


---

## HU-C4 — Endurecer la autenticación JWT y mover las llaves a Secret

# Historia de Usuario: Endurecer la autenticación JWT y mover las llaves a Secret

## Como administrador del sistema
Quiero que la autenticación use llaves gestionadas como Secret y que la contraseña del admin no esté escrita en el código
Para que ninguna credencial viva en el repositorio

## Criterios de Aceptación:
- [ ] Crear, actualizar y eliminar exigen token JWT (401 sin token)
- [ ] JWT_SECRET y ADMIN_PASSWORD llegan por variable de entorno desde el Secret de Kubernetes
- [ ] k8s/secret.example.yaml como plantilla y k8s/secret.yaml en .gitignore
- [ ] Pruebas de autenticación en verde

## Componente: Autenticación
## Estimación: 2
## Sprint: 1
## Responsable: @bdmaderam


---

## HU-C5 — Publicar las imágenes Docker en GitHub Container Registry

# Historia de Usuario: Publicar las imágenes Docker en GitHub Container Registry

## Como desarrollador del equipo
Quiero que las imágenes del backend y del frontend se construyan y publiquen en ghcr.io
Para poder desplegarlas en cualquier clúster

## Criterios de Aceptación:
- [ ] Workflow imagenes.yml construye y publica ambas imágenes
- [ ] El frontend se construye con REACT_APP_API_URL=/api
- [ ] Las imágenes quedan públicas y descargables

## Componente: Kubernetes
## Estimación: 3
## Sprint: 2
## Responsable: @Danielsuarez1-ops


---

## HU-C6 — Manifiestos de Kubernetes de la aplicación

# Historia de Usuario: Manifiestos de Kubernetes de la aplicación

## Como desarrollador del equipo
Quiero manifiestos en k8s/ para desplegar la aplicación completa
Para levantar todo el sistema con un solo comando

## Criterios de Aceptación:
- [ ] Deployment de la API con 2 réplicas, Service, ConfigMap y Secret
- [ ] Probes de liveness (/api/salud) y readiness (/api/listo)
- [ ] resources.requests y resources.limits definidos
- [ ] PostgreSQL en StatefulSet con volumen persistente
- [ ] kubectl apply -k k8s/ deja todos los pods en Running

## Componente: Kubernetes
## Estimación: 8
## Sprint: 2
## Responsable: @bdmaderam


---

## HU-C7 — Prometheus y Grafana dentro del clúster

# Historia de Usuario: Prometheus y Grafana dentro del clúster

## Como desarrollador del equipo
Quiero kube-prometheus-stack con un ServiceMonitor de la API y el dashboard cargado
Para monitorear la aplicación donde corre

## Criterios de Aceptación:
- [ ] Valores de Helm en k8s/monitoring/
- [ ] ServiceMonitor y PrometheusRule aplicados con kubectl apply -k k8s/monitoring/
- [ ] El dashboard aparece en Grafana sin importarlo
- [ ] El target de la API aparece UP en Prometheus

## Componente: Kubernetes
## Estimación: 5
## Sprint: 2
## Responsable: @[tercer-integrante]


---

## HU-C8 — Ingress y HorizontalPodAutoscaler (opcional)

# Historia de Usuario: Ingress y HorizontalPodAutoscaler (opcional)

## Como usuario de la aplicación
Quiero entrar por una sola URL y que la API escale con la carga
Para tener disponibilidad bajo uso intenso

## Criterios de Aceptación:
- [ ] Ingress enruta / al frontend y /api al backend (no publica /metrics)
- [ ] HPA escala la API entre 2 y 6 réplicas según CPU
- [ ] Se demuestra con generate-traffic.py --hilos 40 --pausa 0

## Componente: Kubernetes
## Estimación: 3
## Sprint: 2
## Responsable: @Danielsuarez1-ops


---

## HU-C9 — Base de conocimiento: temas y reglas de calidad

# Historia de Usuario: Base de conocimiento: temas y reglas de calidad

## Como jefe de área
Quiero que el sistema conozca los temas de las anotaciones y las buenas prácticas de redacción
Para detectar problemas que se repiten y evitar anotaciones incompletas o riesgosas

## Criterios de Aceptación:
- [ ] Catálogo de al menos 12 temas en lexico_temas.py y al menos 25 reglas de calidad en revisor.py
- [ ] Reglas por categoría: forma, lenguaje, contenido según el tipo, coherencia e historial
- [ ] Manejo de negaciones y puntaje de 0 a 100 con nivel
- [ ] Una prueba positiva y una negativa por regla; textos bien escritos salen 'Lista'

## Componente: Inteligencia artificial
## Estimación: 5
## Sprint: 3
## Responsable: @[tercer-integrante]


---

## HU-C10 — Detectar temas y reincidencia al revisar una anotación

# Historia de Usuario: Detectar temas y reincidencia al revisar una anotación

## Como jefe de área
Quiero que al revisar una anotación el sistema muestre sus temas y avise si el empleado repite uno
Para identificar patrones y no tratar cada hecho como aislado

## Criterios de Aceptación:
- [ ] POST /api/ia/revisar-anotacion (JWT) devuelve puntaje, problemas, temas y reincidencias
- [ ] Botón 'Revisar calidad' en Nueva y Editar anotación, y tarjeta 'Temas y reincidencia' en el detalle del empleado
- [ ] GET /api/ia/temas-empleado/{id}, GET /api/ia/reincidencias y GET /api/ia/auditoria-anotaciones
- [ ] Pruebas de backend y de frontend en verde

## Componente: Inteligencia artificial
## Estimación: 5
## Sprint: 3
## Responsable: @bdmaderam


---

## HU-C11 — Métricas de IA en Grafana y documento docs/ia.md

# Historia de Usuario: Métricas de IA en Grafana y documento docs/ia.md

## Como profesor evaluador
Quiero ver las métricas del revisor en Grafana y un documento que explique la decisión
Para entender el problema, el enfoque, las reglas y las limitaciones

## Criterios de Aceptación:
- [ ] Métricas ia_revisiones_total, ia_puntaje_calidad, ia_hallazgos_total, ia_revision_duracion_seconds, ia_reglas_cargadas, ia_temas_detectados_total e ia_reincidencias_total
- [ ] Fila de IA en el dashboard de Grafana
- [ ] docs/ia.md con problema, enfoque, reglas, pruebas, limitaciones y mejoras

## Componente: Inteligencia artificial
## Estimación: 3
## Sprint: 3
## Responsable: @Danielsuarez1-ops


---

## HU-C12 — README y documentación del Proyecto 3

# Historia de Usuario: README y documentación del Proyecto 3

## Como persona nueva en el proyecto
Quiero un README que explique cómo construir las imágenes, desplegar y correr todo
Para replicar el proyecto sin ayuda

## Criterios de Aceptación:
- [ ] README con secciones de Kubernetes, monitoreo e IA
- [ ] Manifiestos comentados y organizados
- [ ] Historias del Proyecto 3 registradas en el tablero

## Componente: Documentación
## Estimación: 3
## Sprint: 3
## Responsable: @[tercer-integrante]
