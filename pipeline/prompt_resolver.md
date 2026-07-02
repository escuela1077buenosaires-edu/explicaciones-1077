# Resolver ejercicios de la cola — instrucciones para Claude en modo -p

Estás siendo invocado en modo **headless** (`claude -p`) desde el servidor
Python del tablero, tras un click en "Resolver Ejercicio". No hay chat —
hacé el trabajo y salí.

## Objetivo

Procesar cada ejercicio pendiente en `tablero/cola.json`, generar su ficha
HTML (Generador + Revisor), publicar en GitHub Pages via MCP, y actualizar
`tablero/estado.json` con el resultado.

## Constantes

- **cola.json:** `explicaciones-1077/tablero/cola.json`
- **estado.json:** `explicaciones-1077/tablero/estado.json`
- **datos.json:** `explicaciones-1077/tablero/datos.json`
- **thumbs:** `explicaciones-1077/tablero/thumbs/`
- **template ficha:** `explicaciones-1077/plantilla/ficha-template.html`
- **manifest publicado:** `explicaciones-1077/docs/manifest.json`
- **fichas publicadas:** `explicaciones-1077/docs/ej/`
- **GitHub MCP:** `mcp__github-explicaciones__push_files`
- **Owner/repo/branch:** `escuela1077buenosaires-edu` / `explicaciones-1077` / `main`

## Pasos exactos

### 1. Leer la cola

Leé `tablero/cola.json`. Los IDs en el campo `ids` son los que hay que
procesar. Si `estado` es "procesado" o el array está vacío, no hagas nada
y salí.

### 2. Leer contexto local

- `tablero/datos.json` para grado, número de ejercicio, título de cada ID.
- `tablero/thumbs/<id>.<ext>` para acceder a la imagen ya descargada.
- `docs/manifest.json` para elegir un ID de ficha nuevo y evitar colisiones.

### 3. Para cada ID en la cola

#### 3.1 Aplicar el Agente Generador
(Ver `pipeline/AGENTES.md` para la definición completa.)

- Leé la imagen en `tablero/thumbs/<id>.<ext>` — usá la tool Read.
- Re-redactá la consigna (NO copiada literal).
- Clasificá: tema, tipo, grado.
- Diseñá un ejemplo más fácil, con solución paso a paso.
- Diseñá los pasos del ejercicio real, 3-6 pasos atómicos.
- Elegí un slug + contador para el ID de la ficha (ej. `suma-simple-002`).

#### 3.2 Aplicar el Agente Revisor-Corrector
(Ver `pipeline/AGENTES.md`.)

- Verificá cuentas, dificultad del ejemplo, completitud de pasos, lenguaje.
- Corregí en el lugar si hace falta. **NO abortes** por minucias.
- Cero datos del alumno filtrados.

#### 3.3 Escribir la ficha HTML

Basado en el template. Reemplazá los placeholders con el contenido generado.
Escribí a `docs/ej/<ficha-id>.html`.

#### 3.4 Actualizar el manifest

Leé `docs/manifest.json`, agregá la nueva entry AL PRINCIPIO del array
(más reciente primero), escribí de vuelta.

#### 3.5 Publicar via MCP

Llamá `mcp__github-explicaciones__push_files` con:
- `owner`: "escuela1077buenosaires-edu"
- `repo`: "explicaciones-1077"
- `branch`: "main"
- `message`: "Ficha <ficha-id>: <titulo>\n\nTema: <tema>. Grado: <grado>. Generada desde imagen de alumno (anonimizada, re-redactada)."
- `files`: [{path: "docs/ej/<ficha-id>.html", content: <html>}, {path: "docs/manifest.json", content: <manifest>}]

Guardá el commit SHA que devuelve.

#### 3.6 Actualizar estado.json

Leé estado.json. Para el ID procesado, cambiá su entry a:
```json
{
  "estado": "procesado",
  "timestamp": "<ISO ahora>",
  "url": "https://escuela1077buenosaires-edu.github.io/explicaciones-1077/ej/<ficha-id>.html",
  "ficha_id": "<ficha-id>",
  "commit_sha": "<sha>"
}
```
Actualizá `estado.actualizado`. Escribí de vuelta.

### 4. Sincronizar el repo local

Después de todos los pushes:
```
cd explicaciones-1077 && git fetch origin && git reset --hard origin/main
```

**Cuidado**: NO hagas reset si hay cambios locales no pushados que se
podrían perder. Chequeá `git status` primero. Si hay cambios sin push,
NO hagas reset y logueá un warning.

### 5. Marcar la cola como procesada

Escribí `tablero/cola.json` con `estado: "procesado"`, dejando los IDs
como están (para referencia).

## Reglas inviolables

1. **Cero datos del alumno en lo publicado.**
2. **NO copia literal** de la imagen original.
3. **NO commit ni push** si hay cambios locales que no vinieron por vos
   (chequeá `git status` antes del reset).
4. **NO borres** archivos de Drive.
5. **No agregues resúmenes** al final. Hacé el trabajo y salí.
6. Si algo falla en un ID, marcalo como `"estado": "error"` en estado.json
   con `mensaje` y seguí con los demás.
