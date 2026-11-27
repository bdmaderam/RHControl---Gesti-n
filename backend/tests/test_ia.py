from datetime import date, timedelta

import pytest

from app.services import revisor
from app.services.revisor import Previa, revisar

HOY = date(2026, 11, 20)

LLAMADO_BUENO = ("El lunes 3 de noviembre llegó 20 minutos tarde, por tercera vez en el mes. Se le informó verbalmente "
                 "y por escrito; explicó que tuvo un problema de transporte. Se acordó llegar antes de las 8:00 am "
                 "y, de repetirse, se aplicará el procedimiento del reglamento interno.")
FELICITACION_BUENA = ("Felicitaciones por entregar el proyecto Alfa antes del plazo y superar la meta de ventas "
                      "del trimestre, gracias a su excelente trabajo en equipo.")
RECONOCIMIENTO_BUENO = ("Reconocimiento por cinco años de servicio y por haber logrado los mejores resultados "
                        "del equipo durante el segundo semestre.")
OBSERVACION_BUENA = ("El martes 4 de noviembre se detectó que falta actualizar la cuenta bancaria en nómina. "
                     "Se programa seguimiento el viernes con el área de talento humano.")


def reglas_de(r):
    return {h["regla"] for h in r["hallazgos"]}


def rev(texto, tipo, **kw):
    return revisar(texto, tipo, hoy=HOY, registrar_metricas=False, **kw)


# ---------- textos bien escritos: deben salir limpios ----------
@pytest.mark.parametrize("texto,tipo", [
    (LLAMADO_BUENO, "Llamado de atención"), (FELICITACION_BUENA, "Felicitación"),
    (RECONOCIMIENTO_BUENO, "Reconocimiento"), (OBSERVACION_BUENA, "Observación"),
])
def test_texto_bien_escrito_es_lista(texto, tipo):
    r = rev(texto, tipo)
    assert r["nivel"] == "lista", r["hallazgos"]
    assert r["puntaje"] >= 90
    assert not any(h["severidad"] == "error" for h in r["hallazgos"])


# ---------- una prueba (positiva y negativa) por regla ----------
CASOS = [
    ("F01", "Llegó tarde", "Llamado de atención", LLAMADO_BUENO),
    ("F02", "palabra " * 130, "Observación", OBSERVACION_BUENA),
    ("F03", "asdfgh qwerty zzzzzz", "Observación", OBSERVACION_BUENA),
    ("F04", "ESTO ES INACEPTABLE Y ASI NO SE PUEDE TRABAJAR!!!", "Observación", OBSERVACION_BUENA),
    ("L01", "Es un imbécil y llegó tarde el lunes", "Llamado de atención", LLAMADO_BUENO),
    ("L02", "Es muy flojo y poco profesional en su trabajo", "Observación", OBSERVACION_BUENA),
    ("L03", "Siempre llega tarde y nunca avisa a nadie", "Observación", OBSERVACION_BUENA),
    ("L04", "Seguramente lo hizo a propósito para molestar", "Observación", OBSERVACION_BUENA),
    ("L05", "Me contaron que dicen que se fue temprano sin permiso", "Observación", OBSERVACION_BUENA),
    ("L06", "Se ausentó por su religión y su embarazo durante la semana", "Observación", OBSERVACION_BUENA),
    ("L07", "Llamarlo al 3101234567 o a juan@correo.com por el pendiente", "Observación", OBSERVACION_BUENA),
]


@pytest.mark.parametrize("regla_id,malo,tipo,bueno", CASOS)
def test_regla_se_dispara_y_no_se_dispara(regla_id, malo, tipo, bueno):
    assert regla_id in reglas_de(rev(malo, tipo)), f"{regla_id} debía dispararse con: {malo[:40]}"
    assert regla_id not in reglas_de(rev(bueno, tipo))


def test_regla_de_texto_sensible_es_error_en_llamado():
    r = rev("El lunes 3 se le llama la atención por su religión, tres veces", "Llamado de atención")
    assert next(h for h in r["hallazgos"] if h["regla"] == "L06")["severidad"] == "error"
    assert r["nivel"] == "requiere_correccion"


