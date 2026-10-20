"""Portada 1080x1920 a partir de cover.json (en la carpeta del video).

Ejemplo de cover.json:
{
  "photo": "img/pexels/marina_2.jpg",   foto clara y real (de las descargadas)
  "crop_y": 0.5,                         0 = parte de arriba de la foto, 1 = parte de abajo
  "lines": [["¿CÓMO SINGAPUR", 140, "white"], ["SE HIZO", 170, "yellow"], ["TAN RICO?", 200, "yellow"]],
  "pill": "Lo echaron de Malasia en 1965",
  "box": {"type": "vs", "left_label": "1965", "left_value": "US$ 500", "left_color": "dark",
          "right_label": "HOY", "right_value": "80.000", "right_color": "green", "middle": "arrow", "caption": ""}
     o   {"type": "single", "label": "AHORRO POR CADA NORUEGO", "value": "US$ 400.000", "color": "green"}
}
Todo el texto queda dentro de la zona que TikTok muestra en la cuadrícula del perfil (y 240–1680).
"""
import json
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

W, H = 1080, 1920
ANTON = "fonts/fontsource-anton/files/anton-latin-400-normal.woff"
MONT = lambda w: f"fonts/fontsource-montserrat/files/montserrat-latin-{w}-normal.woff"
COL = {"white": (255, 255, 255), "yellow": (255, 224, 27), "red": (229, 57, 53), "green": (39, 174, 96),
       "dark": (40, 40, 40), "gray": (110, 110, 110), "blue": (66, 133, 244)}
BLACK = (0, 0, 0)
C = json.load(open("cover.json"))

src = Image.open(C["photo"]).convert("RGB")
s = max(W / src.width, H / src.height) * 1.08
src = src.resize((int(src.width * s), int(src.height * s)), Image.LANCZOS)
x0 = (src.width - W) // 2; y0 = int((src.height - H) * C.get("crop_y", 0.5))
img = src.crop((x0, y0, x0 + W, y0 + H))
img = ImageEnhance.Color(img).enhance(1.2); img = ImageEnhance.Contrast(img).enhance(1.05)
img = img.convert("RGBA")
g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
for y in range(900):
    gd.line([(0, y), (W, y)], fill=(10, 20, 40, int(120 * (1 - y / 900) ** 1.6)))
img.alpha_composite(g)

def text_shadow(txt, font, cx, y, fill, stroke=9):
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((cx + 6, y + 9), txt, font=font, fill=(0, 0, 0, 170), anchor="ma", stroke_width=stroke, stroke_fill=(0, 0, 0, 170))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(7)))
    ImageDraw.Draw(img).text((cx, y), txt, font=font, fill=fill, anchor="ma", stroke_width=stroke, stroke_fill=BLACK)

def fit(txt, size, fontp, maxw=980):
    while size > 40:
        f = ImageFont.truetype(fontp, size)
        if f.getlength(txt) <= maxw:
            return f
        size -= 4
    return ImageFont.truetype(fontp, size)

y = 280
for txt, size, color in C["lines"]:
    f = fit(txt, size, ANTON)
    text_shadow(txt, f, W / 2, y, COL.get(color, COL["white"]))
    y += int(f.size * 1.17)
y += 40

d = ImageDraw.Draw(img)
if C.get("pill"):
    f3 = fit(C["pill"], 46, MONT(900), 900)
    tw_ = d.textlength(C["pill"], font=f3); pad = 34
    d.rounded_rectangle([W / 2 - tw_ / 2 - pad, y - 4, W / 2 + tw_ / 2 + pad, y + 82], radius=44, fill=COL["red"])
    d.text((W / 2, y + 39), C["pill"], font=f3, fill=COL["white"], anchor="mm")

B = C.get("box")
yb = 1290
if B:
    box = Image.new("RGBA", (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(box)
    bd.rounded_rectangle([98, yb + 12, W - 82, yb + 272], radius=36, fill=(0, 0, 0, 120))
    img.alpha_composite(box.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([90, yb, W - 90, yb + 260], radius=36, fill=COL["white"])
    fl = ImageFont.truetype(MONT(800), 38)
    if B["type"] == "single":
        d.text((W / 2, yb + 55), B["label"], font=fit(B["label"], 40, MONT(800), 860), fill=COL["gray"], anchor="mm")
        d.text((W / 2, yb + 160), B["value"], font=fit(B["value"], 130, ANTON, 860), fill=COL.get(B.get("color", "green")), anchor="mm")
    else:
        for side, cx in (("left", 285), ("right", 790)):
            d.text((cx, yb + 52), B[f"{side}_label"], font=fit(B[f"{side}_label"], 38, MONT(800), 380), fill=COL["gray"], anchor="mm")
            d.text((cx, yb + 158), B[f"{side}_value"], font=fit(B[f"{side}_value"], 104, ANTON, 380), fill=COL.get(B.get(f"{side}_color", "dark")), anchor="mm")
        if B.get("middle", "vs") == "arrow":
            ax, ay = 535, yb + 158
            d.line([(ax - 40, ay), (ax + 40, ay)], fill=COL["red"], width=16)
            d.polygon([(ax + 62, ay), (ax + 30, ay - 30), (ax + 30, ay + 30)], fill=COL["red"])
        else:
            d.text((W / 2, yb + 158), "VS", font=ImageFont.truetype(ANTON, 70), fill=(150, 150, 150), anchor="mm")
        if B.get("caption"):
            d.text((W / 2, yb + 228), B["caption"], font=ImageFont.truetype(MONT(700), 26), fill=(120, 120, 120), anchor="mm")

# marca
f4 = ImageFont.truetype(MONT(900), 40); tag = "MAPA DEL DINERO"
tw_ = d.textlength(tag, font=f4); bx = W / 2 - (tw_ + 96) / 2; by = yb + 300
d.rounded_rectangle([bx, by, bx + tw_ + 96, by + 70], radius=14, fill=(10, 20, 40))
d.ellipse([bx + 18, by + 17, bx + 54, by + 53], fill=(242, 183, 5))
d.text((bx + 36, by + 36), "$", font=ImageFont.truetype(ANTON, 30), fill=(120, 80, 0), anchor="mm")
d.text((bx + 72, by + 35), tag, font=f4, fill=COL["white"], anchor="lm")
img.convert("RGB").save("out/portada.png")
print("portada ok")
