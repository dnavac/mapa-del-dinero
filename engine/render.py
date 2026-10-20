"""Monta el video vertical 1080x1920: fotos con Ken Burns, mapas animados, textos, iconos,
subtítulos palabra por palabra, efectos de sonido y música."""
import json, math, os, re, subprocess, sys, unicodedata
from functools import lru_cache
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import mapa

W, H, FPS = 1080, 1920, 30
ANTON = "fonts/fontsource-anton/files/anton-latin-400-normal.woff"
MONT = lambda w: f"fonts/fontsource-montserrat/files/montserrat-latin-{w}-normal.woff"
YEL = (255, 224, 27); RED = (229, 57, 53); WHITE = (255, 255, 255); BLACK = (0, 0, 0)
GREEN = (46, 204, 113); BLUE = (66, 133, 244)

A = json.load(open("audio/aligned.json"))

def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in w if unicodedata.category(c) != "Mn"))

def tw(line, sub=None, nth=0):
    ws = [a for a in A if a["line"] == line]
    if sub is None:
        return ws[0]["s"]
    m = [a for a in ws if norm(sub) in norm(a["w"])]
    return m[nth]["s"]

VOICE_END = A[-1]["e"]
DUR = VOICE_END + 1.6

def exists(p): return os.path.exists(p)
P = lambda n: f"img/pexels/{n}.jpg"

# ---------------------------------------------------------------- escenas (fondos)
CUTS = []   # (t, bg)
OV = []     # overlays
SFX = []    # (t, name, gain)

def cut(t, bg, sfx="whoosh", gain=0.7):
    CUTS.append((t, bg))
    if sfx: SFX.append((max(0, t - 0.12), sfx, gain))

def ov(t, kind, **kw):
    kw.update(kind=kind, t=t); OV.append(kw)

def sfx(t, name, gain=1.0): SFX.append((t, name, gain))

def photo(path, z0=1.0, z1=1.12, p0=(0.5, 0.5), p1=(0.5, 0.5), blur=0, dim=0.0, fit=False):
    return dict(type="photo", path=path, z0=z0, z1=z1, p0=p0, p1=p1, blur=blur, dim=dim, fit=fit)

def mapbg(cam0, cam1, colors=None, timed_colors=None):
    return dict(type="map", cam0=cam0, cam1=cam1, colors=colors or {}, timed=timed_colors or [])

exec(open(os.environ.get("SCENES", "scenes.py"), encoding="utf-8").read())

CUTS.sort(key=lambda c: c[0])
CUT_T = [c[0] for c in CUTS]

def scene_at(T):
    i = max(k for k, t in enumerate(CUT_T) if t <= T + 1e-6)
    t0 = CUT_T[i]; t1 = CUT_T[i + 1] if i + 1 < len(CUT_T) else DUR
    return i, t0, t1

for o in OV:
    if "until" not in o:
        nxt = [t for t in CUT_T if t > o["t"] + 0.05]
        o["until"] = nxt[0] if nxt else DUR

# ---------------------------------------------------------------- utilidades de dibujo
def ease_out(p): return 1 - (1 - min(max(p, 0), 1)) ** 3
def ease_io(p): p = min(max(p, 0), 1); return p * p * (3 - 2 * p)
def back(p):
    p = min(max(p, 0), 1); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (p - 1) ** 3 + c1 * (p - 1) ** 2

@lru_cache(maxsize=64)
def font(path, size): return ImageFont.truetype(path, size)

