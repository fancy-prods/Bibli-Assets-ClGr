# Estilo "cédula": guia v0 (proposta)

> **Status: proposta de 13/11/2026, aguardando aprovação do Arthur.** Nada daqui foi usado em vídeo.
> Catálogo: [`catalog.json`](catalog.json). Demo: [`demo/demo.html`](demo/demo.html) (8 s, "Uma ideia rende juros").
> Nenhum asset de `palco` ou `pop-explica` foi reaproveitado.

## 1. Princípio

Papel-moeda. Tudo é **gravura em talho-doce**: imagem feita só de linhas paralelas que engrossam no escuro e se curvam com o volume, cercada de guilhochês, tipografia capitular, numeração de série e carimbo. O vídeo trata cada ideia do livro como algo de **valor**: impresso, numerado, assinado.

O truque do motor: pinta-se qualquer coisa em **tons de cinza** (Canvas 2D, com degradês simples) e um shader converte tom em linha gravada. Não se desenha linha nenhuma à mão.

## 2. Paleta

| Papel | `#efe8d3` com manchas e fibrinhas de segurança (vermelhas, azuis, verdes) |
|---|---|
| Tintas (`Cedula.TINTAS`) | verde `#1d5741`, sépia `#5b3a21`, azul `#1c3d6b`, bordô `#7a1f2c`, grafite `#22252b` |
| Numeração | vermelho `#b3261e` e azul-noite `#1b2440` |
| Selo | vermelho `#b3261e`, em multiply |

Regras: **uma tinta principal por nota** (retrato, título, moldura) e **uma secundária** para a vinheta e o numeral. Vermelho só em numeração e selo. Trocar a tinta principal é trocar de "valor"/capítulo (verde, depois azul, depois bordô).

## 3. A gravação (`Cedula.Stage` → `toneBegin()` / `print()`)

| Parâmetro | Default | Efeito |
|---|---|---|
| `period` | 6,4 px | distância entre linhas (5,5 a 7; abaixo disso vira cinza em 720p) |
| `angle` | −0,12 rad | direção das linhas; use ângulos diferentes para tintas diferentes (a demo usa −0,12 e 0,5) |
| `depth` | 26 px | quanto o tom (borrado) desloca as linhas: é o que dá relevo |
| `wave` | 2,2 px | ondulação leve das linhas |
| `cross` | 1 | hachura cruzada a +62° onde o tom passa de 0,48 |
| `gain` | 1 | multiplica o tom; animar de 0 a 1 faz a gravura "morder" o papel |

Como pintar o tom (`Cedula.T`):

- Branco = sem tinta; preto = linha cheia. **Trabalhe entre 0,15 e 0,9.** Abaixo de 0,09 a linha some.
- Volume vem de degradê radial (luz na maçã do rosto, sombra sob o queixo). O relevo das linhas vem do tom borrado, então transições suaves rendem mais que contorno duro.
- Contorno e detalhes finos (olho, armação dos óculos, lapela) em tom 0,95 a 1, com 4 a 6 px.
- Texto gravado: degradê vertical 0,9 → 0,35 dentro da letra (`T.texto`) + contorno vetorial por cima (`Cedula.contorno`).

Pintores prontos: `ovalBg`, `busto` (perfil clássico, com óculos opcionais), `livro` (aberto, com raios), `moedas` (pilha), `texto`.

## 4. Guilhochê (`Cedula.G`)

Curvas finas (1,1 px) entrelaçadas, sempre vetoriais, **nunca gravadas**.

| Peça | Fórmula | Uso |
|---|---|---|
| `rosette` | n curvas `r(θ) = R + a·sin(kθ + fase_i)` | rosácea atrás de numeral, cantos |
| `oval` | rosácea achatada | anel do medalhão |
| `band` | n senoides defasadas | faixas da moldura |
| `frame` | filetes + 4 faixas + 4 rosáceas | moldura completa |

A fase anda com o tempo (0,3 a 0,8 rad/s): o guilhochê "respira" o vídeo inteiro. É o movimento de fundo do estilo.

## 5. Composição da nota

- Moldura a 34 px da borda; área útil de 100 a 1820 × 100 a 980.
- **Medalhão oval** à esquerda (270 × 350 de raio) com o retrato; dois anéis de guilhochê.
- **Título** em Cinzel 900, 128 a 138 px, duas linhas, à direita do medalhão.
- **Linha de autoridade** acima do título (Cinzel 700, 34 px, espaçamento 13 px) e **cláusula** abaixo (Cinzel 500, 28 px).
- **Microtexto**: duas linhas de 11 px repetindo a frase-chave. Só se lê no zoom, e é para isso.
- **Vinheta** (livro, moedas, o objeto do capítulo) e **numeral** dentro de rosácea, na segunda tinta.
- **Numeração de série** (Zilla Slab 700) em dois cantos; **assinatura** (laçadas que se escrevem); **selo** batido por cima.

## 6. Movimento

| Tempo (demo) | O que acontece |
|---|---|
| 0 a 1,5 s | macro no retrato (zoom 2,15); as linhas engrossam do nada (`gain` 0 → 1) |
| 1,5 a 3,4 s | a câmera abre até a nota inteira |
| 2,8 a 4,4 s | título, cláusula, vinheta e numeral são gravados em sequência |
| 4,0 s | numeração entra dígito a dígito |
| 4,7 s | selo bate (escala 1,9 → 1 em 0,22 s) e a câmera treme 0,3 s |
| 5,2 a 6,2 s | assinatura se escreve |
| 6,2 a 7,7 s | brilho varre a nota (luz rasante) |

- A câmera só faz zoom e pan sobre a nota: macro ↔ inteira. No macro, as linhas ficam grossas e bonitas; use para cada detalhe que a narração cita.
- Nada "pula". Tudo é gravado (gain), escrito (assinatura) ou batido (selo).

## 7. Formatos

Em 9:16 a nota fica em pé: medalhão em cima, título no meio, vinheta e numeral embaixo; ou mantém-se a nota deitada e a câmera passeia em macro. Não testado.

## 8. Quando usar / quando não

- **Usar**: finanças, economia, investimento, negócios, história, biografias de figuras públicas, qualquer "regra de ouro" ou "lei" (cada lei vira uma nota).
- **Evitar**: narrativa com ação, humor físico, temas leves e infantis.

## 9. Como rodar

```bash
node shared/web/render.cjs styles/cedula/demo/demo.html -o quadro.png -t 6.6
node shared/web/render.cjs styles/cedula/demo/demo.html -o demo.mp4 --scale 0.6667
```

## 10. Pendências

- [ ] Aprovação do estilo.
- [ ] Mais retratos (frente, mulher, idoso) e vinhetas (balança, ampulheta, chave, cofre, árvore).
- [ ] Verso da nota (paisagem gravada) e moeda.
- [ ] Gravar render 3D em tons de cinza (o shader aceita qualquer imagem).
