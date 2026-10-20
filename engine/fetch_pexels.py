import json, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor

env = dict(l.strip().split("=", 1) for l in open(".env") if "=" in l)
KEY = env["PEXELS_KEY"]
QUERIES = json.load(open("queries.json"))

def fetch(item):
    name, q = item
    url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode({"query": q, "per_page": 6, "orientation": "portrait"})
    d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"Authorization": KEY, "User-Agent": "Mozilla/5.0"}), timeout=30))
    out = []
    for k, p in enumerate(d.get("photos", [])[:4]):
        fn = f"img/pexels/{name}_{k}.jpg"
        open(fn, "wb").write(urllib.request.urlopen(urllib.request.Request(p["src"]["large2x"], headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read())
        out.append({"file": fn, "alt": p.get("alt"), "by": p["photographer"], "url": p["url"]})
    return name, out

with ThreadPoolExecutor(6) as ex:
    meta = dict(ex.map(fetch, QUERIES.items()))
json.dump(meta, open("img/pexels/meta.json", "w"), indent=1)
print({k: len(v) for k, v in meta.items()})
