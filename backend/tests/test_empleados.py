def nuevo_empleado(**extra):
    datos = {
        "nombres": "Ana",
        "apellidos": "Torres",
        "tipo_documento": "CC",
        "numero_documento": "1001",
        "cargo": "Analista",
        "salario": 3500000,
        "dependencia": "Finanzas",
    }
    datos.update(extra)
    return datos


def test_crear_empleado(client, auth_headers):
    r = client.post("/api/empleados", json=nuevo_empleado(), headers=auth_headers)
    assert r.status_code == 201
    cuerpo = r.json()
    assert cuerpo["id"] > 0
    assert cuerpo["nombres"] == "Ana"
    assert cuerpo["activo"] is True


def test_listar_empleados(client, auth_headers):
    client.post("/api/empleados", json=nuevo_empleado(), headers=auth_headers)
    client.post("/api/empleados", json=nuevo_empleado(nombres="Luis", numero_documento="1002"), headers=auth_headers)
    r = client.get("/api/empleados", headers=auth_headers)
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_obtener_empleado_por_id(client, auth_headers):
    creado = client.post("/api/empleados", json=nuevo_empleado(), headers=auth_headers).json()
    r = client.get(f"/api/empleados/{creado['id']}", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["numero_documento"] == "1001"


def test_obtener_empleado_inexistente_da_404(client, auth_headers):
    r = client.get("/api/empleados/9999", headers=auth_headers)
    assert r.status_code == 404


def test_actualizar_empleado(client, auth_headers):
    creado = client.post("/api/empleados", json=nuevo_empleado(), headers=auth_headers).json()
    r = client.put(f"/api/empleados/{creado['id']}", json={"cargo": "Coordinadora"}, headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["cargo"] == "Coordinadora"
    assert r.json()["nombres"] == "Ana"


def test_eliminar_empleado(client, auth_headers):
    creado = client.post("/api/empleados", json=nuevo_empleado(), headers=auth_headers).json()
    r = client.delete(f"/api/empleados/{creado['id']}", headers=auth_headers)
    assert r.status_code == 204
    assert client.get(f"/api/empleados/{creado['id']}", headers=auth_headers).status_code == 404


def test_documento_duplicado_da_409(client, auth_headers):
    client.post("/api/empleados", json=nuevo_empleado(), headers=auth_headers)
    r = client.post("/api/empleados", json=nuevo_empleado(nombres="Otra"), headers=auth_headers)
    assert r.status_code == 409
    assert "documento" in r.json()["detail"].lower()


def test_validacion_rechaza_tipo_de_documento_invalido(client, auth_headers):
    r = client.post("/api/empleados", json=nuevo_empleado(tipo_documento="XX"), headers=auth_headers)
    assert r.status_code == 422


def test_sin_token_da_401(client):
    assert client.get("/api/empleados").status_code == 401