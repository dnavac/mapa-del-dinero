"""Efectos de sonido y música de fondo sintetizados (sin copyright)."""
import numpy as np, scipy.io.wavfile as wf, scipy.signal as ss, os

SR = 44100
OUT = os.environ.get("SFX_DIR", "audio/sfx")
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(7)

def t(d): return np.arange(int(d * SR)) / SR
def save(name, x, gain=0.9):
    x = x / (np.abs(x).max() + 1e-9) * gain
    wf.write(f"{OUT}/{name}.wav", SR, (x * 32767).astype(np.int16))

def env(n, a, r, curve=3):
    e = np.ones(n); A = max(1, int(a * SR)); R = max(1, int(r * SR))
    e[:A] = np.linspace(0, 1, A); e[-R:] *= np.linspace(1, 0, R) ** curve
    return e

def bp(x, lo, hi, order=2):
    b, a = ss.butter(order, [lo / (SR / 2), hi / (SR / 2)], "band"); return ss.lfilter(b, a, x)

def lp(x, f, order=2):
    b, a = ss.butter(order, f / (SR / 2)); return ss.lfilter(b, a, x)

# whoosh: noise through a sweeping band-pass
def whoosh(d=0.5, f0=300, f1=4000):
    n = int(d * SR); x = rng.standard_normal(n); out = np.zeros(n); blk = 512
    for i in range(0, n, blk):
        p = i / n; fc = f0 * (f1 / f0) ** (np.sin(p * np.pi))
        out[i:i + blk] = bp(x[i:i + blk], fc * 0.6, min(fc * 1.6, 20000))
    e = np.sin(np.linspace(0, np.pi, n)) ** 2
    return out * e
save("whoosh", whoosh(), 0.55)
save("whoosh_fast", whoosh(0.3, 500, 6000), 0.5)

# impact / boom
def boom(d=1.2, f=48):
    tt = t(d); s = np.sin(2 * np.pi * f * tt * (1 + 0.6 * np.exp(-tt * 8))) * np.exp(-tt * 3.5)
    c = lp(rng.standard_normal(len(tt)), 900) * np.exp(-tt * 25)
    return s + 0.6 * c
save("impact", boom(), 0.95)

# pop (texto que aparece)
tt = t(0.12); save("pop", np.sin(2 * np.pi * (500 + 2500 * tt) * tt) * np.exp(-tt * 40), 0.5)

# reloj tic-tac
def ticktock(d=2.0):
    n = int(d * SR); x = np.zeros(n)
    for k, st in enumerate(np.arange(0, d, 0.5)):
        i = int(st * SR); L = int(0.03 * SR)
        f = 3200 if k % 2 == 0 else 2300
        cl = bp(rng.standard_normal(L), f * 0.8, f * 1.3) * np.exp(-np.arange(L) / SR * 220)
        x[i:i + L] += cl[: n - i]
    return x
save("ticktock", ticktock(), 0.6)

# moneda / clink
def coin(d=0.6):
    tt = t(d); parts = [(2637, 1), (3951, 0.6), (5274, 0.45), (6644, 0.3)]
    return sum(a * np.sin(2 * np.pi * f * tt) * np.exp(-tt * (6 + f / 900)) for f, a in parts)
c = coin(); x = np.zeros(int(1.0 * SR))
for st, g in [(0, 1), (0.12, 0.7), (0.21, 0.5), (0.33, 0.35)]:
    i = int(st * SR); x[i:i + len(c)] += g * c[: len(x) - i]
save("coins", x, 0.55)

# ding / caja registradora
tt = t(1.2); ding = sum(a * np.sin(2 * np.pi * f * tt) * np.exp(-tt * 3) for f, a in [(1568, 1), (3136, .4), (4704, .2)])
save("ding", ding, 0.5)

# sello (stamp)
tt = t(0.35); st_ = np.sin(2 * np.pi * 90 * tt) * np.exp(-tt * 18) + lp(rng.standard_normal(len(tt)), 2500) * np.exp(-tt * 45) * 0.8
save("stamp", st_, 0.9)