def test_fecha_futura_y_registro_tardio():
    assert "F05" in reglas_de(rev(LLAMADO_BUENO, "Llamado de atención", fecha=HOY + timedelta(days=3)))
    assert "F06" in reglas_de(rev(LLAMADO_BUENO, "Llamado de atención", fecha=HOY - timedelta(days=200)))
    assert not {"F05", "F06"} & reglas_de(rev(LLAMADO_BUENO, "Llamado de atención", fecha=HOY))
    assert "F06" not in reglas_de(rev(OBSERVACION_BUENA, "Observación", fecha=HOY - timedelta(days=200)))


def test_llamado_incompleto_pide_cuando_cuantas_consecuencia_notificacion_descargos():
    r = rev("Llegó tarde a la oficina y no hizo el informe de ventas completo", "Llamado de atención")
    assert {"C01", "C02", "C03", "C04", "C05"} <= reglas_de(r)


def test_felicitacion_sin_logro_y_reconocimiento_sin_periodo():
    assert "C07" in reglas_de(rev("Felicitaciones por todo lo que hace por la empresa", "Felicitación"))
    assert "C08" in reglas_de(rev("Reconocimiento por haber logrado excelentes resultados", "Reconocimiento"))
    assert "C08" not in reglas_de(rev(RECONOCIMIENTO_BUENO, "Reconocimiento"))


def test_observacion_sin_seguimiento():
    assert "C09" in reglas_de(rev("El martes 4 de noviembre se vio una situación rara en bodega", "Observación"))


def test_norma_obligatoria_ante_falta_grave():
    texto = "El lunes 3 de noviembre hubo una falta grave y se le informó; se acordó una sanción en tres ocasiones"
    assert "C06" in reglas_de(rev(texto, "Llamado de atención"))
    assert "C06" not in reglas_de(rev(texto + " según el reglamento interno", "Llamado de atención"))


# ---------- coherencia y negaciones ----------
def test_felicitacion_con_texto_negativo_es_incoherente():
    r = rev("Llegó tarde tres veces esta semana y faltó sin justificación al turno", "Felicitación")
    assert "T01" in reglas_de(r)


def test_llamado_con_texto_positivo_es_incoherente():
    assert "T01" in reglas_de(rev("Excelente trabajo, felicitaciones por entregar el proyecto antes del plazo", "Llamado de atención"))


def test_negacion_invierte_la_polaridad():
    # "no cumplió las metas" es negativo aunque contenga una palabra positiva
    assert "T01" in reglas_de(rev("No cumplió las metas del trimestre y entregó tarde el informe", "Reconocimiento"))
    # "sin ausencias" es positivo y no debe contradecir a una felicitación
    assert "T01" not in reglas_de(rev("Felicitaciones por cumplir todas las metas del trimestre, sin ausencias", "Felicitación"))


def test_texto_mixto_sugiere_separar():
    r = rev("Excelente trabajo en el proyecto del trimestre pero llegó tarde tres veces", "Observación")
    assert "T02" in reglas_de(r)


# ---------- historial ----------
def test_duplicado_y_reincidencia():
    previa = Previa(1, "llamado", HOY - timedelta(days=30), LLAMADO_BUENO)
    r = rev(LLAMADO_BUENO, "Llamado de atención", fecha=HOY, historial=[previa])
    assert {"H01", "H02"} <= reglas_de(r)
    assert "n.º 2" in next(h for h in r["hallazgos"] if h["regla"] == "H02")["mensaje"]


def test_historial_viejo_no_cuenta_y_se_excluye_la_propia_anotacion():
    vieja = Previa(1, "llamado", HOY - timedelta(days=400), "Otro hecho distinto de hace mucho tiempo")
    assert "H02" not in reglas_de(rev(LLAMADO_BUENO, "Llamado de atención", fecha=HOY, historial=[vieja]))
    propia = Previa(7, "llamado", HOY, LLAMADO_BUENO)
    r = rev(LLAMADO_BUENO, "Llamado de atención", fecha=HOY, historial=[propia], anotacion_id=7)
    assert not {"H01", "H02"} & reglas_de(r)


# ---------- puntaje y tipos ----------
def test_el_puntaje_baja_con_los_hallazgos_y_nunca_es_negativo():
    r = rev("TODO ES UNA MIERDA Y ERES UN IDIOTA SIEMPRE!!!", "Llamado de atención")
    assert 0 <= r["puntaje"] < 50 and r["nivel"] == "requiere_correccion"


