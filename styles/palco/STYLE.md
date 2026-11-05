# Estilo "palco": guia v1

> Versão 1, aprovada em 31/10/2026. Nome definitivo "palco" escolhido em 04/11/2026 (antes: "curtos", provisório).
> Catálogo do estilo: [`catalog.json`](catalog.json). Técnica de iluminação compartilhada: [`/shared/motion-utils/lighting.svg.md`](../../shared/motion-utils/lighting.svg.md).

## 1. Princípio

Profundidade em vídeo 2D por meio de iluminação e sombreamento em camadas, sem Three.js nem Blender. Situações do dia a dia, não suspense.

## 2. Iluminação

### Pilha de camadas (de baixo para cima)

| Ordem | Camada | Técnica | Mesclagem | Valor validado |
|---|---|---|---|---|
| 1 | Cenário | Chapado, sem contorno, com sombras de contato | Normal | Paleta clara e saturada |
| 2 | Escuridão global | Retângulo escuro sobre o cenário, **nunca sobre o personagem** | Multiply | 0,1 de dia; 0,18 no entardecer (cor `#2a2240`) |
| 3 | Personagem | Desenhado depois da escuridão, com contorno de silhueta | Normal | Sempre o elemento mais nítido |
| 4 | Poças de luz | Gradiente radial, opaco no centro e transparente na borda | Screen | 0,5 a 0,65 no centro, cerca de 0,2 no meio do raio |
| 5 | Fontes de luz | Cúpula, lâmpada ou janela redesenhadas por cima de tudo | Normal | Cor clara cheia |
| 6 | Vinheta | Gradiente radial invertido | Normal | 0,25 a 0,35 na borda, começando a 60% do raio |

### Regras de iluminação

- A área mais iluminada da cena é onde está o personagem.
- Fontes de luz nunca recebem a escuridão.
- Tudo que toca o chão tem sombra de contato: elipse preta com opacidade de 0,22 a 0,3.
- Luz nunca em modo normal; use `mix-blend-mode: screen`.
- O fade vem do gradiente; não use formas com blur.
- Contraste de temperatura: uma fonte quente e outra fria na mesma cena.
- Contraste de cor entre a roupa do personagem e o fundo atrás dele.
- Fundo mais escuro e frio, primeiro plano mais claro e quente.
- Variante lanterna (cenas de pouca luz): a camada de escuridão recebe uma máscara com gradiente radial (centro preto = buraco). Usar só quando a cena pede.

Presets: [`presets/lighting.json`](presets/lighting.json): `dia` e `entardecer`.

## 3. Personagens

Figuras chapadas montadas por camadas. A silhueta é a mesma para todos; variam roupa, cabelo, cor da íris, pose, expressão e acessórios.

### Anatomia

Cabeça circular, sem nariz, boca ou orelhas. Rosto só com olhos e sobrancelhas. Braços em duas peças (braço e antebraço) com pivôs no ombro e no cotovelo; as pontas arredondadas se sobrepõem no cotovelo, então a junção não aparece. Pernas inteiriças, girando só no quadril.

### Proporções (H = diâmetro da cabeça)

| Parte | Medida |
|---|---|
| Altura total | ~4,6 H |
| Tronco | 1,66 H de altura, 0,95 H de largura nos ombros |
| Pernas | 2 H de comprimento, 0,28 H de largura cada |
| Braço | 0,73 H do ombro ao cotovelo, 0,19 H de largura |
| Antebraço | 0,69 H do cotovelo ao centro da mão |
| Mão | 0,19 H de diâmetro, cai na altura do quadril |
| Pivô do ombro | 0,53 H para cada lado do centro, 0,6 H abaixo do centro da cabeça |
| Olhos | 0,24 H de diâmetro, 0,07 H abaixo do centro da cabeça, 0,34 H entre os centros |
| Sobrancelhas | 0,14 H acima do centro da cabeça |

Coordenadas de referência (H = 116, centro em x = 340): ver seção 10 e [`tools/compose_character.py`](tools/compose_character.py), que é a fonte da verdade da geometria.

### Camadas (de trás para frente)

1. Cabelo de trás
2. Braço de trás
3. Pernas
4. Sapatos
5. Tronco
6. Cabeça
7. Olhos
8. Sobrancelhas
9. Cabelo da frente
10. Braço da frente (quando cruza o corpo)
11. Objeto segurado
12. Mão
13. Acessórios

Cada cabelo é um asset com duas partes (de trás e da frente). Ver [`characters/base/cabelos/`](characters/base/cabelos/).

