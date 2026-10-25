"""Dibujos animados hechos con código para los formatos nuevos (sin fotos de stock):
billetes, fajos, maletín, camión, Tierra, siluetas de países, barras y fondos claros.
Se importa desde scenes.py:  import viz"""
import math
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
ANTON = "fonts/fontsource-anton/files/anton-latin-400-normal.woff"
MONT = lambda w: f"fonts/fontsource-montserrat/files/montserrat-latin-{w}-normal.woff"
BILL = (200, 226, 190); BILL_D = (60, 118, 78); BILL_DD = (34, 78, 50)
INK = (30, 36, 48)

@lru_cache(maxsize=32)
def F(path, size): return ImageFont.truetype(path, size)

def ease(p): p = min(max(p, 0), 1); return p * p * (3 - 2 * p)
def eout(p): return 1 - (1 - min(max(p, 0), 1)) ** 3
def back(p):
    p = min(max(p, 0), 1); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (p - 1) ** 3 + c1 * (p - 1) ** 2

@lru_cache(maxsize=16)
def gradient(top=(214, 236, 255), bottom=(255, 250, 238)):
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return im

def bg(top=(214, 236, 255), bottom=(255, 250, 238)):
    return gradient(top, bottom).copy().convert("RGBA")

@lru_cache(maxsize=8)
def bill(w=620):
    """Billete de 100 dólares estilizado (dibujo propio, no una reproducción)."""
    h = int(w * 0.425)
    im = Image.new("RGBA", (w + 30, h + 30), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([12, 18, w + 12, h + 18], 14, fill=(0, 0, 0, 90))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], 14, fill=BILL, outline=BILL_D, width=max(3, w // 120))
    m = w // 22
    d.rounded_rectangle([m, m, w - m, h - m], 10, outline=BILL_D, width=max(2, w // 220))
    cx, cy, r = w // 2, h // 2, int(h * 0.33)
    d.ellipse([cx - r * 0.8, cy - r, cx + r * 0.8, cy + r], fill=(176, 208, 168), outline=BILL_D, width=max(2, w // 200))
    d.text((cx, cy), "$", font=F(ANTON, int(r * 1.3)), fill=BILL_D, anchor="mm")
    f = F(ANTON, int(h * 0.26))
    for (x, y, a) in [(m * 2.2, m * 1.6, "la"), (w - m * 2.2, m * 1.6, "ra"), (m * 2.2, h - m * 1.6, "ld"), (w - m * 2.2, h - m * 1.6, "rd")]:
        d.text((x, y), "100", font=f, fill=BILL_DD, anchor=a)
    d.text((cx, m * 1.9), "DÓLARES", font=F(MONT(900), int(h * 0.075)), fill=BILL_DD, anchor="ma")
    return im

@lru_cache(maxsize=8)
def bill_edge(w=420, thick=3):
    """Billete visto de canto (para apilar)."""
    im = Image.new("RGBA", (w, thick), BILL + (255,))
    ImageDraw.Draw(im).line([(0, thick - 1), (w, thick - 1)], fill=BILL_D)
    return im

def paste(fr, spr, cx, cy, scale=1.0, alpha=1.0, angle=0):
    if scale <= 0.01 or alpha <= 0.01: return
    if angle: spr = spr.rotate(angle, resample=Image.BICUBIC, expand=True)
    if abs(scale - 1) > 0.005:
        spr = spr.resize((max(1, int(spr.width * scale)), max(1, int(spr.height * scale))), Image.BILINEAR)
    if alpha < 0.999:
        spr = spr.copy(); spr.putalpha(spr.getchannel("A").point(lambda v: int(v * alpha)))
    fr.alpha_composite(spr, (int(cx - spr.width / 2), int(cy - spr.height / 2)))

def brick(d, x, y, w, h, top=True):
    """Fajo de billetes en perspectiva (bloque verde con faja)."""
    d.rectangle([x, y, x + w, y + h], fill=BILL, outline=BILL_D, width=2)
    d.rectangle([x + w * 0.42, y, x + w * 0.58, y + h], fill=(240, 220, 150), outline=BILL_D, width=1)
    if top:
        k = h * 0.35
        d.polygon([(x, y), (x + k, y - k), (x + w + k, y - k), (x + w, y)], fill=(222, 240, 214), outline=BILL_D)
        d.polygon([(x + w, y), (x + w + k, y - k), (x + w + k, y + h - k), (x + w, y + h)], fill=(150, 190, 145), outline=BILL_D)

def person(d, cx, base_y, h, color=INK):
    """Silueta humana simple para dar escala."""
    r = h * 0.11
    d.ellipse([cx - r, base_y - h, cx + r, base_y - h + 2 * r], fill=color)
    d.rounded_rectangle([cx - h * 0.16, base_y - h + 2.2 * r, cx + h * 0.16, base_y - h * 0.42], int(h * 0.06), fill=color)
    d.rectangle([cx - h * 0.13, base_y - h * 0.45, cx - h * 0.03, base_y], fill=color)
    d.rectangle([cx + h * 0.03, base_y - h * 0.45, cx + h * 0.13, base_y], fill=color)

def label(fr, text, cx, cy, size=60, fg=(255, 255, 255), bgc=INK, font=None):
    d = ImageDraw.Draw(fr); f = F(font or MONT(900), size)
    tw = d.textlength(text, font=f); pad = size * 0.45
    d.rounded_rectangle([cx - tw / 2 - pad, cy - size * 0.75, cx + tw / 2 + pad, cy + size * 0.75], int(size * 0.35), fill=bgc)
    d.text((cx, cy), text, font=f, fill=fg, anchor="mm")

def big_text(fr, text, cx, cy, size, color=(255, 224, 27), stroke=10):
    d = ImageDraw.Draw(fr)
    d.text((cx, cy), text, font=F(ANTON, size), fill=color, anchor="mm", stroke_width=stroke, stroke_fill=(0, 0, 0))

def fmt(n, dec=0):
    s = f"{n:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

# ---------------------------------------------------------------- siluetas de países
def silhouette(mapa, cid, box_w, box_h, color, outline=(255, 255, 255)):
    """Silueta del país (polígono principal y sus islas grandes) escalada para caber en box_w x box_h."""
    rings = mapa.COUNTRIES[cid]
    big = max(rings, key=lambda r: len(r))
    xs = [x for x, _ in big]; ys = [y for _, y in big]
    lat0 = (min(ys) + max(ys)) / 2
    k = math.cos(math.radians(lat0))
    keep = [r for r in rings if len(r) > len(big) * 0.08]
    allx = [x * k for r in keep for x, _ in r]; ally = [y for r in keep for _, y in r]
    x0, x1, y0, y1 = min(allx), max(allx), min(ally), max(ally)
    s = min((box_w - 20) / max(1e-6, x1 - x0), (box_h - 20) / max(1e-6, y1 - y0))
    im = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    ox = (box_w - (x1 - x0) * s) / 2; oy = (box_h - (y1 - y0) * s) / 2
    for r in keep:
        pts = [(ox + (x * k - x0) * s, oy + (y1 - y) * s) for x, y in r]
        d.polygon(pts, fill=color, outline=outline)
        d.line(pts + [pts[0]], fill=outline, width=5)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.paste((0, 0, 0, 70), (8, 12), im.getchannel("A"))
    out = sh.filter(ImageFilter.GaussianBlur(8)); out.alpha_composite(im)
    return out
