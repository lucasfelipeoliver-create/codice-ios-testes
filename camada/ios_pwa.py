# -*- coding: utf-8 -*-
r"""CAMADA IPHONE do PUBLICADOR — tags da Apple, ícone da tela de início e telas de abertura (24/09/2026, Direção 1
do canvas "Códice iPhone", aprovada por ele; peças "Comum 3 · abertura" do mesmo canvas).

REUSO: TIER0=icones_marca.py (MARCA = o vetor S4 que já faz os ícones do Android; mesma rasterização PyMuPDF+PIL)
+ publicar_pages.CAMADA_HEAD (este módulo só a ESTENDE) TIER1=AUSENTE_TIER1(ios pwa webview capacitor)
TIER2=elegantapp/pwa-asset-generator (MIT, 3.036★): MÉTODO adaptado — a tabela de aparelhos abaixo é a do
`src/config/apple-fallback-data.json` dele (lida em 24/09/2026, 59 aparelhos → 14 tamanhos distintos de iPhone) e a
media query por aparelho segue o formato dele; o Chromium/Puppeteer dele NÃO entra (as imagens saem do nosso vetor).
VEREDITO=ADAPTAR.

Doutrina (a mesma do publicador): nada disto existe no entregue local (Desktop/MOVE); só na cópia hospedada.
Uso pelo publicador: CAMADA_HEAD = ios_pwa.camada_head(CAMADA_HEAD) · ios_pwa.gerar(pasta_do_site, COR_TEMA) ·
ios_pwa.verificar(pasta_do_site). `python ios_pwa.py --autoteste` prova os dois lados (bom passa, quebrado reprova).
"""
from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PASTA_ABERTURA = "ios"
ICONE_APPLE = "apple-touch-icon.png"
TITULO = "Códice"
LEGENDA = "Critério, escopo e preço nos 13 bancos oficiais"

# (largura_px, altura_px, escala) em retrato — apple-fallback-data.json do pwa-asset-generator, só iPhone/iPod.
APARELHOS = [
    (1320, 2868, 3),  # iPhone 17 Pro Max, 16 Pro Max
    (1290, 2796, 3),  # iPhone 16 Plus, 15 Pro Max, 15 Plus, 14 Pro Max
    (1284, 2778, 3),  # iPhone 14 Plus, 13 Pro Max, 12 Pro Max
    (1260, 2736, 3),  # iPhone Air
    (1242, 2688, 3),  # iPhone 11 Pro Max, XS Max
    (1206, 2622, 3),  # iPhone 17 Pro, 17, 16 Pro
    (1179, 2556, 3),  # iPhone 16, 15 Pro, 15, 14 Pro
    (1170, 2532, 3),  # iPhone 16e, 14, 13 Pro, 13, 12 Pro, 12
    (1125, 2436, 3),  # iPhone 11 Pro, XS, X
    (1080, 2340, 3),  # iPhone 13 mini, 12 mini
    (1242, 2208, 3),  # iPhone 8 Plus, 7 Plus, 6s Plus, 6 Plus
    (828, 1792, 2),   # iPhone 11, XR
    (750, 1334, 2),   # iPhone 8, 7, 6s, 6, SE 4.7"
    (640, 1136, 2),   # iPhone SE 4", iPod touch
]


def _nome(w: int, h: int) -> str:
    return f"{PASTA_ABERTURA}/abertura-{w}x{h}.png"


def tags() -> str:
    linhas = [
        f'<link rel="apple-touch-icon" href="{ICONE_APPLE}">',
        '<meta name="apple-mobile-web-app-capable" content="yes">',
        '<meta name="mobile-web-app-capable" content="yes">',
        '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">',
        f'<meta name="apple-mobile-web-app-title" content="{TITULO}">',
    ]
    for w, h, s in APARELHOS:
        mq = (f"(device-width: {w // s}px) and (device-height: {h // s}px) and "
              f"(-webkit-device-pixel-ratio: {s}) and (orientation: portrait)")
        linhas.append(f'<link rel="apple-touch-startup-image" media="{mq}" href="{_nome(w, h)}">')
    return "".join("\n" + x for x in linhas)


VIEWPORT_BASE = '<meta name="viewport" content="width=device-width, initial-scale=1">'
VIEWPORT_IOS = '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'


def camada_head(base: str) -> str:
    """Estende a CAMADA_HEAD do publicador: viewport-fit=cover (o conteúdo vai até atrás da Dynamic Island; a camada
    mobile_ios.css devolve o espaço com env(safe-area-inset-*)) + as tags da Apple. ABORTA se a base mudou de forma."""
    if base.count(VIEWPORT_BASE) != 1:
        raise ValueError("ios_pwa: a CAMADA_HEAD do publicador não traz a viewport esperada — revisar antes de publicar")
    return base.replace(VIEWPORT_BASE, VIEWPORT_IOS) + tags()


def _rasterizar_marca(lado_util: int):
    import fitz  # PyMuPDF
    from PIL import Image
    from icones_marca import MARCA
    doc = fitz.open(stream=MARCA.read_text(encoding="utf-8").encode("utf-8"), filetype="svg")
    pg = doc[0]
    esc = lado_util / pg.rect.width
    pix = pg.get_pixmap(matrix=fitz.Matrix(esc, esc), alpha=True)
    return Image.frombytes("RGBA", (pix.width, pix.height), pix.samples)


