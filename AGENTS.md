# Pop Explica — contexto para agentes (Claude Code / Codex)

Você está produzindo vídeos curtos (TikTok Shop, 1080×1920, ~35–45 s) no estilo **Pop Explica**:
ilustração vetorial chapada, fundo com raios girando, narração TTS e legenda palavra a palavra.
Esta é uma operação **lateral e automatizada** do Arthur: ele manda um prompt, revisa o resultado.
Trabalhe sozinho do começo ao fim, sem parar para perguntar, a não ser nos bloqueios listados no fim.

Leia também, nesta ordem: `STYLE.md` (regras visuais, hooks, alegações) e a pasta do vídeo pedido.

## Mapa

| Caminho | O quê |
|---|---|
| `engine/popx.py` | Motor: fundo, legenda, transições, componentes, render. Ver índice em STYLE.md §9 |
| `engine/fonts/` | Rubik (legenda). Não trocar |
| `tools/align.py` | Áudio + texto narrado → `words.json` (tempo por palavra) |
| `tools/cutout.py` | Foto de produto com fundo liso → PNG transparente |
| `videos/_template/` | Modelo de vídeo. Copiar para `videos/<slug>/` |
| `videos/<slug>/` | Um vídeo: `roteiro.md`, `narracao.mp3`, `assets/`, `video.py`, saídas |
| `examples/demo.py` | Demo do estilo sem áudio (referência de uso dos componentes) |
| `ASSETS.md` | O que o Grok entrega em `assets/` |
| `PROMPT.md` | Prompts padrão que o Arthur usa para abrir sessões |

## Setup (uma vez por sessão)

```
bash pop-explica/setup.sh
```

## Tarefa A — escrever o roteiro (`roteiro.md`)

Entrada: `videos/<slug>/produto.md` (dados da página do produto) e `assets/`.
1. Ler STYLE.md §3 (blocos e tipos de hook) e §10 (alegações).
2. Escrever `roteiro.md` com: ângulo escolhido (1 linha), tabela de blocos (bloco → trecho → o que aparece
   → tema de cor), e a seção `## Narração` com o texto corrido exato para o ElevenLabs.
3. Narração: 85–120 palavras, frases curtas, 2ª pessoa, português falado. Termina com CTA de carrinho.
   Tags do ElevenLabs entre `[ ]`, raras; notas de edição entre `{{ }}`, fora da seção Narração.
4. Escrever 2 hooks alternativos no fim, para o Arthur escolher.
5. Toda alegação sobre o produto precisa estar em `produto.md`. Nada inventado.
O Arthur revisa o roteiro antes de gerar o áudio. Não produza o vídeo nesta tarefa.

## Tarefa B — produzir o vídeo

Entrada: `videos/<slug>/` com `roteiro.md`, `narracao.mp3` e `assets/` (produto em PNG).
1. **Texto narrado:** copiar a seção `## Narração` do roteiro para `narracao.txt` (se não existir).
2. **Alinhar:** `python tools/align.py videos/<slug>/narracao.mp3 videos/<slug>/narracao.txt videos/<slug>/words.json`.
   Se o casamento ficar abaixo de 85%, o áudio provavelmente não bate com o texto: siga, mas registre no relatório.
3. **Assets:** conferir `assets/`. Produto sem transparência → `tools/cutout.py`. Olhar o PNG resultante.
4. **Código:** copiar `videos/_template/video.py` para a pasta (se não existir) e escrever as cenas:
   uma função por bloco do roteiro, todas `f(ctx, t)`, cada entrada ancorada em `T("palavra")`.
   Usar componentes do motor; preencher `HIGHLIGHT` com cores semânticas.
5. **Storyboard:** `python videos/<slug>/video.py stills` → abrir `storyboard.jpg` e olhar de verdade.
   Checklist: legenda não cobre nada importante; nenhum elemento cortado ou fora da tela; produto real
   visível (não o tubo genérico); textos de pílula/checklist legíveis; troca de cor na palavra da virada;
   CTA no fim. Corrigir e gerar de novo até passar (no máximo 4 rodadas). Para conferir um trecho:
   `python video.py stills 12.5 13 13.5`.
6. **Render:** `python videos/<slug>/video.py render` → `out/<slug>.mp4`. Se o ambiente tiver limite de
   tempo por comando, rode em segundo plano e acompanhe:
   `setsid nohup python video.py render > render.log 2>&1 < /dev/null &`
7. **Conferir a saída:** `ffprobe` (duração ≈ áudio, tem faixa de áudio) e 4 frames extraídos do MP4 final.
8. **Commit:** `video.py`, `words.json`, `narracao.txt`, `storyboard.jpg`, `out/<slug>.mp4`, assets recortados.
9. **Relatório final** (curto): o que aparece em cada bloco com os segundos, decisões tomadas sozinho,
   o que ficou abaixo do ideal, e qualquer asset que faltou.

## Regras de produto (obrigatórias)

- O TikTok exige o produto real no vídeo. Ele aparece pela foto oficial recortada, no mínimo da virada até
  o fim, e no CTA. O tubo genérico (`placeholder_tube`) nunca vai para um render final.
- Não redesenhar a embalagem nem a marca: usar a foto como ela é.
- Alegações: só o que está em `produto.md`; seguir STYLE.md §10.

## Regras de código

- **Não editar `engine/popx.py` para resolver um vídeo específico.** Ilustração própria do vídeo
  (personagem, cenário, diagrama) fica em `video.py`.
- Se você criar algo claramente reutilizável (ex.: corte transversal de pele, placar, calendário), pode
  promover para o motor como componente genérico, com docstring, e adicionar ao índice da STYLE.md §9.
  Diga no relatório.
- Tudo é função de `t`. Nada de estado entre frames (o render é paralelo e cada processo começa do zero).
- Nada parado mais de ~1,5 s: personagens com bob, produto flutuando, sparkles.

## Quando parar e avisar (em vez de inventar)

- Falta `narracao.mp3` ou a foto do produto.
- A foto do produto não recorta (fundo com gradiente/texto) e não há outra em `assets/`.
- O roteiro pede uma alegação que não está em `produto.md`.
Nesses casos: faça tudo o que dá, deixe o resto anotado no relatório e no commit.
