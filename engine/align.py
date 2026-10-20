"""Alinea las palabras del guion (SUBS) con los tiempos de Whisper."""
import json, re, unicodedata, difflib
from script import SUBS

def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", w)

NUM = {"2": "dos", "3": "tres"}
W = json.load(open("audio/words_final.json"))
wt = [norm(x["w"]) for x in W]

script = []  # (display word, line index)
for li, line in enumerate(SUBS):
    for tok in line.split():
        script.append((tok, li))
st = [NUM.get(norm(t), norm(t)) for t, _ in script]

sm = difflib.SequenceMatcher(a=st, b=wt, autojunk=False)
times = [None] * len(st)
for a, b, n in sm.get_matching_blocks():
    for k in range(n):
        times[a + k] = (W[b + k]["s"], W[b + k]["e"])
# replace/insert blocks: distribute proportionally
for tag, a1, a2, b1, b2 in sm.get_opcodes():
    if tag in ("replace", "delete"):
        if b2 > b1:
            s0, e0 = W[b1]["s"], W[b2 - 1]["e"]
        else:
            prev = next((times[i][1] for i in range(a1 - 1, -1, -1) if times[i]), 0)
            nxt = next((times[i][0] for i in range(a2, len(st)) if times[i]), prev + 0.3)
            s0, e0 = prev, nxt
        tot = sum(max(1, len(st[i])) for i in range(a1, a2))
        t = s0
        for i in range(a1, a2):
            d = (e0 - s0) * max(1, len(st[i])) / tot
            times[i] = (t, t + d)
            t += d
out = [{"w": script[i][0], "line": script[i][1], "s": round(float(times[i][0]), 3), "e": round(float(times[i][1]), 3)}
       for i in range(len(st))]
json.dump(out, open("audio/aligned.json", "w"), ensure_ascii=False, indent=0)
for li in range(len(SUBS)):
    ws = [o for o in out if o["line"] == li]
    print(li, ws[0]["s"], ws[-1]["e"], SUBS[li][:50])
for tag, a1, a2, b1, b2 in sm.get_opcodes():
    if tag != "equal":
        print(tag, st[a1:a2], wt[b1:b2])
