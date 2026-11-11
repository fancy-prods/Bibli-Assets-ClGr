# Estilo "Pop Explica" — guia de produção

Vídeo explicativo de produto para TikTok Shop: ilustração vetorial chapada, fundo com raios girando,
narração TTS e legenda palavra-a-palavra. Engenharia reversa de dois vídeos de referência
(pasta clareadora 4,6M views; kit de pele 1,7M views).

Este guia vale igual para Claude e Codex. O motor é `engine/popx.py` (pycairo + Pillow + numpy + ffmpeg).
**Não altere o motor para um vídeo específico.** Cada vídeo é uma pasta em `videos/`.

---

## 1. Quando usar

Praticamente qualquer produto que caiba numa **situação** dramatizável: um problema, um momento do dia,
um olhar dos outros, uma característica técnica que dá pra mostrar (IPX7, 20000 mAh, fixação, cheiro).
Ex.: pasta dental, skincare, body splash, guarda-chuva, power bank, fone, filtro, produto de limpeza.
O que não rende: peça de moda cujo único argumento é a aparência (saia, vestido) — aí o vídeo vira vitrine.

## 2. Especificação técnica

- 1080×1920, 30 fps, H.264 CRF 18, áudio AAC 192k normalizado a ~-14 LUFS.
- Duração 35–45 s. Narração ElevenLabs, ritmo rápido (~2,8 palavras/s).
- Tempos de palavra vêm do alinhador do kit (`tools/align.py`) → `popx.words_from_align()`.
- Nenhum elemento fica parado por mais de ~1,5 s (sempre há bob, flutuação, raios, bokeh, brilho).
  Isso também protege contra a violação de "conteúdo estático".

## 3. Estrutura do roteiro (blocos, não fórmula)

O roteiro é montado com blocos. Só três são obrigatórios: **hook**, **virada para o produto** e **CTA**.
Os outros entram quando o produto tem material para eles.

| Bloco | Obrigatório? | Tema de cor típico | O que aparece |
|-------|--------------|--------------------|---------------|
| Hook | sim | quente ou do contexto (chuva = `blue`) | Personagem/cena da situação + algo que chama atenção |
| Identificação | não | idem | Checklist "teste rápido", vilões do dia a dia, contador de dias |
| Mecanismo do problema | não | `orange`/`blue` | Corte transversal, barra caindo, rótulo em pílula |
| Tentativa frustrada | não | idem | Placar, "você faz X e continua" |
| Virada + produto | sim | cor da embalagem | Produto entra com pop + brilho; mecanismo ou característica-chave |
| Demonstração real | não | idem | Vídeo enviado pelo Arthur em `clip_card` ou `clip_full` |
| Prova / confiança | não | idem | Checklist branco, selo, números (vendidos, nota, IPX7) |
| CTA | sim | idem | Produto + botão laranja pulsando + seta |

Regra de cor: a troca de tema acontece na palavra da virada. Quando o hook é um problema, ele fica em cor
quente; quando é uma situação (chuva, academia, noite), usa a cor da situação.

### Tipos de hook

| Tipo | Exemplo | Produto |
|------|---------|---------|
| Correção de hábito | "Para de espremer essa espinha, você está empurrando a inflamação pra dentro." | skincare |
| Olhar dos outros | "Todo mundo já reparou no seu dente amarelo. Menos você." / "As pessoas sempre reparam no seu cheiro." | pasta, body splash |
| Situação iminente | "A chuva tá chegando." (e a chuva já chega na cena) | guarda-chuva |
| Pane do dia a dia | "Bateria em 5% e você ainda tem o dia inteiro." | power bank |
| Pergunta de identificação | "Seu rosto brilha antes do almoço?" | skincare |

Depois do hook, a virada clássica continua valendo: "Não é [causa óbvia], não. É [causa real]."

## 4. Paleta (medida nas referências)

| Tema | Meio | Canto (vinheta) | Uso |
|------|------|-----------------|-----|
| red | #e8727c | #9d2c3e | problema, alerta |
| orange | #f6af6a | #a9541d | causa, hábito |
| blue | #7ec8e8 | #1f5f8a | mecanismo, óleo/água |
| green | #8ed570 | #237442 | solução natural, pele |
| teal | #5fc2b4 | #196963 | suavidade |
| purple | #b49ee8 | #3a227a | solução premium |

Destaques de legenda: yellow #ffd23f (padrão), green, red, blue, orange, pink. Contorno: #1b1015.
Cor de destaque é semântica: "chá" verde, "refrigerante" vermelho, "esmalte" azul. Sem tag = amarelo.

