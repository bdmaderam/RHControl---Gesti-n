# Correspondencia con la actividad

| Requisito | Implementación RHControl |
|---|---|
| Backend Spring Boot/Django/FastAPI | FastAPI |
| PostgreSQL obligatorio | PostgreSQL 16 |
| Frontend web | React |
| Dos entidades relacionadas | Empleados y Anotaciones |
| CRUD entidad 1 | GET, GET por id, POST, PUT, DELETE de empleados |
| CRUD entidad 2 | GET, GET por empleado, POST, PUT, DELETE de anotaciones |
| Relación | `anotaciones.empleado_id` → `empleados.id` |
| Formularios crear/editar | React |
| Listado y eliminación | React |
| Detalles | Vista de detalle de empleado |
| Navegación | React Router |
| Errores | Validación FastAPI + mensajes frontend |
| Docker | Docker Compose con PostgreSQL, FastAPI y Nginx/React |
| ER | `database/diagram.mmd` |
| Schema SQL | `database/schema.sql` |
| Datos de prueba | Seed automático de FastAPI + `database/seed.sql` |
| Documentación API | Swagger en `/docs` + `docs/api-documentation.md` |

## Pendiente por decisión de etapa

El PDF también exige despliegue en un único proveedor cloud (GCP, AWS o Azure), configuración de variables de entorno, conectividad entre componentes y URLs públicas. Esos elementos se dejan pendientes en esta versión local.
