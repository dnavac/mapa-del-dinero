import json, re, unicodedata, subprocess, numpy as np, scipy.io.wavfile as wf
from faster_whisper import WhisperModel
def norm(w):
    w = unicodedata.normalize("NFD", w.lower()); return re.sub(r"[^a-z0-9]", "", "".join(c for c in w if unicodedata.category(c) != "Mn"))
sr, x = wf.read("audio/raw.wav"); x = x.astype(np.float32)
# 1) acortar silencios largos
win = int(0.02*sr); n = len(x)//win
db = 20*np.log10(np.sqrt((x[:n*win].reshape(n,win)**2).mean(1)+1e-9)/32768); sil = db < -40
segs=[]; i=0
while i<n:
    j=i
    while j<n and sil[j]==sil[i]: j+=1
    segs.append((sil[i], i*win, j*win)); i=j
pieces=[]
for k,(s,a,b) in enumerate(segs):
    seg=x[a:b]
    if s:
        keep = 0.05 if k==0 else (0.6 if k==len(segs)-1 else min((b-a)/sr, 0.36))
        L=int(keep*sr); seg=np.concatenate([seg[:L//2], seg[len(seg)-(L-L//2):]])
    pieces.append(seg)
y=np.concatenate(pieces); y=y/np.abs(y).max()*0.89*32767
wf.write("audio/tight.wav", sr, y.astype(np.int16))
m = WhisperModel("small", device="cpu", compute_type="int8")
def words(path):
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",path,"-ar","16000","-ac","1","-f","f32le","audio/tmp.f32"],check=True)
    a=np.fromfile("audio/tmp.f32",dtype=np.float32)
    segs,_=m.transcribe(a,language="es",word_timestamps=True,beam_size=5)
    return [{"w":w.word.strip(),"s":float(w.start),"e":float(w.end)} for s in segs for w in s.words]
W=words("audio/tight.wav")
nw=[norm(v["w"]) for v in W]
from script import LINES
fw = [norm(w) for w in LINES[0].split()[:2]]
start=next(i for i in range(len(nw)-1) if nw[i]==fw[0] and nw[i+1]==fw[1])
cut=max(0,int((W[start]["s"]-0.06)*sr))
if start>0: cut=max(cut,int(W[start-1]["e"]*sr))
y=y[cut:]
wf.write("audio/voz_final.wav", sr, y.astype(np.int16))
W2=words("audio/voz_final.wav")
json.dump(W2, open("audio/words_final.json","w"), ensure_ascii=False)
print("lead words skipped:", start, "dur", len(y)/sr)
print(" ".join(v["w"] for v in W2))
