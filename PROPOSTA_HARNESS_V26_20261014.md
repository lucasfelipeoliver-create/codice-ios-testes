# PROPOSTA DE APRIMORAMENTO DO HARNESS GMAI — rumo à V26

Data: 14/10/2026 · Origem: sessão Claude Code na nuvem (`claude.ai/code`) · Destinatário: a sessão local (Kernel GMAI V25.4.9)
e o Lucas, que decide. Esta proposta é CANDIDATA: nada aqui muda o kernel; quem muda é a sessão local, pelo rito
(lint → autoteste → bateria → ciclo → paridade → bump por decisão dele).

## 0. Fontes lidas e limites declarados

| Fonte | O que foi lido | Limite |
|---|---|---|
| `ESTADO_ATUAL_MISSAO.md` V25.4.9 (Drive `1klyjkYHP2lRQznI9fvScSnu6TXJGalWV`, 16/09) | INTEIRO, 566 linhas, 68 KB | cópia de 16/09; a viva está no cofre Obsidian, fora do backup |
| `~/.claude/settings.json` (Drive `1oTz8XCYAGeDBSFtjH0Ofa4Sbd_QZs6ke`, 16/09) | íntegra: 13 handlers, 11 scripts, autoMode | — |
| `passo_zero_gate.py`, `lint_hook.py`, `guarda_harness_hook.py`, `portao_reuso.py`, `portao_conclusao.py` | íntegra (cópias 08–14/09) | `roteador.py` (205 KB) e `lint_execucao.py` (125 KB) só por cabeçalho e docstrings |
| `CLAUDE.md` global (cópias 11 e 12/09), `MEMORY.md` (backup 16/09), `_CONHECIMENTO` (REGRAS_DE_OURO, INDICE_DE_GATILHOS, PERFIL, GMAI_ARQUITETURA) | íntegra ou snippet máximo | memória viva do C: fora do backup |
| `MATRIZ_APRIMORAMENTO_HARNESS_20260915.md`, RETOMADAs de 10–15/09 | por resumo do agente de pesquisa | — |
| Documentação oficial do Claude Code (hooks, memory, sub-agents, skills, plugins, plugin-evals, prompt-caching, costs, monitoring, sandboxing, permission-modes, context-window, remote-control, scheduled-tasks), posts de engenharia da Anthropic, issues #83913/#84011/#93490, docs do Codex e do Antigravity (por trecho), ~20 fontes de comunidade e 8 papers (por resumo) | 45 fontes, lidas 14/10/2026 | `developers.openai.com`, `antigravity.google`, `arxiv.org` bloqueados pelo proxy: itens de lá são [DOC-2ª] ou [PAPER-2ª] |

Rótulos: **FATO** (medido na fonte), **INFERÊNCIA** (dedução minha), **HIPÓTESE** (a medir), **[DOC]/[DOC-2ª]/[COMUNIDADE]/[PAPER-2ª]** (confiança da fonte externa).
Defasagem declarada: o backup do Drive vai até 18/09 e o repositório `acervo-bancos-referencia` até 30/09. Mudanças do kernel entre
18/09 e hoje NÃO estão refletidas aqui. Antes de executar qualquer item, a sessão local confere contra o estado vivo.

## 1. O que o harness já faz bem e NÃO deve mudar

FATO, pelos próprios instrumentos: (1) **trava > texto**, com prova de reprovação pelo `main()` real; (2) **fail-open VISÍVEL**
(RC 1 + stderr, nunca RC 0 mudo); (3) **sentinela** que prova os portões armados a cada partida; (4) contratos e hooks das outras
plataformas **GERADOS** do canônico, com portão de paridade; (5) cabeçalho `REUSO:` obrigatório; (6) fila do TREINE em **quarentena**;
(7) `meta_prova_harness` que cega uma função por vez para apanhar suíte tautológica; (8) memória como **markdown + índice gerado**.
Sobre (8), a pesquisa é unânime no ponto que interessa: a auto-memory nativa do Claude Code (fev/2026) convergiu para exatamente
esse desenho (MEMORY.md truncado em 200 linhas / 25 KB + arquivos de tópico) [DOC]; e os benchmarks de Mem0/Zep/Letta são
auto-reportados, com reproduções independentes caindo para 37–52 % [COMUNIDADE]. A decisão de 26/08 de não adotar mem0/Graphiti/
LightRAG continua correta. Não há motivo para vetor ou grafo como fonte de verdade de um único usuário.

