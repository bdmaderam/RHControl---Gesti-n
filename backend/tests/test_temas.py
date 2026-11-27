from datetime import date, timedelta

import pytest

from app.services import temas
from app.services.revisor import Previa

HOY = date(2026, 11, 20)


def claves(texto, tipo="Llamado de atención"):
    return {t["tema"] for t in temas.detectar(texto, tipo)}


# ---------- un caso positivo y uno negativo por tema ----------
CASOS = [
    ("puntualidad", "Llegó tarde tres veces esta semana", "Entregó el informe de ventas a tiempo"),
    ("asistencia", "Se ausentó dos días sin avisar", "Realizó la entrega del informe"),
    ("seguridad", "No usó el casco ni los guantes en la bodega", "Presentó el informe de ventas"),
    ("trato", "Faltó al respeto a un compañero y gritó en la reunión", "Entregó el informe mensual"),
    ("desempeno", "Incumplió la entrega del informe en la fecha acordada", "Llegó a las 8:00 am"),
    ("normas", "Incumplió el reglamento interno de trabajo", "Llegó a las 8:00 am"),
    ("recursos", "Hizo uso indebido del computador de la empresa", "Llegó a las 8:00 am"),
    ("comunicacion", "No avisó ni respondió los mensajes del jefe", "Llegó a las 8:00 am"),
    ("equipo", "No colaboró con sus compañeros del área", "Llegó a las 8:00 am"),
    ("cliente", "Recibió un reclamo de un cliente por mala atención", "Llegó a las 8:00 am"),
    ("liderazgo", "Mostró liderazgo e iniciativa en el proyecto", "Llegó a las 8:00 am"),
    ("formacion", "Completó el curso de certificación", "Llegó a las 8:00 am"),
    ("administrativo", "Falta actualizar la cuenta bancaria en nómina", "Llegó a las 8:00 am"),
]


@pytest.mark.parametrize("tema,malo,neutro", CASOS)
def test_detecta_el_tema_y_no_se_activa_sin_pistas(tema, malo, neutro):
    assert tema in claves(malo), f"{tema} debía detectarse"
    assert tema not in claves(neutro)


def test_catalogo_completo():
    assert len(temas.TEMAS) >= 12


def test_negacion_anula_el_tema():
    assert "puntualidad" not in claves("Sin tardanzas durante todo el mes", "Felicitación")
    assert "asistencia" not in claves("No se ausentó ni un solo día", "Felicitación")


def test_tono_segun_tipo_y_texto():
    assert temas.detectar("Llegó tarde", "Llamado de atención")[0]["tono"] == "negativo"
    assert temas.detectar("Puntualidad ejemplar", "Felicitación")[0]["tono"] == "positivo"
    assert temas.detectar("Llegó tarde varias veces", "Observación")[0]["tono"] == "negativo"
    assert temas.detectar("Pendiente revisar el horario", "Observación")[0]["tono"] == "neutro"
    # los temas positivos por naturaleza nunca son negativos
    assert all(t["tono"] == "positivo" for t in temas.detectar("Curso de liderazgo", "Llamado de atención")
               if t["tema"] in ("liderazgo", "formacion"))


def test_varios_temas_en_una_anotacion():
    assert {"puntualidad", "trato"} <= claves("Llegó tarde y gritó a un compañero")


# ---------- reincidencia ----------
def previa(i, dias, texto, tipo="llamado"):
    return Previa(i, tipo, HOY - timedelta(days=dias), texto)


def test_segunda_vez_se_repite_y_tercera_es_reincidente():
    una = [previa(1, 10, "Llegó 15 minutos tarde")]
    r = temas.analizar("Otra vez llegó tarde", "Llamado de atención", HOY, una, hoy=HOY, registrar_metricas=False)
    assert r["reincidencias"][0]["tema"] == "puntualidad" and r["reincidencias"][0]["nivel"] == "se_repite"
    dos = una + [previa(2, 30, "Tardanza de media hora")]
    r = temas.analizar("Otra vez llegó tarde", "Llamado de atención", HOY, dos, hoy=HOY, registrar_metricas=False)
    assert r["reincidencias"][0]["ocurrencias"] == 3 and r["reincidencias"][0]["nivel"] == "reincidente"


def test_no_hay_reincidencia_si_es_antigua_otro_tema_o_positiva():
    vieja = [previa(1, 400, "Llegó tarde")]
    otro = [previa(2, 5, "Falta actualizar la cuenta bancaria")]
    positiva = [previa(3, 5, "Puntualidad ejemplar", "felicitacion")]
    for h in (vieja, otro, positiva):
        r = temas.analizar("Llegó tarde", "Llamado de atención", HOY, h, hoy=HOY, registrar_metricas=False)
        assert r["reincidencias"] == []


