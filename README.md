# RHControl

![CI](https://github.com/bdmaderam/RHControl---Gesti-n/actions/workflows/ci.yml/badge.svg)
![Deploy](https://github.com/bdmaderam/RHControl---Gesti-n/actions/workflows/deploy.yml/badge.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Python%203.12-009688?style=flat-square&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Cloud%20Run-4285F4?style=flat-square&logo=googlecloud&logoColor=white)

**RHControl** es una aplicación web para la gestión de recursos humanos: registro de empleados, consulta de su información laboral, anotaciones (reconocimientos, observaciones, llamados de atención) y reportes con exportación a CSV. Es el proyecto sobre el que se desarrollaron el **Proyecto 2 – Gestión colaborativa con GitHub Projects** y el **Proyecto 3 – Monitoreo, Kubernetes, autenticación e inteligencia artificial** de la materia *Desarrollo de Aplicaciones en la Nube*.

## Aplicación en producción

| Servicio | URL |
|---|---|
| Frontend | https://rhcontrol-frontend-3cugxgrrsa-uc.a.run.app |
| API (backend) | https://rhcontrol-backend-3cugxgrrsa-uc.a.run.app |
| Documentación interactiva (Swagger) | https://rhcontrol-backend-3cugxgrrsa-uc.a.run.app/docs |

Usuario de demostración: `admin` / `admin123` (se crea al iniciar la API por primera vez; debe cambiarse en un uso real).

> Los servicios de Cloud Run se escalan a cero cuando no hay tráfico, por lo que la primera petición después de un rato puede tardar unos segundos.

## Tabla de contenido

- [Características](#características)
- [Arquitectura](#arquitectura)
- [Tecnologías](#tecnologías)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Ejecución local con Docker](#ejecución-local-con-docker)
- [Monitoreo con Prometheus y Grafana](#monitoreo-con-prometheus-y-grafana)
- [Despliegue en Kubernetes](#despliegue-en-kubernetes)
- [Autenticación](#autenticación)
- [Inteligencia artificial](#inteligencia-artificial)
- [Ejecución local sin Docker](#ejecución-local-sin-docker)
- [Variables de entorno](#variables-de-entorno)
- [Pruebas](#pruebas)
- [Integración y despliegue continuo](#integración-y-despliegue-continuo)
- [Despliegue en Google Cloud](#despliegue-en-google-cloud)
- [Historias de usuario y sprints](#historias-de-usuario-y-sprints)
- [Flujo de trabajo del equipo](#flujo-de-trabajo-del-equipo)
- [Documentación adicional](#documentación-adicional)
- [Autores](#autores)
- [Licencia](#licencia)

## Características

- Inicio de sesión con usuario y contraseña; la API devuelve un token JWT (Bearer) que el frontend envía en cada petición. Si el token vence o es inválido, la sesión se cierra automáticamente (401).
- CRUD completo de empleados con validaciones (tipo de documento CC/CE/PA, documento único, salario no negativo).
- Búsqueda de empleados por nombre, número de documento y estado (activo/inactivo).
- Anotaciones por empleado: crear, consultar, editar y eliminar.
- Panel de control con indicadores generales y módulo de reportes con exportación a CSV.
- Estados de carga, mensajes de error claros y botones deshabilitados mientras se guarda.
- Pruebas automatizadas del backend y del frontend ejecutadas en cada Pull Request.
- **Monitoreo:** endpoint `/metrics` (Prometheus) y dashboard en Grafana con throughput, latencia, errores y métricas de IA.
- **Kubernetes:** manifiestos en `k8s/` (API con 2 réplicas, probes, recursos, ConfigMap, Secret, PostgreSQL con volumen, Ingress y HPA).
- **IA:** al escribir una anotación, etiqueta cada anotación con temas (puntualidad, seguridad, trato...), **avisa cuando un empleado repite un tema negativo** y revisa la calidad de la redacción (puntaje 0-100 y cómo corregirla). Todo con reglas, sin costo. Ver [docs/ia.md](docs/ia.md).

## Arquitectura

```
                     ┌──────────────────────── Google Cloud ────────────────────────┐
                     │                                                               │
 Navegador ────────► │  Cloud Run: rhcontrol-frontend (nginx + React, puerto 80)     │
     │               │                                                               │
     └─ API REST ──► │  Cloud Run: rhcontrol-backend (FastAPI, puerto 8000)          │
        (JWT)        │        │  secretos: DATABASE_URL, JWT_SECRET (Secret Manager) │
                     │        ▼                                                      │
                     │  Cloud SQL: PostgreSQL 16 (socket /cloudsql)                  │
                     │                                                               │
                     │  Artifact Registry: imágenes Docker del backend y frontend    │
                     └───────────────────────────────────────────────────────────────┘
                                         ▲
   GitHub (production) ── GitHub Actions ┘  (build, push y deploy)
```

## Tecnologías

| Capa | Tecnologías |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2, Pydantic v2, PyJWT, psycopg 3, Uvicorn |
| Base de datos | PostgreSQL 16 (Docker en local, Cloud SQL en producción) |
| Frontend | React 18, React Router 6, Chart.js, Create React App (react-scripts 5) |
| Pruebas | pytest + httpx (backend), Jest + Testing Library (frontend) |
| Contenedores | Docker y Docker Compose; nginx para servir el frontend |
| Orquestación | Kubernetes (Minikube, kind, k3d o Docker Desktop), Kustomize, ingress-nginx, HPA |
| Observabilidad | Prometheus, Grafana, `prometheus-client`, kube-prometheus-stack (Helm) |
| Inteligencia artificial | Sistema experto basado en reglas (Python estándar, sin modelos ni claves) |
| Registro de imágenes | GitHub Container Registry (`ghcr.io`) |
| CI/CD | GitHub Actions |
| Nube | Google Cloud: Cloud Run, Cloud SQL, Artifact Registry, Secret Manager |
| Gestión | GitHub Projects (tablero Kanban), Issues, Pull Requests y rulesets |

## Estructura del repositorio

```
.
├── .github/
│   ├── ISSUE_TEMPLATE/historia-de-usuario.md   # plantilla de historias de usuario
│   ├── pull_request_template.md                # plantilla de Pull Request
│   └── workflows/
│       ├── project-automation.yml              # mueve las tarjetas del tablero
│       ├── ci.yml                              # pruebas y build en cada PR
│       └── deploy.yml                          # despliegue en Google Cloud
├── backend/
│   ├── app/
│   │   ├── api/                # rutas: auth, empleados, anotaciones, ia
│   │   ├── metrics.py          # métricas Prometheus y middleware
│   │   ├── core/config.py      # configuración por variables de entorno
│   │   ├── models/             # modelos SQLAlchemy
│   │   ├── schemas/            # esquemas Pydantic
│   │   ├── services/           # auth.py (JWT), lexico*.py, temas.py y revisor.py (IA)
│   │   └── main.py             # aplicación FastAPI
│   ├── tests/                  # pruebas con pytest
│   ├── Dockerfile
│   ├── requirements.txt
│   └── requirements-dev.txt
├── frontend/
│   ├── src/                    # App.js, api.js y pruebas
│   ├── Dockerfile              # build de React + nginx
│   └── nginx.conf
├── database/                   # schema.sql, seed.sql y diagrama
├── docs/                       # API, métricas, retrospectiva, ia.md e historias del Proyecto 3
├── k8s/                        # manifiestos de Kubernetes (kustomization.yaml, secret.example.yaml)
│   └── monitoring/             # ServiceMonitor, alertas, dashboard de Grafana y valores de Helm
├── monitoring/                 # Prometheus y Grafana para Docker Compose
├── scripts/                    # tráfico de prueba, creación del Secret y de las historias
├── docker-compose.yml
├── docker-compose.monitoring.yml
└── README.md
```

## Ejecución local con Docker

Requisitos: Docker y Docker Compose.

```bash
git clone https://github.com/bdmaderam/RHControl---Gesti-n.git
cd RHControl---Gesti-n
docker compose up --build -d
```

| Servicio | URL local |
|---|---|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| Swagger | http://localhost:8000/docs |

Usuario inicial: `admin` / `admin123`. Para detener todo: `docker compose down` (agrega `-v` para borrar también los datos).

## Ejecución local sin Docker

Requisitos: Python 3.12, Node.js 20 y un PostgreSQL 16 accesible.

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate      # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
export DATABASE_URL="postgresql+psycopg://usuario:clave@localhost:5432/rhcontrol"
export JWT_SECRET="una-clave-de-al-menos-16-caracteres"
uvicorn app.main:app --reload --port 8000

# Frontend (otra terminal)
cd frontend
npm install --legacy-peer-deps
REACT_APP_API_URL=http://localhost:8000/api npm start
```

## Variables de entorno

Backend (ver `backend/.env.example`):

| Variable | Descripción |
|---|---|
| `DATABASE_URL` | Cadena de conexión SQLAlchemy, con el driver `postgresql+psycopg://` |
| `JWT_SECRET` | Clave para firmar los tokens (mínimo 16 caracteres) |
| `CORS_ORIGINS` | Orígenes permitidos, separados por comas |
| `ADMIN_PASSWORD` | Contraseña del usuario `admin` que se crea al primer arranque (por defecto `admin123`, solo para uso local; en Kubernetes viene del Secret) |

Frontend (se fija al construir la imagen):

| Variable | Descripción |
|---|---|
| `REACT_APP_API_URL` | URL base de la API, por ejemplo `http://localhost:8000/api` |

Los archivos `.env` no se versionan. En Kubernetes los valores sensibles viven en un `Secret` (plantilla en `k8s/secret.example.yaml`). En producción los valores sensibles viven en Google Secret Manager y en GitHub Secrets, nunca en el repositorio.

## Monitoreo con Prometheus y Grafana

La API expone `GET /metrics` en formato Prometheus (fuera de `/api`, por lo que el Ingress no lo publica; `/metrics` y las probes no se cuentan a sí mismos).

| Métrica | Tipo | Qué mide |
|---|---|---|
| `http_requests_total{method,endpoint,status}` | Counter | Requests por ruta y código (throughput y errores) |
| `http_request_duration_seconds{method,endpoint}` | Histogram | Latencia (promedio, p95, p99) |
| `http_requests_in_progress` | Gauge | Requests atendiéndose ahora |
| `rhcontrol_empleados_activos` | Gauge | Empleados activos (se lee de la base en cada scrape) |
| `ia_revisiones_total`, `ia_puntaje_calidad`, `ia_hallazgos_total`, `ia_revision_duracion_seconds`, `ia_reglas_cargadas`, `ia_temas_detectados_total`, `ia_reincidencias_total` | Varias | Funcionalidad de IA |

La etiqueta `endpoint` usa la ruta definida (`/api/empleados/{empleado_id}`) y no la URL real, para mantener baja la cardinalidad.

**Opción A: Docker Compose** (la más rápida)

```bash
docker compose -f docker-compose.yml -f docker-compose.monitoring.yml up --build -d
python scripts/generate-traffic.py --url http://localhost:8000 --duracion 300
```

| Servicio | URL |
|---|---|
| Prometheus | http://localhost:9090 (Status > Targets: `rhcontrol-backend` en UP) |
| Grafana | http://localhost:3001 (usuario `admin`, clave `GRAFANA_PASSWORD`, por defecto `admin`). Dashboard **RHControl - API e IA** |

**Opción B: dentro del clúster** (se valora más): ver [Despliegue en Kubernetes](#despliegue-en-kubernetes), paso 5.

El dashboard (`k8s/monitoring/dashboards/rhcontrol.json`) tiene 19 paneles en dos filas (API e IA): throughput total y por endpoint, latencia promedio/p95/p99, errores 5xx, requests por código, requests en curso, réplicas de la API, memoria por pod, empleados activos y una fila de IA (revisiones por nivel, puntaje medio, reglas cargadas, latencia, hallazgos por regla, temas detectados y alertas de reincidencia).

**Evidencias del monitoreo** (clúster de Docker Desktop, con `scripts/generate-traffic.py` corriendo):

![Dashboard de Grafana: fila de API](docs/evidencias/11-grafana-api.png)
*Fila de API: throughput, latencia (promedio, p95, p99), errores 5xx, requests en curso, réplicas de la API (2) y empleados activos.*

![Dashboard de Grafana: fila de IA](docs/evidencias/12-grafana-ia.png)
*Fila de IA: revisiones por nivel, puntaje medio, 26 reglas cargadas, latencia de revisión en microsegundos, hallazgos por regla y alertas de reincidencia.*

![Prometheus: targets en UP](docs/evidencias/13-prometheus-targets.png)
*Prometheus, Status > Target health: el `ServiceMonitor` `rhcontrol/backend` descubre y raspa las réplicas del backend (todas en UP).*

`scripts/generate-traffic.py` inicia sesión y mezcla lecturas, escrituras, llamadas de IA y errores a propósito. Parámetros: `--url`, `--duracion`, `--hilos`, `--pausa`, `--password` (o la variable `ADMIN_PASSWORD`).

## Despliegue en Kubernetes

Arquitectura dentro del clúster:

```
 Navegador ──► Ingress (rhcontrol.local)
                 ├── /     ──► Service frontend ──► Deployment frontend (2 réplicas, nginx + React)
                 └── /api  ──► Service backend  ──► Deployment backend  (2 a 6 réplicas, HPA por CPU)
                                                         │  ConfigMap: CORS_ORIGINS
                                                         │  Secret: DATABASE_URL, JWT_SECRET, ADMIN_PASSWORD
                                                         ▼
                                            Service postgres ──► StatefulSet postgres + volumen persistente (1 Gi)

 Prometheus (kube-prometheus-stack) ── ServiceMonitor ──► /metrics de cada pod del backend ──► Grafana
```

| Archivo en `k8s/` | Contenido |
|---|---|
| `namespace.yaml` | Namespace `rhcontrol` |
| `secret.example.yaml` | **Plantilla** del Secret (el real no se versiona) |
| `configmap.yaml` | Configuración no sensible |
| `postgres.yaml` | StatefulSet, volumen persistente y Service de PostgreSQL |
| `backend.yaml` | Deployment (2 réplicas, probes, requests/limits) y Service de la API |
| `frontend.yaml` | Deployment y Service del frontend |
| `ingress.yaml` | (Opcional) Ingress hacia frontend y API |
| `hpa.yaml` | (Opcional) HorizontalPodAutoscaler de la API |
| `monitoring/` | ServiceMonitor, alertas, dashboard de Grafana y valores del chart de Helm |

Probes de la API: **liveness** `/api/salud` (el proceso responde) y **readiness** `/api/listo` (además, la base de datos responde).

### Requisitos

Docker, `kubectl`, `helm` y un clúster local: [kind](https://kind.sigs.k8s.io/), Minikube, k3d o Docker Desktop con Kubernetes.

### Paso a paso (ejemplo con kind)

**1. Clúster con Ingress**

Crea un archivo `kind-config.yaml`:

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
    kubeadmConfigPatches:
      - |
        kind: InitConfiguration
        nodeRegistration:
          kubeletExtraArgs:
            node-labels: "ingress-ready=true"
    extraPortMappings:
      - {containerPort: 80, hostPort: 80, protocol: TCP}
```

```bash
kind create cluster --name rhcontrol --config kind-config.yaml
kubectl apply -f https://kind.sigs.k8s.io/examples/ingress/deploy-ingress-nginx.yaml
kubectl -n ingress-nginx wait --for=condition=ready pod -l app.kubernetes.io/component=controller --timeout=120s
```

En Minikube basta con `minikube start` y `minikube addons enable ingress metrics-server`.
El HPA necesita *metrics-server*. En kind se instala con `kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml` y se le agrega el argumento `--kubelet-insecure-tls` al contenedor (`kubectl -n kube-system edit deployment metrics-server`).

**2. Imágenes.** Hay dos caminos:

- *Desde el registro (GHCR).* El workflow `imagenes.yml` las publica al hacer push a `development` o `production`: `ghcr.io/bdmaderam/rhcontrol-backend` y `ghcr.io/bdmaderam/rhcontrol-frontend`. La primera vez, en GitHub, sección *Packages*, cambia cada paquete a visibilidad **Public**. Para publicarlas a mano:

  ```bash
  echo "$GITHUB_TOKEN" | docker login ghcr.io -u bdmaderam --password-stdin   # token con permiso write:packages
  docker build -t ghcr.io/bdmaderam/rhcontrol-backend:latest ./backend
  docker build --build-arg REACT_APP_API_URL=/api -t ghcr.io/bdmaderam/rhcontrol-frontend:latest ./frontend
  docker push ghcr.io/bdmaderam/rhcontrol-backend:latest
  docker push ghcr.io/bdmaderam/rhcontrol-frontend:latest
  ```

- *Locales, sin registro.* Construye las imágenes, cárgalas al clúster y apunta Kustomize a ellas:

  ```bash
  docker build -t rhcontrol-backend:local ./backend
  docker build --build-arg REACT_APP_API_URL=/api -t rhcontrol-frontend:local ./frontend
  kind load docker-image rhcontrol-backend:local rhcontrol-frontend:local --name rhcontrol   # Minikube: minikube image load <imagen>
  cd k8s
  kustomize edit set image ghcr.io/bdmaderam/rhcontrol-backend=rhcontrol-backend:local
  kustomize edit set image ghcr.io/bdmaderam/rhcontrol-frontend=rhcontrol-frontend:local
  cd ..
  ```

  (No subas ese cambio de `k8s/kustomization.yaml` al repositorio.)

**3. Secret (credenciales).** Nada de esto se guarda en el repositorio:

```bash
./scripts/k8s-crear-secret.sh        # genera valores aleatorios y muestra las claves una sola vez
# o a mano: copia k8s/secret.example.yaml a k8s/secret.yaml, edita los valores y kubectl apply -f k8s/secret.yaml
```

**4. Aplicación**

```bash
kubectl apply -k k8s/
kubectl -n rhcontrol get pods,svc,hpa
```

![Pods, Services e Ingress en Kubernetes](docs/evidencias/15-k8s-pods.png)
*Backend con 2 réplicas, frontend con 2 réplicas, PostgreSQL como StatefulSet, Services `ClusterIP` e Ingress `nginx` para `rhcontrol.local`.*

Agrega `127.0.0.1 rhcontrol.local` al archivo de hosts (Linux/macOS: `/etc/hosts`; Windows: `C:\Windows\System32\drivers\etc\hosts`). Abre http://rhcontrol.local e inicia sesión con `admin` y la clave que mostró el script.

El Ingress solo enruta `/` y `/api`; para ver Swagger usa `kubectl -n rhcontrol port-forward svc/backend 8000:8000` y abre http://localhost:8000/docs.

**5. Monitoreo dentro del clúster**

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  -n monitoring -f k8s/monitoring/values-kube-prometheus-stack.yaml
kubectl apply -k k8s/monitoring/                  # ServiceMonitor, alertas y dashboard
kubectl -n monitoring port-forward svc/kube-prometheus-stack-grafana 3001:80       # http://localhost:3001
kubectl -n monitoring port-forward svc/kube-prometheus-stack-prometheus 9090:9090  # Status > Targets
```

El Secret de Grafana (`grafana-admin`) lo crea `k8s-crear-secret.sh` en el paso 3, por eso ese paso va antes.

**6. Probar el autoescalado (opcional)**

```bash
kubectl -n rhcontrol get hpa backend -w        # en una terminal
python scripts/generate-traffic.py --url http://rhcontrol.local --hilos 40 --pausa 0 --duracion 180   # en otra
```

![HorizontalPodAutoscaler del backend](docs/evidencias/16-k8s-hpa.png)
*El HPA lee la CPU real gracias a metrics-server (3 % sobre el objetivo de 50 %), con mínimo de 2 y máximo de 6 réplicas.*

**7. Limpieza**

```bash
kind delete cluster --name rhcontrol        # o: minikube delete
```

Si usas un clúster administrado en la nube (GKE, EKS, AKS), elimínalo al terminar para evitar costos.

### Comandos útiles para la sustentación

```bash
kubectl -n rhcontrol get pods,svc                             # pods y réplicas corriendo
kubectl -n rhcontrol describe deployment backend              # probes, resources, variables desde Secret/ConfigMap
kubectl -n rhcontrol delete pod -l app=backend --wait=false   # se recrean solos
kubectl -n rhcontrol scale deployment backend --replicas=3
```

## Autenticación

Mecanismo elegido: **JWT** (cabecera `Authorization: Bearer <token>`).

| Endpoint | Protección |
|---|---|
| `POST /api/auth/login` | Público; devuelve el token (vence en 8 h) |
| `/api/empleados...` y `/api/anotaciones...` (crear, actualizar, eliminar y también leer) | Requieren token; las lecturas también se protegieron por decisión del equipo |
| `/api/ia/...` | Requieren token |
| `/api/salud`, `/api/listo`, `/metrics` | Públicos (probes y Prometheus; `/metrics` no sale por el Ingress) |

La llave de firma (`JWT_SECRET`) y la contraseña del admin (`ADMIN_PASSWORD`) llegan por variables de entorno; en Kubernetes salen del Secret `rhcontrol-secret`, nunca del código ni de los manifiestos.

```bash
curl -i http://rhcontrol.local/api/empleados     # 401 sin token
TOKEN=$(curl -s -X POST http://rhcontrol.local/api/auth/login -H 'Content-Type: application/json' \
  -d '{"usuario":"admin","contraseña":"<ADMIN_PASSWORD>"}' | python -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')
curl -s -H "Authorization: Bearer $TOKEN" http://rhcontrol.local/api/empleados   # 200 con token
```

![Petición sin token rechazada con 401](docs/evidencias/19-auth-401.png)
*Sin token, la API responde `401 Unauthorized` con `WWW-Authenticate: Bearer`.*

## Inteligencia artificial

**Detección de temas y reincidencia + revisor de calidad**, con sistemas basados en reglas (sin modelos entrenados, sin costo y sin enviar datos fuera del clúster). Resumen:

- **Temas:** 13 temas (puntualidad, asistencia, seguridad, trato, desempeño...) en `backend/app/services/lexico_temas.py`. Cada anotación recibe sus etiquetas con las palabras que las activaron.
- **Reincidencia:** si un empleado repite un tema negativo en 90 días, se avisa (2 veces = *se repite*, 3 o más = *reincidente*). Se ve al revisar una anotación y en la tarjeta *Temas y reincidencia* del detalle del empleado.
- **Calidad:** el botón **Revisar calidad** devuelve puntaje 0-100, problemas con evidencia y cómo corregirlos (26 reglas).
- **Endpoints (JWT):** `POST /api/ia/revisar-anotacion`, `GET /api/ia/temas-empleado/{id}`, `GET /api/ia/reincidencias`, `GET /api/ia/auditoria-anotaciones`, `GET /api/ia/reglas`.
- **Métricas propias:** `ia_revisiones_total`, `ia_puntaje_calidad`, `ia_hallazgos_total`, `ia_revision_duracion_seconds`, `ia_reglas_cargadas`, `ia_temas_detectados_total` e `ia_reincidencias_total`, visibles en Grafana.
- **Ampliar el conocimiento:** editar `lexico_temas.py` / `lexico.py` o agregar una regla con `@regla` en `revisor.py`.
- **Evaluación, límites y mejoras:** [docs/ia.md](docs/ia.md).

![Revisión de calidad de una anotación](docs/evidencias/20-ia-revision.png)
*Nueva anotación: el revisor marca como error un texto demasiado corto ("buen trabajo"), sugiere indicar qué logró la persona y muestra los 14 criterios que sí cumple (71/100, *Requiere corrección*).*

![Tarjeta Temas y reincidencia en el detalle del empleado](docs/evidencias/23-ia-tarjeta-empleado.png)
*Detalle del empleado: tres llamados de atención por *Puntualidad* en los últimos 90 días activan la alerta de reincidencia.*

## Pruebas

```bash
# Backend: 80 pruebas (usan SQLite, no necesitan PostgreSQL)
cd backend
pip install -r requirements.txt -r requirements-dev.txt
pytest

# Frontend: 10 pruebas
cd frontend
npm ci --legacy-peer-deps
npm test
```

## Integración y despliegue continuo

| Workflow | Cuándo corre | Qué hace |
|---|---|---|
| `project-automation.yml` | Cuando un Pull Request enlazado a un issue cambia de estado | Mueve la tarjeta del issue enlazado (`Closes #N`) a **Review** y luego a **Done** en GitHub Projects |
| `ci.yml` | En cada Pull Request | Job `backend`: instala dependencias y ejecuta pytest. Job `frontend`: instala, ejecuta las pruebas y construye la aplicación |
| `deploy.yml` | En cada push a `production` | Construye las imágenes, las sube a Artifact Registry, despliega el backend y luego el frontend en Cloud Run, y actualiza el CORS del backend con la URL del frontend |

Los checks `backend` y `frontend` son obligatorios para fusionar: el ruleset de las ramas protegidas exige además un Pull Request con al menos una aprobación.

## Despliegue en Google Cloud

Recursos del proyecto `rhcontrol` (región `us-central1`):

| Recurso | Nombre |
|---|---|
| Cloud Run | `rhcontrol-backend`, `rhcontrol-frontend` |
| Cloud SQL (PostgreSQL 16, `db-f1-micro`) | `rhcontrol-db`, base `rhcontrol` |
| Artifact Registry (Docker) | `rhcontrol` |
| Secret Manager | `database-url`, `jwt-secret` |
| Cuentas de servicio | `rhcontrol-run` (ejecuta la app), `github-deployer` (despliega desde GitHub Actions) |

Secretos del repositorio en GitHub: `GCP_SA_KEY`, `GCP_PROJECT_ID`, `CLOUDSQL_CONNECTION` y `PROJECT_TOKEN`.

Para desplegar una nueva versión basta con fusionar un Pull Request de `development` hacia `production`.

Para detener los costos al terminar el proyecto:

```bash
gcloud run services delete rhcontrol-frontend rhcontrol-backend --region us-central1
gcloud sql instances delete rhcontrol-db
gcloud artifacts repositories delete rhcontrol --location us-central1
```

## Historias de usuario y sprints

El trabajo se organizó en **12 historias de usuario** (47 puntos), repartidas en partes iguales: las **HU-A** son de Brayan y las **HU-B** de Daniel. Cada historia es un issue creado con la plantilla `.github/ISSUE_TEMPLATE/historia-de-usuario.md`, se trabaja en su propia rama `feature/...` y se cierra con un Pull Request que la referencia con `Closes #N`, con revisión cruzada. Cada sprint termina con un Pull Request de release de `development` a `production`.

**Proyecto 3:** las historias HU-C1 a HU-C12 (monitoreo, autenticación, Kubernetes e IA) están en [docs/historias-proyecto3.md](docs/historias-proyecto3.md).

Tablero del proyecto: [GitHub Projects](https://github.com/bdmaderam/RHControl---Gesti-n/projects) · Métricas: [docs/metricas.md](docs/metricas.md) · Retrospectiva: [docs/retrospectiva.md](docs/retrospectiva.md)

### Sprint 1: Backend y base de datos
- **Historias completadas** (15 de 15 puntos):
  - **HU-A1** — Proteger el API de empleados y anotaciones con JWT (5 pts, Brayan). Issue [#4](https://github.com/bdmaderam/RHControl---Gesti-n/issues/4), Pull Request [#15](https://github.com/bdmaderam/RHControl---Gesti-n/pull/15). Estado: Done.
  - **HU-A2** — Configuración y secretos por variables de entorno (2 pts, Brayan). Issue [#5](https://github.com/bdmaderam/RHControl---Gesti-n/issues/5), Pull Request [#17](https://github.com/bdmaderam/RHControl---Gesti-n/pull/17). Estado: Done.
  - **HU-B1** — Pruebas pytest del CRUD de empleados (5 pts, Daniel). Issue [#10](https://github.com/bdmaderam/RHControl---Gesti-n/issues/10), Pull Request [#16](https://github.com/bdmaderam/RHControl---Gesti-n/pull/16). Estado: Done.
  - **HU-B2** — Workflow que mueve las cards del tablero (3 pts, Daniel). Issue [#2](https://github.com/bdmaderam/RHControl---Gesti-n/issues/2), Pull Request [#3](https://github.com/bdmaderam/RHControl---Gesti-n/pull/3). Estado: Done.
- **Evidencias y enlaces:**
  - Release del sprint: [Pull Request #18](https://github.com/bdmaderam/RHControl---Gesti-n/pull/18) (`development` → `production`).
  - Plantillas de issue y de Pull Request: [PR #1](https://github.com/bdmaderam/RHControl---Gesti-n/pull/1).
  - Pruebas del backend: 12 pruebas con pytest que se ejecutan en CI ([workflow `ci.yml`](https://github.com/bdmaderam/RHControl---Gesti-n/actions/workflows/ci.yml)).
  - Automatización del tablero: [workflow `project-automation.yml`](https://github.com/bdmaderam/RHControl---Gesti-n/actions/workflows/project-automation.yml).
  - Velocity: 15 puntos planificados y 15 completados ([detalle y burndown](docs/metricas.md)).
  - Reglas de ramas (Pull Request con aprobación y checks obligatorios): ![Reglas de las ramas](docs/evidencias/06-ruleset.png)

### Sprint 2: Frontend
- **Historias completadas** (11 de 11 puntos):
  - **HU-A3** — Enviar el token en Authorization y cerrar sesión con 401 (3 pts, Brayan). Issue [#6](https://github.com/bdmaderam/RHControl---Gesti-n/issues/6), Pull Request [#19](https://github.com/bdmaderam/RHControl---Gesti-n/pull/19). Estado: Done.
  - **HU-A4** — GET de anotación por id y uso en EditNote (2 pts, Brayan). Issue [#7](https://github.com/bdmaderam/RHControl---Gesti-n/issues/7), Pull Request [#20](https://github.com/bdmaderam/RHControl---Gesti-n/pull/20). Estado: Done.
  - **HU-B3** — Estados de carga, vacíos y errores claros en formularios (3 pts, Daniel). Issue [#11](https://github.com/bdmaderam/RHControl---Gesti-n/issues/11), Pull Request [#21](https://github.com/bdmaderam/RHControl---Gesti-n/pull/21). Estado: Done.
  - **HU-B4** — Pruebas del frontend con Testing Library (3 pts, Daniel). Issue [#12](https://github.com/bdmaderam/RHControl---Gesti-n/issues/12), Pull Request [#22](https://github.com/bdmaderam/RHControl---Gesti-n/pull/22). Estado: Done.
- **Evidencias y enlaces:**
  - Release del sprint: [Pull Request #23](https://github.com/bdmaderam/RHControl---Gesti-n/pull/23) (`development` → `production`).
  - Pruebas del frontend: 6 pruebas con Jest y Testing Library en CI.
  - Pull Requests fusionados con revisión cruzada: ![Pull Requests cerrados](docs/evidencias/03-prs-cerrados.png)
  - Velocity: 11 puntos planificados y 11 completados ([detalle y burndown](docs/metricas.md)).

### Sprint 3: Despliegue y documentación
- **Historias completadas** (21 de 21 puntos):
  - **HU-A5** — Desplegar backend y base de datos en GCP (8 pts, Brayan). Issue [#8](https://github.com/bdmaderam/RHControl---Gesti-n/issues/8), Pull Request [#25](https://github.com/bdmaderam/RHControl---Gesti-n/pull/25). Estado: Done.
  - **HU-A6** — Desplegar frontend y despliegue continuo con Actions (5 pts, Brayan). Issue [#9](https://github.com/bdmaderam/RHControl---Gesti-n/issues/9), Pull Request [#27](https://github.com/bdmaderam/RHControl---Gesti-n/pull/27). Estado: Done.
  - **HU-B5** — CI en cada Pull Request con pruebas y build (5 pts, Daniel). Issue [#13](https://github.com/bdmaderam/RHControl---Gesti-n/issues/13), Pull Request [#24](https://github.com/bdmaderam/RHControl---Gesti-n/pull/24). Estado: Done.
  - **HU-B6** — README final, documentación de la API y retrospectiva (3 pts, Daniel). Issue [#14](https://github.com/bdmaderam/RHControl---Gesti-n/issues/14), Pull Request [#29](https://github.com/bdmaderam/RHControl---Gesti-n/pull/29). Estado: Done.
- **Evidencias y enlaces:**
  - Releases a producción: [PR #26](https://github.com/bdmaderam/RHControl---Gesti-n/pull/26), [PR #28](https://github.com/bdmaderam/RHControl---Gesti-n/pull/28), [PR #30](https://github.com/bdmaderam/RHControl---Gesti-n/pull/30) y [PR #33](https://github.com/bdmaderam/RHControl---Gesti-n/pull/33).
  - Despliegue continuo: [workflow `deploy.yml`](https://github.com/bdmaderam/RHControl---Gesti-n/actions/workflows/deploy.yml) y CI en [`ci.yml`](https://github.com/bdmaderam/RHControl---Gesti-n/actions/workflows/ci.yml): ![Workflows de GitHub Actions en verde](docs/evidencias/05-actions-verde.png)
  - Aplicación en producción: [frontend](https://rhcontrol-frontend-3cugxgrrsa-uc.a.run.app) y [API con Swagger](https://rhcontrol-backend-3cugxgrrsa-uc.a.run.app/docs).
    - ![Frontend en producción](docs/evidencias/07-app-produccion.png)
    - ![Swagger de la API](docs/evidencias/08-swagger.png)
  - Recursos en Google Cloud: ![Cloud Run](docs/evidencias/09-gcp-cloud-run.png) ![Cloud SQL](docs/evidencias/10-gcp-cloud-sql.png)
  - Conflicto de merge provocado y resuelto: [PR #31](https://github.com/bdmaderam/RHControl---Gesti-n/pull/31) y [PR #32](https://github.com/bdmaderam/RHControl---Gesti-n/pull/32) (ambos modifican la misma línea de la licencia del README): ![Conflicto de merge en el PR #32](docs/evidencias/11-conflicto-pr.png)
  - Documentación: [API](docs/api-documentation.md), [métricas](docs/metricas.md) y [retrospectiva](docs/retrospectiva.md).
  - Velocity: 21 puntos planificados y 21 completados.

### Evidencias del tablero y del equipo
- Tablero con las 12 historias en Done: ![Tablero Kanban](docs/evidencias/01-tablero-board.png)
- Vista de tabla con Sprint, Prioridad, Tipo y Estimación: ![Tablero en tabla](docs/evidencias/02-tablero-tabla.png)
- Participación de los dos integrantes: ![Contribuidores](docs/evidencias/04-contribuidores.png)

## Flujo de trabajo del equipo

- **Tablero Kanban** en GitHub Projects con las columnas Backlog → Ready → In Progress → Review → Done, y los campos personalizados Sprint, Prioridad, Tipo y Estimación (puntos).
- **Ramas:** `main` (base del repositorio), `production` (lo desplegado), `development` (integración) y `feature/sprintN-*` (una por historia).
- **Pull Requests:** cada historia entra a `development` con un PR que referencia su issue (`Closes #N`), revisión cruzada y checks en verde. Los releases de `development` a `production` se hacen con PR y *merge commit*.
- **Roles alternados:** quien abre el PR no es quien lo aprueba y lo fusiona; los releases alternan autor y revisor.
- **Tres sprints:** 1) backend y base de datos, 2) frontend, 3) despliegue y documentación.

## Documentación adicional

- [Documentación de la API](docs/api-documentation.md)
- [Métricas del proyecto](docs/metricas.md)
- [Retrospectiva](docs/retrospectiva.md)
- [Mapeo de requisitos](docs/requirements-mapping.md)
- [Funcionalidad de IA](docs/ia.md)
- [Historias de usuario del Proyecto 3](docs/historias-proyecto3.md)

## Autores

- **Daniel Suárez** — [@Danielsuarez1-ops](https://github.com/Danielsuarez1-ops)
- **Brayan Madera** — [@bdmaderam](https://github.com/bdmaderam)

## Licencia
