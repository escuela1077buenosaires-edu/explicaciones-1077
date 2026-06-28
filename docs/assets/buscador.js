/* =========================================================================
   Buscador del indice - explicaciones-1077
   Compatible con Internet Explorer 9+.
   - Sin let/const/arrow functions/fetch/template literals.
   - Carga manifest.json con XMLHttpRequest.
   - Filtra por texto sobre titulo, tema, tipo y grado.
   ========================================================================= */

(function () {

    var manifestUrl = 'manifest.json';
    var fichas = [];
    var inputBuscar, contenedorLista, mensajeSinResultados;

    // --- Utilidades ---

    function normalizar(texto) {
        if (texto === null || typeof texto === 'undefined') { return ''; }
        var s = String(texto).toLowerCase();
        // Quita acentos comunes en espanol (para que "matematica" matchee con "Matemática").
        s = s.replace(/[áàäâã]/g, 'a');
        s = s.replace(/[éèëê]/g, 'e');
        s = s.replace(/[íìïî]/g, 'i');
        s = s.replace(/[óòöôõ]/g, 'o');
        s = s.replace(/[úùüû]/g, 'u');
        s = s.replace(/ñ/g, 'n');
        return s;
    }

    function escaparHtml(texto) {
        if (texto === null || typeof texto === 'undefined') { return ''; }
        return String(texto)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function formatearGrado(grado) {
        if (typeof grado === 'number') { return grado + 'er/do grado'; }
        return String(grado || '');
    }

    // --- Carga del manifest ---

    function cargarManifest(callback) {
        var xhr = new XMLHttpRequest();
        xhr.open('GET', manifestUrl, true);
        xhr.onreadystatechange = function () {
            if (xhr.readyState !== 4) { return; }
            if (xhr.status >= 200 && xhr.status < 300) {
                try {
                    var datos = JSON.parse(xhr.responseText);
                    callback(null, datos);
                } catch (err) {
                    callback(err, null);
                }
            } else {
                callback(new Error('No se pudo cargar el manifest (HTTP ' + xhr.status + ')'), null);
            }
        };
        xhr.send();
    }

    // --- Render ---

    function tarjetaHtml(ficha) {
        var titulo = escaparHtml(ficha.titulo);
        var tema = escaparHtml(ficha.tema);
        var tipo = escaparHtml(ficha.tipo);
        var grado = escaparHtml(formatearGrado(ficha.grado));
        var url = escaparHtml(ficha.url);

        return '' +
            '<li>' +
                '<a class="tarjeta" href="' + url + '">' +
                    '<span class="t-titulo">' + titulo + '</span>' +
                    '<span class="t-meta">' +
                        '<span class="etiqueta">' + tema + '</span>' +
                        '<span class="etiqueta">' + tipo + '</span>' +
                        '<span class="etiqueta">' + grado + '</span>' +
                    '</span>' +
                '</a>' +
            '</li>';
    }

    function renderLista(lista) {
        if (!lista || lista.length === 0) {
            contenedorLista.innerHTML = '';
            mensajeSinResultados.style.display = 'block';
            return;
        }
        mensajeSinResultados.style.display = 'none';
        var html = '';
        for (var i = 0; i < lista.length; i++) {
            html += tarjetaHtml(lista[i]);
        }
        contenedorLista.innerHTML = html;
    }

    // --- Filtro ---

    function filtrar(texto) {
        var q = normalizar(texto).replace(/^\s+|\s+$/g, '');
        if (q === '') { return fichas.slice(); }

        // Divide por espacios: todas las palabras tienen que aparecer en algun campo.
        var palabras = q.split(/\s+/);
        var resultado = [];

        for (var i = 0; i < fichas.length; i++) {
            var f = fichas[i];
            var blob = normalizar(
                (f.titulo || '') + ' ' +
                (f.tema || '') + ' ' +
                (f.tipo || '') + ' ' +
                (f.grado || '')
            );
            var matchea = true;
            for (var j = 0; j < palabras.length; j++) {
                if (blob.indexOf(palabras[j]) === -1) {
                    matchea = false;
                    break;
                }
            }
            if (matchea) { resultado.push(f); }
        }
        return resultado;
    }

    function onInput() {
        renderLista(filtrar(inputBuscar.value));
    }

    // --- Arranque ---

    function init() {
        inputBuscar = document.getElementById('buscar');
        contenedorLista = document.getElementById('lista-fichas');
        mensajeSinResultados = document.getElementById('sin-resultados');

        if (!inputBuscar || !contenedorLista || !mensajeSinResultados) {
            // La pagina no tiene los elementos esperados, no hago nada.
            return;
        }

        cargarManifest(function (err, datos) {
            if (err) {
                contenedorLista.innerHTML = '';
                mensajeSinResultados.innerHTML = 'No se pudo cargar la lista de fichas.';
                mensajeSinResultados.style.display = 'block';
                return;
            }
            fichas = datos || [];
            // Orden inicial: mas recientes primero.
            fichas.sort(function (a, b) {
                var fa = String(a.fecha || '');
                var fb = String(b.fecha || '');
                if (fa > fb) { return -1; }
                if (fa < fb) { return 1; }
                return 0;
            });
            renderLista(fichas);
        });

        if (inputBuscar.addEventListener) {
            inputBuscar.addEventListener('input', onInput, false);
            inputBuscar.addEventListener('keyup', onInput, false);
        } else if (inputBuscar.attachEvent) {
            // Fallback historico para IE viejos (IE8). En IE9+ no hace falta.
            inputBuscar.attachEvent('onkeyup', onInput);
        }
    }

    if (document.addEventListener) {
        document.addEventListener('DOMContentLoaded', init, false);
    } else if (document.attachEvent) {
        document.attachEvent('onreadystatechange', function () {
            if (document.readyState === 'complete') { init(); }
        });
    } else {
        window.onload = init;
    }

})();
