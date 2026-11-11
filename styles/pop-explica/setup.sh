#!/usr/bin/env bash
# Setup do Pop Explica (Linux, ambiente do Claude Code/Codex). Idempotente.
set -e
cd "$(dirname "$0")"
need_apt=0
command -v ffmpeg >/dev/null || need_apt=1
pkg-config --exists cairo 2>/dev/null || need_apt=1
if [ "$need_apt" = 1 ]; then
  SUDO=""; [ "$(id -u)" != 0 ] && SUDO="sudo"
  $SUDO apt-get update -qq && $SUDO apt-get install -y -qq ffmpeg libcairo2-dev pkg-config python3-dev >/dev/null
fi
PIP="pip install -q"
pip install --help 2>/dev/null | grep -q break-system-packages && PIP="$PIP --break-system-packages"
$PIP -r requirements.txt
# faster-whisper é opcional: sem ele (ou sem acesso ao modelo), o align.py usa o fallback por pausas
$PIP faster-whisper 2>/dev/null || echo "faster-whisper indisponível: align.py vai usar o fallback"
python3 -c "import cairo, PIL, numpy; print('pop-explica ok | cairo', cairo.version)"
ffmpeg -version | head -1
