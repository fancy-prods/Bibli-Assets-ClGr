# Biblioteca de assets do Claude

Assets reutilizáveis para vídeos animados gerados com o Claude, organizados por estilo, catalogados e parametrizados, para gerar o mínimo possível do zero em cada vídeo.

- **Regras de uso:** [`CLAUDE.md`](CLAUDE.md)
- **Compartilhado entre estilos:** [`shared/`](shared/) ([catálogo](shared/catalog.json)): técnica de iluminação.
- **Estilos:**
  - [`styles/palco/`](styles/palco/) (v1): [guia](styles/palco/STYLE.md), [catálogo](styles/palco/catalog.json), montador paramétrico de personagem e animação ociosa (frames SVG).
  - [`styles/desenho-na-tela/`](styles/desenho-na-tela/): placeholder.
- **Arquivados:** [`archive/`](archive/)

Gerar um personagem:

```bash
python styles/palco/tools/compose_character.py styles/palco/params/neutro.json -o styles/palco/renders/neutro.svg
```
