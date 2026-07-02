# Refresh del tablero — instrucciones para Claude en modo -p

Estás siendo invocado en modo **headless** (`claude -p`) desde el servidor
Python del tablero. No hay usuario esperando en un chat — hacé el trabajo
en silencio y salí.

## Objetivo

Actualizar `explicaciones-1077/tablero/datos.json` con los archivos actuales
del folder `EjerciciosEduten` en Google Drive. Descargar thumbnails de los
que sean nuevos.

## Constantes

- **Drive folder ID:** `1S6DB8GD2A5gAzYNyKInuCOr-kBXHxXod`
- **Drive folder nombre:** `EjerciciosEduten`
- **Cuenta:** `escuela1077buenosaires@gmail.com`
- **datos.json:** `explicaciones-1077/tablero/datos.json`
- **thumbs dir:** `explicaciones-1077/tablero/thumbs/`

## Pasos exactos

### 1. Leer estado actual

Leé `explicaciones-1077/tablero/datos.json`. Anotá qué IDs ya están en la
lista de items.

**También leé `explicaciones-1077/tablero/eliminados.json` si existe.**
Ese archivo tiene la forma `{"ids": ["id1", "id2", ...], "actualizado": ...}`.
Esos IDs son de archivos que el docente eliminó manualmente de la lista local
— **NO los vuelvas a traer aunque sigan en Drive**. Los ignorás por completo.

### 2. Consultar Drive

Llamá `mcp__80b532c6-f680-4c21-9ff7-06792bdee891__search_files` con:
- `query`: `"parentId = '1S6DB8GD2A5gAzYNyKInuCOr-kBXHxXod'"`
- `pageSize`: 50
- `excludeContentSnippets`: true

### 3. Detectar nuevos

Compará: los IDs que aparecen en la respuesta de Drive pero NO estaban en
datos.json Y NO están en `eliminados.json` son los archivos nuevos que hay
que descargar.

Regla estricta: **si un ID está en `eliminados.json`, lo salteas siempre**,
aunque no esté en datos.json.

Si NO hay nuevos, saltá al paso 5 (solo actualizás la timestamp).

### 4. Descargar y guardar thumbnails de los nuevos

Para cada archivo nuevo:

a. Llamá `mcp__80b532c6-f680-4c21-9ff7-06792bdee891__download_file_content`
   con `fileId` = el ID del archivo. Si el resultado es muy grande, el MCP
   te lo va a guardar en un archivo temp — te va a decir la ruta.

b. Usá Bash + Python para decodificar el base64 y guardar como imagen:
   ```
   python -c "import json,base64; d=json.load(open('<ruta_temp>','r',encoding='utf-8')); open('explicaciones-1077/tablero/thumbs/<id>.<ext>','wb').write(base64.b64decode(d['content']))"
   ```
   Usá `<ext>` = el campo `fileExtension` del metadata, en minusculas.

c. Parseá el campo `description` del metadata para extraer:
   - `Grado: N` → grado (int)
   - `Numero de ejercicio: N` → numero_ejercicio (int)

### 5. Escribir datos.json

Construí y escribí `explicaciones-1077/tablero/datos.json` con esta estructura:

```json
{
  "actualizado": "<timestamp ISO UTC actual>",
  "fuente": {
    "drive_folder_id": "1S6DB8GD2A5gAzYNyKInuCOr-kBXHxXod",
    "drive_folder_nombre": "EjerciciosEduten",
    "cuenta": "escuela1077buenosaires@gmail.com"
  },
  "items": [
    {
      "id": "<file id>",
      "titulo": "<file title>",
      "thumb": "/thumbs/<id>.<ext>",
      "subido_str": "<yyyy-MM-dd HH:mm UTC>",
      "tamano_bytes": <fileSize as int>,
      "mime_type": "<mimeType>",
      "grado": <parsed int o null>,
      "numero_ejercicio": <parsed int o null>,
      "consigna": null,
      "view_url": "<viewUrl>"
    }
  ]
}
```

Los items van **ordenados por `createdTime` descendente** (nuevos primero).

**Importante:** para los items que ya estaban en datos.json, preservá los
campos que ya tenían (no los re-descargues, no los re-parsees). Solo agregá
los nuevos y reordená.

**La timestamp `actualizado`** SIEMPRE se actualiza, aunque no haya archivos
nuevos — el tablero polles ese campo para saber que respondiste.

## Reglas inviolables

1. **NO hagas `git commit`, NO llames a GitHub, NO uses `mcp__github-explicaciones__*`.**
2. **NO borres nada de Drive** (no llames create/copy/etc del MCP de Drive).
3. **NO toques nada fuera de `explicaciones-1077/tablero/`.**
4. **No agregues resúmenes ni explicaciones** al final. Hacé el trabajo y salí.
5. Si algo falla (p. ej. Drive MCP no responde), escribí una línea al
   stdout diciendo qué falló y terminá con exit code distinto a 0.
