"""Hojas de contacto para revisar a ojo.
  python3 ENGINE/sheets.py photos            -> img/sheet0.jpg, img/sheet1.jpg ... (todas las fotos descargadas)
  python3 ENGINE/sheets.py preview           -> out/sheet_prev0.jpg ... (de out/prev_*.jpg)
  python3 ENGINE/sheets.py final t1 t2 ...   -> out/sheet_final.jpg (fotogramas del video final) + volumen LUFS
"""
import glob, subprocess, sys
from PIL import Image, ImageDraw

mode = sys.argv[1]
if mode == "photos":
    files = sorted(glob.glob("img/pexels/*.jpg")); tw, th, cols = 160, 240, 12
    for part in range(0, (len(files) + 47) // 48):
        sub = files[part * 48:(part + 1) * 48]; r = (len(sub) + cols - 1) // cols
        s = Image.new("RGB", (cols * tw, r * (th + 18)), "white"); d = ImageDraw.Draw(s)
        for i, f in enumerate(sub):
            im = Image.open(f).convert("RGB"); im.thumbnail((tw, th)); x = (i % cols) * tw; y = (i // cols) * (th + 18)
            s.paste(im, (x, y)); d.text((x + 2, y + th + 2), f.split("/")[-1][:-4], fill="black")
        s.save(f"img/sheet{part}.jpg", quality=80); print(f"img/sheet{part}.jpg")
elif mode == "preview":
    fs = sorted(glob.glob("out/prev_*.jpg"))
    for part in range(0, (len(fs) + 11) // 12):
        sub = fs[part * 12:(part + 1) * 12]
        s = Image.new("RGB", (6 * 300, 2 * 545), "white"); d = ImageDraw.Draw(s)
        for i, f in enumerate(sub):
            x = (i % 6) * 300; y = (i // 6) * 545
            s.paste(Image.open(f).resize((300, 533)), (x, y)); d.text((x + 4, y + 535), f[9:-4], fill="black")
        s.save(f"out/sheet_prev{part}.jpg", quality=85); print(f"out/sheet_prev{part}.jpg")
elif mode == "final":
    ts = sys.argv[2:]
    s = Image.new("RGB", (270 * 6, 480 * ((len(ts) + 5) // 6)))
    for i, t in enumerate(ts):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", t, "-i", "out/video.mp4", "-frames:v", "1",
                        "-vf", "scale=270:480", f"out/chk_{i}.jpg"], check=True)
        s.paste(Image.open(f"out/chk_{i}.jpg"), ((i % 6) * 270, (i // 6) * 480))
    s.save("out/sheet_final.jpg"); print("out/sheet_final.jpg")
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", "out/video.mp4", "-af", "ebur128=framelog=quiet", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    print([l.strip() for l in r.splitlines() if l.strip().startswith("I:")][-1:])
    print(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "out/video.mp4"],
                         capture_output=True, text=True).stdout.strip(), "s")