def _fonte(tam: int, negrito: bool):
    from PIL import ImageFont
    for nome in (("segoeuib.ttf", "arialbd.ttf") if negrito else ("segoeui.ttf", "arial.ttf")):
        p = Path(r"C:\Windows\Fonts") / nome
        if p.exists():
            return ImageFont.truetype(str(p), tam)
    return ImageFont.load_default()


def gerar(pasta: Path, cor_fundo: str) -> list[Path]:
    """apple-touch-icon.png 180 (opaco — o iOS preenche transparência de preto) + 14 telas de abertura."""
    from PIL import Image, ImageDraw
    feitos = []
    ic = Image.new("RGBA", (180, 180), cor_fundo)
    m = _rasterizar_marca(int(180 * 0.80))
    ic.alpha_composite(m, ((180 - m.width) // 2, (180 - m.height) // 2))
    ic.convert("RGB").save(pasta / ICONE_APPLE, "PNG", optimize=True)
    feitos.append(pasta / ICONE_APPLE)
    (pasta / PASTA_ABERTURA).mkdir(exist_ok=True)
    for w, h, s in APARELHOS:
        img = Image.new("RGBA", (w, h), cor_fundo)
        lado = int(120 * s)
        mk = _rasterizar_marca(lado)
        y0 = int(h * 0.40) - mk.height
        img.alpha_composite(mk, ((w - mk.width) // 2, y0))
        d = ImageDraw.Draw(img)
        f1, f2 = _fonte(34 * s, True), _fonte(15 * s, False)
        y = y0 + mk.height + 18 * s
        for texto, fnt, cor, passo in ((TITULO, f1, "#ffffff", 44), (LEGENDA, f2, "#c7d2e0", 0)):
            cx = d.textbbox((0, 0), texto, font=fnt)
            d.text(((w - (cx[2] - cx[0])) / 2 - cx[0], y - cx[1]), texto, font=fnt, fill=cor)
            y += passo * s
        destino = pasta / _nome(w, h)
        img.convert("RGB").save(destino, "PNG", optimize=True)
        feitos.append(destino)
    return feitos


def verificar(pasta: Path) -> list[str]:
    """Portão de staging: cada imagem citada no index existe, com o tamanho declarado; ícone 180 opaco."""
    import re
    from PIL import Image
    erros = []
    idx = (pasta / "index.html").read_text(encoding="utf-8")
    if "viewport-fit=cover" not in idx:
        erros.append("index sem viewport-fit=cover")
    for nome in ("apple-mobile-web-app-capable", "apple-mobile-web-app-status-bar-style", "apple-mobile-web-app-title"):
        if idx.count(f'name="{nome}"') != 1:
            erros.append(f"meta {nome} ausente ou duplicada")
    if idx.count('rel="apple-touch-icon"') != 1:
        erros.append("apple-touch-icon ausente ou duplicado")
    ic = pasta / ICONE_APPLE
    if not ic.exists() or Image.open(ic).size != (180, 180) or Image.open(ic).mode != "RGB":
        erros.append(f"{ICONE_APPLE} ausente, fora de 180x180 ou com transparência")
    citadas = re.findall(r'rel="apple-touch-startup-image" media="[^"]+" href="([^"]+)"', idx)
    if len(citadas) != len(APARELHOS):
        erros.append(f"telas de abertura citadas: {len(citadas)} (esperadas {len(APARELHOS)})")
    for rel in citadas:
        p = pasta / rel
        mm = re.search(r"abertura-(\d+)x(\d+)\.png$", rel)
        if not p.exists():
            erros.append(f"abertura citada e ausente: {rel}")
        elif mm and Image.open(p).size != (int(mm.group(1)), int(mm.group(2))):
            erros.append(f"abertura com tamanho errado: {rel} = {Image.open(p).size}")
    return erros


def _autoteste() -> int:
    import shutil
    import tempfile
    base = ('\n<link rel="manifest" href="manifest.webmanifest">\n<meta name="theme-color" content="#0b2a4a">\n'
            + VIEWPORT_BASE)
    tmp = Path(tempfile.mkdtemp(prefix="ios_pwa_", dir=r"D:\_temp_ios"))
    falhas = 0
    try:
        cab = camada_head(base)
        (tmp / "index.html").write_text("<html><head>" + cab + "</head><body></body></html>", encoding="utf-8")
        gerar(tmp, "#0b2a4a")
        e = verificar(tmp)
        print(("PASS" if not e else "FAIL") + f"  caso bom: {len(APARELHOS)} aberturas + ícone + tags — {e}")
        falhas += bool(e)
        (tmp / _nome(*APARELHOS[3][:2])).unlink()
        e = verificar(tmp)
        print(("PASS" if e else "FAIL") + f"  caso quebrado (1 abertura apagada) reprova — {e}")
        falhas += not e
        try:
            camada_head(base.replace("initial-scale=1", "initial-scale=1.0"))
            print("FAIL  base de viewport alterada devia abortar")
            falhas += 1
        except ValueError:
            print("PASS  base de viewport alterada aborta (ValueError)")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("AUTOTESTE " + ("PASS" if not falhas else f"REPROVADO ({falhas})"))
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.path.insert(0, str(AQUI))
    sys.stdout.reconfigure(encoding="utf-8")
    if "--autoteste" in sys.argv:
        sys.exit(_autoteste())
    print(__doc__)
