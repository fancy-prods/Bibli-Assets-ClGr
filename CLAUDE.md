# CLAUDE.md: regras de uso da biblioteca de assets

Este repositório é a biblioteca de assets reutilizáveis para vídeos animados gerados com o Claude. O objetivo é **minimizar gerações novas por vídeo**: o que pode ser reaproveitado vive aqui, catalogado e parametrizado.

## 1. Separação por estilo

- Cada estilo tem pasta própria em `/styles/<estilo>/`, com `STYLE.md` e `catalog.json` próprios.
- Em cada vídeo, consulte **apenas** o catálogo do estilo do vídeo atual, mais `/shared/catalog.json`.
- Estilos atuais: `curtos` (v1 ativo) e `desenho-na-tela` (placeholder, guia ainda não escrito).

## 2. Assets não migram entre estilos; são redesenhados

O catálogo pode registrar "conceito existe em outro estilo" (em `notes`), mas o arquivo **nunca** é copiado de um estilo para outro.

## 3. Fluxo por vídeo

1. Ler o roteiro e listar os assets necessários.
2. Cruzar a lista com o catálogo e classificar cada item como:
   - **reusar**: o asset existe e serve como está;
   - **adaptar**: parametrizar algo existente (novo valor de parâmetro, preset novo);
   - **criar**: não existe nada aproveitável.
3. Apresentar esse relatório **antes de produzir**, com a taxa de reuso: `(reusar + adaptar) / total`, em %.
4. No fim, propor quais assets criados devem entrar na biblioteca, com justificativa. **Nada entra sem aprovação do Arthur.**

Ao usar um asset, acrescente o identificador do vídeo em `used_in` da entrada no catálogo.

## 4. Critério de entrada (as três perguntas)

1. **É genérico ou específico de um livro/vídeo?** Só o genérico entra.
2. **Quanto custa gerar de novo?** Se é trivial e sai consistente, não entra.
3. **Dá para parametrizar algo existente em vez de duplicar?** Se sim, adicione o parâmetro ao asset existente.

## 5. Revisão periódica

Um asset não reusado em 15 vídeos vai para `/archive/`: sai do catálogo ativo (`status: "archived"`, `path` atualizado), mas **não é apagado**.

## 6. Binários pesados

PNG grandes e vídeos não entram no Git. Ficam no Drive, com o link registrado no catálogo (campo `path` com a URL, ou em `notes`). O `.gitignore` bloqueia as extensões mais comuns.

## 7. Esquema de cada entrada do catálogo

```json
{
  "id": "curtos.olhos",
  "name": "Módulo de olhos paramétrico",
  "style": "curtos",
  "type": "component",
  "dimension": "2d",
  "tags": ["olhos", "expressao"],
  "params": {"look_x": "-1..1"},
  "path": "styles/curtos/characters/base/olho.svg",
  "used_in": [],
  "status": "active",
  "notes": ""
}
```

| Campo | Significado |
|---|---|
| `id` | Identificador único, `<estilo>.<nome>` (ou `shared.<nome>`) |
| `name` | Nome legível |
| `style` | Pasta do estilo, ou `shared` |
| `type` | `character`, `component`, `filter`, `preset`, `tool`, `module`, `ui`, `scene`, ... |
| `dimension` | `2d`, `3d` ou `2.5d` |
| `tags` | Palavras-chave para busca |
| `params` | Parâmetros aceitos e suas faixas |
| `path` | Caminho relativo à raiz do repositório (ou link do Drive para binários) |
| `used_in` | Lista de vídeos que usaram o asset |
| `status` | `active` ou `archived` |
| `notes` | Observações livres |

## 8. Ferramentas

- Montador do personagem do estilo curtos:
  `python styles/curtos/tools/compose_character.py params.json -o styles/curtos/renders/nome.svg`
- Animação (idle + roteiro por canais) do estilo curtos, um SVG por frame:
  `python styles/curtos/tools/animate.py timeline.json -o styles/curtos/renders/frames/`
  Não versione sequências completas de frames: mantenha no máximo 1 a cada 15 como amostra.
- Antes de commitar: todo SVG gerado deve fazer parse com `xml.etree.ElementTree`, todo `catalog.json` deve fazer parse e cada `path` local deve existir.
