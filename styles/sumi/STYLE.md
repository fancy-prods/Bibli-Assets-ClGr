# Estilo "sumi": guia v0 (proposta)

> **Status: proposta de 13/11/2026, aguardando aprovação do Arthur.** Nada daqui foi usado em vídeo.
> Catálogo: [`catalog.json`](catalog.json). Demo: [`demo/demo.html`](demo/demo.html) (8 s, "Ler devagar").
> Nenhum asset de `palco` ou `pop-explica` foi reaproveitado.

## 1. Princípio

Nanquim e aguada sobre papel de arroz. **O vazio é o personagem principal**: o papel ocupa mais da metade do quadro e cada marca precisa merecer estar ali. Uma cena é pintada diante do espectador, marca por marca, na velocidade de quem respira.

Três tipos de marca, e só três:

1. **Aguada**: tinta diluída que abre devagar, com borda mais escura (a "linha de maré") e granulação. Montanhas, pedras, névoa.
2. **Pincelada**: traço único com entrada, pressão e saída; o pincel seca ao longo do caminho e as cerdas falham. Troncos, galhos, mantos, chão.
3. **Selo**: um único ponto de vermelho por quadro (sol **ou** carimbo; os dois juntos só no quadro final).

## 2. Paleta

| Papel | `#f0eadb`, com fibras longas e manchas |
|---|---|
| Tinta | `#191715`, sempre em multiply; os cinzas são a mesma tinta diluída (alfa), nunca outra cor |
| Vermelho | `#c0281f` (selo, sol) |

Não existe quarta cor. Tons permitidos de tinta: 0,3 (longe), 0,5, 0,72, 0,9 a 0,95 (perto). Quanto mais longe, mais diluído.

## 3. Marcas ([`engine/sumi.js`](engine/sumi.js))

| Função | Parâmetros que importam |
|---|---|
| `Sumi.stroke({pts, w, tone, dry, tin, tout, seed, wfn})` | `dry` 0,15 (encharcado, agulhas) a 0,85 (seco, chão); `tin`/`tout` = entrada e saída em ponta; `wfn(u)` = perfil de largura próprio (manto) |
| `Sumi.wash({rx, ry, tone, edge, rough})` | `edge` = força da linha de maré; `rough` = irregularidade do contorno |
| `Sumi.mountain({y, amp, tone, fade, freq, peaks})` | crista por ruído + picos explícitos `[x, altura, largura]`; tinta forte na crista, some para baixo em `fade` px |
| `Sumi.needles({x, y, ang, spread, n, len})` | leque de riscos (agulhas de pinheiro, capim) |
| `Sumi.mist(ctx, t, lista)` | borrões da cor do papel que andam devagar entre as cordilheiras |
| `Sumi.bird`, `Sumi.seal`, `Sumi.text`, `Sumi.paper` | pássaro em "v", carimbo, texto que assenta, papel |

Cada marca é renderizada uma vez (com semente) e guardada; o tempo só **revela**. A pincelada se revela ao longo do próprio traçado (`draw(ctx, k)`), a montanha da esquerda para a direita com borda macia, a aguada abre de 72% a 100% do tamanho enquanto escurece.

## 4. Desenho

- **Profundidade por diluição e névoa**: três cordilheiras (tom 0,3 / 0,5 / 0,72), névoa entre elas. Sem perspectiva linear.
- **Figura humana em quatro marcas**: manto (uma pincelada gorda com `wfn`), joelho, cabeça (aguada pequena e escura), chapéu (um arco). Mais braço e livro em riscos finos. Sem rosto, sem mãos. A postura conta tudo.
- **Assimetria**: massa escura num terço (o pinheiro), vazio nos outros dois. Texto no vazio.
- **Pincel seco para o que é velho ou áspero** (tronco, chão: `dry` 0,5 a 0,85); pincel molhado para o que é vivo (manto, agulhas: 0,15 a 0,3).

## 5. Texto

Shippori Mincho. Título em minúsculas, 500, 112 px, espaçamento 3 px. Linha de apoio em caixa alta, 23 px, espaçamento 4 px, tom 0,75. Texto entra **borrado e claro e firma** em ~0,9 s (`Sumi.text`). Selo quadrado vermelho de 72 px com as iniciais, batido por último, no fim da linha do título.

Nada de caixa, tarja ou fundo atrás do texto: ele é tinta no mesmo papel.

## 6. Movimento

| Ordem (demo) | Marca | Duração |
|---|---|---|
| 0,1 a 3,0 s | três cordilheiras, da mais distante à mais próxima | ~1,8 s cada, sobrepostas |
| 1,4 a 3,2 s | chão e tronco (de baixo para cima) | 1,6 s |
| 2,7 a 4,9 s | galhos, depois tufos de agulhas em sequência | 0,55 s por tufo, 0,11 s de intervalo |
| 3,9 a 5,5 s | pedra, manto, joelho, cabeça, chapéu, braço, livro | 0,2 a 0,6 s cada |
| 4,6 a 5,6 s | sol | 1 s |
| 5,6 a 6,9 s | título e linha de apoio | 0,9 s |
| 6,8 s | selo | 0,25 s |

- Ritmo: **uma marca de cada vez**, com pausa. A pincelada tem a velocidade de um braço (0,3 a 1,6 s conforme o comprimento).
- Depois de pintado, quase nada se move: névoa deriva, pássaros cruzam, a câmera aproxima de 1,00 a 1,045 em 8 s.
- Sem corte seco dentro do capítulo. Para trocar de cena, uma aguada grande cobre o quadro e o papel "seca" em branco.

## 7. Formatos

O 9:16 é o formato do rolo vertical (kakemono) e funciona melhor que o 16:9: pinheiro subindo pela lateral, montanhas no alto, figura embaixo, texto em coluna. Não testado.

## 8. Quando usar / quando não

- **Usar**: filosofia, estoicismo, meditação, foco, hábitos lentos, natureza, luto, poesia; citações.
- **Evitar**: listas, números, humor, qualquer coisa com muitos elementos na tela.

## 9. Como rodar

```bash
node shared/web/render.cjs styles/sumi/demo/demo.html -o quadro.png -t 7.5
node shared/web/render.cjs styles/sumi/demo/demo.html -o demo.mp4 --scale 0.6667
```

## 10. Pendências

- [ ] Aprovação do estilo.
- [ ] Mais motivos: bambu, garça, barco, lua, ponte, ensō (círculo de uma pincelada).
- [ ] Figura em pé e caminhando (3 marcas).
- [ ] Transição de aguada cobrindo o quadro; versão 9:16.
