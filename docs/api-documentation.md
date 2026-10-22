# Documentación de la API — RHControl

| Entorno | URL base |
|---|---|
| Producción | `https://rhcontrol-backend-3cugxgrrsa-uc.a.run.app` |
| Local | `http://localhost:8000` |

Documentación interactiva (Swagger / OpenAPI): `/docs`. Todas las rutas usan el prefijo `/api`.

## Autenticación

La API usa **JWT con esquema Bearer**. Primero se inicia sesión para obtener un token y luego se envía en la cabecera `Authorization` de cada petición protegida.

### POST /api/auth/login

Público. Recibe las credenciales y devuelve un token válido por 8 horas.

```json
{ "usuario": "admin", "contraseña": "admin123" }
```

Respuesta `200 OK`:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "usuario": "admin",
  "nombre": "Administrador RH"
}
```

Si las credenciales son incorrectas responde `401` con `{"detail": "Usuario o contraseña incorrectos"}`.

### Uso del token

```
Authorization: Bearer <access_token>
```

Las rutas de **empleados** y **anotaciones** exigen el token. Sin token, con un token vencido o inválido responden `401 Unauthorized` con la cabecera `WWW-Authenticate: Bearer`. El frontend, ante un 401, borra la sesión y vuelve al inicio de sesión.

Ejemplo con `curl`:

```bash
API=https://rhcontrol-backend-3cugxgrrsa-uc.a.run.app

TOKEN=$(curl -s -X POST "$API/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"usuario":"admin","contraseña":"admin123"}' | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

curl -s "$API/api/empleados" -H "Authorization: Bearer $TOKEN"
```

## Sistema

### GET /api/salud

Público. Verifica que el servicio está activo.

```json
{ "estado": "ok", "servicio": "RHControl API" }
```

## Empleados

Requieren token Bearer.

### GET /api/empleados

Lista empleados, del más reciente al más antiguo. Parámetros opcionales:

| Parámetro | Tipo | Descripción |
|---|---|---|
| `documento` | texto | Coincidencia parcial con el número de documento |
| `nombre` | texto | Coincidencia parcial con nombres o apellidos |
| `activos` | booleano | `true` solo activos, `false` solo inactivos |

Respuesta `200 OK`: lista de empleados.

### GET /api/empleados/{id}

Devuelve un empleado. `404` si no existe.

### POST /api/empleados

Crea un empleado. Respuesta `201 Created`.

```json
{
  "nombres": "Ana",
  "apellidos": "Martínez",
  "tipo_documento": "CC",
  "numero_documento": "111222333",
  "fecha_nacimiento": "1995-04-12",
  "cargo": "Analista",
  "salario": 3500000,
  "dependencia": "Tecnología",
  "tiene_cuenta_bancaria": true,
  "es_temporal": false,
  "activo": true
}
```

Reglas de validación:

| Campo | Regla |
|---|---|
| `nombres`, `apellidos` | Obligatorios, hasta 100 caracteres |
| `tipo_documento` | `CC`, `CE` o `PA` (por defecto `CC`) |
| `numero_documento` | Obligatorio, único, hasta 30 caracteres |
| `salario` | Número mayor o igual a 0 |
| `cargo`, `dependencia` | Hasta 120 caracteres |

Un documento repetido responde `409 Conflict`.

### PUT /api/empleados/{id}

Actualiza uno o varios campos (envía solo los que cambian). Respuesta `200 OK`; `404` si no existe; `409` si el nuevo documento ya pertenece a otro empleado.

### DELETE /api/empleados/{id}

Elimina el empleado y sus anotaciones. Respuesta `204 No Content`; `404` si no existe.

## Anotaciones

Requieren token Bearer.

### GET /api/anotaciones

Lista todas las anotaciones, de la más reciente a la más antigua.

### GET /api/anotaciones/{id}

Devuelve una anotación por su ID. `404` si no existe.

### GET /api/anotaciones/empleado/{empleado_id}

Lista las anotaciones de un empleado. `404` si el empleado no existe.

### POST /api/anotaciones/empleado/{empleado_id}

Crea una anotación para el empleado. Respuesta `201 Created`.

```json
{
  "tipo": "Felicitación",
  "descripcion": "Excelente desempeño en el proyecto.",
  "fecha": "2026-10-22"
}
```

| Campo | Regla |
|---|---|
| `tipo` | Hasta 40 caracteres (por defecto `Llamado de atención`) |
| `descripcion` | Obligatoria, de 1 a 2000 caracteres |
| `fecha` | Formato `AAAA-MM-DD` (por defecto, la fecha de hoy) |

### PUT /api/anotaciones/{id}

Actualiza una anotación. Respuesta `200 OK`; `404` si no existe.

### DELETE /api/anotaciones/{id}

Elimina una anotación. Respuesta `204 No Content`; `404` si no existe.

## Códigos de respuesta

| Código | Significado |
|---|---|
| `200` | Operación exitosa |
| `201` | Recurso creado |
| `204` | Eliminación exitosa, sin contenido |
| `401` | Credenciales incorrectas o token ausente, vencido o inválido |
| `404` | Recurso no encontrado |
| `409` | Conflicto, por ejemplo documento duplicado |
| `422` | Datos de entrada no válidos |

Los errores se devuelven en JSON dentro de la propiedad `detail`.
