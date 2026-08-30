#!/bin/bash
# Sube la clave de aplicación al secreto SIN que aparezca en pantalla ni en el historial.
#
# Por qué no se usa el portapapeles: la instrucción anterior pedía copiar un comando que LEE el
# portapapeles, así que el portapapeles acababa conteniendo el comando. Aquí no hay esa trampa:
# se pega cuando el guion lo pide, y `read -s` no muestra lo pegado.
set -euo pipefail
read -rs -p "Pega la clave de aplicación y pulsa Enter (no se verá): " CLAVE
echo
LIMPIA="$(printf '%s' "$CLAVE" | tr -d '[:space:]')"
unset CLAVE
N=${#LIMPIA}
if [ "$N" -ne 16 ]; then
  echo "  ✖ Son $N caracteres y deben ser 16. No se sube nada." >&2
  unset LIMPIA; exit 1
fi
printf '%s' "$LIMPIA" | gcloud secrets versions add smtp-clave-cleveria-web \
  --project=cleveria-495203 --data-file=- >/dev/null
unset LIMPIA
echo "  ✓ Subida. Ahora: bash web/desplegar.sh"
