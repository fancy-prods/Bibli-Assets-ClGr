# Biblioteca de assets do Claude

Assets reutilizáveis para vídeos animados gerados com o Claude, organizados por estilo, catalogados e parametrizados, para gerar o mínimo possível do zero em cada vídeo.

- **Regras de uso:** [`CLAUDE.md`](CLAUDE.md)
- **Compartilhado entre estilos:** [`shared/`](shared/) ([catálogo](shared/catalog.json)): técnica de iluminação.
- **Estilos:**
  - [`styles/curtos/`](styles/curtos/) (v1): [guia](styles/curtos/STYLE.md), [catálogo](styles/curtos/catalog.json), montador paramétrico de personagem.
  - [`styles/desenho-na-tela/`](styles/desenho-na-tela/): placeholder.
- **Arquivados:** [`archive/`](archive/)

Gerar um personagem:

```bash
python styles/curtos/tools/compose_character.py styles/curtos/params/neutro.json -o styles/curtos/renders/neutro.svg
```
