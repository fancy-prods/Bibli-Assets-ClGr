# Estilo "bebop": guia v0 (proposta)

> **Status: proposta de 13/11/2026, aguardando aprovação do Arthur.** Nada daqui foi usado em vídeo.
> Catálogo: [`catalog.json`](catalog.json). Demo: [`demo/demo.html`](demo/demo.html) (8 s, 16 tempos a 120 bpm).
> Nenhum asset de `palco` ou `pop-explica` foi reaproveitado.

## 1. Princípio

Capa de disco de jazz dos anos 50/60 que se mexe no compasso. Tipografia condensada enorme, blocos de cor chapada, figuras de papel recortado com tesoura, retícula no lugar de degradê, e a imperfeição de uma impressão em três chapas. Feito para casar com a trilha de jazz dos vídeos da Unfold: **tudo entra, pulsa e troca no tempo da música**.

Regra de ouro: **três tintas e o papel**. Não existe quarta cor, degradê liso, sombra, contorno ou transparência. Tom intermediário só por retícula ou por sobreimpressão (uma tinta em cima da outra, em multiply).

## 2. Prensagens (paletas)

Cada prensagem é papel + preto (K) + duas tintas (A, B). `Bebop.PRENSAGENS`:

| Nome | Papel | K | A (bloco, título 2) | B (acento, objeto) |
|---|---|---|---|---|
| `cobalto` | `#f0e8d6` | `#15171c` | `#1f4fd8` | `#ff5a1f` |
| `mostarda` | `#efe5cd` | `#1b1814` | `#dfa000` | `#0f7f7c` |
| `carmim` | `#f3ecdf` | `#17151c` | `#e23a4e` | `#2a2f96` |
| `menta` | `#eef0e2` | `#14181a` | `#18a07a` | `#f2478b` |

- Uma prensagem por capítulo. Trocar de prensagem em corte seco no tempo forte é a "virada" do estilo.
- A ocupa área (bloco, palavra grande). B é pequena e pontual (o livro, o chapéu, o disco, 1 barra em 7).
- A sobre B escurece: use de propósito (título atravessando o disco). Quando B precisa ficar pura sobre A, abra janela em A (`P.on(..., true)`).

## 3. Como a "prensa" funciona

[`engine/bebop.js`](engine/bebop.js), `Bebop.Press`: três telas (chapas A, B, K) onde se desenha só com alfa. No fim do quadro, cada chapa:

1. perde tinta num manchado suave (ruído largo) e em pontinhos (ruído fino, troca a cada pose);
2. é tingida com a cor da prensagem;
3. é impressa em multiply sobre o papel, A e B **fora de registro** (±2,4 px, mais um tremor de 0,4 px por pose).

Por cima, grão de papel. Fervura a 12 poses por segundo, mesmo com o vídeo a 30 fps.

## 4. Composição

- Grade de 12 colunas, margem de 72 px. Um **bloco A** de 4 a 5 colunas de um lado; texto do outro.
- **Título** em League Gothic, caixa alta, ajustado à largura da coluna (`Bebop.fit`): fica com 300 a 420 px de altura. Linha 1 em K, linha 2 em A. O título pode ser atravessado por um disco/círculo em B.
- **Créditos** em Space Mono 24 a 27 px, com espaçamento 6 a 9 px; um deles sempre na vertical, na margem direita (número de catálogo: `UF-0113 · ESTÉREO · 33⅓ RPM · LADO A`).
- **Subtítulo** em Playfair Display itálico 700, 54 px, sobre um filete de 5 px.
- **Formas**: retângulo, círculo, barra, filete. Nada de cantos arredondados, nada de ícones.
- **Barras de ritmo**: fileira de 34 barras na base; 1 a cada 7 em B.
- Muito papel vazio. Se o quadro está cheio, tire um elemento.

## 5. Figuras recortadas

`Bebop.cut`: polígonos de lados retos com vértices tremidos (±3,5 px, semente fixa), como papel cortado à tesoura. `Bebop.leitor`: figura sentada de perfil, lendo.

- Corpo em K. Sem rosto: só um olho, que é **janela** no preto (aparece a cor de baixo).
- Um ou dois objetos em B (livro, chapéu), com janela nas outras chapas para a cor ficar pura.
- Volume por **retícula** (`Bebop.halftone`): furos redondos no preto, em grade a 45°, maiores do lado da luz.
- Peças não se encaixam perfeitamente; a folga entre elas faz parte.
- Proporção angulosa, ~5 cabeças. Cada peça é um polígono de 4 a 8 vértices.

## 6. Movimento

`Bebop.Tempo(bpm, swing)` dá o relógio. Tudo é marcado em tempos, não em segundos.

| Gesto | Função | Uso |
|---|---|---|
| Entrada seca com sobra | `snap(t, tempo, 0.26..0.34)` | blocos, disco, figura |
| Entrada seca sem sobra | `hit(t, tempo, 0.3)` | janelas de revelação do texto |
| Revelação por janela | `Bebop.reveal` | título sobe da linha de base; subtítulo abre da esquerda |
| Pulso | `pulse(t, decay)` | cabeça acena, pé bate, barras crescem, ponto pula |
| Colcheia com swing | `eighth(n)`, razão 0,66 | a segunda entrada de um par cai atrasada: é isso que dá o balanço |

- Uma entrada por tempo, no máximo. Tempos 1 e 3 para as grandes, contratempo com swing para as pequenas.
- Depois de montada, a capa **não para**: disco gira, barras trocam a cada colcheia, figura marca o tempo.
- Sem easing longo, sem fade, sem câmera. Troca de quadro é corte seco ou troca de prensagem.
- Ajuste `bpm` ao da trilha; a demo usa 120.

## 7. Formatos

Em 9:16, o bloco A vira faixa horizontal (terço de cima ou de baixo) e o título quebra em 3 linhas. Não testado.

## 8. Quando usar / quando não

- **Usar**: aberturas, viradas de capítulo, listas ("3 ideias do livro"), citações, livros de negócios, criatividade, música, design; qualquer trecho guiado por texto.
- **Evitar**: cenas narrativas longas com personagem atuando; o estilo é gráfico, não cênico.

## 9. Como rodar

```bash
node shared/web/render.cjs styles/bebop/demo/demo.html -o quadro.png -t 5.4
node shared/web/render.cjs styles/bebop/demo/demo.html -o demo.mp4 --scale 0.6667
```

## 10. Pendências

- [ ] Aprovação do estilo.
- [ ] Mais figuras recortadas (em pé, músico, mão segurando livro) e objetos (xícara, relógio, escada).
- [ ] Modelos de quadro: citação, lista numerada, "lado B" (encerramento).
- [ ] Detectar o BPM da trilha e alimentar `Tempo`.
