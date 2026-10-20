#!/usr/bin/env bash
# Prepara el kit en una sesión nueva. Uso:  bash setup.sh "<GOOGLE_KEY>" "<PEXELS_KEY>"
set -e
KIT="$(cd "$(dirname "$0")" && pwd)"
cd "$KIT"
printf 'GOOGLE_KEY=%s\nPEXELS_KEY=%s\n' "$1" "$2" > .env; chmod 600 .env
mkdir -p fonts && cd fonts
if [ ! -d fontsource-anton ]; then
  npm pack @fontsource/anton@5.3.0 @fontsource/montserrat@5.3.0 world-atlas@2.0.2 --silent >/dev/null
  for t in *.tgz; do tar xzf "$t"; n="${t%%-[0-9]*}"; rm -rf "$n"; mv package "$n"; done
  mv fontsource-anton-* fontsource-anton 2>/dev/null || true
fi
cd "$KIT"
ls fonts
pip install --break-system-packages -q faster-whisper scipy numpy pillow 2>&1 | grep -v -i "warning" || true
SFX_DIR="$KIT/sfx" python3 engine/sfx.py
# precarga el modelo de Whisper
python3 -c "from faster_whisper import WhisperModel; WhisperModel('small', device='cpu', compute_type='int8')" 2>&1 | tail -1
echo "SETUP OK"
