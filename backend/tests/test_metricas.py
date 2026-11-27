def valor(texto, prefijo):
    """Suma el valor de las líneas de /metrics que empiezan con el prefijo."""
    return sum(float(l.rsplit(" ", 1)[1]) for l in texto.splitlines() if l.startswith(prefijo))


def test_metrics_es_publico_y_tiene_formato_prometheus(client):
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "text/plain" in r.headers["content-type"]
    for nombre in ("http_requests_total", "http_request_duration_seconds", "http_requests_in_progress",
                   "rhcontrol_empleados_activos", "ia_reglas_cargadas", "ia_puntaje_calidad_bucket"):
        assert nombre in r.text


def test_cuenta_requests_con_la_ruta_definida(client, auth_headers):
    antes = valor(client.get("/metrics").text, 'http_requests_total{endpoint="/api/empleados/{empleado_id}"')
    client.get("/api/empleados/1", headers=auth_headers)   # 404: no existe, pero se mide
    client.get("/api/empleados/2", headers=auth_headers)
    despues = valor(client.get("/metrics").text, 'http_requests_total{endpoint="/api/empleados/{empleado_id}"')
    assert despues - antes == 2  # una sola serie para todos los ids, no una por id


def test_no_mide_metrics_ni_probes(client):
    client.get("/api/salud"); client.get("/api/listo"); client.get("/metrics")
    texto = client.get("/metrics").text
    assert 'endpoint="/metrics"' not in texto
    assert 'endpoint="/api/salud"' not in texto
    assert 'endpoint="/api/listo"' not in texto


def test_gauge_de_empleados_activos(client, auth_headers):
    payload = {"nombres": "Ana", "apellidos": "Ruiz", "numero_documento": "555", "cargo": "Analista"}
    assert client.post("/api/empleados", json=payload, headers=auth_headers).status_code == 201
    assert valor(client.get("/metrics").text, "rhcontrol_empleados_activos ") == 1.0


def test_probes(client):
    assert client.get("/api/salud").status_code == 200
    r = client.get("/api/listo")
    assert r.status_code == 200 and r.json()["estado"] == "listo"
