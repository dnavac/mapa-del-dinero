"""Voz corrida: un solo audio con todo el guion. El estilo va como instrucción de sistema,
así el modelo no lo lee en voz alta."""
import base64, json, subprocess, sys, urllib.request, urllib.error
from script import LINES

env = dict(l.strip().split("=", 1) for l in open(".env") if "=" in l)
KEY = env["GOOGLE_KEY"]
MODEL, VOICE = "gemini-3.8-flash-tts", "Charon"
STYLE = ("Eres un creador latinoamericano de TikTok que le cuenta a un amigo un dato increíble sobre dinero. "
         "Lee el texto en español latino neutro, cercano y natural, como una conversación y no como un locutor ni un documental: "
         "ritmo ágil, sorpresa real en las cifras, sonrisa en la voz y pausas cortas. "
         "Lee solo el texto del usuario, sin añadir nada.")

def call(with_system):
    body = {"contents": [{"role": "user", "parts": [{"text": "\n".join(LINES)}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": VOICE}}}}}
    if with_system:
        body["systemInstruction"] = {"parts": [{"text": STYLE}]}
    else:
        body["contents"][0]["parts"][0]["text"] = "Cuéntalo como a un amigo, cercano y con sorpresa:\n\n" + "\n".join(LINES)
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={KEY}",
        data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=300))

try:
    res = call(True)
except urllib.error.HTTPError as e:
    print("system instruction no aceptada:", e.code, e.read().decode()[:300])
    res = call(False)
part = res["candidates"][0]["content"]["parts"][0]["inlineData"]
open("audio/raw.wav", "wb").write(base64.b64decode(part["data"]))
print("mime", part["mimeType"])
