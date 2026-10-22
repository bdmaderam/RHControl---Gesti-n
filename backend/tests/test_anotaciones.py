def crear_empleado(client, headers):
    r = client.post(
        "/api/empleados",
        json={"nombres": "Ana", "apellidos": "Torres", "numero_documento": "2001", "cargo": "Analista"},
        headers=headers,
    )
    return r.json()["id"]


def crear_anotacion(client, headers, empleado_id):
    r = client.post(
        f"/api/anotaciones/empleado/{empleado_id}",
        json={"tipo": "Felicitación", "descripcion": "Excelente trabajo en el proyecto"},
        headers=headers,
    )
    return r.json()["id"]


def test_obtener_anotacion_por_id(client, auth_headers):
    empleado_id = crear_empleado(client, auth_headers)
    anotacion_id = crear_anotacion(client, auth_headers, empleado_id)
    r = client.get(f"/api/anotaciones/{anotacion_id}", headers=auth_headers)
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["id"] == anotacion_id
    assert cuerpo["empleado_id"] == empleado_id
    assert cuerpo["tipo"] == "Felicitación"


def test_obtener_anotacion_inexistente_da_404(client, auth_headers):
    r = client.get("/api/anotaciones/9999", headers=auth_headers)
    assert r.status_code == 404
    assert "anotación" in r.json()["detail"].lower()


def test_obtener_anotacion_sin_token_da_401(client):
    assert client.get("/api/anotaciones/1").status_code == 401