# Mapa del Dinero — cómo producir un video (instrucciones para la tarea diaria)

Canal de Diego: **Mapa del Dinero** (TikTok registrado en Francia, contenido en español; también YouTube Shorts, Reels y Facebook).
Temas: economía y geopolítica explicada en 3 líneas — **países** ("¿Por qué [país] es rico/pobre?"), **empresas y apps** ("¿Cómo gana dinero ___?", casinos, juegos gratis…) y **actualidad** (guerras, disputas, aranceles y acuerdos vistos por el lado del dinero). Objetivo n.º 1: que se vuelva viral — gancho fuerte, que vean hasta el final y que entren al perfil a ver más. Meta: seguidores, reproducciones, comentarios y llegar a la monetización de YouTube antes del 1 de febrero de 2027.

## Reglas fijas (Diego las pidió)
- Todo en español. Responder a Diego en español.
- **Una sola voz corrida** con todo el guion (Google TTS, voz Charon, modelo gemini-3.8-flash-tts). Nunca una voz por escena. Sobre esa voz se cuadran imágenes, animaciones y efectos.
- **Siempre subtítulos** (el motor los pone solos, palabra activa en amarillo).
- **Diseño claro**: fotos reales luminosas, nada de fondos oscuros ni capas negras encima.
- **Efectos de sonido suaves** (el motor ya los mezcla bajo: factor 0.28; no subirlo; ganancias por efecto entre 0.5 y 0.9).
- **Máximo 5 hashtags** por publicación.
- Cada video lleva **portada** (una sola para todas las plataformas) y **descripción**.
- Duración **35–50 s** (cambio del 24-oct-2026: el canal necesita seguidores antes que monetización; TikTok solo paga desde 10.000 seguidores, así que hasta llegar ahí manda la retención).
- **Cada video es un episodio de una serie** con nombre y número (`series.json`). La serie es la razón para seguir: la gente sigue cuando sabe que viene otro igual.
- Datos verificados con búsqueda web. Tono de datos, sin opinar de política ni señalar partidos o gobiernos.

## 0. Preparar (una vez por sesión, ~3 min)
El kit vive en el repositorio de GitHub de Diego **dnavac/mapa-del-dinero** (público; solo código y videos, nunca claves).
1. Conecta el repo a la sesión: herramienta `add_repo` con `owner: "dnavac"`, `repo: "mapa-del-dinero"`, `access: "push"`. Sigue la instrucción de clonado que devuelve, clonando en `~/mdd/kit` (si te da otra ruta, usa esa y ajusta las rutas de este documento).
2. Luego:
```
cd ~/mdd/kit
bash setup.sh "<GOOGLE_KEY>" "<PEXELS_KEY>"   # las claves vienen en el mensaje de la tarea; nunca las escribas en archivos del repo
```
Debe terminar en `SETUP OK`. No hagas `git commit` ni `git push` del kit: solo se usa el repo para releases (paso 11).

## 1. Elegir el tema
1. Busca en Google Drive el historial: `search_files` con `title contains 'MDD_hist_'`. Los títulos tienen la forma `MDD_hist_AAAA-MM-DD_AM|PM_<slug>`. Esos slugs ya se hicieron (además de suiza, singapur, noruega, colombia).
2. **Plan del día del analista (va primero):** busca `title contains 'MDD_plan_<AAAA-MM-DD de hoy>'` y léelo. Trae el tema del turno AM y del PM con slug, título, **gancho exacto**, ángulo, datos y fuentes. Si existe, usa el de tu turno tal cual (puedes mejorar el gancho, no cambiar el tema). Si su slug ya está en el historial, usa el otro turno o sigue al punto 3.
3. Si no hay plan: busca el documento `MDD_pedidos` (Google Doc) y léelo con `read_file_content`. Son temas que la gente pidió en comentarios. Si hay uno no hecho, ese es el tema (inventa un slug corto).
4. Si no, toma el primer tema de `temas.json` cuyo slug no esté en el historial.
5. Alterna categorías (`pais`, `empresa`, `actualidad`): no repitas la misma categoría dos veces seguidas, salvo que el plan del analista diga otra cosa.
6. **Serie y número**: si el plan los trae, úsalos tal cual. Si no, lee `series.json`, elige la serie que corresponda al tema (por categoría y promesa) y calcula el número: episodios listados en `series.json` + archivos `MDD_hist_*` cuyo contenido diga `Serie: <nombre>` y no estén ya en esa lista, + 1. Elige también el **próximo episodio** que vas a anunciar al final (de `ideas` de la misma serie, que no esté en el historial).
7. Temas de **actualidad** (guerras, disputas, acuerdos, aranceles): siempre vistos por el lado del dinero (precios, comercio, quién gana y quién pierde), con noticias de los últimos días verificadas en 2+ fuentes. Nada de imágenes de violencia ni heridos; nada de opinar sobre gobiernos o bandos. **Casinos, loterías y apuestas**: solo educativo ("por qué la casa siempre gana"); nunca invitar a apostar, ni nombrar o mostrar casas de apuestas.

