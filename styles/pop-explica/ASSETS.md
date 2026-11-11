# Assets do Pop Explica — o que o Grok entrega

Tudo vai em `videos/<slug>/assets/`, mais o arquivo `videos/<slug>/produto.md`.

**Origem no Drive:** o Grok deixa o material de cada produto em uma subpasta de
https://drive.google.com/drive/u/2/folders/1W2me8e97X9BJGQFehNAQV8-Xlst1i7aR
(`<Produto>/imagens/`, `<Produto>/videos/`, `sources.txt`). Os nomes vêm numerados
(ex.: `02_packshot_tubo_caixa_fundo_transparente.png`): escolher os arquivos e copiar para `assets/`
com os nomes abaixo. Binários não entram no Git além do que o AGENTS.md manda commitar.
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
