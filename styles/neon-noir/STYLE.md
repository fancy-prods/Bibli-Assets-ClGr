# Estilo "neon-noir": guia v0 (proposta)

> **Status: proposta de 13/11/2026, aguardando aprovação do Arthur.** Nada daqui foi usado em vídeo.
> Catálogo: [`catalog.json`](catalog.json). Demo: [`demo/demo.html`](demo/demo.html) (8 s, "Rua do Sax").
> Nenhum asset de `palco` ou `pop-explica` foi reaproveitado; motor, figuras e cenário são próprios.

## 1. Princípio

Noite, chuva e luz de neon. A cena é **escura por padrão** e só existe onde uma fonte de luz colorida a revela. Vista lateral em camadas (2.5D), como um jogo de plataforma cinematográfico, mas **vetorial e liso: nada de pixel art**. Pensado para os vídeos longos da Unfold com trilha de jazz: ritmo lento, câmera que desliza, tensão contida.

Três ideias sustentam o estilo:

1. **A luz conta a história.** Letreiros são o texto da cena (headline, capítulo, palavra-chave). Quem acende e quem falha é direção de arte.
2. **Personagem é silhueta.** Sem rosto. Identidade vem do recorte (chapéu, sobretudo, instrumento) e de um objeto aceso (livro, brasa, olhos do gato).
3. **Tudo está molhado.** O chão espelha a cena em riscos verticais; a chuva só aparece onde há luz.

## 2. Paleta

| Papel | Cor | Uso |
|---|---|---|
| Noite | `#06041a` | topo do céu, sombras |
| Ambiente | `#2c2256` | luz ambiente (multiplica o albedo; é o "preto" da cena) |
| Névoa | `#8a2a78` → `#4a1560` | horizonte, prédios distantes |
| **Magenta** | `#ff2e88` | neon principal 1 (perigo, desejo, a "pergunta") |
| **Ciano** | `#19e6ff` | neon principal 2 (razão, descoberta, a "resposta") |
| **Âmbar** | `#ffab40` | luz quente: janelas, poste, interior, livro aberto |
| Vermelho | `#ff3d3d` | só pontual (luz de antena, alerta) |
| Verde ácido | `#b6ff3c` | raríssimo (olhos do gato, um detalhe por cena) |

Regras: **dois neons frios/saturados + um quente por plano**. Magenta e ciano nunca na mesma intensidade: um domina, o outro responde. Âmbar marca onde há gente (interiores, o livro). Albedo dos materiais é médio-claro e dessaturado (tijolo `#8a5f68`, reboco `#6c7691`, calçada `#8f8a9c`); quem dá cor é a luz.

## 3. Pipeline de luz (o que o motor faz por quadro)

[`engine/nn-core.js`](engine/nn-core.js), classe `NN.Shot`:

| Ordem | Etapa | Técnica |
|---|---|---|
| 1 | Céu + 3 camadas de horizonte | paralaxe 0,10 / 0,24 / 0,5; névoa magenta crescendo para a base |
| 2 | Fachada e chão | **albedo × luz** (multiply). A luz é a soma (lighter) de gradientes radiais, um por fonte, sobre a cor ambiente |
| 3 | Emissivos | tubos acesos, janelas, lâmpadas: desenhados à parte, somados por cima |
| 4 | Reflexo molhado | fachada+emissivos espelhados na base da parede, figuras espelhadas nos pés; borrão vertical de 9 passos; máscara de "molhado" (calçada 0,3, asfalto 0,5, poças 0,9) |
| 5 | Volumetria | cone do poste (gradiente + blur), vapor de bueiro (bolhas aditivas) |
| 6 | Figuras | silhueta + rim por peça + "wrap" suave na figura inteira; sombra de contato elíptica |
| 7 | Chuva | 3 profundidades; cada gota recebe a cor do bloom local, então some no escuro e brilha perto do neon; respingos no chão |
| 8 | Primeiro plano | silhuetas quase pretas, desfocadas (blur 4 a 5 px), paralaxe 1,45 a 1,7 |
| 9 | Bloom | curto (1/4 da resolução) atrás das figuras; largo (1/8) por cima de tudo, vira névoa |
| 10 | Pós (WebGL) | aberração cromática radial 0,0035, sangramento de croma, scanlines 7%, grão 5,5%, vinheta 62%, véu violeta nas sombras, glitch de fita nas viradas |

### Regras de iluminação

- Toda fonte de luz existe três vezes: como **emissivo** (o tubo), como **luz** na parede/chão (gradiente radial) e como **reflexo** no asfalto. Se faltar uma das três, a cena fica falsa.
- Área sem luz não é preta: é o ambiente violeta multiplicando o albedo. Preto puro só no primeiro plano.
- O personagem importante fica **contra** uma fonte clara (vitrine, porta) ou **sob** um letreiro, nunca no escuro uniforme.
- Sombra de contato sempre. Sombra projetada, nunca (a noite já resolve).
- Bloom largo passa por cima das silhuetas de propósito: é a névoa úmida que separa os planos.

## 4. Letreiros de neon

`NN.textTube` e `NN.tubeStroke`. Cada tubo tem miolo quase branco (78% branco) com 42% da espessura e corpo na cor saturada; o halo vem do bloom.

| Modo | Fonte | Uso |
|---|---|---|
| `outline` | Bebas Neue, contorno de 6 a 8 px | palavra-chave, título, letreiro de fachada |
| `fill` | Sacramento (manuscrita monolinha) | frase curta, assinatura, "ao vivo" |
| traçado livre | `tubeStroke` com um path | ícones: livro, seta, nota musical, moldura |

