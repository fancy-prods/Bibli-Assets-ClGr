# Toyadent Ultravioleta — roteiro (v2)

**Ângulo:** dor primeiro, depois a quebra de expectativa. A pessoa escova e o dente continua amarelado; a resposta
esperada seria um produto ou um hábito, e o vídeo responde com uma **cor**: "é falta de... roxo?". O shampoo
matizador (roxo tira o amarelado do loiro) vira a explicação do mecanismo. Do vídeo de referência fica só a
lógica do efeito óptico (roxo neutraliza o amarelo, sem agente clareador); o hook e a cena são outros.

## Blocos

Tempos estimados a ~2,8 palavras/s; os reais saem do `words.json`.

| Bloco | Trecho da narração | O que aparece | Tema |
|---|---|---|---|
| Hook: dor (0–3 s) | "Você escova todo dia e o dente continua amarelado?" | Dente-personagem amarelado, olhos cansados, gotinha de suor; uma escova esfrega rápido de um lado para o outro. Pílula "AMARELADO" treme | `red` |
| Hook: quebra (3–6 s) | "Não é falta de escovar. É falta de... roxo?" | Em "escovar", a escova recebe um X e sai. Em "falta de...", uma **roleta de caça-níquel** gira com as respostas que a pessoa espera: "ESCOVA NOVA", "BICARBONATO", "CARVÃO", "CLAREAMENTO". Na pausa ela desacelera… e para numa janela **só de tinta roxa**, sem palavra. Em "roxo?", respingo roxo cobre a roleta, o dente arregala os olhos (surpresa) e os raios do fundo param por um instante | `red` → respingo roxo |
| Mecanismo (6–15 s) | "Sabe o shampoo roxo… aparece o branco." | Personagem loira; frasco roxo genérico (sem marca) passa pelo cabelo e os fios amarelados ficam platinados. Depois, cartão branco com círculo cromático: bolinhas amarela e roxa em lados opostos se sobrepõem e no meio nasce o branco. Pílulas "AMARELO", "ROXO", "BRANCO". O dente ganha película roxa e fica branco, sorrindo com os olhos | `blue` |
| Virada + produto (15–22 s) | "Essa é a Toyadent Ultravioleta… nano-hidroxiapatita." | Íris para roxo na palavra **Toyadent**. `produto.png` entra com pop, brilho e sparkles. Pílulas em sequência: "0 AGENTE CLAREADOR", "SEM SULFATO", "FLÚOR + NANO-HIDROXIAPATITA" | `purple` |
| Demonstração ilustrada (22–25 s) | "Você escova normal, e a espuma muda de roxo pra azul." | A mesma escova do hook volta, agora com espuma roxa; as bolhas mudam de roxo para azul. Produto visível no canto | `purple` |
| Prova (25–31 s) | "Testada clinicamente… uns noventa dias." | Checklist branco: "TESTADO CLINICAMENTE", "+256 MIL VENDIDOS · NOTA 4,4", "90 G ≈ 90 DIAS". Produto flutuando ao lado | `purple` |
| CTA (31–36 s) | "Toca no carrinho… no seu sorriso." | TV retrô (ilustrada) passando `demo.mp4` (trecho 8–12 s: tampa aberta, pasta azul) ao lado do produto; botão "TOCA NO CARRINHO" pulsando com seta | `purple` |

Destaques de legenda (`HIGHLIGHT`): "amarelado"/"amarelo" → yellow, "escovar" → red, "roxo" → roxo
(acrescentar ao motor; hoje o mais próximo é pink), "branco" → blue, "azul" → blue, "carrinho" → yellow.

{{ "roxo?" é a palavra que segura o vídeo: pausa audível antes dela e entonação de pergunta. Se o ElevenLabs
   não fizer a pausa com as reticências, testar `[pause]` antes de "roxo". }}
{{ A roleta mostra só o que a pessoa espera ouvir; nenhuma afirmação sobre bicarbonato, carvão ou clareamento. }}
{{ O respingo roxo no hook não é a troca de tema da virada: o fundo volta ao `red` → íris para `blue` no
   mecanismo. A troca para o roxo da embalagem continua na palavra "Toyadent". }}
{{ A escova do hook e a da demonstração são a mesma: a primeira "não resolve", a segunda volta com a espuma roxa. }}
{{ Componentes a criar: roleta (`slot_reel`), círculo cromático, TV (`tv_frame`). Os três são genéricos e
   podem ir para o motor. }}

## Narração

Você escova todo dia e o dente continua amarelado? Não é falta de escovar. É falta de... roxo?

Sabe o shampoo roxo que tira o amarelado do cabelo loiro? Pois é. No círculo das cores, o roxo fica do lado oposto do amarelo. Quando os dois se encontram, o tom amarelo é neutralizado e aparece o branco.

Essa é a Toyadent Ultravioleta. Zero agente clareador, sem sulfato, com flúor e nano-hidroxiapatita.

Você escova normal, e a espuma muda de roxo pra azul.

Testada clinicamente, mais de duzentas e cinquenta mil vendidas, e um tubo dura uns noventa dias.

Toca no carrinho e testa o truque do roxo no seu sorriso.

## Alegações usadas (todas em `produto.md`)

| Fala | Fonte |
|---|---|
| roxo neutraliza o amarelo, cores opostas no círculo | arte 11 ("o roxo pode neutralizar o amarelo"); embalagem "amarelo + roxo = branco" |
| zero agente clareador | "0 de agentes clareadores"; STYLE §10 ("sem agente clareador" + efeito óptico) |
| sem sulfato, flúor, nano-hidroxiapatita | embalagem e anúncio |
| espuma muda de roxo pra azul | arte 10 |
| testada clinicamente | tubo: "testado e aprovado clinicamente" |
| +250 mil vendidas | print do Arthur (256,6 mil, 11/11/2026); conferir antes de publicar |
| tubo dura uns noventa dias | arte 08 ("90 g, suficiente para 90 dias de uso") |

Fora de propósito: nada de "clareia em X dias", "dissolve manchas", "em 1 segundo", antes/depois de pessoa.
O hook descreve a dor ("continua amarelado"); não promete que o dente vai ficar branco.
O shampoo é citado como categoria ("shampoo roxo"), sem marca.

## Hooks alternativos

1. "Sabe o shampoo roxo que tira o amarelado do cabelo loiro? Fizeram a mesma coisa pra dente." (v1: curiosidade/analogia; corta o "Pois é")
2. "Você sorri na foto, dá zoom e apaga. Por causa da cor do dente." (vergonha; segue com "Sabe o shampoo roxo...")