## 2. Investigar (5 min)
- 3–5 búsquedas web. Necesitas 3–5 datos duros (años, cifras, porcentajes) **actuales y verificados**. Si una cifra cambia con el tiempo (PIB, población, fondos), usa la más reciente y redondea hacia abajo ("más de…", "unos…").
- Si un dato no se puede verificar, no va. Guarda los enlaces para las fuentes.

## 3. Guion → `script.py`
```
bash ~/mdd/kit/new_video.sh <slug>   # crea ~/mdd/kit/videos/<slug> y lo imprime
cd ~/mdd/kit/videos/<slug>
```
`script.py` con dos listas del mismo largo (ver `ejemplos/script_*.py`):
- `LINES`: lo que se dice. **Números en palabras** ("mil novecientos sesenta y cinco", "uno coma cinco por ciento").
- `SUBS`: lo mismo para subtítulos, **números en cifras** ("1965", "1,5%", "80.000"). Mismas palabras en el mismo orden; solo cambian los números.
- **10–13 líneas, 100–140 palabras en total (≈ 35–50 s).** Si te sobra material, quita razones, no aceleres. Mejor 3 datos que se entienden que 6 que se pierden.
- Tono: **como un amigo que te cuenta algo increíble**, no como un noticiero ni un documental. Frases de máx. ~14 palabras, palabras de la calle ("plata", "o sea", "imagínate"), segunda persona ("tú", "tu bolsillo").
- Estructura (pensada para que se queden hasta el final **y luego sigan la cuenta**):
  1. **Gancho en la primera línea** (≤ 2,5 s, máx. 12 palabras): paradoja, cifra que choque o algo que le toca el bolsillo al que mira. El formato que más ha funcionado en el canal: **cifra gigante + "…y aun así"** ("Estados Unidos debe más de 40 billones… y aun así todos le prestan"). Sin "Hola", sin presentarse, sin "en este video". Las dos primeras palabras del guion deben ser distintivas (se usan para recortar el inicio del audio). En la primera escena el texto grande en pantalla dice el gancho (o su cifra) desde el fotograma 1.
  2. **Línea 2: serie + bucle abierto en la misma frase corta**: la `frase_serie` de `series.json` o una versión breve, y la promesa que se resuelve al final ("Episodio seis de los países ricos sin nada… y al final te digo quién le presta"). Máx. 18 palabras.
  3. 2–3 razones **numeradas** ("Primero:", "Segundo:"…), cada una con un dato concreto. Cambio visual cada 2–3 s.
  4. Giro o dato curioso ("Y lo más loco…") justo pasada la mitad.
  5. Cerrar el bucle abierto con la cifra prometida.
  6. **Cierre para seguir (1 línea, siempre)**: anuncia el **próximo episodio concreto** de la serie y pide seguir para verlo: "El próximo de la serie es Dinamarca. Sígueme para no perdértelo." Nunca un "sígueme" sin razón.
  7. **Pregunta para comentar** (en la descripción y en el texto final de pantalla, no hace falta decirla): de **una palabra o sí/no**, fácil de contestar ("¿Le prestarías tú? SÍ o NO", "Escribe tu país"). Nada de preguntas abiertas largas.
  8. Nada de "Parte 1 / Parte 2": no funcionaron. Si el tema da para más, es otro episodio de la serie con título propio.
- Portada: pregunta o cifra en 3–5 palabras enormes ("¿POR QUÉ LA CASA SIEMPRE GANA?"), con la cara/objeto del tema y colores vivos. La **píldora roja** lleva el nombre de la serie y el número ("RICOS SIN NADA #6"): así el perfil se ve como una colección.

