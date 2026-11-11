# Prompts padrão

Cole no Claude Code (web) ou no Codex, trocando `<slug>`. Cada vídeo = sessão nova (contexto curto custa menos).

## 1. Roteiro
```
Leia styles/pop-explica/AGENTS.md e execute a Tarefa A para styles/pop-explica/videos/<slug>.
Rode o setup se precisar. Commit do roteiro.md no fim.
```

## 2. Vídeo (depois de revisar o roteiro e subir narracao.mp3)
```
Leia styles/pop-explica/AGENTS.md e execute a Tarefa B para styles/pop-explica/videos/<slug>.
Trabalhe sem parar para perguntar. Commit das saídas e relatório curto no fim.
```

## 3. Ajuste depois de assistir
```
Leia styles/pop-explica/AGENTS.md. No vídeo styles/pop-explica/videos/<slug>, ajuste:
- <ex.: aos 12 s o checklist cobre o produto; subir o produto>
- <ex.: destacar "neutraliza" em roxo>
Gere storyboard dos trechos alterados, renderize de novo e faça commit.
```

## Antes da Tarefa B, a pasta precisa ter
- `roteiro.md` revisado (seção `## Narração` igual ao que foi gravado)
- `narracao.mp3` (ElevenLabs)
- `assets/produto.png` + `produto.md` (Grok, ver ASSETS.md)
