#!/usr/bin/env bash
# Crea la carpeta de un video nuevo con los enlaces al kit. Uso:  bash new_video.sh <slug>
set -e
KIT="$(cd "$(dirname "$0")" && pwd)"
V="$KIT/videos/$1"
mkdir -p "$V/audio" "$V/img/pexels" "$V/out"
cd "$V"
ln -sfn "$KIT/fonts" fonts
ln -sfn "$KIT/.env" .env
ln -sfn "$KIT/sfx" audio/sfx
ln -sfn "$KIT/sfx/music.wav" audio/music.wav
for f in render.py align.py prep_voice.py tts.py fetch_pexels.py mapa.py cover.py; do cp "$KIT/engine/$f" "$f"; done
echo "$V"
