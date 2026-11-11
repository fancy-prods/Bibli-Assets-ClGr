# Assets do Pop Explica — o que o Grok entrega

Tudo vai em `videos/<slug>/assets/`, mais o arquivo `videos/<slug>/produto.md`.
A ilustração (personagens, cenários, ícones) é desenhada em código; o Grok não precisa buscar desenhos.

## Obrigatório

| Arquivo | O quê | Requisito |
|---|---|---|
| `produto.png` | Foto oficial da embalagem principal, de frente | Fundo transparente OU fundo liso (branco/cinza/cor única). Sem banner, sem texto atrás. Mín. 800 px de altura |
| `produto.md` | Dados da página do produto | Ver modelo abaixo. Copiar o que a página diz, sem resumir alegações |

## Opcional (quando existir)

| Arquivo | O quê |
|---|---|
| `kit.png` | Foto do kit/combo completo (mesmo requisito de fundo) |
| `produto_lado.png`, `produto_aberto.png` | Outros ângulos (tampa aberta, textura, aplicador) |
| `demo.mp4` | Vídeo real de uso (vertical de preferência, 3–15 s, sem marca d'água de outro criador) |
| `selo_*.png` | Selos oficiais que aparecem na embalagem (Anvisa, testado etc.) |

Nomes fora deste padrão são aceitos, mas mencione no `produto.md`.

## Modelo de `produto.md`

```
# <Nome do produto>
Link: <url da página no TikTok Shop>
Preço: R$ xx,xx (de R$ yy,yy) | Nota: x,x | Vendidos: nn mil
Cor dominante da embalagem: <ex.: roxo>

## Alegações da página (copiar como está)
- ...

## Ingredientes / especificações
- ...

## Selos e registros visíveis na embalagem
- ...

## Observações
- (ex.: "produto.png veio com fundo cinza", "não achei foto do kit")
```