## 4. Olhos (paramétricos)

Um único asset de olho cobre todas as expressões. Estrutura, de trás para frente: branco do olho (também é a máscara de recorte), íris colorida com contorno, pupila preta, pálpebra superior, pálpebra inferior e contorno do olho. A íris tem cerca de 45% do diâmetro do olho e a pupila, cerca de 19%.

| Parâmetro | Faixa | Efeito |
|---|---|---|
| `look_x` | −1 a 1 | Desloca íris e pupila na horizontal (até 0,47 do raio do olho) |
| `look_y` | −1 a 1 | Desloca íris e pupila na vertical (até 0,45 do raio) |
| `lid_upper` | 0 a 1 | 0 aberto, 1 fechado |
| `lid_lower` | 0 a 1 | 0 aberto, 1 fechado |
| `iris` | paleta | castanho `#7a5230`, azul `#3f7fc4`, verde `#4a9a5c`, mel `#c08a2e`, cinza `#8f9aa3` |

- A borda da pálpebra superior fica em `cy − r + lid_upper·2r`. A inferior fica em `cy + r − lid_lower·2r`, nunca acima da superior. Cada borda tem uma linha preta, oculta quando o valor é menor que 0,03.
- Piscar: a pálpebra superior vai a 1 e volta em cerca de 170 ms (curva seno), em intervalos aleatórios de 2,5 a 5 s.
- A cor da íris é fixa por personagem.
- Divisão de papéis: a **pálpebra controla energia** (sono, tédio, atenção, desconfiança); a **sobrancelha controla emoção** (raiva, preocupação, surpresa, tristeza).

Presets (provisórios): [`presets/expressions.json`](presets/expressions.json).

## 5. Contorno

- O personagem tem contorno preto de silhueta; o cenário não tem contorno.
- O contorno é um filtro aplicado ao grupo, não um traço por peça (ver seção 10). Contornar peça por peça é proibido, porque mostraria a emenda do cotovelo.
- Todo membro que cruza o corpo forma um grupo com filtro próprio: braço, antebraço, objeto segurado e mão.
- Os olhos mantêm o próprio contorno, mais fino.
- **A mão tem contorno próprio em todo o círculo** (anel de 3,5 por baixo), sempre, para não sumir quando passa na frente do corpo. O braço que cruza o corpo e o objeto segurado também ganham contorno explícito por baixo (não dependem do filtro), então continuam contornados quando o vídeo troca o filtro por uma cópia preta do personagem inteiro. Decidido em 05/11/2026.
- Objetos segurados ficam atrás da mão.

## 6. Acessórios

Pack separado, preso a âncoras fixas da cabeça:

| Âncora | Uso |
|---|---|
| Topo da cabeça | Chapéus |
| Linha dos olhos | Óculos |
| Centro inferior do rosto | Bigodes |

- Chapéus trazem uma forma de recorte que esconde o cabelo acima da aba.
- Óculos ficam sobre os olhos e abaixo das sobrancelhas.

## 7. Animação ociosa

Por padrão, todo personagem tem movimentos de repouso, como o idle de um jogo. **O idle nunca sobrescreve o roteiro.** Cada parte do personagem é um canal; o roteiro assume só os canais de que precisa, e os demais continuam no idle.

Implementação: [`tools/animate.py`](tools/animate.py) (gera um SVG por frame usando o montador).

| Canal | Idle | Tipo | Quando o roteiro assume |
|---|---|---|---|
| `breath` | `b = (1 − cos(2πt/4))/2`; grupo superior (cabelo, braços, tronco, cabeça, olhos, sobrancelhas, franja) sobe `2.5·b` unidades base; ombros abrem `1.5·b` graus. Pernas e sapatos não se movem | Aditivo | Nunca desligado; soma por cima de qualquer pose |
| `blink` | Fecha e abre em 0,17 s (`sin(π·k)`), a cada 2,5 a 5 s; em 50% das mudanças de olhar do idle, pisca junto | Aditivo | Suprimido proporcionalmente ao peso do roteiro no canal `lids` |
| `gaze` | Alterna entre o centro (`look_x 0`, `look_y 0.1`) e um desvio (`look_x` ±0,35 a 0,7, `look_y` ±0,25). Fica 0,8 a 2 s no desvio e 3 a 7 s no centro. Aproximação rápida: `cur += (tgt − cur)·min(1, dt·18)` | Substituível | Roteiro define `look_x/look_y` ou um alvo |
| `lids` | `lid_upper` 0,12 | Substituível | Roteiro define a abertura |
| `pose` | Preset `neutro` | Substituível | Roteiro define preset ou ângulos |

