# RETOMADA — sessões na nuvem

Canal de estado entre sessões do Claude Code na nuvem. Atualizar ao fim de cada sessão (o que foi feito, com prova;
o que ficou; próximo passo). Fontes desta entrada: backup do Drive até ~18/09/2026, repositório
`acervo-bancos-referencia` (último commit 30/09/2026), Gmail/Agenda (leitura em 14/10/2026).

## Estado em 14/10/2026

**Códice** = nome (16/09) do Buscador de Bancos V5: HTML estático gerado por `build_buscador_v5.py`
(`D:\GOOGLE DRIVE\BANCOS\_SCRIPTS\busca_bancos\v3\f10_interface\build_v5\`), 13 bancos, 67.113 códigos, 5 portões
Playwright antes de publicar; preços em `_precos/*.js`.
- Publicação: GitHub Pages (`acervo-bancos-referencia`) com PWA/service worker; vitrine `/vitrine/` (30/09);
  APK TWA `io.github.lucasfelipeoliver.codice` 1.0.1–1.0.3; Cloudflare Pages `codice-f12.pages.dev`; domínio
  `codice.app.br` na Cloudflare (ativo 04/10).
- Acesso: porteiro em Cloudflare Pages Functions + Supabase Auth (ES256/JWKS, cookie HttpOnly via BFF); piloto por
  convite; ~7–8 convites enviados 30/09–05/10.
- Cobrança: desenhada com Stripe (Checkout, Portal, webhook único que libera acesso); onboarding Stripe incompleto;
  decisão dele: pagamento real espera, prioridade é o piloto.
- Dados: ciclo diário de datas-base (`ciclo_datas_base.py`, Agendador `\GMAI-Vigia-DatasBase` 07:15). Em 18/09:
  SINAPI 2026-08, SICRO 2026-04, SUDECAP 2026-07, SIURB 2026-07, AGESUL 2026-06, DER-ES 2026-05.
- iPhone: este repositório — camada 2 (Safari no Simulador via GitHub Actions); workflow ainda não instalado (falta
  permissão `workflow`); próxima etapa: Maestro (modo app instalado).

## Pendências conhecidas (dele = ato de conta/decisão)

- [dele] Supabase: projeto antigo pausado (restaurável até ~28/12); migrar Oregon → São Paulo; a partir de 30/10
  tabelas novas em `public` exigem GRANT explícito; SMTP pelo Gmail pessoal tem limite.
- [dele] Confirmar `codice.app.br` como domínio do Pages e ajustar redirect do Supabase Auth (ainda `pages.dev`).
- [dele] Stripe onboarding; entidade fiscal; preços; INPI; contas de loja (Play/Apple).
- [dele] GitHub App "Claude": novas permissões pendentes desde 01/10.
- [técnica] Re-apontar a TWA para o novo host (E4) e corte do GitHub Pages (E7) — o `preparar_site.py` deste repo
  ainda baixa do Pages do acervo.
- [técnica] Plano de 13/09 (busca por eixo, sinônimos, exportação fiel, carimbo de build) não executado até 18/09.
- [técnica] 230 composições novas SINAPI 2026-08 dependem do rebuild do índice f8 (decisão dele).
- [ALERTA segurança] keystore Android e `_senhas_keystore.json` estão no backup do Google Drive — retirar ou restringir.

## Candidatos ao TREINE

- (vazio)
