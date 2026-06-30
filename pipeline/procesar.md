# Procedimiento de procesado — explicaciones-1077

Este documento describe el **flujo operativo completo** para procesar una
imagen de ejercicio y publicarla. Es el "manual del motor" de la Fase 1.

> **Lectura para el docente:** las secciones 1 y 2 te dicen qué tenés que
> hacer vos. El resto es para Claude Code, que lo sigue al pie de la letra.

---

## 1. Cómo invocar el procesado (para el docente)

### Modo A — Imagen en `/entrada/` (lo que hace el flujo "real" en Fase 3)

1. Dejá la imagen del ejercicio en `entrada/` (carpeta dentro del repo,
   ya está en `.gitignore` así que **nunca llega a GitHub**).
2. Abrí una sesión de Claude Code en `D:\Proyectos\ActividadesEducativas\ResolucionActividadesEduten`.
3. Decime algo así: **"procesá lo que hay en `/entrada/`"**.
   - Si querés especificar grado: "procesá lo de entrada, es de 4to grado".
   - Si querés pasar la consigna del alumno: "procesá lo de entrada, el
     alumno dijo 'no entiendo cómo se hace la división'".
4. Yo proceso, te muestro qué generé, vos aprobás o pedís cambios, publico.

### Modo B — Imagen pegada directo en el chat (lo más rápido para test)

1. Arrastrá la imagen al chat de Claude Code.
2. Decime: **"procesá esta imagen, es de Xto grado"**.
3. Mismo flujo que A desde acá.

---

## 2. Qué tenés que aprobar antes de publicar (siempre)

Cuando termine de generar+revisar, te muestro:

- **La consigna re-redactada** (texto plano).
- **El ejemplo elegido** (qué números usé y por qué es más fácil).
- **Los pasos** (uno por renglón).
- **El reporte del revisor** (qué corrigió, si corrigió algo).
- **Los metadatos** (id, tema, tipo, grado, fecha).

**Vos confirmás** ("dale" / "publicá") o pedís cambios. **Nada se publica
sin tu OK.**

---

## 3. Flujo paso a paso (para Claude Code)

Cuando el docente pide procesar, hago **exactamente esto**, en orden:

### Paso 1 — Inventario
- `ls D:\Proyectos\ActividadesEducativas\ResolucionActividadesEduten\explicaciones-1077\entrada\`
  para ver qué imágenes hay.
- Si el docente pegó la imagen en chat, esa es la entrada.
- Si hay más de una imagen, las proceso de a una, en orden alfabético del
  nombre del archivo.

### Paso 2 — Generador
- Aplico el **Agente Generador** descrito en [AGENTES.md](AGENTES.md),
  paso A hasta G.
- Produzco el HTML completo y la entrada de manifest.

### Paso 3 — Revisor
- Aplico el **Agente Revisor-Corrector** descrito en [AGENTES.md](AGENTES.md).
- Aplico correcciones en el lugar si hace falta.
- Genero el reporte interno de qué cambié.

### Paso 4 — Presentación al docente para aprobación
- Le muestro: consigna re-redactada, ejemplo, pasos, reporte del revisor,
  metadatos.
- **ESPERO confirmación explícita.** No publico nada sin OK.
- Si el docente pide cambios, los aplico y vuelvo a mostrar.

### Paso 5 — Escritura local
- Escribo `docs/ej/<id>.html` con el HTML final.
- Leo `docs/manifest.json`, agrego la nueva entrada (al principio del
  array — orden más recientes primero), escribo el manifest actualizado.

### Paso 6 — Publicación vía MCP
- Uso `mcp__github-explicaciones__push_files` con los archivos nuevos o
  modificados:
  - `docs/ej/<id>.html` (nuevo)
  - `docs/manifest.json` (modificado)
- Commit message:
  ```
  Ficha <id>: <titulo>

  Tema: <tema>. Grado: <grado>. Generada desde imagen de alumno
  (anonimizada, re-redactada).
  ```
- Owner: `escuela1077buenosaires-edu`, repo: `explicaciones-1077`,
  branch: `main`.

### Paso 7 — Sincronización local
- `cd` al repo local.
- `git fetch origin && git reset --hard origin/main` para que el repo
  local quede alineado con lo publicado.
- (Antes de reset, verifico que no haya cambios sin commitear que se
  vayan a perder. Si hay, paro y consulto.)

### Paso 8 — Verificación final
- Llamo `mcp__github-explicaciones__list_commits` para confirmar que el
  commit nuevo está arriba.
- Le paso al docente la URL pública de la ficha:
  `https://escuela1077buenosaires-edu.github.io/explicaciones-1077/ej/<id>.html`
- Recordatorio: GitHub Pages tarda 30-90 segundos en re-publicar.

### Paso 9 — Limpieza (SOLO en Fase 4, NO ahora)
- En la Fase 1 NO borro la imagen de `/entrada/` automáticamente — la
  dejo para que el docente revise.
- En la Fase 4 esto cambia: la imagen original (que vendrá del Drive del
  alumno) se borra tras commit confirmado.

---

## 4. Manejo de errores

- **No puedo leer la imagen** → le aviso al docente, pregunto si me la
  puede pegar directo en chat o re-encodear.
- **Consigna ambigua o incomprensible** → le aviso al docente con una
  pregunta concreta. No invento contenido.
- **Push falla (MCP da error)** → no toco el repo local. Le aviso al
  docente, mostrando el error. Re-intento solo con OK explícito.
- **Conflicto de ID** (ya existe un archivo con ese nombre) → incremento
  el contador y reintento (no sobrescribo silenciosamente).

---

## 5. Lo que NO hace el motor en Fase 1

- **No toca AppScript ni Drive.** Eso es Fase 2.
- **No usa el tablero local.** Eso es Fase 3.
- **No borra imágenes de `/entrada/`** automáticamente. Eso es Fase 4.
- **No procesa imágenes desde URL externa.** Solo archivos locales o
  pegados en chat.

---

## 6. Para el docente — cuándo está pasando qué

| Lo que hacés vos | Lo que hago yo |
|---|---|
| Dejás imagen en `/entrada/` | Nada todavía |
| Me decís "procesá" | Leo, genero, reviso (~30-60s) |
| Te muestro el resultado | Espero tu OK |
| Decís "dale" | Publico vía MCP + sync local (~10s) |
| Te paso la URL pública | Esperás 30-90s a que Pages la publique |