## 5. Fundo

Cor do tema + 20 raios alternados girando a ~5°/s a partir de (540, 1060), brilho radial no centro,
vinheta escurecendo até a cor de canto, 16 bolhas de bokeh subindo devagar. Tudo em `background()`.

## 6. Legenda

- Rubik Black (peso 900), caixa alta, 104 px, contorno 11 px #1b1015, sombra curta para baixo.
- Centro em y = 300. Frases de até 3 palavras; quebra também em pontuação ou largura > 960 px.
- A frase é diagramada inteira e centralizada; as palavras surgem no lugar final (sem recentralizar),
  cada uma com pop de 0,22 s.
- Palavra falada agora = colorida; anteriores = brancas.

## 7. Ilustração

- Vetor chapado, formas arredondadas, no máximo 1 tom de sombra interna + highlight branco.
- Personagens: traço médio (~9 px) marrom-escuro ou nenhum; olhos em ponto com brilho, blush rosa,
  boca simples. A expressão segue a narração (triste no problema, feliz no resultado, gotinha de suor).
- Sempre sombra elíptica suave no chão.
- Diagramas (poro, esmalte) em cartão branco arredondado com sombra; rótulos em pílula.
- Produto real: PNG recortado (sem fundo) da foto oficial, entra só a partir da virada.
  Pode ficar solto (flutuando) ou em cartão branco (kits/combos).

## 8. Movimento

| Ação | Duração | Curva |
|------|---------|-------|
| Entrada de qualquer elemento | 0,28 s | back-out (overshoot ~10%) |
| Palavra da legenda | 0,22 s | back-out |
| Troca de tema (íris com aro branco) | 0,42 s | ease-in-out, origem no elemento principal |
| Cartão de checklist | 0,32 s | desliza da esquerda + back-out; check desenha em 0,2 s |
| Idle personagem | contínuo | bob 6 px, ~0,5 Hz |
| Idle produto | contínuo | flutua ±12 px, gira ±2°, sparkles piscando |
| CTA | contínuo | pulso 4,5% a 1,4 Hz, seta balançando |

Elementos entram ancorados na palavra da narração que os nomeia (`T("palavra")`), nunca em segundos fixos.

## 9. Componentes (`popx.py`)

`background`, `timeline` (cenas + íris), `Captions`, `pill`, `checklist`, `progress_bar`, `seal`,
`product`, `sparkles`, `glow`, `cta`, `tooth` (personagem-exemplo), `eyes_pair`, `ground_shadow`,
`clip_card`, `clip_full`, `Clip`, `soft_shadow`, `text_sprite`, `blit`, `pop`, `prog`, easings, `render`, `still`, `words_from_align`.
Faltam (criar quando o roteiro pedir, e adicionar ao `popx.py` como componente genérico):
corte transversal de pele, placar "AO VIVO", calendário "DIA 67", círculo cromático com rótulos,
passos numerados (badge verde com número), placa "PARA!".

## 9b. Vídeo real (demonstração)

Quando o Arthur manda um vídeo do produto (ex.: guarda-chuva abrindo na chuva), ele entra no estilo,
não como corte seco para outro visual:
- `Clip("assets/demo.mp4", w=760, h=1000, start=2.0)` + `clip_card(...)`: cartão branco arredondado,
  levemente inclinado, flutuando sobre o fundo de raios, com pílula opcional ("IPX7", "TESTE REAL").
  É o padrão.
- `clip_full(...)`: tela cheia (Clip com w=1080, h=1920) só quando o vídeo for forte o bastante sozinho;
  a legenda continua por cima.
- 2 a 5 s por trecho. Recorte o momento que prova a característica, não o vídeo inteiro.
- O vídeo não tem áudio no resultado final; só a narração.

## 10. Alegações (TikTok Shop + Anvisa)

- Explicar mecanismo, não prometer resultado. "Ajuda a", "visivelmente", "neutraliza o tom".
- Nada de "cura", "elimina", "trata", "100%", "em X dias", "antes e depois" de pessoa real.
- Só citar registro/teste que está na embalagem ou na página do produto.
- Na dúvida, copiar a precisão do vídeo da pasta: "sem agente clareador" + efeito óptico.

## 11. Fluxo por vídeo

Ver `AGENTS.md` (Tarefa A: roteiro; Tarefa B: vídeo) e `PROMPT.md`.
O motor fica em `engine/popx.py`; cada vídeo em `videos/<slug>/video.py`, copiado de `videos/_template/`.
