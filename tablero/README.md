# tablero/

Interfaz local de revisión y procesado de ejercicios pendientes.

## Cómo se usa (para el docente)

1. **Doble click** en [`ejecutar.bat`](ejecutar.bat).
   - Se abre una ventana negra (servidor) — **no la cierres** mientras uses el tablero.
   - Se abre el navegador en `http://127.0.0.1:8765/` con el tablero visual.

2. **Tené Claude Code abierto** en la carpeta del proyecto.
   - Decile **una sola vez** al empezar: **"iniciá tablero"**.
   - Eso hace que Claude:
     - Lea la carpeta `EjerciciosEduten` del Drive de la escuela vía MCP.
     - Baje los thumbnails y arme el snapshot (`datos.json` + `thumbs/`).
     - **Empiece a vigilar `cola.json`** para procesar lo que selecciones.

3. **En el navegador**:
   - Vas a ver los ejercicios pendientes con thumbnails y checkboxes.
   - Marcá los que querés resolver → click **"Resolver Ejercicio"**.
   - Claude los procesa automáticamente (Generador → Revisor → publica en GitHub Pages).

4. **Cuando termines**: cerrá la ventana negra del servidor para apagar todo.

## Arquitectura interna

```
ejecutar.bat
   └─> arranca servidor.py (Python stdlib) en localhost:8765
       └─> sirve tablero.html, datos.json y thumbs/

Navegador (tablero.html)
   └─> POST /api/resolver con la selección
       └─> servidor.py escribe cola.json

Claude Code (en otra ventana)
   └─> Monitor vigilando cola.json
       └─> cada vez que cambia → procesa la cola → publica via MCP de GitHub
```

## Archivos generados (no versionados)

Estos viven solo localmente, están en `.gitignore`:

| Archivo | Quién lo escribe | Para qué |
|---|---|---|
| `datos.json` | Claude (al hacer "iniciá tablero" o "actualizá tablero") | Snapshot de Drive: lista de ejercicios + metadata |
| `thumbs/*` | Claude | Thumbnails de cada imagen para mostrar en el tablero |
| `cola.json` | El servidor (al apretar "Resolver Ejercicio") | Selección a procesar; Claude lo lee y procesa |

## Por qué hace falta Claude Code corriendo

Por la restricción "cero API paga" del proyecto: el análisis de las imágenes y la redacción de las fichas las hace **Claude Code bajo la suscripción del docente**, no un script Python automático. Por eso el servidor Python es solo un puente — todo el trabajo "inteligente" pasa en Claude Code.

## Si algo falla

- **El navegador dice "No se puede acceder al sitio"** → la ventana negra del servidor se cerró. Volvé a hacer doble click en `ejecutar.bat`.
- **El tablero dice "No hay datos.json todavia"** → no hiciste el paso 2 (decirle a Claude "iniciá tablero"). Hacelo y refrescá la página.
- **No aparecen ejercicios nuevos** → revisá que estén en la carpeta correcta de Drive (`EjerciciosEduten`), y pedile a Claude "actualizá el tablero" para refrescar el snapshot.
- **Apreté "Resolver" pero no pasa nada** → fijate en la ventana de Claude Code que esté procesando. Si no, capaz cerraste la sesión.
