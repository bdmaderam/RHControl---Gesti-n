# Documentación de API — RHControl

Base local: `http://localhost:8000`

Swagger/OpenAPI: `http://localhost:8000/docs`

## Empleados

### GET /api/empleados
Lista empleados. Parámetros opcionales: `documento`, `nombre`, `activos`.

### GET /api/empleados/{id}
Obtiene un empleado por ID.

### POST /api/empleados
Crea un empleado.

Ejemplo:
```json
{
  "nombres": "Ana",
  "apellidos": "Martínez",
  "tipo_documento": "CC",
  "numero_documento": "111222333",
  "cargo": "Analista",
  "salario": 3500000,
  "dependencia": "Tecnología",
  "tiene_cuenta_bancaria": true,
  "es_temporal": false,
  "activo": true
}
```
Respuesta: `201 Created`.

### PUT /api/empleados/{id}
Actualiza uno o varios campos. Respuesta `200 OK`.

### DELETE /api/empleados/{id}
Elimina el empleado y sus anotaciones relacionadas. Respuesta `204 No Content`.

## Anotaciones

### GET /api/anotaciones
Lista todas las anotaciones.

### GET /api/anotaciones/empleado/{id}
Lista las anotaciones de un empleado.

### POST /api/anotaciones/empleado/{id}
Crea una anotación relacionada.

```json
{
  "tipo": "Felicitación",
  "descripcion": "Excelente desempeño.",
  "fecha": "2026-09-09"
}
```

### PUT /api/anotaciones/{id}
Actualiza una anotación.

### DELETE /api/anotaciones/{id}
Elimina una anotación.

## Autenticación

`POST /api/auth/login` recibe `usuario` y `contraseña`, y devuelve un token JWT.

## Códigos HTTP

- `200`: operación exitosa.
- `201`: recurso creado.
- `204`: eliminación exitosa sin contenido.
- `401`: credenciales incorrectas.
- `404`: recurso no encontrado.
- `409`: conflicto de datos, por ejemplo documento duplicado.
- `422`: datos de entrada no válidos.

Los errores de FastAPI se entregan en JSON mediante la propiedad `detail`.
