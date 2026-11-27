#!/usr/bin/env bash
# Crea en el clúster el Secret de la aplicación (y el de Grafana) con valores ALEATORIOS.
# Nada se guarda en archivos ni en el repositorio. Las claves generadas se muestran una sola vez.
#
#   ./scripts/k8s-crear-secret.sh
#   ADMIN_PASSWORD=miClave ./scripts/k8s-crear-secret.sh     # para fijar la clave del usuario admin
set -euo pipefail

aleatorio() { python3 -c "import secrets; print(secrets.token_urlsafe(${1:-24}))"; }

DB_PASS="$(aleatorio 18)"
JWT_SECRET="$(aleatorio 32)"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-$(aleatorio 12)}"
GRAFANA_PASSWORD="${GRAFANA_PASSWORD:-$(aleatorio 12)}"

kubectl apply -f k8s/namespace.yaml
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

kubectl -n rhcontrol create secret generic rhcontrol-secret \
  --from-literal=POSTGRES_USER=rhcontrol \
  --from-literal=POSTGRES_PASSWORD="$DB_PASS" \
  --from-literal=DATABASE_URL="postgresql+psycopg://rhcontrol:${DB_PASS}@postgres:5432/rhcontrol" \
  --from-literal=JWT_SECRET="$JWT_SECRET" \
  --from-literal=ADMIN_PASSWORD="$ADMIN_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl -n monitoring create secret generic grafana-admin \
  --from-literal=admin-user=admin \
  --from-literal=admin-password="$GRAFANA_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f -

echo
echo "Secrets creados. Guarda estas claves (no se vuelven a mostrar):"
echo "  Usuario de la app : admin / $ADMIN_PASSWORD"
echo "  Grafana           : admin / $GRAFANA_PASSWORD"
echo "AVISO: si la base de datos ya existe (volumen persistente), NO vuelvas a ejecutar este script:"
echo "cambiaría POSTGRES_PASSWORD y la base conservaría la contraseña anterior."
