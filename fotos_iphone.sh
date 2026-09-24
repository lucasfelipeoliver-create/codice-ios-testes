#!/bin/bash
# Roda NO MAC do GitHub Actions: Safari REAL no Simulador de iPhone, uma captura por estado e por aparelho.
# Os estados abrem por URL (link profundo ?cod= do Códice e os ganchos de teste do preparar_site.py) — sem digitação.
set -uo pipefail
python3 -m http.server 8000 --directory site > /tmp/servidor.log 2>&1 &
sleep 3
mkdir -p fotos
xcrun simctl list runtimes
for DEV in "iPhone 16" "iPhone SE (3rd generation)" "iPhone 16 Pro Max"; do
  UDID=$(xcrun simctl list devices available -j | python3 -c '
import json, sys
d = json.load(sys.stdin)["devices"]
c = sorted((rt, x["udid"]) for rt, l in d.items() if "iOS-18" in rt for x in l if x["name"] == sys.argv[1])
print(c[-1][1] if c else "")' "$DEV")
  if [ -z "$UDID" ]; then echo "SEM SIMULADOR: $DEV"; continue; fi
  echo "== $DEV ($UDID)"
  xcrun simctl boot "$UDID" || true
  xcrun simctl bootstatus "$UDID" -b
  N=$(echo "$DEV" | tr ' ()' '___')
  for PAR in "inicio|" "ficha|?cod=SICRO:1106135" "instalar|?teste-instalar=1" "entrar_app|?sem-sessao=1&teste-app=1"; do
    NOME=${PAR%%|*}; Q=${PAR#*|}
    xcrun simctl openurl "$UDID" "http://localhost:8000/index.html$Q"
    sleep 75
    xcrun simctl io "$UDID" screenshot "fotos/${N}_${NOME}.png" && echo "foto: ${N}_${NOME}"
  done
  xcrun simctl shutdown "$UDID" || true
done
ls -la fotos