@lru_cache(maxsize=256)
def text_sprite(text, size, color, box=None, fontp=ANTON, stroke=10, pad=(36, 14)):
    """Bloque de texto (varias líneas con '|'), con contorno y sombra; opcionalmente sobre caja de color."""
    f = font(fontp, size)
    lines = text.split("|")
    asc, desc = f.getmetrics()
    lh = int((asc + desc) * 1.0)
    widths = [int(f.getlength(l)) for l in lines]
    w = max(widths) + 2 * pad[0] + 40; h = lh * len(lines) + 2 * pad[1] + 40
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if box:
        sh = Image.new("RGBA", (w, h), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
        sd.rounded_rectangle([20 + 6, 20 + 10, w - 20 + 6, h - 20 + 10], radius=22, fill=(0, 0, 0, 110))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
        d.rounded_rectangle([20, 20, w - 20, h - 20], radius=22, fill=box + (255,))
        stroke_fill, sw = None, 0
    else:
        stroke_fill, sw = BLACK, stroke
        sh = Image.new("RGBA", (w, h), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
        y = 20 + pad[1]
        for l in lines:
            sd.text((w / 2 + 6, y + 8), l, font=f, fill=(0, 0, 0, 160), anchor="ma", stroke_width=sw, stroke_fill=(0, 0, 0, 160))
            y += lh
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    y = 20 + pad[1]
    for l in lines:
        d.text((w / 2, y), l, font=f, fill=color, anchor="ma", stroke_width=sw, stroke_fill=stroke_fill)
        y += lh
    return im

def paste_center(frame, spr, cx, cy, scale=1.0, alpha=1.0, angle=0):
    if scale <= 0.01 or alpha <= 0.01: return
    if angle: spr = spr.rotate(angle, resample=Image.BICUBIC, expand=True)
    if abs(scale - 1) > 0.005:
        spr = spr.resize((max(1, int(spr.width * scale)), max(1, int(spr.height * scale))), Image.BILINEAR)
    if alpha < 0.999:
        spr = spr.copy(); spr.putalpha(spr.getchannel("A").point(lambda v: int(v * alpha)))
    frame.alpha_composite(spr, (int(cx - spr.width / 2), int(cy - spr.height / 2)))

# ---------------------------------------------------------------- fondos
@lru_cache(maxsize=6)
def load_photo(path, blur, dim):
    im = Image.open(path).convert("RGB")
    # cubrir 1080x1920 con margen para zoom 1.25
    s = max(W * 1.25 / im.width, H * 1.25 / im.height)
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(1.15)
    im = ImageEnhance.Contrast(im).enhance(1.06)
    im = ImageEnhance.Brightness(im).enhance(1.05)
    if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
    if dim: im = Image.blend(im, Image.new("RGB", im.size, (0, 0, 0)), dim)
    return im

@lru_cache(maxsize=4)
def load_fit(path):
    src = Image.open(path).convert("RGB")
    src = ImageEnhance.Color(src).enhance(1.15); src = ImageEnhance.Brightness(src).enhance(1.08)
    s = max(W / src.width, H / src.height)
    back_ = src.resize((int(src.width * s) + 2, int(src.height * s) + 2), Image.BILINEAR).crop((0, 0, W, H)).filter(ImageFilter.GaussianBlur(30))
    fg = src.resize((W, int(src.height * W / src.width)), Image.LANCZOS)
    return back_, fg

def render_photo(bg, p, punch):
    if bg.get("fit"):
        back_, fg = load_fit(bg["path"])
        z = (bg["z0"] + (bg["z1"] - bg["z0"]) * ease_io(p)) * punch
        fr = back_.copy()
        f2 = fg.resize((int(fg.width * z), int(fg.height * z)), Image.BILINEAR)
        fr.paste(f2, (int(W / 2 - f2.width / 2), int(820 - f2.height / 2)))
        return fr
    im = load_photo(bg["path"], bg["blur"], bg["dim"])
    z = bg["z0"] + (bg["z1"] - bg["z0"]) * ease_io(p)
    z *= punch
    # tamaño de recorte en la imagen grande (zoom 1 = cubrir exacto)
    base = min(im.width / W, im.height / H)
    cw, chh = W * base / z, H * base / z
    px = bg["p0"][0] + (bg["p1"][0] - bg["p0"][0]) * ease_io(p)
    py = bg["p0"][1] + (bg["p1"][1] - bg["p0"][1]) * ease_io(p)
    cx = cw / 2 + (im.width - cw) * px; cy = chh / 2 + (im.height - chh) * py
    box = (cx - cw / 2, cy - chh / 2, cx + cw / 2, cy + chh / 2)
    return im.resize((W, H), Image.BILINEAR, box=box)

def cam_at(bg, p):
    e = ease_io(p)
    return tuple(bg["cam0"][i] + (bg["cam1"][i] - bg["cam0"][i]) * e for i in range(3))

def render_map(bg, p, T, punch):
    lon, lat, k = cam_at(bg, p)
    colors = dict(bg["colors"])
    for tt, cols in bg["timed"]:
        if T >= tt: colors.update(cols)
    im = mapa.draw_map(W, H, (lon, lat, k * punch), colors, ss=2)
    return im

def geo_xy(T, geo):
    i, t0, t1 = scene_at(T)
    bg = CUTS[i][1]
    if bg["type"] != "map": return None
    p = (T - t0) / max(0.01, t1 - t0)
    return mapa.project(geo[0], geo[1], cam_at(bg, p), W, H)

# ---------------------------------------------------------------- overlays
def draw_overlay(fr, o, T):
    dt = T - o["t"]; k = o["kind"]
    if dt < 0 or T > o["until"]: return
    d = ImageDraw.Draw(fr)
    if k in ("title", "big"):
        size = o.get("size", 112 if k == "title" else 210)
        spr = text_sprite(o["text"], size, o["color"], o.get("box"))
        s = back(dt / 0.28) if dt < 0.28 else 1.0
        paste_center(fr, spr, W / 2, o["y"] + spr.height / 2 - 20, scale=s)
    elif k == "tag":
        spr = text_sprite(o["text"], 64, o["color"], o.get("bg", (0, 0, 0)), fontp=MONT(900), pad=(30, 10))
        x = W / 2 + (1 - ease_out(dt / 0.3)) * -700
        paste_center(fr, spr, x, o["y"])
    elif k == "chip":
        spr = text_sprite(o["text"], 52, BLACK, YEL, fontp=MONT(900), pad=(24, 8))
        s = back(dt / 0.25) if dt < 0.25 else 1
        paste_center(fr, spr, o["x"], o["y"], scale=s)
    elif k == "label":
        xy = geo_xy(T, o["geo"])
        if xy is None: return
        spr = text_sprite(o["text"], 70, WHITE, o["color"], fontp=MONT(900), pad=(26, 8))
        s = back(dt / 0.25) if dt < 0.25 else 1
        paste_center(fr, spr, xy[0], xy[1] - 120, scale=s)
        d.polygon([(xy[0] - 18, xy[1] - 86), (xy[0] + 18, xy[1] - 86), (xy[0], xy[1] - 58)], fill=o["color"])
    elif k == "xmark":
        p = ease_out(dt / 0.25); cx, cy, r = W / 2, 820, 260
        for (x0, y0, x1, y1), dl in [((-1, -1, 1, 1), 0), ((1, -1, -1, 1), 0.12)]:
            q = ease_out((dt - dl) / 0.2)
            if q <= 0: continue
            a = (cx + x0 * r, cy + y0 * r); b = (cx + x0 * r + (x1 - x0) * r * q, cy + y0 * r + (y1 - y0) * r * q)
            d.line([a, b], fill=BLACK, width=74); d.line([a, b], fill=RED, width=56)
    elif k == "ban":
        s = back(dt / 0.3) if dt < 0.3 else 1; r = 250 * s; cx, cy = W / 2, o["y"]
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=RED, width=int(46 * s))
        a = r * 0.7071
        d.line([(cx - a, cy - a), (cx + a, cy + a)], fill=RED, width=int(46 * s))
    elif k == "pie":
        p = ease_out(dt / 0.9); cx, cy, r = W / 2, o["y"], 230
        s = back(dt / 0.25) if dt < 0.25 else 1; r *= s
        d.ellipse([cx - r - 10, cy - r - 10, cx + r + 10, cy + r + 10], fill=WHITE)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(200, 210, 220))
        d.pieslice([cx - r, cy - r, cx + r, cy + r], -90, -90 + 360 * o["frac"] * p, fill=(52, 152, 219))
        spr = text_sprite(o["label"], int(150 * s) or 1, WHITE)
        paste_center(fr, spr, cx, cy + 6)
    elif k == "counter":
        p = ease_out(dt / o["dur"]); v = int(round(o["a"] + (o["b"] - o["a"]) * p))
        spr = text_sprite(o.get("pre", "") + (f"{v:,}".replace(",", ".") if o.get("thousands") else str(v)) + o.get("suf", ""), o.get("size", 230), o.get("color", YEL))
        s = 1 + 0.12 * math.exp(-max(0, dt - o["dur"]) * 10) if dt >= o["dur"] else 1
        paste_center(fr, spr, W / 2, o["y"] + 110, scale=s)
    elif k == "stamp":
        spr = text_sprite(o["text"], 150, o["color"], None, stroke=0, pad=(40, 14))
        # marco de sello
        fw, fh = spr.size
        frame_spr = Image.new("RGBA", (fw + 40, fh + 20), (0, 0, 0, 0)); fd = ImageDraw.Draw(frame_spr)
        fd.rounded_rectangle([14, 14, fw + 26, fh + 6], radius=18, outline=o["color"] + (255,), width=16, fill=(255, 255, 255, 215))
        frame_spr.alpha_composite(spr, (20, 4))
        s = 2.4 - 1.4 * ease_out(dt / 0.15) if dt < 0.15 else 1.0
        paste_center(fr, frame_spr, W / 2, o["y"], scale=s, angle=o.get("angle", -12), alpha=min(1, dt / 0.06 + 0.2))
    elif k == "arrow":
        a = mapa.project(*o["a"], cam_at(CUTS[scene_at(T)[0]][1], (T - scene_at(T)[1]) / max(.01, scene_at(T)[2] - scene_at(T)[1])), W, H)
        b = geo_xy(T, o["b"])
        if b is None: return
        p = ease_io(dt / o["dur"])
        mx, my = (a[0] + b[0]) / 2, min(a[1], b[1]) + o.get("bend", -200)
        pts = []
        for i in range(41):
            u = i / 40 * p
            pts.append(((1 - u) ** 2 * a[0] + 2 * (1 - u) * u * mx + u * u * b[0], (1 - u) ** 2 * a[1] + 2 * (1 - u) * u * my + u * u * b[1]))
        d.line(pts, fill=BLACK, width=34, joint="curve"); d.line(pts, fill=YEL, width=22, joint="curve")
        if len(pts) > 2:
            (x1, y1), (x2, y2) = pts[-3], pts[-1]
            ang = math.atan2(y2 - y1, x2 - x1); L = 60
            tri = [(x2 + 20 * math.cos(ang), y2 + 20 * math.sin(ang)),
                   (x2 - L * math.cos(ang - .55), y2 - L * math.sin(ang - .55)),
                   (x2 - L * math.cos(ang + .55), y2 - L * math.sin(ang + .55))]
            d.polygon(tri, fill=YEL, outline=BLACK, width=5)
    elif k == "pin":
        xy = geo_xy(T, o["geo"])
        if xy is None: return
        p = ease_out(dt / 0.3); x, y = xy[0], xy[1] - (1 - p) * 300
        d.ellipse([x - 34, y - 110, x + 34, y - 42], fill=RED, outline=WHITE, width=6)
        d.polygon([(x - 26, y - 62), (x + 26, y - 62), (x, y)], fill=RED)
        d.ellipse([x - 12, y - 88, x + 12, y - 64], fill=WHITE)
        spr = text_sprite(o["text"], 60, BLACK, YEL, fontp=MONT(900), pad=(20, 6))
        paste_center(fr, spr, x, y + 60, alpha=p)
    elif k == "lock":
        s = back(dt / 0.3) if dt < 0.3 else 1; cx, cy = W / 2, o["y"]
        sh = 1 - ease_out((dt - 0.2) / 0.2) if o["mode"] == "close" else 0
        bw, bh = 260 * s, 200 * s
        d.arc([cx - bw * .34, cy - bh * 1.05 - sh * 50, cx + bw * .34, cy - bh * .05 - sh * 50], 180, 360, fill=(220, 220, 225), width=int(34 * s))
        d.line([(cx - bw * .34 + 17 * s, cy - bh * .55 - sh * 50), (cx - bw * .34 + 17 * s, cy - bh * .1)], fill=(220, 220, 225), width=int(34 * s))
        d.line([(cx + bw * .34 - 17 * s, cy - bh * .55 - sh * 50), (cx + bw * .34 - 17 * s, cy - bh * .1)], fill=(220, 220, 225), width=int(34 * s))
        d.rounded_rectangle([cx - bw / 2, cy - bh * .2, cx + bw / 2, cy + bh * .8], radius=int(30 * s), fill=YEL, outline=BLACK, width=8)
        d.ellipse([cx - 22 * s, cy + bh * .15, cx + 22 * s, cy + bh * .15 + 44 * s], fill=BLACK)
        d.rectangle([cx - 9 * s, cy + bh * .3, cx + 9 * s, cy + bh * .55], fill=BLACK)
    elif k == "crack":
        rng = np.random.default_rng(3); cx, cy = W / 2, o["y"]
        p = ease_out(dt / 0.2)
        for j in range(11):
            ang = j / 11 * 2 * math.pi + rng.uniform(-.2, .2); x, y = cx, cy; pts = [(x, y)]
            for s_ in range(6):
                L = rng.uniform(40, 110) * p; ang += rng.uniform(-.5, .5)
                x += L * math.cos(ang); y += L * math.sin(ang); pts.append((x, y))
            d.line(pts, fill=BLACK, width=12); d.line(pts, fill=WHITE, width=6)
    elif k == "people":
        cx, cy = W / 2, o["y"]
        for j in range(3):
            x = cx + (j - 1) * 230
            on = j < 2 and dt > 0.25 + j * 0.35
            col = YEL if on else (235, 235, 235)
            sc = 1 + (0.15 * math.exp(-(dt - (0.25 + j * 0.35)) * 8) if on else 0)
            r = 58 * sc
            d.ellipse([x - r, cy - 150 * sc - r, x + r, cy - 150 * sc + r], fill=col, outline=BLACK, width=8)
            d.rounded_rectangle([x - 90 * sc, cy - 70 * sc, x + 90 * sc, cy + 120 * sc], radius=int(70 * sc), fill=col, outline=BLACK, width=8)
    elif k == "comment":
        s = back(dt / 0.3) if dt < 0.3 else 1; cx, cy = W / 2, o["y"]
        bw, bh = 640 * s, 200 * s
        d.rounded_rectangle([cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2], radius=int(50 * s), fill=WHITE, outline=BLACK, width=8)
        d.polygon([(cx - bw * .25, cy + bh / 2 - 4), (cx - bw * .32, cy + bh / 2 + 70 * s), (cx - bw * .1, cy + bh / 2 - 4)], fill=WHITE, outline=BLACK)
        d.line([(cx - bw * .25 + 4, cy + bh / 2 - 4), (cx - bw * .1 - 4, cy + bh / 2 - 4)], fill=WHITE, width=12)
        # texto que se escribe
        full = o.get("txt", "Noruega, Dubái...")
        n = int(min(len(full), max(0, dt - 0.3) * 14))
        f = font(MONT(800), int(50 * s) or 1)
        d.text((cx, cy), full[:n] + ("|" if int(dt * 3) % 2 == 0 else ""), font=f, fill=(40, 40, 40), anchor="mm")
    elif k == "ring":
        xy = geo_xy(T, o["geo"])
        if xy is None: return
        for j in range(2):
            q = ((dt + j * 0.6) % 1.2) / 1.2
            r = 26 + 150 * q
            d.ellipse([xy[0] - r, xy[1] - r, xy[0] + r, xy[1] + r], outline=RED, width=max(2, int(12 * (1 - q))))
        d.ellipse([xy[0] - 15, xy[1] - 15, xy[0] + 15, xy[1] + 15], fill=RED, outline=WHITE, width=5)
    elif k == "follow":
        pul = 1 + 0.06 * math.sin(dt * 9)
        s = (back(dt / 0.3) if dt < 0.3 else 1) * pul
        spr = text_sprite("+ SÍGUEME", 80, WHITE, (254, 44, 85), fontp=MONT(900), pad=(46, 16))
        paste_center(fr, spr, W / 2, o["y"], scale=s)

