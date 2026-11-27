# Guion de sustentación (15 minutos)

Guion sugerido para la sustentación del Proyecto 3. **Todos los integrantes deben poder explicar cualquier parte**: se selecciona al expositor en clase.

## Antes de empezar (preparar y ensayar)

- Clúster arriba y aplicación desplegada (`kubectl -n rhcontrol get pods` con todo en `Running` y `READY`).
- `rhcontrol.local` en el archivo de hosts y la clave del admin a la mano (la mostró `k8s-crear-secret.sh`).
- Dos terminales listas: una con `kubectl -n rhcontrol get hpa backend -w` y otra con el script de tráfico.
- Grafana abierto en el dashboard **RHControl - API e IA** (`kubectl -n monitoring port-forward svc/kube-prometheus-stack-grafana 3001:80`).
- Una anotación de ejemplo escrita para la demostración de IA.

## 1. Equipo y contexto (2 min)

- **Antes (Proyectos 1 y 2):** RHControl con FastAPI, React y PostgreSQL, JWT ya aplicado, desplegado en Cloud Run con CI/CD y gestión en GitHub Projects.
- **Ahora (Proyecto 3):** monitoreo (Prometheus y Grafana), Kubernetes, autenticación con llaves en Secret y una funcionalidad de IA.

## 2. Demostración en vivo (8 min)

| Min | Qué mostrar | Cómo |
|---|---|---|
| 1 | Clúster | `kubectl -n rhcontrol get pods,svc,hpa`: 2 réplicas del backend, 2 del frontend, PostgreSQL con StatefulSet |
| 1 | Resiliencia | `kubectl -n rhcontrol delete pod -l app=backend --wait=false` y volver a listar: se recrean solos |
| 2 | Autenticación | `curl -i http://rhcontrol.local/api/empleados` → **401**; iniciar sesión en la web; mostrar que crear/editar/eliminar funcionan con la sesión iniciada |
| 3 | Grafana con tráfico | Ejecutar `python scripts/generate-traffic.py --url http://rhcontrol.local --duracion 120` y señalar throughput, latencia, errores y requests en curso |
| 1 | IA | Crear 2 llamados de atención a un empleado ("Llegó tarde el lunes", "Tardanza de 30 minutos el jueves") → en una tercera, **Revisar calidad** → aparece el tema *Puntualidad* y la alerta *3.ª vez en 90 días*. Abrir el detalle del empleado → tarjeta *Temas y reincidencia*. Luego escribir "Es un flojo y siempre llega tarde" para mostrar el puntaje bajo. Mostrar la fila de IA en Grafana |

Si sobra tiempo: autoescalado con `--hilos 40 --pausa 0` y mirar el HPA subir réplicas.

## 3. Explicación técnica (3 min)

- **Arquitectura en Kubernetes:** Ingress → Services → Deployments; ConfigMap para configuración, Secret para `DATABASE_URL`, `JWT_SECRET` y `ADMIN_PASSWORD`; PostgreSQL en StatefulSet con volumen persistente.
- **Probes:** *liveness* `/api/salud` (reinicia si el proceso se cuelga) y *readiness* `/api/listo` (saca el pod del Service si la base no responde). `requests` y `limits` definidos; el HPA calcula el porcentaje de CPU sobre `requests`.
- **IA:** detección de temas y reincidencia (13 temas) y revisión de calidad (26 reglas), ambas basadas en reglas. Se eligió porque la base real tiene pocos datos para entrenar, es gratis, no envía datos sensibles fuera del clúster y es explicable (cada etiqueta muestra sus palabras). Un clasificador entrenado con datos sintéticos falló y se descartó. Limitaciones en [ia.md](ia.md).

## 4. Reflexión (2 min)

Preguntas para preparar: ¿qué fue lo más difícil de Kubernetes? ¿qué cambió al correr varias réplicas (métricas por pod, arranque concurrente con el lock de PostgreSQL)? ¿por qué reglas y no un modelo? ¿cómo se amplía el vocabulario?

## Preguntas probables

- *¿Por qué readiness y liveness son rutas distintas?* La primera revisa también la base de datos; si la base cae no conviene reiniciar la API, solo dejar de enviarle tráfico.
- *¿Dónde están las credenciales?* Solo en el Secret del clúster; el repositorio tiene `secret.example.yaml` con marcadores.
- *¿Por qué `/metrics` no sale por el Ingress?* Está fuera de `/api` y el Ingress solo enruta `/` y `/api`; Prometheus lo lee dentro del clúster.
- *¿Cómo se suman las métricas de varias réplicas?* Cada pod tiene sus contadores; en PromQL se usa `sum(rate(...))`.
- *¿El modelo es confiable?* Es una ayuda, no una decisión: se entrenó con datos sintéticos, la confianza no está calibrada y la persona confirma siempre.