## 4. Voz y tiempos (≈ 3 min)
```
python3 tts.py && python3 prep_voice.py && python3 align.py
```
- `tts.py` genera **un solo audio** de todo el guion. El modelo no acepta instrucción de sistema (error 400 "Developer instruction"): es normal, cae al modo con prefijo y `prep_voice.py` recorta lo que sobra.
- `prep_voice.py` acorta silencios, recorta el inicio y saca tiempos por palabra con Whisper.
- `align.py` imprime inicio/fin de cada línea y las diferencias con lo que entendió Whisper (es normal ver `replace` en números o nombres propios).
- Si la duración final queda > 52 s, recorta el guion y repite; si queda < 32 s, alárgalo.

## 5. Imágenes
- `queries.json`: 16–24 búsquedas en inglés para Pexels, `{"nombre": "consulta"}` (ej. `"port": "container port cranes"`). Fotos claras, reales, del país y de cada idea.
- `python3 fetch_pexels.py && python3 ~/mdd/kit/engine/sheets.py photos` y **mira** `img/sheet0.jpg`, `img/sheet1.jpg` con Read. Elige las mejores (`P("port_1")` = `img/pexels/port_1.jpg`). Evita fotos oscuras, con logos grandes o que no correspondan.
- Mapas: `map.json` con la región y resolución, p. ej. `{"res": "10m", "bbox": [-84, -6, -64, 14]}` (10m para países pequeños o zoom alto; 50m para regiones grandes). Ids de países: `mapa.cid("Colombia")`, `mapa.cid("United States of America")` (nombres en inglés de Natural Earth).
- Wikimedia Commons limita mucho las descargas (error 429): úsalo solo si es imprescindible (retratos históricos de dominio público).

## 6. Escenas → `scenes.py`
Copia el estilo de `~/mdd/kit/ejemplos/scenes_colombia.py` (y singapur/noruega). Se ejecuta dentro de `render.py`, así que tienes disponible:

**Tiempos**: `tw(linea, "palabra", nth=0)` = segundo en que se dice esa palabra en esa línea (sin tildes ni signos; para cifras usa los dígitos: `tw(2, "80")`, `tw(5, "1965")`). `tw(linea)` = inicio de la línea. `VOICE_END` = fin de la voz.

**Fondos** (cada `cut` cambia la escena con destello + whoosh):
- `cut(t, photo(P("nombre"), z0, z1, p0=(x,y), p1=(x,y), blur=0, fit=False))` — foto con zoom lento de z0 a z1 (1.0↔1.15) y paneo.
- `cut(t, mapbg((lon, lat, px_por_grado), (lon, lat, px_por_grado), {id: color}, timed_colors=[(t, {id: color})]))` — mapa animado entre dos cámaras.
- `cut(t, bg, sfx="whoosh_fast", gain=0.5)` para cortes rápidos; `sfx=None` sin sonido.
- **Cambia de imagen cada 2–5 s** y en cada idea nueva. La imagen debe corresponder a lo que dice la voz.

