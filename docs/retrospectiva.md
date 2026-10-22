# Retrospectiva del proyecto

Retrospectiva del **Proyecto 2 – Gestión colaborativa con GitHub Projects**, desarrollado por Brayan Madera y Daniel Suárez sobre la aplicación RHControl (FastAPI, PostgreSQL, React y Docker), con despliegue en Google Cloud.

## Resumen

| Aspecto | Resultado |
|---|---|
| Historias de usuario | 12, repartidas en 6 por integrante |
| Puntos | 47 planificados, 47 completados (15, 11 y 21 por sprint) |
| Sprints | 1) Backend y base de datos, 2) Frontend, 3) Despliegue y documentación |
| Pull Requests fusionados | 18 (13 de historias o tareas y 5 releases a `production`), todos con revisión cruzada |
| Automatización | Tablero movido por GitHub Actions, CI en cada PR y despliegue continuo a Google Cloud |
| Resultado | Aplicación en producción: backend y base de datos en Cloud Run y Cloud SQL, frontend en Cloud Run |

Las métricas detalladas están en [metricas.md](metricas.md).

## Qué salió bien

- **El flujo de ramas y Pull Requests funcionó.** Cada historia entró por su propia rama `feature/...`, con un PR que referencia su issue (`Closes #N`), y la regla del repositorio impidió que alguien aprobara su propio trabajo.
- **El tablero reflejó el trabajo real.** La automatización moviendo las tarjetas a Review y Done dio visibilidad sin tareas manuales, y los campos Sprint, Prioridad, Tipo y Estimación permitieron calcular velocity y burndown.
- **La integración continua evitó errores.** Los checks `backend` y `frontend` son obligatorios, y las pruebas automatizadas sacaron a la luz problemas a tiempo, como una dependencia que faltaba para ejecutar las pruebas del frontend.
- **Los secretos nunca estuvieron en el repositorio.** La base de datos y la clave JWT viven en Secret Manager; la llave del despliegue vive en GitHub Secrets.
- **El despliegue continuo quedó completo.** Fusionar `development` en `production` construye, publica y despliega ambos servicios, y el propio workflow configura el CORS del backend con la URL del frontend.
- **El reparto fue equilibrado.** Cada integrante tuvo 6 historias y los dos abrieron y revisaron Pull Requests (ver [metricas.md](metricas.md)).

## Qué salió mal y cómo lo resolvimos

| Problema | Causa | Solución | Lección |
|---|---|---|---|
| No se podía fusionar el primer PR (*Review required*) | Quien abre el PR no puede aprobarlo | La otra persona aprueba desde su sesión | Planificar quién revisa cada PR desde el inicio |
| La tarjeta no se movía de columna | El PR no tenía `Closes #N` en la descripción, y el comando `gh project` no resolvía el tipo de propietario | Se corrigió la descripción y se reescribió el workflow con la API GraphQL de GitHub | La plantilla de PR debe exigir el enlace al issue |
| Un token de acceso quedó expuesto en una captura de pantalla | Se pegó en el lugar equivocado al iniciar sesión | Se revocó y se generó uno nuevo; ahora solo existe como secreto de GitHub | Nunca compartir tokens; revocar de inmediato si se filtran |
| Un push salió con credenciales de otra cuenta | El administrador de credenciales de Git conservó guardada la sesión de otra cuenta de GitHub | Se fijó el usuario en la URL del remoto y se verificó el autor de cada commit | Comprobar siempre la cuenta activa (`gh auth status`) antes de hacer push |
| Comandos que fallaban en PowerShell | Comillas y acentos en Windows PowerShell 5.1, y pegados dobles de código | Se usaron archivos JSON y bloques con comprobaciones | Preferir archivos y scripts verificables frente a comandos largos |
| La facturación de Google Cloud estaba cerrada | La cuenta de prueba anterior ya no estaba activa | Se creó y activó una cuenta de facturación nueva con prepago | Verificar la nube y la facturación antes del último sprint, no durante |
| La URL de la base de datos habría fallado en la nube | El driver de la aplicación es `psycopg` y la URL usaba el prefijo `postgresql://` | Se corrigió el secreto a `postgresql+psycopg://` antes de desplegar | Revisar el código contra la configuración de producción |
| Una historia quedó en Ready tras fusionarse su PR | No se había movido a In Progress antes del PR, y la automatización solo avanza desde esa columna | Se movió manualmente a Done | Mover la tarjeta a In Progress al empezar a trabajar |
| Un PR se fusionó con *merge commit* en vez de *squash* | Se eligió la opción por defecto del botón | Se dejó la historia como está y se acordó usar squash para las ramas de historias | Dejar *squash* como único método permitido para esas ramas |

## Qué aprendimos

- Un tablero solo sirve si las tarjetas se mueven a tiempo; automatizarlo reduce el trabajo, pero la disciplina de mantener el estado sigue siendo del equipo.
- Las reglas de protección de ramas parecen un obstáculo al principio, pero son lo que garantiza la revisión cruzada y los checks en verde.
- Desplegar en la nube conviene hacerlo **pronto** y de forma continua: la mayor parte de los imprevistos (facturación, permisos, URLs, CORS) aparecen solo al desplegar.
- Estimar en puntos ayuda a ver dónde está el riesgo: la historia de despliegue (8 puntos) fue la más pesada y la que más preparación necesitó.
- Medir con datos reales muestra los límites de las métricas: nuestro cycle time es muy bajo porque gran parte del trabajo se hizo localmente antes del primer commit.

## Qué haríamos distinto

1. **Empezar a desplegar desde el Sprint 1.** Un despliegue mínimo desde el principio habría revelado antes los problemas de facturación y configuración.
2. **Repartir el trabajo en más sprints reales.** Concentramos el trabajo en dos días; con más tiempo, las ventanas semanales del tablero reflejarían mejor el ritmo del equipo.
3. **Hacer commits pequeños y frecuentes.** Cada historia se commiteó casi al final; commits más frecuentes mejorarían el cycle time medido y la trazabilidad.
4. **Definir desde el inicio las reglas de fusión** (squash para historias y *merge commit* para releases) y configurarlas en el repositorio.

## Acciones de mejora

- Reemplazar la llave JSON de la cuenta de servicio por *Workload Identity Federation*, para no almacenar credenciales de larga duración en GitHub.
- Activar copias de seguridad y alta disponibilidad en Cloud SQL (se desactivaron para reducir el costo del proyecto).
- Agregar pruebas de humo posteriores al despliegue (por ejemplo, un inicio de sesión de prueba) además de la comprobación de salud.
- Actualizar las versiones de las acciones de GitHub Actions que avisan por la próxima retirada de Node 20.
- Añadir alertas de presupuesto y monitoreo (registros y métricas) de los servicios en Cloud Run.
- Cambiar la contraseña del usuario `admin` de demostración y mover la creación de usuarios fuera del arranque de la API.
