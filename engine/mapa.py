"""Mapas a partir de world-atlas (Natural Earth, dominio público).
Región y resolución en map.json del video: {"res": "10m"|"50m", "bbox": [lon_min, lat_min, lon_max, lat_max]}."""
import json, math, os, unicodedata
from PIL import Image, ImageDraw

CFG = json.load(open("map.json")) if os.path.exists("map.json") else {"res": "50m", "bbox": [-180, -60, 180, 85]}
TOPO = json.load(open(f"fonts/world-atlas/countries-{CFG['res']}.json"))
BX0, BY0, BX1, BY1 = CFG["bbox"]
SC, TR = TOPO["transform"]["scale"], TOPO["transform"]["translate"]

def _arcs():
    out = []
    for arc in TOPO["arcs"]:
        x = y = 0; pts = []
        for dx, dy in arc:
            x += dx; y += dy
            pts.append((x * SC[0] + TR[0], y * SC[1] + TR[1]))
        out.append(pts)
    return out
ARCS = _arcs()

def ring(idx):
    pts = []
    for i in idx:
        a = ARCS[i] if i >= 0 else ARCS[~i][::-1]
        pts.extend(a if not pts else a[1:])
    return pts

COUNTRIES = {}
NAMES = {}
for g in TOPO["objects"]["countries"]["geometries"]:
    polys = []
    if g["type"] == "Polygon":
        polys = [g["arcs"]]
    elif g["type"] == "MultiPolygon":
        polys = g["arcs"]
    rings = []
    for p in polys:
        r = ring(p[0])
        if any(BX0 < x < BX1 and BY0 < y < BY1 for x, y in r):
            rings.append(r)
    NAMES[g.get("id")] = g.get("properties", {}).get("name", "")
    if rings:
        COUNTRIES[g.get("id")] = rings

def _n(t):
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")

def cid(name):
    """Id de un país por su nombre en inglés (Natural Earth), p. ej. cid("Colombia"), cid("United States of America")."""
    for k, v in NAMES.items():
        if _n(v) == _n(name):
            return k
    m = [k for k, v in NAMES.items() if _n(name) in _n(v)]
    if m:
        return m[0]
    raise KeyError(name)


SEA = (164, 214, 245)
LAND = (250, 243, 222)
BORDER = (170, 160, 140)

def project(lon, lat, cam, W, H):
    lon0, lat0, k = cam
    x = (lon - lon0) * math.cos(math.radians(lat0)) * k + W / 2
    y = -(lat - lat0) * k + H / 2
    return x, y

def draw_map(W, H, cam, colors=None, ss=1):
    """cam = (lon0, lat0, px_per_degree). colors: {id: rgb}"""
    colors = colors or {}
    Ws, Hs = W * ss, H * ss
    img = Image.new("RGB", (Ws, Hs), SEA)
    d = ImageDraw.Draw(img)
    cam2 = (cam[0], cam[1], cam[2] * ss)
    for cid, rings in COUNTRIES.items():
        fill = colors.get(cid, LAND)
        for r in rings:
            pts = [project(x, y, cam2, Ws, Hs) for x, y in r]
            xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
            if max(xs) < 0 or min(xs) > Ws or max(ys) < 0 or min(ys) > Hs:
                continue
            d.polygon(pts, fill=fill, outline=BORDER)
            if cid in colors:
                d.line(pts + [pts[0]], fill=(255, 255, 255), width=max(2, int(4 * ss)))
    if ss > 1:
        img = img.resize((W, H), Image.LANCZOS)
    return img

