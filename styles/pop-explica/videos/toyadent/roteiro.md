# Toyadent Ultravioleta — roteiro

**Ângulo:** o "truque do matizador". Todo mundo conhece o shampoo roxo que tira o amarelado do cabelo loiro;
a pasta usa o mesmo princípio de cor no dente. O hook é curiosidade e analogia, não "olhar dos outros".
Assim o vídeo se afasta do de referência e mantém só a lógica do mecanismo (efeito óptico, sem agente clareador).

## Blocos

Tempos estimados a ~2,8 palavras/s; os reais saem do `words.json`.

| Bloco | Trecho da narração | O que aparece | Tema |
|---|---|---|---|
| Hook (0–4 s) | "Sabe o shampoo roxo… Fizeram a mesma coisa pra dente." | Personagem loira; frasco roxo genérico (sem marca) passa pelo cabelo e os fios amarelados ficam platinados. Em "dente", um dente-personagem amarelado entra com pop, desconfiado | `orange` |
| Mecanismo (4–13 s) | "Funciona assim… É óptica, não é química." | Cartão branco com círculo cromático: bolinha amarela e bolinha roxa em lados opostos, deslizam e se sobrepõem; no meio nasce o branco. Pílulas "AMARELO", "ROXO", "BRANCO". Dente amarelo ganha película roxa e fica branco, sorrindo com os olhos | `blue` |
| Virada + produto (13–21 s) | "Essa é a Toyadent Ultravioleta… nano-hidroxiapatita." | Íris para roxo na palavra **Toyadent**. `produto.png` entra com pop, brilho e sparkles. Pílulas em sequência: "0 AGENTE CLAREADOR", "SEM SULFATO", "FLÚOR + NANO-HIDROXIAPATITA" | `purple` |
| Demonstração ilustrada (21–27 s) | "Você escova normal… o cheiro é de maracujá." | Escova com espuma roxa sobre o dente; bolhas mudam de roxo para azul. Pílula com ícone de maracujá. Produto continua visível no canto | `purple` |
| Prova (27–33 s) | "Testada clinicamente… uns noventa dias." | Checklist branco: "TESTADO CLINICAMENTE", "+256 MIL VENDIDOS · NOTA 4,4", "90 G ≈ 90 DIAS". Produto flutuando ao lado | `purple` |
| CTA (33–39 s) | "Toca no carrinho… no seu sorriso." | TV retrô (ilustrada) passando `demo.mp4` (trecho 8–12 s: tampa aberta, pasta azul) ao lado do produto; botão "TOCA NO CARRINHO" pulsando com seta | `purple` |

Destaques de legenda (`HIGHLIGHT`): "roxo" → pink (o motor não tem roxo), "amarelado"/"amarelo" → yellow,
"branco" → branco com contorno (sem destaque) ou blue, "azul" → blue, "maracujá" → orange, "carrinho" → yellow.

{{ A TV não existe no motor: desenhar em `video.py`; se ficar boa, propor como componente `tv_frame`. }}
{{ Círculo cromático está na lista de "faltam" da STYLE.md §9: criar como componente genérico. }}
{{ O frasco do hook é genérico, sem marca nem texto (não é anúncio de outro produto). }}

## Narração

Sabe o shampoo roxo que tira o amarelado do cabelo loiro? Fizeram a mesma coisa pra dente.

Funciona assim: no círculo das cores, o roxo fica do lado oposto do amarelo. Quando os dois se encontram, o tom amarelo é neutralizado e o que aparece é o branco. É óptica, não é química.

Essa é a Toyadent Ultravioleta. Zero agente clareador, sem sulfato, com flúor e nano-hidroxiapatita.

Você escova normal, e a espuma muda de roxo pra azul. E o cheiro é de maracujá.

Testada clinicamente, mais de duzentas e cinquenta mil vendidas, e um tubo dura uns noventa dias.

Toca no carrinho e testa o truque do roxo no seu sorriso.

## Alegações usadas (todas em `produto.md`)

| Fala | Fonte |
|---|---|
| roxo neutraliza o amarelo, cores opostas no círculo | arte 11 ("o roxo pode neutralizar o amarelo"); embalagem "amarelo + roxo = branco" |
| "É óptica, não é química" / zero agente clareador | "0 de agentes clareadores"; STYLE §10 ("sem agente clareador" + efeito óptico) |
| sem sulfato, flúor, nano-hidroxiapatita | embalagem e anúncio |
| espuma muda de roxo pra azul | arte 10 |
| cheiro de maracujá | arte 09 (nota principal maracujá) |
| testada clinicamente | tubo: "testado e aprovado clinicamente" |
| +250 mil vendidas | print do Arthur (256,6 mil, 11/11/2026); conferir antes de publicar |
| tubo dura uns noventa dias | arte 08 ("90 g, suficiente para 90 dias de uso") |

Fora de propósito: nada de "clareia em X dias", "dissolve manchas", "em 1 segundo", antes/depois de pessoa.
O shampoo do hook é citado como categoria ("shampoo roxo"), sem marca.

## Hooks alternativos

1. "Seu dente não precisa de clareamento. Precisa de um pouco de roxo." (paradoxo; segue igual a partir de "Funciona assim")
2. "Quem é loira já conhece esse truque. Agora ele chegou na pasta de dente." (identificação; troca a 1ª frase)