# candado: click-clack
x = np.zeros(int(0.4 * SR))
for st in [0.0, 0.16]:
    i = int(st * SR); L = int(0.04 * SR)
    x[i:i + L] += bp(rng.standard_normal(L), 1500, 6000) * np.exp(-np.arange(L) / SR * 120)
save("lock", x, 0.7)

# riser (suspenso antes de una pregunta)
tt = t(1.4); r = bp(rng.standard_normal(len(tt)), 800, 8000) * (tt / 1.4) ** 2.5
r += 0.4 * np.sin(2 * np.pi * (200 + 600 * (tt / 1.4) ** 2) * tt) * (tt / 1.4) ** 2
save("riser", r, 0.45)

# guerra: explosiones lejanas
x = np.zeros(int(2.4 * SR))
for st, f in [(0.0, 40), (0.7, 35), (1.3, 45)]:
    b = boom(1.1, f); i = int(st * SR); x[i:i + len(b)] += b[: len(x) - i]
x += lp(rng.standard_normal(len(x)), 200) * 0.25 * env(len(x), 0.3, 1.0)
save("war", x, 0.8)

# cristal / quiebre (secreto que se rompe)
x = np.zeros(int(0.8 * SR))
for k in range(28):
    i = int(rng.uniform(0, 0.25) * SR); L = int(rng.uniform(0.05, 0.4) * SR); f = rng.uniform(2500, 9000)
    x[i:i + L] += np.sin(2 * np.pi * f * np.arange(L) / SR) * np.exp(-np.arange(L) / SR * rng.uniform(10, 30)) * rng.uniform(.2, 1)
x[: int(0.05 * SR)] += bp(rng.standard_normal(int(0.05 * SR)), 2000, 10000) * 1.5
save("shatter", x, 0.6)

# pulso de laboratorio / burbuja
tt = t(0.5); save("bubble", np.sin(2 * np.pi * (300 + 900 * tt) * tt) * np.exp(-tt * 9), 0.4)

# ---------------- música de fondo (pad + pulso), 72 s ----------------
D = 120.0; tt = t(D); bpm = 100; beat = 60 / bpm
chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]  # Am F C G
m = np.zeros(len(tt))
bar = beat * 4
for k in range(int(D / bar)):
    notes = chords[k % 4]; a = int(k * bar * SR); b = min(len(tt), int((k + 1) * bar * SR))
    seg = tt[a:b] - tt[a]
    for nn in notes:
        f = 440 * 2 ** ((nn - 69) / 12)
        tone = sum(np.sin(2 * np.pi * f * h * seg + h) / h ** 1.3 for h in (1, 2, 3))
        m[a:b] += tone * env(b - a, 0.25, 0.4, 1) * 0.18
    # bajo
    f = 440 * 2 ** ((notes[0] - 12 - 69) / 12)
    for q in range(4):
        i = a + int(q * beat * SR); L = int(beat * 0.9 * SR)
        if i + L <= len(tt):
            s = np.arange(L) / SR
            m[i:i + L] += np.sin(2 * np.pi * f * s) * np.exp(-s * 4) * 0.35
# kick suave
for q in range(int(D / beat)):
    i = int(q * beat * SR); L = int(0.25 * SR)
    if i + L <= len(tt):
        s = np.arange(L) / SR
        m[i:i + L] += np.sin(2 * np.pi * (50 + 90 * np.exp(-s * 30)) * s) * np.exp(-s * 14) * 0.5
# hi-hat en contratiempo
for q in range(int(D / beat)):
    i = int((q + 0.5) * beat * SR); L = int(0.05 * SR)
    if i + L <= len(tt):
        m[i:i + L] += bp(rng.standard_normal(L), 7000, 14000) * np.exp(-np.arange(L) / SR * 80) * 0.12
m = lp(m, 9000)
save("music", m, 0.9)
# bocina de barco
tt = t(1.6); e = np.minimum(1, tt / 0.08) * np.clip((1.6 - tt) / 0.5, 0, 1)
h = sum(np.sign(np.sin(2 * np.pi * f * tt)) * a for f, a in [(110, 1), (138.6, 0.6), (165, 0.4)])
save("horn", lp(h, 900, 3) * e, 0.8)
print("sfx ok")
