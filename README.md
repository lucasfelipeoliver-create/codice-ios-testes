# codice-ios-testes

Camada 2 do teste do app Códice no iPhone: **Safari real no Simulador de iPhone**, num Mac do GitHub Actions
(`macos-15`, simuladores iOS 18.x), sem Mac local.

1. `preparar_site.py` baixa o Códice publicado (GitHub Pages) e aplica a camada iPhone (`camada/`, cópias fiéis de
   `build_v5\mobile_ios.*` e `publicar_pages\ios_pwa.py`), mais ganchos de teste que só existem nesta cópia.
2. `fotos_iphone.sh` sobe o site num servidor local do Mac, abre cada estado no Safari do Simulador (iPhone 16,
   iPhone SE 3ª geração, iPhone 16 Pro Max) e tira uma captura por estado.
3. As capturas saem como artefato `fotos-iphone` da execução.

O arquivo `workflow_iphone.yml` vira `.github/workflows/iphone.yml` quando a conta tiver a permissão `workflow`.
Limite declarado: o modo "app instalado" (tela de início, entalhe) exige o fluxo de "Adicionar à Tela de Início" —
próxima etapa (Maestro).
