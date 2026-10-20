# Mapa del Dinero — kit de producción

Kit que usan las tareas programadas de Claude para producir los videos de **Mapa del Dinero** (economía y geopolítica en español, 60–90 s, vertical).

- `WORKFLOW.md`: instrucciones paso a paso (guion → voz → imágenes → escenas → render → portada → publicación en Metricool).
- `engine/`: motor de video (voz con Google TTS, tiempos con Whisper, render con PIL + ffmpeg, mapas de Natural Earth, portada).
- `ejemplos/`: guiones y escenas de videos ya publicados.
- `temas.json`: cola de temas.

Las claves de API **no** van en el repo: se pasan a `setup.sh` al arrancar.
Los videos se publican como *releases* temporales (se borran a los 7 días) para que Metricool los descargue.
