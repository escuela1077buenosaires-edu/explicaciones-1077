# local/

Esta carpeta contiene archivos **locales y privados** que NO se versionan ni se publican.

Todo lo que se ponga acá adentro (excepto este README) queda fuera de Git gracias al `.gitignore` de la raíz.

## Qué va acá

- `config.json` — clave secreta del web app de Apps Script y otras credenciales.
- Logs del motor de procesamiento.
- Caché temporal de imágenes ya procesadas.
- Notas personales del docente.

## Por qué

El repo es **público** (necesario para GitHub Pages gratuito). Cualquier archivo fuera de `local/` con datos sensibles puede terminar publicado por error. Esta carpeta es la zona segura.