- Todo letreiro tem versão **apagada** pintada no albedo (tubo cinza com suporte). Quando falha, o tubo continua lá.
- `NN.flicker(t, seed, amount)`: cintilação de rede elétrica sempre; quedas em rajada conforme `amount` (0 = estável, 1 = temperamental, 2+ = quase quebrado). **Um** letreiro instável por plano.
- Texto de letreiro: no máximo 2 palavras. Frase inteira vai na caixa de diálogo.

## 5. Figuras

[`engine/nn-figure.js`](engine/nn-figure.js). Vista de perfil, altura nominal 400 unidades, cerca de 8 cabeças. Sem olhos, boca ou feições: só o perfil (nariz e queixo) e o que a pessoa veste ou carrega.

| Figura | Função | Parâmetros |
|---|---|---|
| `leitor` | protagonista de sobretudo e fedora, lendo um livro aceso | `look` 0..1 (levanta o olhar), `bookColor` |
| `saxofonista` | figurante/atmosfera; marca o compasso com os joelhos | `saxRim` (rim próprio do instrumento) |
| `passante` | ciclo de caminhada com guarda-chuva; serve de primeiro plano desfocado | `speed`, `umbrella` |
| `gato` | detalhe vivo; olhos emissivos que piscam | `eyes` |

Peças reutilizáveis (`NN.Fig.parts`): `leg`, `arm`, `head` (chapéu `fedora`/`boina`, cabelo `coque`/`curto`), `coat`.

### Luz de recorte (rim)

Cada peça é desenhada numa tela de rascunho; o rim é "a peça menos a peça deslocada para longe da luz". Parâmetros: `{color, dir:[x,y], w, a, soft, add}`.

| Tipo | `w` | `soft` | `a` | Onde |
|---|---|---|---|---|
| Rim duro | 3 a 5 px | 1 | 0,8 a 0,95 | por peça (`rims`); desenha a forma |
| Wrap | 14 a 16 px | 8 a 9 | 0,22 a 0,3, aditivo | na figura inteira (`wrap`); dá volume |

- Até **duas** cores de rim por figura: a do letreiro mais próximo e a da fonte quente oposta.
- A direção do rim aponta para a fonte real da cena. Rim sem fonte visível é erro.
- Objetos brilhantes (sax, livro, guarda-chuva molhado) têm rim próprio mais claro.

## 6. Texto na tela

| Elemento | Fonte | Regra |
|---|---|---|
| Caixa de diálogo (`NN.dialog`) | Chakra Petch 500, 44 px | fundo `rgba(8,5,20,0.86)`, borda de 3 px na cor de quem fala, etiqueta do falante; texto **digitado** a ~30 caracteres/s; palavra-chave colorida com brilho; no máximo uma palavra tremendo |
| HUD de fita (`NN.hud`) | Share Tech Mono 34 px | "▶ PLAY" e timecode, 72% de opacidade; opcional, marca flashback ou "gravação" |
| Headline | letreiro de neon na parede (seção 4) | o título do vídeo é um letreiro que acende |

Cor do falante: narrador ciano, protagonista âmbar, antagonista/dúvida magenta.

## 7. Movimento

- **Câmera**: desliza de lado, 10 a 20 px/s, com zoom de 1,00 a 1,04 em 8 s. Sem cortes secos dentro da cena; a paralaxe faz o trabalho.
- **Sempre vivo**: chuva, cintilação, vapor, respiração das figuras, timecode. Nada fica parado.
- **Transição**: glitch de fita (0,3 s: faixas deslocadas + salto vertical) entrando e saindo. Uso: troca de capítulo, não de plano.
- **Ênfase**: letreiro acende (0 → 1 com duas falhas rápidas), nunca "pop" de escala.
- **Compasso**: figuras de fundo se movem no tempo da trilha (o saxofonista usa 2,1 rad/s; ajustar ao BPM).

## 8. Formatos

Mundo com base da parede em y = 800 e câmera com `y = 64` (sobra asfalto para o reflexo). Para 9:16, o mesmo cenário serve com a câmera centrada no personagem e zoom ~1,25; letreiros verticais (como "JAZZ") funcionam melhor que horizontais. A demo foi composta em 16:9; o 9:16 ainda não foi testado.

## 9. Quando usar / quando não

- **Usar**: livros de suspense, crime, memórias, psicologia sombria, biografias de músicos, histórias de cidade e madrugada; aberturas e encerramentos da Unfold.
- **Evitar**: conteúdo infantil, tutoriais passo a passo, qualquer cena de dia (o estilo não tem dia; o mais claro que existe é interior âmbar).

## 10. Como rodar

```bash
node shared/web/render.cjs styles/neon-noir/demo/demo.html -o quadro.png -t 6.4          # um quadro 1920×1080
node shared/web/render.cjs styles/neon-noir/demo/demo.html -o demo.mp4 --scale 0.6667    # vídeo 1280×720
```

Custo: ~0,7 s por quadro em 1080p (CPU, 4 páginas em paralelo).

## 11. Pendências

- [ ] Aprovação do estilo e do nome.
- [ ] Interior (clube de jazz por dentro): palco, mesas, fumaça.
- [ ] Mais figuras: bartender, cantora, detetive sem livro; poses sentadas.
- [ ] Testar 9:16.
- [ ] Sincronizar cintilação e compasso com o BPM da trilha.
