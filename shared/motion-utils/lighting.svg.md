# Módulo de iluminação em SVG (agnóstico de estilo)

Técnica para dar profundidade a cenas 2D só com camadas, gradientes e modos de mesclagem, sem 3D. Os **valores** (opacidades, cores) são definidos por cada estilo no seu `presets/lighting.json`; aqui fica só a técnica.

## Pilha de camadas (de baixo para cima)

| Ordem | Camada | Técnica | Mesclagem |
|---|---|---|---|
| 1 | Cenário | Formas chapadas + sombras de contato | normal |
| 2 | Escuridão global | `<rect>` do tamanho do canvas, cor fria escura | `multiply` |
| 3 | Personagens | Desenhados **depois** da escuridão | normal |
| 4 | Poças de luz | `<radialGradient>` opaco no centro → transparente na borda | `screen` |
| 5 | Fontes de luz | Lâmpada/cúpula/janela redesenhadas por cima | normal |
| 6 | Vinheta | `<radialGradient>` invertido (transparente → escuro) | normal |

## Esqueleto SVG

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 W H">
  <defs>
    <!-- 4. poça de luz: centro opaco, meio do raio ~0.2, borda 0 -->
    <radialGradient id="pool-warm">
      <stop offset="0"   stop-color="LIGHT_COLOR" stop-opacity="CENTER"/>
      <stop offset="0.5" stop-color="LIGHT_COLOR" stop-opacity="MID"/>
      <stop offset="1"   stop-color="LIGHT_COLOR" stop-opacity="0"/>
    </radialGradient>
    <!-- 6. vinheta: transparente até START, escura na borda -->
    <radialGradient id="vignette" r="0.75">
      <stop offset="START" stop-color="#000" stop-opacity="0"/>
      <stop offset="1"     stop-color="#000" stop-opacity="EDGE"/>
    </radialGradient>
  </defs>

  <g id="cenario">
    ...
    <!-- sombra de contato: elipse preta, opacidade 0.22–0.3 -->
    <ellipse cx="..." cy="..." rx="..." ry="..." fill="#000" opacity="0.25"/>
  </g>

  <rect id="escuridao" width="100%" height="100%" fill="DARK_COLOR" opacity="DARKNESS"
        style="mix-blend-mode: multiply"/>

  <g id="personagens"> ... </g>

  <ellipse id="poca" cx="..." cy="..." rx="..." ry="..." fill="url(#pool-warm)"
           style="mix-blend-mode: screen"/>

  <g id="fontes-de-luz"> ... </g>

  <rect id="vinheta" width="100%" height="100%" fill="url(#vignette)"/>
</svg>
```

## Variante lanterna

Para cenas de pouca luz: a camada de escuridão recebe uma máscara com gradiente radial. Na máscara, **preto = buraco** (a escuridão some ali), branco = escuridão plena.

```xml
<radialGradient id="torch-grad">
  <stop offset="0"   stop-color="#000"/>
  <stop offset="0.6" stop-color="#000"/>
  <stop offset="1"   stop-color="#fff"/>
</radialGradient>
<mask id="torch">
  <rect width="100%" height="100%" fill="#fff"/>
  <circle cx="TX" cy="TY" r="TR" fill="url(#torch-grad)"/>
</mask>
<rect id="escuridao" ... mask="url(#torch)"/>
```

## Regras gerais

- A área mais iluminada da cena coincide com o personagem principal.
- Escuridão nunca cobre personagens nem fontes de luz (por isso eles são desenhados depois dela).
- Luz nunca em modo normal: sempre `mix-blend-mode: screen`.
- O fade vem do gradiente; não usar `feGaussianBlur` em formas de luz.
- Contraste de temperatura: uma fonte quente e outra fria.
- Fundo mais escuro e frio; primeiro plano mais claro e quente.
- Tudo que toca o chão tem sombra de contato.

## Parâmetros

| Parâmetro | Significado |
|---|---|
| `DARK_COLOR`, `DARKNESS` | Cor e opacidade da escuridão global |
| `LIGHT_COLOR`, `CENTER`, `MID` | Cor da poça e opacidades no centro e no meio do raio |
| `START`, `EDGE` | Início (fração do raio) e opacidade na borda da vinheta |
| `TX`, `TY`, `TR` | Centro e raio da lanterna (variante) |
