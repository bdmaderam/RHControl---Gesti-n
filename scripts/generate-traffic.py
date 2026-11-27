#!/usr/bin/env python3
"""Genera tráfico de prueba hacia la API de RHControl (solo librería estándar).

Sirve para llenar de datos los paneles de Grafana y para demostrar el HorizontalPodAutoscaler.
Mezcla lecturas, escrituras (crea y borra un empleado de prueba), llamadas al clasificador de IA
y algunos errores a propósito (sin token -> 401, ruta inexistente -> 404).

Uso:
    python scripts/generate-traffic.py                          # 120 s contra http://localhost:8000
    python scripts/generate-traffic.py --url http://rhcontrol.local --duracion 300
    python scripts/generate-traffic.py --hilos 40 --pausa 0     # carga alta (dispara el HPA)

La contraseña del usuario admin se toma de --password o de la variable ADMIN_PASSWORD.
"""
import argparse
import json
import os
import random
import threading
import time
import urllib.error
import urllib.request

TEXTOS_IA = [  # (tipo, descripción): mezcla de anotaciones bien y mal redactadas para variar los hallazgos
    ("Llamado de atención", "Es un flojo y siempre llega tarde"),
    ("Llamado de atención", "El lunes 3 de noviembre llegó 20 minutos tarde por tercera vez. Se le informó por escrito y se acordó llegar antes de las 8:00; de repetirse se aplicará el reglamento."),
    ("Felicitación", "Felicitaciones por entregar el proyecto Alfa antes del plazo y superar la meta de ventas del trimestre"),
    ("Felicitación", "Buen trabajo"),
    ("Reconocimiento", "Reconocimiento por cinco años de servicio y por lograr los mejores resultados del segundo semestre"),
    ("Observación", "Seguramente se fue temprano, me contaron que no estaba en su puesto"),
    ("Observación", "El martes 4 se detectó que falta actualizar la cuenta bancaria; se programa seguimiento el viernes"),
    ("Llamado de atención", "ES UN INCOMPETENTE!!! NUNCA HACE NADA BIEN!!!"),
]

contador = {"total": 0, "errores_red": 0}
lock = threading.Lock()


def llamar(base, metodo, ruta, token=None, cuerpo=None):
    """Hace una petición y devuelve (código, JSON o None). Los errores HTTP no son excepciones."""
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(base + ruta, data=datos, method=metodo)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            texto = r.read()
            return r.status, (json.loads(texto) if texto else None)
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception:
        with lock:
            contador["errores_red"] += 1
        return 0, None


def iniciar_sesion(base, usuario, password):
    codigo, datos = llamar(base, "POST", "/api/auth/login", cuerpo={"usuario": usuario, "contraseña": password})
    if codigo != 200:
        raise SystemExit(f"No se pudo iniciar sesión (HTTP {codigo}). Revisa --url y --password / ADMIN_PASSWORD.")
    return datos["access_token"]


def ciclo(base, token, id_hilo):
    azar = random.random()
    if azar < 0.25:
        llamar(base, "GET", "/api/empleados", token)
    elif azar < 0.35:
        llamar(base, "GET", "/api/anotaciones", token)
    elif azar < 0.45:
        llamar(base, "GET", f"/api/empleados/{random.randint(1, 5)}", token)   # algunos 404
    elif azar < 0.75:
        tipo, texto = random.choice(TEXTOS_IA)
        llamar(base, "POST", "/api/ia/revisar-anotacion", token, {"descripcion": texto, "tipo": tipo})
    elif azar < 0.82:
        llamar(base, "GET", "/api/ia/auditoria-anotaciones", token)           # la llamada más pesada
        llamar(base, "GET", "/api/ia/reincidencias", token)
    elif azar < 0.90:
        documento = f"T{id_hilo}{int(time.time() * 1000) % 10**9}"
        codigo, emp = llamar(base, "POST", "/api/empleados", token,
                             {"nombres": "Prueba", "apellidos": "Tráfico", "numero_documento": documento, "cargo": "Test"})
        if codigo == 201 and emp:
            llamar(base, "DELETE", f"/api/empleados/{emp['id']}", token)
    elif azar < 0.95:
        llamar(base, "GET", "/api/empleados")                                  # sin token -> 401
    elif azar < 0.98:
        llamar(base, "GET", "/api/ruta-inexistente", token)                    # 404
    else:
        llamar(base, "POST", "/api/auth/login", cuerpo={"usuario": "admin", "contraseña": "incorrecta"})   # 401
    with lock:
        contador["total"] += 1
        if contador["total"] % 50 == 0:
            print(f"[{time.strftime('%H:%M:%S')}] {contador['total']} ciclos enviados")


def trabajador(base, token, fin, pausa, id_hilo):
    while time.time() < fin:
        ciclo(base, token, id_hilo)
        if pausa > 0:
            time.sleep(random.uniform(0, pausa))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default="http://localhost:8000", help="URL base de la API (sin /api)")
    ap.add_argument("--duracion", type=int, default=120, help="segundos de duración")
    ap.add_argument("--hilos", type=int, default=6, help="usuarios simulados en paralelo")
    ap.add_argument("--pausa", type=float, default=0.3, help="pausa máxima (s) entre peticiones de un hilo; 0 = sin pausa")
    ap.add_argument("--usuario", default="admin")
    ap.add_argument("--password", default=os.environ.get("ADMIN_PASSWORD", "admin123"))
    a = ap.parse_args()

    base = a.url.rstrip("/")
    token = iniciar_sesion(base, a.usuario, a.password)
    print(f"Generando tráfico a {base} durante {a.duracion}s con {a.hilos} hilos. Ctrl+C para parar.")
    fin = time.time() + a.duracion
    hilos = [threading.Thread(target=trabajador, args=(base, token, fin, a.pausa, i), daemon=True) for i in range(a.hilos)]
    for h in hilos:
        h.start()
    try:
        while time.time() < fin and any(h.is_alive() for h in hilos):
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    print(f"Listo. Ciclos: {contador['total']} (errores de red: {contador['errores_red']})")


if __name__ == "__main__":
    main()
