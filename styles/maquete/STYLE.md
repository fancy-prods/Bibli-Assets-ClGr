# Estilo "maquete": guia v0 (proposta)

> **Status: proposta de 13/11/2026, aguardando aprovação do Arthur.** Nada daqui foi usado em vídeo.
> Catálogo: [`catalog.json`](catalog.json). Demo: [`demo/demo.html`](demo/demo.html) (8 s, "A biblioteca que cabe na mão").
> 3D de verdade (Three.js, câmera ortográfica). Nenhum asset de `palco` ou `pop-explica` foi reaproveitado.

## 1. Princípio

Cada ideia do livro vira uma **maquete em miniatura**: uma sala em corte, um quarteirão, uma mesa, vistos de cima em isométrica, como brinquedo de madeira pintada fotografado com lente tilt-shift. O espectador segura o mundo na mão. Bom para explicar sistemas, rotinas, lugares e "como as peças se encaixam".

- **Tudo é sólido simples** de canto arredondado, fosco, sem textura. A cor é a informação.
- **A maquete brota**: cada peça nasce do chão com sobra (escala em Y), na ordem em que a narração a cita.
- **Gente é boneco-pino**: corpo cônico, cabeça esférica, dois pontinhos de olho. Atua com o corpo inteiro (pulinho, inclinação), não com o rosto.

## 2. Paleta

`PAL` em [`engine/maquete.js`](engine/maquete.js):

| Grupo | Cores |
|---|---|
| Fundo (degradê radial) | `#f4d9c6` → `#e9b9a4` |
| Arquitetura | parede `#f6ecdf`, rodapé `#eadccb`, piso `#e3bf95` / `#d8b084`, base `#b98a63` |
| Madeira | `#a9744f`, `#8a5a3c` |
| Acentos | coral `#f0725a`, mostarda `#f2b441`, turquesa `#35a79c`, marinho `#2d3f73`, ameixa `#8a4f7d`, folha `#5aa469` |
| Neutros | creme `#fbf3e4`, grafite `#3b3a42` |
| Pele | `#f2c9a5`, `#d99a6c`, `#8d5a3b`, `#f7dcc4` |

Regras: arquitetura sempre clara e neutra; acentos só em móveis, livros, roupas. Um acento dominante por maquete (na demo, turquesa da poltrona) e os demais em pequenas doses. O fundo é chapado quente; para outro clima, troque só o par `fundo` (ex.: noite `#2d3f73` → `#1c2748` com a luminária acesa).

## 3. Luz e câmera

| Item | Valor |
|---|---|
| Câmera | ortográfica, 45° de azimute, 33° de elevação; `span` 8 (altura visível em unidades de mundo) |
| Luz principal | direcional `#ffeed6`, 2,9, vinda da frente-direita (8, 10.5, 3.2); sombra PCF suave, raio 5, mapa 2048 |
| Céu/chão | hemisférica `#fff1e0` / `#b9806e`, 0,82 |
| Preenchimento | direcional azulada `#c4d6ff`, 0,55 |
| Luz prática | luminária: ponto `#ffc466` até 9, com abajur e lâmpada emissivos; acende com `on(k)` |
| Tom | ACES, exposição 1,0 |
| Compositor 2D | tilt-shift (cópia com blur 6 px, nítida numa faixa de ±22% em torno de y = 52%), vinheta marrom 30%, grão a 12 poses/s |

- Sempre **uma luz quente prática** dentro da cena (abajur, janela, tela).
- A maquete gira devagar: de −0,16 a +0,14 rad em 8 s, com zoom de 0,97 a 1,05. Nunca mais que isso: as duas paredes de fundo precisam continuar atrás.
- Nada de perspectiva, nada de câmera andando por dentro.

## 4. Peças

| Função | O que faz |
|---|---|
| `sala(L, h)` | base, piso de tábuas e duas paredes de fundo |
| `estante(w, h, d, {rows, seed})` | estante com livros aleatórios (em pé, tombados, pilhas); `userData.books` para animar |
| `poltrona`, `mesa`, `luminaria`, `tapete`, `planta`, `quadro`, `janela`, `caneca`, `pilha` | móveis e objetos |
| `manchaDeLuz` | paralelogramo aditivo no piso (sol da janela) |
| `pino({body, skin, hair, hat, sit, book})` | boneco; `userData.head`, `.arms`, `.book` |
| `etiqueta(texto)` | cartão flutuante com haste, sempre de frente |
| `box`, `cyl`, `ball` | primitivas com canto arredondado e sombra |

Escala: 1 unidade ≈ 1 m; sala de 6 × 6; boneco em pé com ~1 m (é brinquedo, não gente).

## 5. Movimento

| Gesto | Função | Regra |
|---|---|---|
| Brotar | `brota(obj, t, t0, 0.55)` | móveis e arquitetura; escala Y de 0 a 1 com `outBack` |
| Cair e quicar | `cai(obj, t, t0)` | bonecos e objetos soltos; amassa 18% no impacto |
| Onda | livros da estante com atraso de 12 ms cada | qualquer coleção |
| Andar | `pulo(p, n, h)` | bonecos não deslizam: andam aos pulinhos (6 a 7 por trajeto), com leve balanço |
| Acender | `luminaria.userData.on(k)` | luz prática entra em 0,25 s e cintila 6% |

Ordem de montagem: estrutura (0,5 s) → objetos grandes → pequenos → bonecos → etiqueta → título. Cerca de 0,2 a 0,3 s entre peças.

## 6. Texto

Fredoka 700 (título, 92 px, marinho) e 500. Título 2D no terço inferior esquerdo, com chip coral em caixa alta acima; linhas entram com sobra, uma por vez. Etiquetas 3D em cartão marinho com texto creme, no máximo 2 palavras. A maquete fica à direita do quadro para sobrar espaço de texto.

## 7. Formatos

Em 9:16, a maquete ocupa os 60% de cima e o título vai embaixo; `span` ≈ 11 para caber a largura. Não testado.

## 8. Quando usar / quando não

- **Usar**: hábitos e rotinas (um cômodo por hábito), negócios e sistemas (loja, fábrica, escritório em corte), mapas de ideias, "antes e depois" do mesmo lugar.
- **Evitar**: emoção intensa, close de rosto, cenas de ação.

## 9. Como rodar

```bash
node shared/web/render.cjs styles/maquete/demo/demo.html -o quadro.png -t 6.3
node shared/web/render.cjs styles/maquete/demo/demo.html -o demo.mp4 --scale 0.6667 --jobs 3
```

Usa WebGL por software (SwiftShader): ~0,5 s por quadro em 1080p.

## 10. Pendências

- [ ] Aprovação do estilo.
- [ ] Outras maquetes: quarteirão, cozinha, escritório, mesa de trabalho vista de cima.
- [ ] Mais poses do boneco (apontar, comemorar, dormir) e acessórios.
- [ ] Clima noturno (par de fundo escuro) e exterior com árvores.
