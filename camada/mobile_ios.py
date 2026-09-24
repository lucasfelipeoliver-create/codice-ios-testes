# -*- coding: utf-8 -*-
r"""CAMADA IPHONE — lado do BUILD (24/09/2026, Direção 1 do canvas "Códice iPhone", aprovada por ele).

REUSO: TIER0=mobile_android.py::injetar (mesmo padrão: arquivo NOVO, injeção antes do último </body>, template
intocado) TIER1=AUSENTE_TIER1(ios pwa webview capacitor) TIER2=khmyznikov/pwa-install (MIT, 948★ — padrão da folha de
instalação Safari × navegador de app, sem dependência) + elegantapp/pwa-asset-generator (MIT, 3.036★ — telas de
abertura, lado do publicador: publicar_pages\ios_pwa.py) VEREDITO=CONSTRUIR módulo ao lado.

Injeta `mobile_ios.css` (id="codice-ios") e `mobile_ios.js` (id="mobile-ios") DEPOIS da camada Android, que é
pré-requisito (as rotas/VOLTAR, a ficha em tela cheia e a barra inferior são dela). Tudo fica sob html.ios.
Portão: test_ios_webkit.py (WebKit do Playwright, perfil iPhone 15, 393 px).
"""
from __future__ import annotations

from pathlib import Path

AQUI = Path(__file__).resolve().parent
CSS = AQUI / "mobile_ios.css"
JS = AQUI / "mobile_ios.js"
ID_CSS = "codice-ios"
ID_JS = "mobile-ios"


def injetar(html: str) -> str:
    if f'id="{ID_CSS}"' in html or f'id="{ID_JS}"' in html:
        raise SystemExit("BUILD ABORTADO: camada iPhone já presente no HTML — injeção dupla")
    if 'id="mobile-android"' not in html:
        raise SystemExit("BUILD ABORTADO: camada iPhone exige a camada Android antes (rotas, ficha, barra inferior)")
    i = html.rfind("</body>")
    if i < 0:
        raise SystemExit("BUILD ABORTADO: template sem </body> — não há onde injetar a camada iPhone")
    bloco = (f'<style id="{ID_CSS}">\n' + CSS.read_text(encoding="utf-8") + "\n</style>\n"
             f'<script id="{ID_JS}">\n' + JS.read_text(encoding="utf-8") + "\n</script>\n")
    return html[:i] + bloco + html[i:]