# ---------------------------------------------------------------- subtítulos
def build_chunks():
    chunks, cur = [], []
    for i, a in enumerate(A):
        cur.append(i)
        txt = " ".join(A[j]["w"] for j in cur)
        nxt_line = i + 1 < len(A) and A[i + 1]["line"] != a["line"]
        if len(cur) >= 3 or len(txt) >= 16 or re.search(r"[.,?!:]$", a["w"]) or nxt_line:
            chunks.append(cur); cur = []
    if cur: chunks.append(cur)
    out = []
    for k, c in enumerate(chunks):
        s = A[c[0]]["s"]
        e = A[chunks[k + 1][0]]["s"] if k + 1 < len(chunks) else A[c[-1]]["e"] + 0.4
        e = min(e, A[c[-1]]["e"] + 0.5)
        out.append((s, e, c))
    return out
CHUNKS = build_chunks()

@lru_cache(maxsize=512)
def sub_sprite(idx, active):
    s, e, c = CHUNKS[idx]
    f = font(MONT(900), 84)
    words = [A[j]["w"].upper() for j in c]
    sp = f.getlength(" ")
    widths = [f.getlength(w) for w in words]
    total = sum(widths) + sp * (len(words) - 1)
    wimg, himg = int(total + 80), 160
    im = Image.new("RGBA", (wimg, himg), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x = 40
    for k, w in enumerate(words):
        col = YEL if k == active else WHITE
        d.text((x + 5, 85), w, font=f, fill=(0, 0, 0, 140), anchor="lm", stroke_width=12, stroke_fill=(0, 0, 0, 140))
        d.text((x, 80), w, font=f, fill=col, anchor="lm", stroke_width=11, stroke_fill=BLACK)
        x += widths[k] + sp
    return im

def draw_subs(fr, T):
    for idx, (s, e, c) in enumerate(CHUNKS):
        if s <= T < e:
            act = 0
            for k, j in enumerate(c):
                if A[j]["s"] <= T: act = k
            spr = sub_sprite(idx, act)
            dt = T - s
            sc = 0.86 + 0.14 * ease_out(dt / 0.1)
            if spr.width * sc > W - 40: sc = (W - 40) / spr.width
            paste_center(fr, spr, W / 2, 1230, scale=sc)
            return

# ---------------------------------------------------------------- frame
def render_frame(n):
    T = n / FPS
    i, t0, t1 = scene_at(T)
    bg = CUTS[i][1]
    p = (T - t0) / max(0.01, t1 - t0)
    dtc = T - t0
    punch = 1 + 0.10 * (1 - ease_out(dtc / 0.22)) if i > 0 else 1
    # sacudida
    shake = (0, 0)
    for o in OV:
        if o["kind"] == "shake" and 0 <= T - o["t"] < o["dur"]:
            a = 22 * (1 - (T - o["t"]) / o["dur"])
            shake = (a * math.sin(T * 90), a * math.cos(T * 70))
    if bg["type"] == "photo":
        fr = render_photo(bg, p, punch)
    else:
        fr = render_map(bg, p, T, punch)
    if shake != (0, 0):
        fr = fr.transform(fr.size, Image.AFFINE, (1, 0, shake[0], 0, 1, shake[1]), resample=Image.BILINEAR)
    fr = fr.convert("RGBA")
    # destello blanco corto en cada corte
    if i > 0 and dtc < 0.08:
        fr.alpha_composite(Image.new("RGBA", fr.size, (255, 255, 255, int(110 * (1 - dtc / 0.08)))))
    for o in OV:
        if o["kind"] != "shake":
            draw_overlay(fr, o, T)
    draw_subs(fr, T)
    # barra de progreso inferior (retención)
    d = ImageDraw.Draw(fr)
    d.rectangle([0, H - 14, int(W * T / DUR), H], fill=YEL)
    return fr.convert("RGB").tobytes()

# ---------------------------------------------------------------- audio
def build_audio(out="out/mix.wav"):
    inputs = ["-i", "audio/voz_final.wav", "-i", "audio/music.wav"]
    filters = ["[0:a]aresample=44100,aformat=channel_layouts=stereo,volume=1.0,apad=pad_dur=2[v]",
               f"[1:a]aformat=channel_layouts=stereo,volume=0.13,afade=t=out:st={DUR - 1.5:.2f}:d=1.5,atrim=0:{DUR:.2f}[m]"]
    labels = ["[v]", "[m]"]
    for k, (t, name, g) in enumerate(sorted(SFX)):
        inputs += ["-i", f"audio/sfx/{name}.wav"]
        ms = int(max(0, t) * 1000)
        filters.append(f"[{k + 2}:a]aformat=channel_layouts=stereo,volume={0.28 * g:.2f},adelay={ms}|{ms}[s{k}]")
        labels.append(f"[s{k}]")
    filters.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=longest,atrim=0:{DUR:.2f},alimiter=limit=0.95[a]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filters),
                    "-map", "[a]", "-ar", "44100", out], check=True)

if __name__ == "__main__":
    os.makedirs("out", exist_ok=True)
    if len(sys.argv) > 1 and sys.argv[1] == "preview":
        ts = [float(x) for x in sys.argv[2:]]
        for T in ts:
            Image.frombytes("RGB", (W, H), render_frame(int(T * FPS))).save(f"out/prev_{T:05.2f}.jpg", quality=85)
        sys.exit()
    build_audio()
    N = int(DUR * FPS)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-i", "out/mix.wav", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
                           "out/raw.mp4"], stdin=subprocess.PIPE)
    with Pool(2) as pool:
        for k, buf in enumerate(pool.imap(render_frame, range(N), chunksize=8)):
            ff.stdin.write(buf)
            if k % 150 == 0: print(f"{k}/{N}", flush=True)
    ff.stdin.close(); ff.wait()
    # volumen final al nivel de TikTok/YouTube (-15 LUFS)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "out/raw.mp4", "-c:v", "copy", "-af", "loudnorm=I=-15:TP=-1.5:LRA=11",
                    "-ar", "44100", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "out/video.mp4"], check=True)
    print("done", DUR)
