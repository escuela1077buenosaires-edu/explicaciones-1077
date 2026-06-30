# appscript/

Web app de subida de ejercicios para alumnos. **Fase 2** del proyecto.

## Qué hace

Genera una URL pública (tipo `https://script.google.com/macros/s/.../exec`) que el alumno abre desde cualquier celular o computadora **sin login ni cuenta de Google**. El alumno:

1. Pone el código de la clase (anti-spam mínimo).
2. Elige su grado (dropdown 1-7).
3. Saca o sube una foto del ejercicio.
4. (Opcional) Escribe "qué no entiendo".
5. Click **Enviar al profe**.

La imagen queda en la carpeta `EjerciciosEduten` del Drive de la escuela, con el grado y la consigna del alumno guardados en la descripción del archivo. El docente la va a ver al refrescar el tablero local.

## Archivos

| Archivo | Va en Apps Script como |
|---|---|
| [`Code.gs`](Code.gs) | Script (`.gs`) |
| [`Form.html`](Form.html) | HTML (`.html`) |

## Cómo deployar (5-10 minutos, en red de confianza)

⚠ **Hacelo en una red de confianza**, no en una red pública. El deploy involucra tu sesión de Google en el browser.

### Paso 1 — Crear el proyecto en Apps Script

1. Andá a https://script.google.com **logueado con la cuenta de la escuela** (`escuela1077buenosaires@gmail.com`).
2. Click en **"+ Nuevo proyecto"**.
3. Cambiale el nombre (arriba a la izquierda donde dice "Untitled project") a algo como `explicaciones-1077-subida`.

### Paso 2 — Pegar el código

1. En el panel izquierdo vas a ver un archivo llamado `Código.gs` (o `Code.gs`).
2. Borrá todo lo que tenga adentro y **pegá el contenido de [`Code.gs`](Code.gs)** de este repo.
3. Verificá que la línea `const DRIVE_FOLDER_ID = '1S6DB8GD2A5gAzYNyKInuCOr-kBXHxXod';` tenga el ID correcto de tu carpeta `EjerciciosEduten`. Si la creaste de nuevo, cambiá el ID.
4. Verificá la línea `const CLASS_CODE = '1077';` y cambiala si querés otro código de clase.
5. Guardá con **Ctrl+S**.

### Paso 3 — Agregar el archivo HTML

1. En el panel izquierdo, click en el **`+`** al lado de "Files" → **"HTML"**.
2. Nombralo exactamente **`Form`** (sin extensión, Apps Script le pone `.html` solo).
3. Borrá lo que tenga adentro y **pegá el contenido de [`Form.html`](Form.html)** de este repo.
4. Guardá con **Ctrl+S**.

### Paso 4 — Autorizar el script

La primera vez que el script accede a Drive, Google te pide autorización. Esto es **una vez sola**.

1. Click en el botón **"Ejecutar"** (▶ play) arriba.
2. Elegí la función `doGet` y dale **Ejecutar**.
3. Aparece un cartel **"Se requiere autorización"** → click **Revisar permisos**.
4. Te muestra la cuenta de Google — elegí la de la escuela.
5. Posiblemente diga **"Google no verificó esta app"** porque es tuya — click **Avanzado** → **Ir a explicaciones-1077-subida (no seguro)**.
6. Click **Permitir** para que el script pueda leer/escribir tu Drive.

### Paso 5 — Deployar como web app

1. Arriba a la derecha, click **"Implementar"** (Deploy) → **"Nueva implementación"**.
2. Click en el ícono del engranaje al lado de "Seleccionar tipo" → elegí **"Aplicación web"**.
3. Configurá:
   - **Descripción**: `Subida de ejercicios v1` (o lo que quieras).
   - **Ejecutar como**: **`Yo` (escuela1077buenosaires@gmail.com)**.
     - ⚠ Esto es importante: hace que las imágenes se suban a TU Drive, no a la de cada alumno.
   - **Quién tiene acceso**: **`Cualquier persona`**.
     - ⚠ Esto permite acceso anónimo. Si la opción no aparece, asegurate de que el dominio de tu cuenta de la escuela esté configurado para permitirlo (cuentas personales gmail.com sí lo permiten).
4. Click **Implementar**.
5. Google te muestra una **URL** larga tipo `https://script.google.com/macros/s/AKfycb.../exec`. **Esa es la URL que les das a los alumnos.**

### Paso 6 — Probar

1. Abrí la URL en **una ventana incógnita** del navegador (para simular que no estás logueado).
2. Deberías ver el formulario.
3. Pone código `1077`, elegí un grado, subí una foto cualquiera, dale enviar.
4. Andá al Drive `EjerciciosEduten` y verificá que la foto esté ahí con el nombre `ejercicio-<timestamp>-g<grado>.jpg`.
5. Abrí el tablero local (ejecutar.bat), pedile a Claude "actualizá el tablero" — deberías verla en la lista.

### Paso 7 — Compartir con los alumnos

Mandales la URL (por la app de mensajería que uses con ellos, o un QR pegado en el aula). **Recordales el código `1077`** (o el que hayas puesto).

## Modificaciones útiles

- **Cambiar el código de clase**: editar la línea `CLASS_CODE` en `Code.gs`, guardar, y re-deployar como **"Nueva versión"** desde el menú Implementar → Administrar implementaciones.
- **Agregar más grados** (ej. secundaria): agregar `<option>` en `Form.html`.
- **Aceptar archivos PDF también**: cambiar `accept="image/*"` por `accept="image/*,application/pdf"` en `Form.html`, y validar en `Code.gs`.

## Importante — privacidad y seguridad

- El URL público permite que **cualquiera** suba archivos. El código de clase es el único freno. Si te llega spam, **cambiá el código y re-deployá** (los URLs viejos quedan obsoletos, los nuevos requieren el código nuevo).
- Los archivos quedan en TU Drive (cuenta de la escuela). El alumno no necesita cuenta. **Ningún dato del alumno se publica** automáticamente — eso lo controlás vos al revisar el tablero antes de procesar.
- Si el alumno escribe su nombre en "qué no entiendo", queda en la descripción del archivo en Drive. Cuando el tablero te muestra esa consigna, **no la transcribís a la ficha publicada** — el agente Generador tiene esa regla.