## 2. Diagnóstico: seis achados medidos

**A1 — O Passo Zero custa ~34 mil tokens por sessão, em 3 plataformas.** FATO: `ESTADO_ATUAL_MISSAO.md` tem 68.328 B / 566 linhas;
o `passo_zero_gate.py` exige leitura INTEGRAL (micro-leitura reprova) em toda sessão de Claude, Codex e Antigravity. Das 566 linhas,
~530 são histórico de lotes (25.3.1 → 25.4.9); estado mesmo são o "Status geral" e o quadro §2. INFERÊNCIA: somando `CLAUDE.md`
(18 KB), `MEMORY.md` (~12 KB) e o pacote do roteador (≤ 9.800 B por prompt), cada sessão nasce com ~50 mil tokens antes do primeiro
pedido. O instinto 29 ("para entrar algo, algo sai") foi aplicado ao `CLAUDE.md` (teto congelado) e ao pacote (9.800 B), mas não à
âncora, que é o maior item e cresce a cada lote.

**A2 — O harness está gastando a cota com ele mesmo.** FATO: o histórico de 25.4.0 a 25.4.9 (02/09 → 16/09) é quase todo trabalho
de kernel (lotes 9–48, revisões cruzadas, 6 passes do Codex sobre lotes do próprio harness); o Codex bateu limite semanal 2× e o
Claude ficou "sem token" em 14/10. INFERÊNCIA: não há métrica de **proporção meta-trabalho × trabalho de domínio** no painel; o
`_TERMO_KERNEL` já classifica missões de kernel no `despachar.py`, então o número existe em potência, mas não é reportado nem tem teto.

