# entrada/

Carpeta **dummy de pruebas** para la Fase 1 del motor.

## Para qué es

En el flujo real (Fase 3 en adelante), las imágenes de ejercicios vienen
del Drive privado de la escuela, traídas por el tablero local de revisión.

**Mientras el tablero no existe**, esta carpeta sirve como **stand-in**:
el docente deja acá las imágenes que quiere procesar, y le pide a Claude
Code que las tome.

## Cómo se usa (Fase 1)

1. Pegá una imagen acá (`.jpg`, `.png`, `.pdf`, `.heic`).
2. Abrí Claude Code y decile: "procesá lo que hay en `/entrada/`".
3. Sigue el flujo descrito en [`../pipeline/procesar.md`](../pipeline/procesar.md).

## Privacidad — qué pasa con las imágenes que dejes acá

- Esta carpeta está en `.gitignore` (línea `entrada/` en el `.gitignore`
  raíz). **NUNCA llega al repositorio público.**
- En la Fase 1, las imágenes se quedan acá hasta que vos las borres
  manualmente.
- En la Fase 4 (cierre del circuito), las imágenes se borran
  automáticamente tras publicar la ficha — pero por ahora, vos las
  manejás a mano.

## Importante

- **No dejes acá imágenes que tengan datos sensibles del alumno** que no
  hagan falta para entender el ejercicio. Si hay un nombre, una firma o
  una foto del alumno en la imagen, recortalo antes de pegarlo acá.
- Igualmente, el motor tiene la regla de **no transcribir datos del
  alumno** a la ficha publicada — pero por defensa en profundidad,
  conviene minimizar la exposición desde la fuente.
