# Cenários (estilo palco)

| Cenário | Arquivos (variantes) | Primeiro uso |
|---|---|---|
| Loja de eletrônicos | `loja_eletronicos.svg` | carlbob1 |
| Escritório de executivo | `escritorio_padrao.svg`, `escritorio_epoca.svg` | — |
| Sala de jantar | `sala_jantar_padrao.svg`, `sala_jantar_epoca_hora-entardecer.svg` | — |
| Fábrica / usina | `fabrica_padrao.svg` | — |
| Parque | `parque_padrao.svg`, `parque_hora-entardecer.svg` | — |
| Balcão de atendimento | `balcao_padrao.svg`, `balcao_epoca.svg` | — |
| Sala de aula | `sala_aula_padrao.svg`, `sala_aula_epoca.svg`, `sala_aula_infantil.svg` | — |
| Sala de estar | `sala_estar_padrao.svg`, `sala_estar_epoca_hora-entardecer.svg` | — |
| Quarto | `quarto_padrao.svg`, `quarto_infantil_hora-dia.svg` | — |
| Rua / calçada | `rua_padrao.svg`, `rua_epoca.svg`, `rua_hora-noite.svg` | — |
| Palco neutro | `palco_neutro_padrao.svg`, `palco_neutro_refletores-um.svg` | — |
| Salão de banquete | `banquete_padrao.svg` | — |

**Cenários paramétricos** (todos menos a loja) seguem a seção 8 do `STYLE.md`: mundo com 1920 de altura, desenhado de x −2000 a 3100; o `viewBox` é o 16:9 inteiro (x −1167 a 2247) e a zona segura do 9:16 é x 0 a 1080. São gerados por `styles/palco/tools/cenarios/exportar.py`; outra hora ou época sai sem redesenhar:

```
python styles/palco/tools/cenarios/exportar.py parque hora=noite -o parque_noite.svg
```

Camadas de cada SVG, na ordem de desenho: `#back` (recebe a escuridão), `#escuridao`, **personagens**, `#front` (mesa, balcão, carteiras: cor já escurecida), `#pocas` (poças de luz em screen), `#sources` (fontes de luz por cima de tudo). Quem senta atrás de um móvel é recortado abaixo de `recorte_y` e desenhado antes do `#front`. As âncoras (posições, pés, escala, recorte) ficam no comentário de cada arquivo.

A **loja de eletrônicos** foi desenhada para 1080×1920 (coordenadas de mundo, estendida para a câmera); conferir as laterais antes de usá-la no 16:9.

Ao criar um cenário, siga o `STYLE.md`: chapado, sem contorno, paleta clara e saturada, sombras de contato em tudo que toca o chão, e a pilha de iluminação de `/shared/motion-utils/lighting.svg.md` com os valores de `presets/lighting.json`. Para um cenário novo paramétrico, escreva a função em `tools/cenarios/`, registre em `CENARIOS` e rode `exportar.py`.
