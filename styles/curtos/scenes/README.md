# Cenários (estilo curtos)

| Cenário | Arquivo | Primeiro uso |
|---|---|---|
| Loja de eletrônicos | `loja_eletronicos.svg` | carlbob1 |

Cada SVG é desenhado em coordenadas de mundo para a tela 1080×1920 e se estende além do quadro para permitir movimentos de câmera (`shared/motion-utils/camera.py`). Para usar numa cena, insira o conteúdo do `<g id="...">` dentro do grupo da câmera. As âncoras (piso, prateleiras, posição e escala dos personagens) ficam no comentário de cada arquivo.

Ainda faltam os cenários **sala de estar** e **cozinha**.

Ao criar um cenário, siga o `STYLE.md`: chapado, sem contorno, paleta clara e saturada, sombras de contato em tudo que toca o chão, e a pilha de iluminação de `/shared/motion-utils/lighting.svg.md` com os valores de `presets/lighting.json`.