**A3 — O cache de prompt não é medido e a injeção por prompt o derruba.** FATO [DOC]: o Claude Code cacheia por prefixo; conteúdo
que muda a cada turno invalida o que vem depois. FATO [COMUNIDADE, issues abertas #83913/#93490]: `additionalContext` em
PreToolUse/PostToolUse reescreve ~22 K tokens por turno e `--resume` reescreve até ~385 K (escrita custa ~80× a leitura em cache).
FATO (kernel): o roteador injeta a cada `UserPromptSubmit` um pacote variável (versão, estado, caixa do nó, saldo das 3 plataformas);
`roteador --agente-hook` injeta em `PreToolUse Agent`. O painel mede bytes por pacote, não cache hit. Manus e a equipe do Claude Code
tratam hit rate < 90 % como incidente [COMUNIDADE].

**A4 — O kernel usa 4 eventos de hook de 33 existentes.** FATO [DOC, hooks reference, v2.1.296]: existem `ConfigChange`,
`InstructionsLoaded`, `SubagentStart` (matcher por tipo), `SessionStart` com matcher `compact`, `PreCompact`/`PostCompact`,
`onFailure: "block"`, handlers `prompt`/`agent`, `async`/`asyncRewake`. FATO (kernel): a guarda de `settings.json` é PostToolUse
(detecta depois de gravar); o despacho por domínio roda em `PreToolUse Agent` por regex no `subagent_type`; nada reinjeta o núcleo
após compactação (o contexto injetado por hook é RESUMIDO junto com o resto [DOC]); nada grava RETOMADA antes de compactar.

**A5 — Governança sem fronteira na máquina.** FATO: `defaultMode: bypassPermissions` + `skipDangerousModePermissionPrompt`; ao mesmo
tempo há `autoMode.soft_deny` (que só vale no modo `auto`) — as duas configurações coexistem e uma delas é inerte. FATO [DOC]: no
Windows nativo não existe sandbox de Bash; hooks e MCP rodam fora dele; deny rules são "fricção, não fronteira" [COMUNIDADE].
FATO: `codice.keystore` e `_senhas_keystore.json` estão no backup do Google Drive (2 cópias cada). FATO: nada escaneia segredo na
fila do TREINE nem na memória, e a fila captura saída de comandos.

**A6 — Durabilidade assimétrica.** FATO: o kernel está em git desde 11/09 (`D:\_git\gmai_scripts.git`, git-dir fora do Drive) —
sem remoto. A memória viva (`C:\Users\Lucas\.claude\projects\...\memory`, ~290 arquivos) está fora do backup D: e fora do git; no Drive
só há o índice de 16/09 e corpos até 08/09. 46 de 68 autotestes exercitam função, não o `main()` (H11, declarado). A suíte noturna
ainda não cumpriu as 3 noites (H18). O `registro_conhecimento.py` só apareceu como `.pyc` no backup.

## 3. Propostas (ordenadas por efeito ÷ custo)

Formato de cada item: achado → proposta → instrumento → prova de reprovação → custo/risco → REUSO → onde roda.

### P1. Âncora em duas camadas: ESTADO (≤ 8 KB) + CHANGELOG (append-only)
- **Achado:** A1.
- **Proposta:** `ESTADO_ATUAL_MISSAO.md` passa a conter só: versão vigente, 5–10 linhas de status, pendências dele, pendências
  técnicas abertas, e o quadro §2 como PONTEIROS (nome da trava + instrumento entre crase), sem narrativa. O histórico de lotes vai
  para `CHANGELOG_HARNESS.md` (só anexa; lido por demanda). O quadro §2 migra para `instincts.json` (já é a SSOT) e deixa de ser
  texto duplicado.
- **Instrumento:** `guarda_harness_hook.py` ganha um teto para a âncora, no mesmo JSON do teto do CLAUDE.md
  (`claude_md_teto.json` → `tetos_contexto.json` com `claude_md`, `estado_missao`, `memory_md`), só mudável por
  `--congelar-teto --motivo`. `passo_zero_gate.py` aceita a âncora curta e recusa o CHANGELOG como Passo Zero (nome ≠ identidade,
  lição do lote 36).
- **Prova de reprovação:** autoteste com âncora de 9 KB → reprova; CHANGELOG lido como Passo Zero → não destrava; `painel_operacao.py`
  publica tokens-por-partida antes/depois (medir com `/context` numa sessão nova: a simulação oficial dá ~4,2 K de system prompt +
  ~680 de MEMORY.md [DOC]; a meta é partida < 15 K tokens no total).
- **Custo/risco:** 1 lote; risco de perder contexto histórico útil → o roteador indexa o CHANGELOG no SQLite e injeta o trecho
  quando o tema casa (já é o padrão "just-in-time" dele).
- **REUSO:** TIER0 = `claude_md_teto.json` + `guarda_harness_hook` (mesma mecânica). TIER2 = padrão "structured note-taking"
  (Anthropic, effective-context-engineering, 09/2025) e "recitação de todo.md no fim do contexto" (Manus). VEREDITO = ADAPTAR o próprio.
- **Onde roda:** local.

### P2. Cache de prompt como métrica de primeira classe
- **Achado:** A3.
- **Proposta:** (a) separar o pacote do roteador em **núcleo estável** (versão, Passo Zero, travas, regras de ouro — byte-idêntico
  entre turnos, sem carimbo de hora, sem saldo) injetado em `SessionStart` (matchers `startup|resume|compact`) e **delta por prompt**
  (só o que casou com o pedido, ≤ 3.000 B); (b) tirar do pacote por prompt tudo que muda sozinho (saldo das 3 plataformas, caixa do
  nó, deriva) e mover para `SessionStart` ou para o `statusLine`; (c) o `--agente-hook` em PreToolUse injeta o mínimo (a recusa é
  deny com razão; o pacote vai na missão, como já é) — nada de `additionalContext` em PreToolUse.
- **Instrumento:** `painel_operacao.py` ganha `cache_hit_pct` lido de `~/.claude/projects/<proj>/*.jsonl` (`cache_read_input_tokens`
  × `cache_creation_input_tokens` por request) e, opcional, OTel (`CLAUDE_CODE_ENABLE_TELEMETRY=1`, exporter `console`/`prometheus`
  local; métrica `claude_code.token.usage` com `type=cacheCreation`) [DOC]. Camada `cache_prompt` no `ciclo.py`.
- **Prova de reprovação:** sessão de controle com pacote variável (como hoje) deve medir hit < 90 %; com núcleo estável, ≥ 90 %
  após o 2º turno. Sem medição = RC 3, nunca verde (regra da casa).
- **Custo/risco:** 1–2 lotes. Risco: `SessionStart` no `resume` reenviar o núcleo sem cache (#93490) — medir; se confirmar, injetar
  o núcleo só em `startup|compact` e deixar o `resume` com o delta.
- **REUSO:** TIER2 = `/usage` linha "Prompt cache (main)" (v2.1.251+), `promptCacheTtl` 1 h em assinatura [DOC];
  `__SYSTEM_PROMPT_DYNAMIC_BOUNDARY__` para quem usa `--system-prompt` [DOC]. VEREDITO = CONSTRUIR o leitor (pequeno).
- **Onde roda:** local.

### P3. Adotar os eventos nativos que substituem regex por contrato
- **Achado:** A4.
- **Proposta, em ordem de valor:**
  1. **`ConfigChange`** (matchers `user_settings|local_settings|skills`): `exit 2` para qualquer mudança em `settings*.json` e
     `skills/` que não venha de um condutor do protocolo (marca em disco, como o `_harness_tocado.flag`). Hoje a guarda só avisa
     depois (PostToolUse); a meia-instalação de 27/08 que trancou duas sessões não teria passado.
  2. **`SessionStart` matcher `compact`** + **`PreCompact`**: antes de compactar, gravar `RETOMADA_<sessao>.md` automático
     (o estado se grava em RETOMADA, regra da casa); após compactar, reinjetar o núcleo estável de P2. Hoje a compactação apaga
     o pacote e nada o repõe [DOC].
  3. **`SubagentStart`** com matcher por tipo: o despacho por domínio passa a ter o tipo pelo contrato, não por regex no payload;
     `roteador --agente-hook` continua em PreToolUse só para a válvula `DESPACHO_DECLARADO` e o ledger.
  4. **`InstructionsLoaded`**: ledger do que entrou no contexto em cada partida (quais CLAUDE.md, rules, AGENTS.md) — fecha a
     medição de A1 sem adivinhar.
  5. **`onFailure: "block"`** (v2.1.295+) SÓ nos portões bloqueantes cuja prova a sentinela já fez na partida
     (`passo_zero_gate`, `lint_hook`): fail-open visível continua sendo o contrato padrão; fail-closed vira opção declarada por
     portão, depois de provado.
  6. **`memory: project`** no frontmatter dos agentes de domínio (especialista-sinapi/sicro/sicor/sudecap): memória própria do
     agente, versionável em `.claude/agent-memory/` [DOC] — tira da fila do TREINE o que é aprendizado local do especialista.
- **Instrumento:** `validar_settings_hooks.py` aprende os eventos novos; `sincronizar_hooks_claude_codex/antigravity.py` declaram
  `SEM_EQUIVALENTE` para o que Codex/AG não têm (Codex tem `PreCompact/PostCompact` e `SubagentStart` desde v0.129 [DOC-2ª];
  AG não tem nenhum dos cinco).
- **Prova de reprovação:** por item, caso negativo no `--testar` (edição de settings sem marca → bloqueada; compactação sem
  RETOMADA → acusada no ciclo; subagente genérico em missão SINAPI → negado pelo matcher).
- **Custo/risco:** 2 lotes. Risco de paridade: os eventos não existem no AG → declarar, como já se faz com `aviso_via_imagem`.
- **REUSO:** TIER2 = reference oficial de hooks e `hooks-guide` ("re-inject context after compaction" é o padrão oficial) [DOC].
  VEREDITO = ADAPTAR.
- **Onde roda:** local.

### P4. Orçamento de meta-trabalho (o harness não pode consumir a cota do domínio)
- **Achado:** A2.
- **Proposta:** declarar um teto de proporção (sugestão para decisão dele: ≤ 25 % dos turnos/tokens por semana em missões de
  kernel) e publicar o número vivo no painel e no pacote de partida.
- **Instrumento:** `placar_despacho.py` já lê `despacho_decisoes.jsonl`; acrescentar a classe `KERNEL` (reusar `_TERMO_KERNEL` do
  `despachar.py`) e somar tokens por classe a partir dos `.jsonl` de sessão. Portão: acima do teto, o pacote de partida injeta
  "ORÇAMENTO DE KERNEL ESTOURADO: só correção de regressão até <data>" e o `roteador --agente-hook` nega missão de kernel sem
  `KERNEL_DECLARADO: <motivo>` (mesma válvula de `DESPACHO_DECLARADO`).
- **Prova de reprovação:** ledger sintético com 40 % kernel → portão nega; 20 % → libera.
- **Custo/risco:** 1 lote. Risco: o teto errado trava correção urgente → a válvula existe para isso e fica no ledger.
- **REUSO:** TIER0 = `placar_despacho.py`, `_TERMO_KERNEL`. VEREDITO = ADAPTAR.
- **Onde roda:** local.

### P5. Memória: esquecimento explícito e avaliação própria
- **Achado:** `uso_memoria.json` já mede memórias "nunca lidas" (26/08); não há política para elas. 290 arquivos crescem linearmente;
  o survey "Always-On Agents" mostra que sem gestão a latência de recuperação sobe com o tamanho [PAPER-2ª].
- **Proposta:** (a) política de **decaimento**: memória `project_*` sem leitura em N dias (sugestão: 120) e sem wikilink de
  entrada vai para `indice_project_historico` (já existe) e sai do `MEMORY.md`; `feedback_*` nunca decai sozinho (é vacina);
  (b) **dedup na consolidação**: o `gravar_memoria.py` já recusa similar; estender ao TREINE como passo que lista pares com
  similaridade alta para fusão de ARQUIVOS (nunca de linhas, lição de 20/08); (c) **avaliação própria**: 20 perguntas do domínio
  (código de composição, critério de medição, BDI) com resposta esperada, rodadas contra o pacote do roteador — é a única medida
  que vale, LoCoMo não prediz desempenho agentic (MemoryArena, 02/2026) [PAPER-2ª].
- **Instrumento:** `indexar_memoria.py --decair --simular|--gravar` (backup carimbado, portão anti-perda já existe);
  `bateria_memoria.py` com gabarito em `_CONHECIMENTO\gabarito_memoria.json`.
- **Prova de reprovação:** memória lida ontem não decai; `feedback_*` não decai; linha some do índice sem backup → RC 1 antes do
  "PORTAO OK" (regra já existente).
- **Custo/risco:** 1 lote + manutenção do gabarito no TREINE.
- **REUSO:** TIER0 = `uso_memoria.py`, `conexoes_memoria.py`, `indexar_memoria.py`. TIER2 = auto-memory nativa (200 linhas/25 KB,
  mesmo corte) [DOC]; A-Mem (Zettelkasten) já inspirou o `conexoes_memoria.py`. VEREDITO = ADAPTAR.
- **Onde roda:** local (decisão de N é dele).

### P6. Kernel e memória como plugin versionado, com evals e CI
- **Achado:** A6 e H11/H18.
- **Proposta:** (a) remoto privado para `D:\_git\gmai_scripts.git` (GitHub, conta já existente) — hoje o único git do kernel está no
  mesmo disco que ele; (b) `~/.claude` versionado (sem `projects/`, `debug/`, credenciais, `scheduled_tasks.lock`) + `memory/` +
  `_CONHECIMENTO` (sem o SQLite, que é regenerável) num repo privado `gmai-harness`; (c) empacotar portões + skills + agentes como
  **plugin pessoal** (`.claude-plugin/plugin.json`) — é a via oficial para instalar em outra máquina (substitui parte do
  `bootstrap_maquina`/bundle) e habilita `claude plugin eval` (v2.1.269+) com casos "deve bloquear despacho genérico", "deve exigir
  Passo Zero", "não deve disparar skill X", 3 rodadas com e sem plugin [DOC]; (d) `pytest` alimentando cada hook por stdin JSON
  (fecha H11: prova pelo `main()` sem modelo) rodando em GitHub Actions `windows-latest` a cada push do kernel — a suíte noturna
  deixa de ser o único juiz e não gasta cota.
- **Instrumento:** workflow `.github/workflows/kernel.yml` (matriz `windows-latest` × Python 3.12); `claude plugin validate` no
  mesmo workflow.
- **Prova de reprovação:** quebrar de propósito uma regra do lint num branch → CI vermelho antes do merge.
- **Custo/risco:** 2 lotes. Risco: segredo versionado → P7 entra ANTES deste. `/rewind` pula symlinks [DOC] → não gerenciar
  `~/.claude` por symlink (stow/chezmoi); git direto na pasta.
- **REUSO:** TIER2 = `claude plugin eval` + `plugin test` [DOC]; `Povaz/claude-code-dotfiles` (symlinks Claude+Codex; recusado
  por causa do `/rewind`) [COMUNIDADE]. VEREDITO = ADAPTAR.
- **Onde roda:** o workflow e a estrutura do repo podem nascer na nuvem; o push do kernel é ato local.

### P7. Segredos e fronteira de permissão
- **Achado:** A5.
- **Proposta:** (1) tirar `codice.keystore` e `_senhas_keystore.json` do Google Drive (4 arquivos, ids em `notas_produto.md` §11) e
  guardar em cofre fora de pasta sincronizada; (2) `gitleaks protect --staged` como pre-commit nos repos de P6, com escopo
  explícito em `.claude/`, `memory/`, `_CONHECIMENTO/`, `treine_fila.jsonl` e no cofre Obsidian; `lint_execucao` ganha regra que
  recusa `--no-verify`; (3) `FileChanged` para `.env|_senhas_*|*.keystore` (aviso); (4) decidir entre `bypassPermissions` e `auto`:
  hoje as duas configs coexistem e o `soft_deny` só vale em `auto` [DOC]. Sugestão: `auto` (padrão oficial desde v2.1.283) com
  allowlist dos condutores do protocolo e deny de `rm -rf`/`git reset --hard`/`--force` — os hooks continuam sendo a fronteira
  real, como já são.
- **Instrumento:** hook pre-commit; regra nova no lint; `ConfigChange` de P3 protege a decisão.
- **Prova de reprovação:** commit com string no formato de chave → bloqueado; `git commit --no-verify` → lint recusa.
- **Custo/risco:** < 1 lote. Risco: `auto` pedir confirmação em fluxo que hoje é cego → medir 1 semana e ajustar allowlist.
- **REUSO:** TIER2 = gitleaks (MIT) [COMUNIDADE]; gist "yolo mode" com 6 camadas e CVE-2025-66032 (bypasses de deny, corrigidos em
  v1.0.93 — não confirmei o CVE) [COMUNIDADE]. VEREDITO = ADAPTAR.
- **Onde roda:** local; (1) é ato dele.

### P8. Tetos declarados de latência dos hooks (H05/H12)
- **Achado:** FATO (15/09): orçamento por evento no Claude = PreToolUse 4 handlers/60 s, UserPromptSubmit 2/40 s, Stop 2/50 s,
  PostToolUse 3/35 s, SessionStart 2/120 s; `sentinela_hooks` 90 s em toda partida; teto NÃO declarado. No AG, PreInvocation p90 92,
  máx 292 por conversa.
- **Proposta:** declarar tetos (sugestão: partida ≤ 20 s percebidos, prompt ≤ 3 s, tool ≤ 2 s) e cumprir por desenho:
  `sentinela_hooks` roda `async: true` e só no matcher `startup` (não em `resume|compact`); `sonda_ambiente` idem; `roteador --hook`
  mede e publica p50/p90 no painel; `treine_captura` já é async.
- **Instrumento:** `validar_settings_hooks --orcamento` compara com o teto (hoje só soma); camada `latencia_hooks` no ciclo.
- **Prova de reprovação:** settings com SessionStart síncrono de 90 s → reprova.
- **Custo/risco:** < 1 lote. Risco: sentinela async não barra a 1ª ferramenta se um portão estiver desarmado → `asyncRewake: true`
  entrega o stderr como lembrete de sistema no 1º turno [DOC].
- **REUSO:** TIER0 = `validar_settings_hooks.py`. VEREDITO = ADAPTAR.
- **Onde roda:** local.

### P9. Paridade: AGENTS.md nativo, 32 KiB do Codex, nuvem como 4ª plataforma
- **Achado:** FATO [DOC]: desde v2.1.277 o Claude Code lê `AGENTS.md` nativamente quando não há `CLAUDE.md` e a doc manda REMOVER
  hooks de SessionStart que imprimem AGENTS.md (duplica contexto). FATO [DOC-2ª]: Codex `project_doc_max_bytes` = 32 KiB
  (`AGENTS.md` dele tem ~12,7 KB, folga). FATO: a nuvem (`claude.ai/code`) não recebe nada do canônico; o espelho que escrevi em
  14/10 (`CLAUDE.md` deste repositório) foi à mão.
- **Proposta:** (a) conferir que nenhuma pasta tem `CLAUDE.md` E `AGENTS.md` carregados juntos (`/doctor prompt-audit`, v2.1.283+,
  também aponta contradições entre CLAUDE.md, rules, skills e agentes [DOC]); (b) `verificar_paridade_claude_codex.py` ganha a
  régua dos 32 KiB; (c) `sincronizar_contratos_claude_nuvem.py` gera o `CLAUDE.md` da nuvem (versão sem D:/C:/hooks) e o
  `RETOMADA_NUVEM.md` a partir do canônico, entra na cadeia do `treine_fechar.py` e na paridade.
- **Instrumento:** os três acima.
- **Prova de reprovação:** CLAUDE.md da nuvem divergente do canônico → paridade reprova.
- **Custo/risco:** < 1 lote.
- **REUSO:** TIER0 = `sincronizar_contratos_claude_codex.py` (mesma função, 4ª plataforma). VEREDITO = ADAPTAR.
- **Onde roda:** gerador local; a nuvem só consome.

### P10. Saúde dos jobs visível de fora da máquina
- **Achado:** FATO: o relatório do `\GMAI-Vigia-DatasBase` (07:15) e o da suíte noturna (03:00) ficam no Desktop e em
  `D:\_temp_*`, fora do Drive; do backup não dá para saber se rodaram depois de 18/09.
- **Proposta:** cada job grava `STATUS_<job>.json` (data, RC, placar) numa pasta sincronizada (`_CONHECIMENTO\status\`) e, em
  falha, manda e-mail pela mesma conta já usada pelo Supabase — assim o estado se lê do celular ou da nuvem sem abrir o PC.
  Manter o Agendador do Windows: as 3 opções oficiais (Routines na nuvem, Desktop scheduled tasks, `/loop`) exigem app aberto ou
  não têm arquivos locais [DOC]; nenhuma substitui o Task Scheduler para o TREINE offline.
- **Instrumento:** 10 linhas em `suite_noturna.py` e `ciclo_datas_base.py`.
- **Prova de reprovação:** job com RC ≠ 0 e sem STATUS → sentinela do dia seguinte acusa `STATUS_AUSENTE`.
- **Custo/risco:** < 1 lote.
- **REUSO:** TIER0 = relatório `Desktop\VIGIA_BANCOS.md`. VEREDITO = ADAPTAR.
- **Onde roda:** local.

## 4. Confronto com o que já existe (para não reconstruir)

| Proposta | Já existe no kernel | O que falta de verdade |
|---|---|---|
| P1 teto da âncora | teto do CLAUDE.md (`claude_md_teto.json`), orçamento do pacote (9.800 B) | o mesmo teto na âncora e o CHANGELOG separado |
| P2 cache | `painel_operacao.py` mede bytes/pacote; `quota_*.py` medem saldo | hit rate de cache; núcleo estável × delta |
| P3 eventos | `guarda_harness_hook` (PostToolUse), despacho por regex | `ConfigChange`, `compact`, `SubagentStart`, `InstructionsLoaded` |
| P4 orçamento de kernel | `_TERMO_KERNEL`, `placar_despacho.py` | somar tokens por classe e o teto |
| P5 decaimento | `uso_memoria.json` ("nunca lidas"), `conexoes_memoria.py`, `indice_project_historico` | a política e o gabarito do domínio |
| P6 git/CI | `D:\_git\gmai_scripts.git` (local), `bateria_harness`, `suite_noturna` | remoto, memória no git, plugin, evals, CI Windows |
| P7 segredos | `soft_deny`, R29/Hook 29 no lint | gitleaks, keystore fora do Drive, decisão auto × bypass |
| P8 tetos | `validar_settings_hooks --orcamento` | o teto declarado e sentinela async |
| P9 paridade | 2 sincronizadores + 2 portões | AGENTS.md nativo, 32 KiB, 4ª plataforma |
| P10 status | relatórios no Desktop | arquivo de status sincronizado |

## 5. Sequência sugerida e aceite

- **Lote A (1 dia, maior efeito na cota):** P1 + P8 + P7(1). Aceite: partida de sessão nova < 15 K tokens medidos em `/context`;
  SessionStart percebido ≤ 20 s; keystore fora do Drive.
- **Lote B (2–3 dias):** P2 + P3(1,2,3). Aceite: `cache_hit_pct` ≥ 90 % a partir do 2º turno em 3 sessões; `ConfigChange` com
  prova de reprovação; RETOMADA automática antes de compactar.
- **Lote C (1 semana, pode ser feito em paralelo pela nuvem):** P6 + P9 + P10. Aceite: CI `windows-latest` verde no repo do kernel;
  `claude plugin eval` com ≥ 5 casos passando 3/3 e baseline reprovando; paridade da nuvem PASS.
- **Lote D (decisão dele):** P4 (teto de meta-trabalho) e P5 (N dias de decaimento).

Cada lote segue o rito da casa: lint → `--testar` com caso negativo → bateria → ciclo com delta limpo → paridade/distribuição →
2º passe cego → bump só por decisão dele. "Bateria verde não prova sistema homologado" continua valendo.

## 6. O que a nuvem pode fazer agora, sem tocar na máquina

1. Estrutura do repositório `gmai-harness` (README, `.gitignore`, pre-commit do gitleaks, workflow `windows-latest`, esqueleto
   `.claude-plugin/plugin.json` e 5 casos de `claude plugin eval`) — P6/P7.
2. Rascunho do `sincronizar_contratos_claude_nuvem.py` seguindo o padrão do sincronizador do Codex — P9.
3. Leitor de `cache_read/cache_creation` dos `.jsonl` de sessão como módulo isolado, com autoteste por stdin — P2.
4. Roteiro de medição do Lote A (comandos exatos, antes/depois) para a sessão local executar quando tiver cota.

## 7. Candidatos ao TREINE (desta sessão)

- **feedback:** âncora do Passo Zero virou diário (68 KB) porque o instinto 29 não tinha teto nela — regra conhecida e não
  aplicada ao maior item = causa E; a trava é o teto de P1, não texto.
- **feedback:** a nuvem (`claude.ai/code`) não recebe o canônico; qualquer espelho manual deriva — a trava é o gerador de P9.
- **reference:** Claude Code v2.1.296: 33 eventos de hook, `onFailure: block`, `memory:` em agentes, `claude plugin eval`,
  AGENTS.md nativo, cache 1 h em assinatura; issues #83913/#93490 sobre cache × hooks (abertas em 14/10/2026).
- **project:** sessão de 14/10/2026 na nuvem: mapa do harness, do Códice e dos dados a partir do backup do Drive (até 18/09) e do
  repositório `acervo-bancos-referencia` (até 30/09); PR #1 com `CLAUDE.md` e `RETOMADA_NUVEM.md`; pendências e segredos
  registrados em `RETOMADA_NUVEM.md`.

## 8. Fontes externas (as que sustentam decisão; lista completa em `notas_web.md` da sessão)

[DOC] code.claude.com/docs/en/hooks · hooks-guide · memory · sub-agents · skills · plugins/overview · plugins/measure · plugin-evals ·
prompt-caching · costs · monitoring-usage · context-window · sandboxing · permission-modes · security · scheduled-tasks ·
desktop-scheduled-tasks · remote-control · cli-reference (lidos 14/10/2026). [DOC] anthropic.com/engineering/effective-context-engineering-for-ai-agents
(29/09/2025); writing-tools-for-agents (11/09/2025). [COMUNIDADE] github.com/anthropics/claude-code/issues/83913, 84011, 93490;
gist hartphoenix "Claude Code Yolo Mode" (05/2026); tianpan.co (resumo do post da Manus); opensourceaireview.com e particula.tech
(reproduções de benchmarks de memória). [PAPER-2ª] arXiv 2602.16313 (MemoryArena), 2606.30306 (Always-On Agents), 2608.13662
(memória ontológica para agentes de código). [DOC-2ª] developers.openai.com/codex/hooks e /guides/agents-md; antigravity.google/docs/ide/hooks.
