# Estilo "cordel": guia v0 (proposta)

> **Status: proposta de 13/11/2026, aguardando aprovação do Arthur.** Nada daqui foi usado em vídeo.
> Catálogo: [`catalog.json`](catalog.json). Demo: [`demo/demo.html`](demo/demo.html) (8 s, "O homem que leu o mundo").
> Nenhum asset de `palco` ou `pop-explica` foi reaproveitado.

## 1. Princípio

Xilogravura de folheto de cordel: uma matriz de madeira entalhada, tinta preta, papel colorido barato. O vídeo é **uma gravura sendo impressa peça por peça**. Tudo é chapado, frontal ou de perfil, sem perspectiva, e o vazio é preenchido com enfeite (asteriscos, serrilha, nuvem em espiral).

O que faz parecer gravura e não vetor limpo:

1. **Borda roída**: toda forma preta passa por um filtro de deslocamento (ruído de baixa frequência, 10 px).
2. **Falha de tinta**: pontinhos de papel dentro do preto (ruído fino) e, raramente, uma falha maior de rolo.
3. **Entalhe**: detalhe nunca é linha preta sobre branco dentro de uma massa; é **risco da cor do papel dentro do preto** (folhas, listras, veios, telhas).
4. **Cor fora de registro**: até 2 cores chapadas por baixo do preto, deslocadas ~5 px, com borda mais mole que a do preto.
5. **Fervura**: o filtro troca de semente a cada 1/6 s e a folha inteira treme ±0,8 px. Parece impresso à mão, quadro a quadro.

## 2. Paleta

| Papel (fundo) | Cor | | Cor chapada | Cor |
|---|---|---|---|---|
| palha (padrão) | `#efd68a` | | urucum | `#cf3a2b` |
| rosa | `#f2a79c` | | anil | `#27599a` |
| verde | `#a9d4a0` | | gema | `#f0b02c` |
| azul | `#9bc7de` | | mata | `#2f8a4e` |
| cru | `#e9dcc0` | | | |
| laranja | `#f3b36a` | | | |

Tinta: `#1a1410` (preto quente, nunca `#000`).

Regras: **um papel por vídeo ou por capítulo** (trocar o papel é trocar de folheto). No máximo **duas** cores chapadas por quadro, e cada uma em no máximo três lugares. A cor nunca carrega informação sozinha: sem ela a gravura continua legível.

## 3. Camadas

[`engine/cordel.js`](engine/cordel.js), `Cordel.stage()`:

| Ordem | Camada | Filtro | Mesclagem |
|---|---|---|---|
| 1 | Papel | `#papel`: fibras + manchas | normal |
| 2 | `spot` (cores chapadas) | `#xilo-spot`: deslocamento 16 px, falhas largas | multiply, deslocada (5, 4) px |
| 3 | `ink` (preto) | `#xilo`: deslocamento 10 px + falha fina + falha de rolo | normal |
| 4 | `type` (legenda) | `#xilo-fino`: deslocamento 5 px, só falha fina | normal |
| 5 | Vinheta | gradiente radial marrom, 42% na borda | multiply |

## 4. Desenho

- **Figuras**: cabeça grande de perfil, olho amendoado enorme visto de frente (como em gravura egípcia), sobrancelha grossa, boca de um risco. Rosto e mãos na cor do papel com contorno preto de 8 a 9 px; roupa em massa preta com listras entalhadas. Proporção atarracada: cerca de 4 cabeças.
- **Natureza**: copa de árvore é uma massa preta cheia de folhas-lente entalhadas; mandacaru é traço grosso com friso pontilhado; chão é morro preto com riscos curvos.
- **Sol com rosto**: 16 raios triangulares alternando comprido/curto; o disco recebe a cor `gema`.
- **Moldura**: filete de 16 px a 44 px da borda, com serrilha (44 dentes) em cima e embaixo.
- **Espessuras**: contorno 8 a 11 px; entalhe 4 a 6,5 px; nada mais fino que 4 px (não sobrevive ao filtro).
- **Horror ao vazio**: céu livre recebe nuvem em espiral, pássaros e asteriscos de 8 pontas.

Peças prontas: `moldura`, `serrilha`, `sol`, `copa`, `tronco`, `mandacaru`, `casa`, `passaro`, `chao`, `tufo`, `nuvem`, `asteriscos`, `leitor` (sentado, com piscar, aceno de cabeça e virada de página).

## 5. Texto

| Elemento | Fonte | Regra |
|---|---|---|
| Título (`Cordel.faixa`) | Alfa Slab One, 78 px, caixa alta | letras da cor do papel entalhadas numa tarja preta de pontas em flâmula |
| Legenda (`Cordel.legenda`) | IM Fell English itálico, 62 px | na faixa lisa do chão (y ≈ 990), cor do papel; entra **palavra por palavra**, cada uma como carimbo |
| Texto corrido (miolo do folheto) | IM Fell English regular | preto sobre papel, em sextilhas quando for verso |

Legenda cabe em uma linha (até ~55 caracteres). Verso de cordel rima; se a narração permitir, quebre a legenda em redondilha.

## 6. Movimento

- **12 poses por segundo** (`Cordel.step`). O vídeo sai a 30 fps, mas nada se move entre as poses.
- **Carimbo** (`Cordel.stamp`): toda peça entra em 3 poses: fantasma 5% maior a 45% de opacidade, leve recuo (98,5%), assenta. A cor chapada entra 2 poses **antes** do preto dela.
- **Ordem de impressão**: moldura, chão, árvore, figura, cenário distante, sol, enfeites, título, legenda. De baixo para cima, do grande para o pequeno.
- **Vida depois de impresso**: raios do sol giram 11,25° a cada 1/3 s; pássaros alternam duas poses de asa (6 por segundo); olhos piscam (2 poses); cabeça inclina em um salto, sem interpolar.
- **Sem câmera**. A folha não faz zoom nem pan. Troca de cena = troca de folha (corte seco, ou a folha nova carimbada por cima).

## 7. Formatos

A demo é 16:9 (friso horizontal). O 9:16 é o formato natural do folheto: título em cima, gravura no meio, legenda embaixo; a mesma função `moldura` aceita `W`/`H`. Ainda não testado.

## 8. Quando usar / quando não

- **Usar**: literatura brasileira, histórias populares, fábulas, biografias, livros de sabedoria prática com tom de causo; qualquer coisa que ganhe com narrador de feira.
- **Evitar**: tecnologia, finanças, ficção científica; cenas que dependam de expressão facial sutil ou de profundidade.

## 9. Como rodar

```bash
node shared/web/render.cjs styles/cordel/demo/demo.html -o quadro.png -t 6.9
node shared/web/render.cjs styles/cordel/demo/demo.html -o demo.mp4 --scale 0.6667
```

## 10. Pendências

- [ ] Aprovação do estilo.
- [ ] Mais figuras: mulher, criança, vaqueiro, bicho (bode, onça, cavalo); figura em pé e andando (2 poses).
- [ ] Capa de folheto 9:16 e página de versos.
- [ ] Transição "rolo de tinta" entre folhas.
