#!/usr/bin/env python3
"""
Servidor local del tablero - explicaciones-1077

Sirve la interfaz HTML del tablero y los datos snapshot de Drive,
y recibe la seleccion de ejercicios a procesar (la guarda en cola.json).

NO se comunica directamente con Google Drive ni con GitHub. Esos accesos
los hace Claude Code via sus MCPs. Este servidor es solo el puente
entre el navegador del docente y los archivos locales que Claude lee.

Usa solo biblioteca estandar de Python (sin dependencias externas).
"""

import http.server
import json
import os
import socketserver
import sys
from datetime import datetime

PUERTO = 8765
DIR_TABLERO = os.path.dirname(os.path.abspath(__file__))


class TableroHandler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR_TABLERO, **kwargs)

    def log_message(self, fmt, *args):
        # Log compacto a stderr
        sys.stderr.write("[%s] %s\n" % (datetime.now().strftime("%H:%M:%S"), fmt % args))

    def end_headers(self):
        # Evitar cache para que el navegador siempre vea la version mas reciente
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Pragma", "no-cache")
        super().end_headers()

    def do_GET(self):
        if self.path == "/" or self.path == "":
            self.send_response(302)
            self.send_header("Location", "/tablero.html")
            super().end_headers()
            return
        return super().do_GET()

    def do_POST(self):
        if self.path == "/api/resolver":
            self._handle_resolver()
        else:
            self.send_error(404, "Endpoint no encontrado")

    def _handle_resolver(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body)

            if "ids" not in data or not isinstance(data["ids"], list):
                self._json_response(400, {"ok": False, "mensaje": "Falta lista 'ids'"})
                return

            if len(data["ids"]) == 0:
                self._json_response(400, {"ok": False, "mensaje": "La seleccion esta vacia"})
                return

            timestamp = datetime.now().isoformat()

            # Escribe la cola (esto dispara el Monitor que vigila Claude Code)
            cola = {
                "timestamp": timestamp,
                "ids": data["ids"],
                "estado": "pendiente"
            }
            self._escribir_json("cola.json", cola)

            # Actualiza estado.json marcando estos IDs como "procesando".
            # El tablero polles estado.json y muestra la transicion al docente.
            estado = self._leer_estado()
            for id_ in data["ids"]:
                estado["items"][id_] = {
                    "estado": "procesando",
                    "timestamp": timestamp
                }
            estado["actualizado"] = timestamp
            self._escribir_json("estado.json", estado)

            self._json_response(200, {
                "ok": True,
                "mensaje": "%d ejercicio(s) enviado(s) a procesar. Mira el estado en el tablero." % len(data["ids"])
            })

        except json.JSONDecodeError:
            self._json_response(400, {"ok": False, "mensaje": "JSON invalido en el body"})
        except Exception as e:
            self._json_response(500, {"ok": False, "mensaje": "Error interno: %s" % str(e)})

    def _leer_estado(self):
        """Lee estado.json. Si no existe o esta vacio, devuelve estructura base."""
        path = os.path.join(DIR_TABLERO, "estado.json")
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if "items" not in data or not isinstance(data["items"], dict):
                    data["items"] = {}
                return data
            except Exception:
                pass
        return {"actualizado": None, "items": {}}

    def _escribir_json(self, nombre_archivo, datos):
        """Escritura atomica: escribe en .tmp y renombra (para que el polling no
        lea un archivo a medio escribir)."""
        path = os.path.join(DIR_TABLERO, nombre_archivo)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)

    def _json_response(self, status, payload):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))


def main():
    # Asegura que existe la carpeta thumbs/ para que no falle el primer GET
    thumbs_dir = os.path.join(DIR_TABLERO, "thumbs")
    if not os.path.isdir(thumbs_dir):
        os.makedirs(thumbs_dir)

    try:
        httpd = socketserver.ThreadingTCPServer(("127.0.0.1", PUERTO), TableroHandler)
    except OSError as e:
        print("ERROR: no se pudo abrir el puerto %d. Detalle: %s" % (PUERTO, e))
        print("Si ya tenes el tablero corriendo en otra ventana, cerra esa primero.")
        sys.exit(1)

    print("=" * 60)
    print(" Tablero corriendo en http://127.0.0.1:%d/" % PUERTO)
    print(" Ctrl+C para detener.")
    print("=" * 60)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nDeteniendo servidor del tablero.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