**Textos y animaciones** (`ov(t, tipo, ...)`; duran hasta el siguiente corte):
- `"title"`: `text="LÍNEA 1|LÍNEA 2", color=YEL|WHITE, box=None|RED|GREEN|BLUE|DARK|(r,g,b), y=330..420, size=96..130` — titular del momento (con caja de color o amarillo con borde).
- `"big"`: texto gigante (`size=150..240`) para preguntas o cifras ("¿POR QUÉ?", "1,5%").
- `"tag"`: etiqueta que entra desde la izquierda (`text, y, color, bg`) — año, lugar, nombre.
- `"chip"`: píldora amarilla (`text, y=820..1100, x=540`) — listas ("SIN CONTRATO", "SIN PENSIÓN"), apiladas cada 110 px.
- `"counter"`: número que sube (`a, b, dur, y, pre="US$ ", suf="%", thousands=True, size`).
- `"stamp"`: sello que golpea (`text, color, y, angle`).
- `"pie"`: gráfico de torta (`frac=0.55, label="55%", y≈780`).
- `"xmark"` (X roja grande), `"ban"` (prohibido, `y`), `"lock"` (candado, `y, mode="close"`), `"crack"` (vidrio roto, `y`), `"people"` (2 de 3 personas, `y`).
- En mapas: `"label"` (`text, geo=(lon,lat), color`), `"pin"` (`geo, text`), `"ring"` (pulso sobre un punto, `geo`), `"arrow"` (`a=(lon,lat), b=(lon,lat), dur, bend=-200..0`).
- `"shake"` (`dur=0.4`) sacude la pantalla.
- **Serie (obligatorio)**: `ov(0, "tag", text="RICOS SIN NADA #6", y=200, color=WHITE, bg=RED, until=VOICE_END)` (con el tag y número de la serie): queda visible todo el video arriba, para que desde el primer segundo se vea que es una colección. Que no choque con los `"title"` (súbelos a y ≥ 330).
- **Seguir a mitad de video (obligatorio)**: `ov(t, "follow", y=1090, until=t + 1.8)` con `t` = cuando termina la primera razón (≈ 40 % del video), y `sfx(t, "pop", 0.6)`. Es silencioso: no lo digas en la voz. Que no tape chips ni pines en esa zona.
- Final: `"comment"` (burbuja que se escribe, `y=880`, `txt=` la respuesta de una palabra que esperas, p. ej. `"SÍ / NO"` o `"Colombia, México..."`) y `"follow"` (botón + SÍGUEME, `y=1090`) cuando la voz dice "Sígueme" en la última línea (`tw(<última línea>, "sigueme")`), no después.

**Efectos**: `sfx(t, nombre, ganancia)` con nombres: `whoosh, whoosh_fast, impact, pop, ticktock, coins, ding, stamp, lock, riser, war, shatter, bubble, horn`. Uno por evento visual, ganancia 0.5–0.9. `riser` 1 s antes de una pregunta grande.

**Zonas de pantalla** (1080×1920): títulos y = 280–560 · contenido central 600–1100 · **subtítulos en y ≈ 1230** (no tapar) · barra de progreso abajo. Deja 40 px de margen lateral; textos largos → baja `size`.

## 7. Revisar antes de renderizar (obligatorio)
```
python3 render.py preview 1.0 3.5 ...   # 18–24 tiempos repartidos en todo el video
python3 ~/mdd/kit/engine/sheets.py preview
```
Mira `out/sheet_prev*.jpg` con Read. Corrige: textos encimados, etiquetas cortadas en los bordes, pines tapados por subtítulos, fotos que no corresponden, escenas vacías más de 4 s.

## 8. Render (≈ 4–5 min)
Ejecútalo con `run_in_background: true` y espera la notificación (no uses `pgrep`/`pkill -f render.py`: se encuentran a sí mismos):
```
python3 render.py > out/render.log 2>&1
```
Genera `out/video.mp4` (con volumen normalizado a −15 LUFS). Revisa:
```
python3 ~/mdd/kit/engine/sheets.py final 0.8 4 8 12 16 20 25 30 35 40 45 <fin-1>
```
Mira `out/sheet_final.jpg`; LUFS ≈ −15 y duración entre 32 y 55 s. Comprueba que se ve la etiqueta de la serie al inicio y el botón de seguir a mitad y al final.

## 9. Portada → `cover.json`
Ver el formato en `engine/cover.py`. Foto **clara** (cielo, ciudad de día, paisaje), 2–3 líneas grandes (la pregunta o la paradoja), una píldora roja corta y una caja con el dato más llamativo (`single` o `vs`). `python3 cover.py` → `out/portada.png`. Mírala con Read.