### Regras de mistura

- Cada canal substituível tem um peso `w` de 0 a 1, que anda linearmente em 0,3 s e é suavizado com `w²(3 − 2w)`. Valor final = `lerp(idle, roteiro, w_suavizado)`. Nunca há salto.
- Pálpebra final = `max(lerp(0.12, roteiro, w), blink·(1 − w))`.
- Cada personagem tem uma semente fixa (derivada do `id`). Toda aleatoriedade do idle usa essa semente; a mesma timeline sempre gera os mesmos frames.
- Alvo de olhar: `{"gaze": {"target": "personagem:maria"}}` ou `{"gaze": {"point": [x, y]}}`. A direção é o vetor normalizado entre o centro da cabeça e o alvo, mapeado para `look_x/look_y` e limitado a ±1.
- Fora dos intervalos `t`–`until`, o canal volta ao idle com a transição de 0,3 s. Na implementação, a rampa de entrada termina em `t` e a de saída começa em `until`: dentro de `[t, until]` o roteiro vale 100%.

### Timeline de entrada (JSON)

```json
{
  "fps": 30,
  "duration": 6,
  "characters": [
    {"id": "joao", "params": {"shirt": "#4f8a6b"}, "position": [340, 0], "scale": 1}
  ],
  "script": [
    {"char": "joao", "t": 1.0, "until": 3.5, "pose": "explicando"},
    {"char": "joao", "t": 2.0, "until": 4.0, "gaze": {"point": [100, 150]}},
    {"char": "joao", "t": 4.5, "until": 5.5, "lids": {"lid_upper": 1}}
  ]
}
```

Saída: `python tools/animate.py timeline.json -o renders/frames/` gera um SVG por frame. O formato final de vídeo ainda não foi decidido; por enquanto o pipeline para nos frames SVG.

## 8. Formatos (16:9 e 9:16)

> Decidido em 04/11/2026. Vale para vídeos curtos (9:16) e longos (16:9).

Os cenários são feitos uma vez e servem aos dois formatos. **Não renderizar em 16:9 e recortar para 9:16**: o recorte de 1920×1080 tem só 608×1080 px (ampliar 1,8× borra) e quebra a composição.

- **Coordenadas de mundo comuns:** altura de 1920 unidades (y 0 a 1920), igual ao cenário `loja_eletronicos`.
- **Cenário largo para o 16:9:** desenhado pelo menos de x −1167 a 2247 (3414 unidades, a largura de um quadro 16:9 com 1920 de altura, centrado em x 540). Desenhar mais largo se a câmera for se mover.
- **Zona segura do 9:16:** x 0 a 1080. O que identifica o lugar (letreiro, porta, móvel principal) fica dentro dela; as laterais completam o 16:9 e não podem ficar vazias.
- **Câmera por formato:** cada formato tem o próprio enquadramento (`viewBox`) sobre o mesmo cenário. O 9:16 usa uma janela de 1080×1920; o 16:9 usa uma janela de proporção 16:9 (de 3414×1920 no plano aberto até janelas menores nos closes). Por ser vetorial, cada formato renderiza direto na resolução final (1080×1920 ou 1920×1080).
- **Personagens, textos e interface posicionados por formato:** no 16:9 ficam lado a lado; no 9:16, mais próximos ou empilhados. Headline, legendas e bloco de notas têm layout próprio em cada formato.
- Âncoras do cenário (piso, prateleiras, letreiro) valem para os dois formatos; registrar no comentário do SVG também os limites desenhados em x e a zona segura.

Pendente: `loja_eletronicos` foi desenhado para 1080×1920; conferir se as laterais estão preenchidas antes de usá-lo no 16:9.

## 9. Pendências (em aberto)

- [x] Nome definitivo do estilo: "palco" (luz de cena no personagem, situações encenadas, NPCs cinza como coro; vale para vídeos curtos e longos)
- [ ] Expressões em planos abertos: emoção nos closes ou olhos e sobrancelhas exagerados
- [ ] Como sinalizar quem está falando, já que não há boca
- [ ] Lista inicial de situações dos presets de olhos e sobrancelhas
- [ ] Legendas: fonte, tamanho e destaque da palavra-chave
- [ ] Ferramenta de montagem (tamanho do canvas decidido na seção 8)

