# Parâmetros de exemplo

JSONs de entrada do montador usados para gerar os exemplos de `../renders/`:

```bash
python tools/compose_character.py params/neutro.json -o renders/neutro.svg
```

Formato completo na docstring de `tools/compose_character.py`.

A timeline de exemplo da animação fica em `../renders/timeline-exemplo.json`; os frames de `../renders/frames/` são uma amostra (1 a cada 15) de:

```bash
python tools/animate.py renders/timeline-exemplo.json -o renders/frames/
```