def test_una_felicitacion_nunca_genera_reincidencia():
    h = [previa(1, 5, "Llegó tarde"), previa(2, 8, "Llegó tarde")]
    r = temas.analizar("Puntualidad ejemplar este mes", "Felicitación", HOY, h, hoy=HOY, registrar_metricas=False)
    assert r["reincidencias"] == []


def test_al_editar_no_se_cuenta_a_si_misma():
    propia = [Previa(7, "llamado", HOY, "Llegó tarde")]
    r = temas.analizar("Llegó tarde", "Llamado de atención", HOY, propia, hoy=HOY, anotacion_id=7, registrar_metricas=False)
    assert r["reincidencias"] == []


def test_perfil_del_empleado():
    h = [previa(1, 5, "Llegó tarde"), previa(2, 20, "Llegó tarde otra vez"), previa(3, 300, "Llegó tarde"),
         previa(4, 2, "Excelente trato con el cliente", "felicitacion")]
    p = temas.perfil_empleado(h, hoy=HOY)
    assert p["anotaciones"] == 4
    assert [a["tema"] for a in p["alertas"]] == ["puntualidad"] and p["alertas"][0]["ocurrencias"] == 2
    punt = next(t for t in p["temas"] if t["tema"] == "puntualidad")
    assert punt["negativas"] == 3
    assert any(t["tema"] == "cliente" and t["positivas"] == 1 for t in p["temas"])


# ---------- endpoints ----------
def crear_emp(client, h, doc="9001"):
    return client.post("/api/empleados", headers=h, json={"nombres": "Rosa", "apellidos": "Díaz", "numero_documento": doc,
                                                           "cargo": "Auxiliar"}).json()["id"]


def anotar(client, h, emp, tipo, texto, dias=0):
    r = client.post(f"/api/anotaciones/empleado/{emp}", headers=h, json={
        "tipo": tipo, "descripcion": texto, "fecha": (date.today() - timedelta(days=dias)).isoformat()})
    assert r.status_code in (200, 201), r.text


def test_endpoints_de_temas_requieren_jwt(client):
    assert client.get("/api/ia/temas-empleado/1").status_code == 401
    assert client.get("/api/ia/reincidencias").status_code == 401


def test_revisar_incluye_temas_y_reincidencia(client, auth_headers):
    emp = crear_emp(client, auth_headers)
    anotar(client, auth_headers, emp, "Llamado de atención", "El lunes llegó tarde por segunda vez", 10)
    r = client.post("/api/ia/revisar-anotacion", headers=auth_headers, json={
        "descripcion": "Hoy otra vez llegó tarde", "tipo": "Llamado de atención", "empleado_id": emp}).json()
    assert r["temas"][0]["tema"] == "puntualidad"
    assert r["reincidencias"][0]["nivel"] == "se_repite"


def test_temas_empleado_y_404(client, auth_headers):
    emp = crear_emp(client, auth_headers)
    anotar(client, auth_headers, emp, "Llamado de atención", "Llegó tarde al turno", 3)
    anotar(client, auth_headers, emp, "Llamado de atención", "Tardanza de 30 minutos", 9)
    d = client.get(f"/api/ia/temas-empleado/{emp}", headers=auth_headers).json()
    assert d["empleado_id"] == emp and d["alertas"][0]["tema"] == "puntualidad"
    assert client.get("/api/ia/temas-empleado/99999", headers=auth_headers).status_code == 404


def test_reincidencias_lista_solo_a_quienes_repiten(client, auth_headers):
    a = crear_emp(client, auth_headers, "9101")
    b = crear_emp(client, auth_headers, "9102")
    for dias in (2, 12, 25):
        anotar(client, auth_headers, a, "Llamado de atención", "Llegó tarde", dias)
    anotar(client, auth_headers, b, "Llamado de atención", "Llegó tarde", 2)
    d = client.get("/api/ia/reincidencias", headers=auth_headers).json()
    assert [e["empleado_id"] for e in d["empleados"]] == [a]
    assert d["empleados"][0]["alertas"][0]["nivel"] == "reincidente"
    assert client.get("/api/ia/reincidencias?minimo=1", headers=auth_headers).status_code == 422


def test_metricas_de_temas(client, auth_headers):
    client.post("/api/ia/revisar-anotacion", headers=auth_headers, json={"descripcion": "Llegó tarde", "tipo": "Llamado de atención"})
    t = client.get("/metrics").text
    assert 'ia_temas_detectados_total{tema="puntualidad",tono="negativo"}' in t
