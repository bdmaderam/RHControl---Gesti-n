# RHControl

![CI](https://github.com/bdmaderam/RHControl---Gesti-n/actions/workflows/ci.yml/badge.svg)
![Deploy](https://github.com/bdmaderam/RHControl---Gesti-n/actions/workflows/deploy.yml/badge.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Python%203.12-009688?style=flat-square&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Cloud%20Run-4285F4?style=flat-square&logo=googlecloud&logoColor=white)

**RHControl** es una aplicación web para la gestión de recursos humanos: registro de empleados, consulta de su información laboral, anotaciones (reconocimientos, observaciones, llamados de atención) y reportes con exportación a CSV. Es el proyecto sobre el que se desarrolla el **Proyecto 2 – Gestión colaborativa con GitHub Projects** de la materia *Desarrollo de Aplicaciones en la Nube*.

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
- [Ejecución local sin Docker](#ejecución-local-sin-docker)
- [Variables de entorno](#variables-de-entorno)
- [Pruebas](#pruebas)
- [Integración y despliegue continuo](#integración-y-despliegue-continuo)
- [Despliegue en Google Cloud](#despliegue-en-google-cloud)
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
│   │   ├── api/                # rutas: auth, empleados, anotaciones
│   │   ├── core/config.py      # configuración por variables de entorno
│   │   ├── models/             # modelos SQLAlchemy
│   │   ├── schemas/            # esquemas Pydantic
│   │   ├── services/auth.py    # hash de contraseñas y validación del JWT
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
├── docs/                       # API, métricas y retrospectiva
├── docker-compose.yml
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

Frontend (se fija al construir la imagen):

| Variable | Descripción |
|---|---|
| `REACT_APP_API_URL` | URL base de la API, por ejemplo `http://localhost:8000/api` |

Los archivos `.env` no se versionan. En producción los valores sensibles viven en Google Secret Manager y en GitHub Secrets, nunca en el repositorio.

## Pruebas

```bash
# Backend: 12 pruebas (usan SQLite, no necesitan PostgreSQL)
cd backend
pip install -r requirements.txt -r requirements-dev.txt
pytest

# Frontend: 6 pruebas
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

## Autores

- **Daniel Suárez** — [@Danielsuarez1-ops](https://github.com/Danielsuarez1-ops)
- **Brayan Madera** — [@bdmaderam](https://github.com/bdmaderam)

## Licencia

Este proyecto se distribuye bajo la licencia **ISC** y se desarrolla para la materia Desarrollo de Aplicaciones en la Nube.
