# -*- coding: utf-8 -*-
"""Roda NO MAC do GitHub Actions (camada 2 do teste do Códice no iPhone — PESQUISA_IOS_GITHUB_20260923.md §4b).

Baixa o Códice PUBLICADO (GitHub Pages, público), aplica a camada iPhone exatamente como o build e o publicador fazem
(mobile_ios.injetar + ios_pwa.camada_head, cópias fiéis em ./camada) e acrescenta GANCHOS DE TESTE (só nesta cópia):
  - sessão gravada (a tela de entrada do celular não cobre o app), exceto com ?sem-sessao;
  - ?teste-instalar abre a folha "Instale o Códice no iPhone" sem precisar digitar duas buscas;
  - ?teste-app força o modo "app instalado" (html.ios-app: aviso de login).
Saída: ./site (index + fatias de preço citadas em data-externa), servida por http.server no próprio Mac.
"""
import re
import sys
import urllib.request
from pathlib import Path

BASE = "https://lucasfelipeoliver-create.github.io/acervo-bancos-referencia/"
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI / "camada"))
import ios_pwa  # noqa: E402
import mobile_ios  # noqa: E402

GANCHO = ("<script id=\"teste-iphone\">(function(){var q=location.search;"
          "try{if(q.indexOf('sem-sessao')<0)sessionStorage.setItem('codice_sessao_ativa_v2',JSON.stringify({usuario:'teste-iphone'}));}catch(e){}"
          "if(q.indexOf('teste-app')>=0)window.__codiceIOSForcar={app:true};"
          "if(q.indexOf('teste-instalar')>=0){var t=setInterval(function(){if(window.__codiceIOS&&window.__codiceIOS.pronto"
          "&&document.body&&document.body.dataset.pronto==='1'){clearInterval(t);window.__codiceIOS.mostrarInstalar(true);}},500);}"
          "})();</script>")


def baixar(rel: str) -> bytes:
    with urllib.request.urlopen(BASE + rel, timeout=180) as r:
        return r.read()


def main():
    site = AQUI / "site"
    site.mkdir(exist_ok=True)
    html = baixar("index.html").decode("utf-8")
    print("index publicado:", len(html), "caracteres")
    if html.count(ios_pwa.VIEWPORT_BASE) != 1:
        sys.exit("ABORTA: viewport do publicado mudou de forma")
    html = html.replace(ios_pwa.VIEWPORT_BASE, ios_pwa.VIEWPORT_IOS + ios_pwa.tags())
    if 'id="codice-ios"' not in html:
        html = mobile_ios.injetar(html)
    i = html.find("<head>")
    html = html[:i + 6] + GANCHO + html[i + 6:]
    (site / "index.html").write_text(html, encoding="utf-8", newline="")
    rels = sorted(set(re.findall(r'data-externa="([^"]+)"', html)))
    for rel in ([] if "--sem-fatias" in sys.argv else rels):  # --sem-fatias: prova local com pouco disco
        p = site / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(baixar(rel))
    n_camada = html.count('id="codice-ios"')
    print(f"site pronto: index + {len(rels)} fatias externas; camada iPhone: {n_camada}")
    if n_camada != 1:
        sys.exit("ABORTA: camada iPhone ausente ou duplicada")


if __name__ == "__main__":
    main()
