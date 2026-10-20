"""Crea out/publicar.mp4: la portada como primeros 3 fotogramas (0,1 s) + el video.
TikTok (cuenta personal) no deja elegir portada por API y usa el primer fotograma;
así la cuadrícula del perfil muestra la portada. Uso (en la carpeta del video):
    python3 ~/mdd/kit/engine/finalize.py
"""
import subprocess

subprocess.run([
    "ffmpeg", "-y", "-loglevel", "error",
    "-loop", "1", "-framerate", "30", "-t", "0.1", "-i", "out/portada.png",
    "-f", "lavfi", "-t", "0.1", "-i", "anullsrc=r=44100:cl=stereo",
    "-i", "out/video.mp4",
    "-filter_complex",
    "[0:v]scale=1080:1920,format=yuv420p,setsar=1,fps=30[c];[2:v]format=yuv420p,setsar=1,fps=30[v];"
    "[c][1:a][v][2:a]concat=n=2:v=1:a=1[outv][outa]",
    "-map", "[outv]", "-map", "[outa]",
    "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "out/publicar.mp4",
], check=True)
d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size", "-of", "csv=p=0",
                    "out/publicar.mp4"], capture_output=True, text=True).stdout.strip()
print("publicar.mp4", d)