def test_tipo_otro_o_vacio_no_rompe():
    assert rev(OBSERVACION_BUENA, "Otro")["puntaje"] > 0
    assert rev(OBSERVACION_BUENA, None)["contexto"]["tipo_evaluado"] is None


def test_catalogo_tiene_reglas_unicas_y_completas():
    ids = [r["id"] for r in revisor.catalogo()]
    assert len(ids) == len(set(ids)) >= 25


# ---------- endpoints ----------
def test_endpoints_requieren_jwt(client):
    assert client.post("/api/ia/revisar-anotacion", json={"descripcion": "hola"}).status_code == 401
    assert client.get("/api/ia/auditoria-anotaciones").status_code == 401
    assert client.get("/api/ia/reglas").status_code == 401


def test_revisar_valida_entrada(client, auth_headers):
    for cuerpo in ({"descripcion": ""}, {"descripcion": "   "}, {"descripcion": "x" * 2001}, {}):
        assert client.post("/api/ia/revisar-anotacion", json=cuerpo, headers=auth_headers).status_code == 422


def test_revisar_devuelve_estructura(client, auth_headers):
    r = client.post("/api/ia/revisar-anotacion", headers=auth_headers,
                    json={"descripcion": FELICITACION_BUENA, "tipo": "Felicitación"})
    assert r.status_code == 200
    d = r.json()
    assert d["nivel"] == "lista" and d["puntaje"] >= 90 and d["cumplidas"]


def test_revisar_usa_el_historial_real(client, auth_headers):
    emp = client.post("/api/empleados", headers=auth_headers, json={
        "nombres": "Ana", "apellidos": "Ruiz", "tipo_documento": "CC", "numero_documento": "555111222",
        "cargo": "Analista", "salario": 3000000, "dependencia": "TI", "tiene_cuenta_bancaria": True}).json()
    g = client.post(f"/api/anotaciones/empleado/{emp['id']}", headers=auth_headers, json={
        "tipo": "Llamado de atención", "descripcion": LLAMADO_BUENO,
        "fecha": date.today().isoformat()})
    assert g.status_code in (200, 201), g.text
    r = client.post("/api/ia/revisar-anotacion", headers=auth_headers, json={
        "descripcion": LLAMADO_BUENO, "tipo": "Llamado de atención", "empleado_id": emp["id"]}).json()
    assert {"H01", "H02"} <= {h["regla"] for h in r["hallazgos"]}
    # al editar la misma anotación no se compara contra sí misma
    r2 = client.post("/api/ia/revisar-anotacion", headers=auth_headers, json={
        "descripcion": LLAMADO_BUENO, "tipo": "Llamado de atención", "empleado_id": emp["id"],
        "anotacion_id": g.json()["id"]}).json()
    assert not {"H01", "H02"} & {h["regla"] for h in r2["hallazgos"]}


def test_auditoria_lista_las_de_baja_calidad(client, auth_headers):
    emp = client.post("/api/empleados", headers=auth_headers, json={
        "nombres": "Luis", "apellidos": "Mora", "tipo_documento": "CC", "numero_documento": "777888999",
        "cargo": "Auxiliar", "salario": 2000000, "dependencia": "Ventas", "tiene_cuenta_bancaria": True}).json()
    for tipo, desc in (("Llamado de atención", "Es un flojo, siempre llega tarde"), ("Felicitación", FELICITACION_BUENA)):
        client.post(f"/api/anotaciones/empleado/{emp['id']}", headers=auth_headers, json={
            "tipo": tipo, "descripcion": desc, "fecha": date.today().isoformat()})
    d = client.get("/api/ia/auditoria-anotaciones", headers=auth_headers).json()
    assert d["revisadas"] == 2 and len(d["anotaciones"]) == 1 and d["anotaciones"][0]["tipo"] == "Llamado de atención"


def test_reglas_y_metricas(client, auth_headers):
    assert client.get("/api/ia/reglas", headers=auth_headers).json()["total"] >= 25
    client.post("/api/ia/revisar-anotacion", headers=auth_headers, json={"descripcion": "Es un flojo", "tipo": "Observación"})
    client.post("/api/ia/revisar-anotacion", headers=auth_headers, json={"descripcion": "Es un flojo", "tipo": "Observación"})
    texto = client.get("/metrics").text
    assert "ia_revisiones_total" in texto and 'ia_hallazgos_total{regla="L02"' in texto
