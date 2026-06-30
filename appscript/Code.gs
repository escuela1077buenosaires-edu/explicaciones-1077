/**
 * Apps Script - Web app de subida de ejercicios para alumnos
 * explicaciones-1077 / Escuela 1077
 *
 * Este script se deploya como una "web app" anonima:
 * - "Ejecutar como": yo (el docente que lo deploya)
 * - "Quien tiene acceso": Cualquiera
 *
 * El alumno NO necesita cuenta de Google ni login. Sube una foto + grado +
 * (opcional) numero de ejercicio, y queda en la carpeta EjerciciosEduten
 * del Drive del docente. Despues el docente revisa en el tablero local.
 *
 * Ver appscript/README.md para los pasos de deploy.
 */

/** ID de la carpeta de Drive donde se guardan las imagenes subidas.
 *  Es la carpeta "EjerciciosEduten" del Drive de la cuenta
 *  escuela1077buenosaires@gmail.com. */
const DRIVE_FOLDER_ID = '1S6DB8GD2A5gAzYNyKInuCOr-kBXHxXod';

/** Tamano maximo aceptado del archivo subido (10 MB). */
const MAX_FILE_BYTES = 10 * 1024 * 1024;


/**
 * Endpoint GET: sirve el formulario HTML.
 */
function doGet() {
  return HtmlService.createTemplateFromFile('Form')
    .evaluate()
    .setTitle('Subir ejercicio - Escuela 1077')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}


/**
 * Procesa el upload desde el formulario (lo llama google.script.run del
 * cliente HTML). Devuelve {ok: bool, mensaje: string}.
 */
function uploadFile(formObject) {
  try {
    // Validaciones basicas
    if (!formObject.foto) {
      return { ok: false, mensaje: 'Hace falta que subas una foto del ejercicio.' };
    }
    if (!formObject.grado) {
      return { ok: false, mensaje: 'Elegí en que grado estás.' };
    }

    var blob = formObject.foto;

    // Tamano
    var sizeBytes = blob.getBytes().length;
    if (sizeBytes > MAX_FILE_BYTES) {
      return {
        ok: false,
        mensaje: 'La foto es muy grande (max 10 MB). Sacala con menos resolucion o recortala.'
      };
    }

    // Tipo de archivo
    var mime = blob.getContentType();
    if (!mime || mime.indexOf('image/') !== 0) {
      return {
        ok: false,
        mensaje: 'Tiene que ser una imagen (jpg, png, heic, etc).'
      };
    }

    // Numero de ejercicio (opcional)
    var numeroRaw = (formObject.numero || '').toString().trim();
    var numero = null;
    if (numeroRaw !== '') {
      var n = parseInt(numeroRaw, 10);
      if (!isNaN(n) && n > 0) {
        numero = n;
      }
    }

    // Nombre con timestamp + grado + (opcional) numero
    var tz = 'America/Argentina/Buenos_Aires';
    var timestamp = Utilities.formatDate(new Date(), tz, 'yyyyMMdd-HHmmss');
    var ext = mime.split('/')[1].toLowerCase();
    if (ext === 'jpeg') ext = 'jpg';
    var fileName = 'ejercicio-' + timestamp + '-g' + formObject.grado;
    if (numero !== null) {
      fileName += '-n' + numero;
    }
    fileName += '.' + ext;

    // Sube a Drive
    var folder = DriveApp.getFolderById(DRIVE_FOLDER_ID);
    var file = folder.createFile(blob).setName(fileName);

    // Metadata en la descripcion (la lee Claude al armar el tablero)
    var lines = [
      'Grado: ' + formObject.grado,
      'Subido: ' + new Date().toISOString()
    ];
    if (numero !== null) {
      lines.push('Numero de ejercicio: ' + numero);
    }
    file.setDescription(lines.join('\n'));

    return {
      ok: true,
      mensaje: '¡Listo! Tu profe lo va a revisar y va a publicar la explicacion en el sitio. Volve en un rato a la pagina de explicaciones de la escuela.'
    };

  } catch (e) {
    Logger.log('Error en uploadFile: ' + (e.stack || e.message || e));
    return {
      ok: false,
      mensaje: 'Hubo un problema al subir. Decile al profe.'
    };
  }
}