## 10. Geometria de referência

Coordenadas base com o centro do personagem em x = 340, H = 116 (cabeça com raio 58).

```xml
<!-- filtro de contorno de silhueta -->
<filter id="outline" x="-15%" y="-10%" width="130%" height="120%">
  <feMorphology in="SourceAlpha" operator="dilate" radius="3.5" result="d"/>
  <feFlood flood-color="#111111"/>
  <feComposite in2="d" operator="in" result="o"/>
  <feMerge><feMergeNode in="o"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>

<!-- cabelo de trás (cabelo default) -->
<ellipse cx="340" cy="132" rx="64" ry="60" fill="HAIR"/>

<!-- braço: pivô do ombro em (279,210) à esquerda e (401,210) à direita -->
<g transform="translate(279,210) rotate(SHOULDER)">
  <rect x="-11" y="-11" width="22" height="107" rx="11" fill="SHIRT"/>
  <g transform="translate(0,85) rotate(ELBOW)">
    <rect x="-11" y="-11" width="22" height="91" rx="11" fill="SHIRT"/>
    <circle cx="0" cy="80" r="11" fill="SKIN"/>
  </g>
</g>

<!-- pernas e sapatos -->
<rect x="304" y="375" width="32" height="235" rx="5" fill="PANTS"/>
<rect x="344" y="375" width="32" height="235" rx="5" fill="PANTS"/>
<ellipse cx="318" cy="614" rx="22" ry="8" fill="SHOES"/>
<ellipse cx="362" cy="614" rx="22" ry="8" fill="SHOES"/>

<!-- tronco -->
<path d="M285 385 L285 225 Q285 192 340 192 Q395 192 395 225 L395 385 Z" fill="SHIRT"/>

<!-- cabeça -->
<circle cx="340" cy="140" r="58" fill="SKIN"/>

<!-- olho esquerdo (o direito é igual com cx = 359.7); raio 13.9, contorno 3, íris r 6.25 com contorno 2, pupila r 2.6 -->
<clipPath id="eL"><circle cx="320.3" cy="148" r="13.9"/></clipPath>
<g clip-path="url(#eL)">
  <circle cx="320.3" cy="148" r="13.9" fill="#ffffff"/>
  <circle cx="IRIS_X" cy="IRIS_Y" r="6.25" fill="IRIS" stroke="#111" stroke-width="2"/>
  <circle cx="IRIS_X" cy="IRIS_Y" r="2.6" fill="#111"/>
  <!-- pálpebras: retângulos na cor da pele + linha de borda com stroke-width 2.5 -->
</g>
<circle cx="320.3" cy="148" r="13.9" fill="none" stroke="#111" stroke-width="3"/>

<!-- sobrancelhas -->
<rect x="308" y="119" width="24" height="5" rx="2.5" fill="BROW"/>
<rect x="348" y="119" width="24" height="5" rx="2.5" fill="BROW"/>

<!-- cabelo da frente (franja default) -->
<path d="M281 136 Q282 85 340 82 Q398 85 399 136 Q381 109 340 112 Q303 110 281 136 Z" fill="HAIR"/>
```

**Cores default:** pele `#f1d6c2`, cabelo `#4a3226`, sobrancelha `#3a2a20`, camisa `#4f8a6b`, calça `#2f3a4a`, sapato `#222222`.

**Rotação:** ângulos em graus no sentido do SVG (positivo = horário). Braço esquerdo para fora = positivo; braço direito para fora = negativo.

### Presets de pose validados ([`presets/poses.json`](presets/poses.json))

| Preset | Ombro dir. | Cotovelo dir. | Ombro esq. | Cotovelo esq. |
|---|---|---|---|---|
| `neutro` | −4 | 0 | 4 | 0 |
| `explicando` | −60 | −90 | 4 | 0 |
| `acenando` | −70 | −100 | 4 | 0 |
| `pensativo` (mão no queixo, braço cruza o corpo) | 40 | 135 | 4 | 0 |
| `segurando_caneca` (braço cruza o corpo) | 10 | 150 | 4 | 0 |

### Presets de iluminação ([`presets/lighting.json`](presets/lighting.json))

| Preset | Escuridão | Poças de luz | Vinheta |
|---|---|---|---|
| `dia` | 0,1 | sol `#ffe2a6` a 0,5 no centro | 0,25 |
| `entardecer` | 0,18 | abajur `#ffcf8f` a 0,6; janela `#9dbcf0` a 0,3 | 0,35 |