## 10. Descripción
Primera línea: `<Nombre de la serie> #<N>`. Luego 2 frases: gancho + pregunta de una palabra o SÍ/NO para comentar. Cierra con "Sigue la serie: el próximo es <próximo episodio>." 1–3 emojis, **máximo 5 hashtags** (el país, #economia, #curiosidades y dos del tema).

## 11. Programar en Metricool (publicación automática en TikTok, Instagram, Facebook y YouTube)
Metricool necesita el video en un enlace público. Se publica en la rama **`media`** del repo dnavac/mapa-del-dinero (las *releases* de GitHub están bloqueadas en estas sesiones). Metricool copia el archivo a su servidor apenas se programa, así que la rama solo guarda lo último.
1. Archivo para TikTok (la portada como primeros 0,1 s; en cuentas personales TikTok usa el primer fotograma como portada):
   `python3 ~/mdd/kit/engine/finalize.py` → `out/publicar.mp4`
2. Súbelo a la rama `media` (reemplaza su contenido; nunca subas claves ni `.env`):
```
rm -rf /tmp/media && mkdir /tmp/media && cd /tmp/media && git init -q -b media
cp ~/mdd/kit/videos/<slug>/out/publicar.mp4 <AAAA-MM-DD>-<slug>.mp4
git add -A && git -c user.name="Diego Navarro" -c user.email="dnavac@users.noreply.github.com" commit -q -m "Media para Metricool: <slug>"
git remote add origin https://github.com/dnavac/mapa-del-dinero && git push -f origin media
```
   URL: `https://raw.githubusercontent.com/dnavac/mapa-del-dinero/media/<AAAA-MM-DD>-<slug>.mp4`. Comprueba con `curl -sIL <url> | grep -i "^HTTP/\|^content-length"` que da 200 y el mismo tamaño.
3. Metricool: marca `blogId` **7532700** (TikTok @mapadeldinero, Instagram @mapadeldinero.tv, Facebook y YouTube conectados), zona horaria `America/Bogota`. **Una sola publicación con los 4 `providers`.**
   - Horarios: turno AM → hoy **12:00**; turno PM → hoy **19:00**. Revisa con `getScheduledPosts` (hoy) que el horario esté libre; si está ocupado o faltan menos de 15 min, usa el siguiente horario libre en pasos de 30 min.
   - `createScheduledPost` con `blogId: "7532700"`, `date` en ISO con −05:00, e `info` (JSON en texto). **`tiktokData.title` es obligatorio** (el título corto del video):
     `{"autoPublish": true, "draft": false, "descendants": [], "firstCommentText": "", "hasNotReadNotes": false, "shortener": false, "smartLinkData": {"ids": []}, "media": ["<URL>"], "mediaAltText": [], "providers": [{"network": "tiktok"}, {"network": "instagram"}, {"network": "facebook"}, {"network": "youtube"}], "publicationDate": {"dateTime": "AAAA-MM-DDTHH:MM:00", "timezone": "America/Bogota"}, "text": "<descripción con máx. 5 hashtags>", "tiktokData": {"title": "<título corto>", "disableComment": false, "disableDuet": false, "disableStitch": false, "privacyOption": "PUBLIC_TO_EVERYONE", "commercialContentThirdParty": false, "commercialContentOwnBrand": false, "autoAddMusic": false, "isAigc": true}, "instagramData": {"type": "REEL", "showReelOnFeed": true, "isAiGenerated": true}, "facebookData": {"type": "REEL"}, "youtubeData": {"title": "<título del video, máx. 90 caracteres> #shorts", "type": "short", "privacy": "public", "madeForKids": false, "category": "EDUCATION"}}`
   - `isAigc` / `isAiGenerated: true` porque la voz es generada con IA (TikTok e Instagram piden declararlo).
   - **No** envíes `videoThumbnailUrl` a YouTube: el canal no está verificado y rechazaría toda la publicación.
   - Si la llamada falla por una red concreta (p. ej. YouTube), repítela quitando solo ese `provider` y su `…Data`, y dilo en la entrega.
   - Guarda el `plannerUrl` de la respuesta.
   - Si GitHub o Metricool fallan, no te detengas: entrega igual (paso 12) y di en el mensaje que la publicación automática no se hizo y por qué.

## 12. Entregar
1. `SendUserFile` con `out/video.mp4` y `out/portada.png` (status `proactive`), con un pie corto: tema y hora a la que se publica en TikTok (o "no se programó" y por qué).
2. `SendUserMessage` con: hora de publicación en TikTok y el enlace `plannerUrl` (Diego puede cancelarla desde Metricool antes de esa hora); en qué redes quedó programado (TikTok, Instagram, Facebook, YouTube); y debajo las fuentes (enlaces).
3. En Google Drive, dentro de la carpeta cuyo id viene en el mensaje de la tarea, crea un archivo de texto `MDD_hist_AAAA-MM-DD_AM|PM_<slug>` (`contentMimeType: text/plain`, `disableConversionToGoogleType: true`) con: una primera línea `Serie: <nombre> #<N>`, una segunda `Próximo anunciado: <slug>`, y luego título del video, hora programada, descripción y fuentes. Así la próxima tarea no repite el tema, sabe qué número sigue y cumple el episodio que se prometió.
