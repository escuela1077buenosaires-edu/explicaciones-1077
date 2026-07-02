#!/usr/bin/env python3
"""
Servidor local del tablero - explicaciones-1077

Sirve la interfaz HTML y recibe:
- POST /api/resolver: encolar ejercicios a resolver
- POST /api/refresh: pedir refresco desde Drive
- POST /api/eliminar: quitar item de la lista local

En AMBOS /api/resolver y /api/refresh, ademas de escribir el archivo
senal (cola.json / refresh.json), spawnea `claude -p` en background
para procesarlo sin depender de una sesion interactiva abierta.

Solo stdlib de Python.
"""

import http.server
import json
import os
import socketserver
import subprocess
import sys
from datetime import datetime

PUERTO = 8765
DIR_TABLERO = os.path.dirname(os.path.abspath(__file__))


class TableroHandler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR_TABLERO, **kwargs)

    def log_message(self, fmt, *args):
        sys.stderr.write("[%s] %s\n" % (datetime.now().strftime("%H:%M:%S"), fmt % args))

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Pragma", "no-cache")
        super().end_headers()

    def do_GET(self):
        if self.path == "/" or self.path == "":
            self.send_response(302)
            self.send_header("Location", "/central.html")
            super().end_headers()
            return
        return super().do_GET()

    def do_POST(self):
        if self.path == "/api/resolver":
            self._handle_resolver()
        elif self.path == "/api/refresh":
            self._handle_refresh()
        elif self.path == "/api/eliminar":
            self._handle_eliminar()
        else:
            self.send_error(404, "Endpoint no encontrado")

    # ================================================================
    # RESOLVER
    # ================================================================
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

            # 1) cola.json (para el Monitor si hay sesion interactiva)
            cola = {"timestamp": timestamp, "ids": data["ids"], "estado": "pendiente"}
            self._escribir_json("cola.json", cola)

            # 2) estado.json: marca los IDs como "procesando"
            estado = self._leer_estado()
            for id_ in data["ids"]:
                estado["items"][id_] = {"estado": "procesando", "timestamp": timestamp}
            estado["actualizado"] = timestamp
            self._escribir_json("estado.json", estado)

            # 3) Spawn claude -p en background (autonomo)
            spawn_ok, spawn_msg = self._spawn_claude(
                "explicaciones-1077/pipeline/prompt_resolver.md"
            )

            self._json_response(200, {
                "ok": True,
                "mensaje": "%d ejercicio(s) enviado(s) a procesar (%s)." % (len(data["ids"]), spawn_msg)
            })
        except json.JSONDecodeError:
            self._json_response(400, {"ok": False, "mensaje": "JSON invalido"})
        except Exception as e:
            self._json_response(500, {"ok": False, "mensaje": "Error interno: %s" % str(e)})

    # ================================================================
    # REFRESH
    # ================================================================
    def _handle_refresh(self):
        try:
            timestamp = datetime.now().isoformat()
            refresh = {"timestamp": timestamp, "estado": "pendiente"}
            self._escribir_json("refresh.json", refresh)

            spawn_ok, spawn_msg = self._spawn_claude(
                "explicaciones-1077/pipeline/prompt_refresh.md"
            )

            self._json_response(200, {
                "ok": True,
                "mensaje": "Buscando ejercicios nuevos en Drive... (%s)" % spawn_msg
            })
        except Exception as e:
            self._json_response(500, {"ok": False, "mensaje": "Error interno: %s" % str(e)})

    # ================================================================
    # ELIMINAR
    # ================================================================
    def _handle_eliminar(self):
        """Borra la copia LOCAL: thumb + entry en datos.json + estado.json.
        Anade el ID a eliminados.json para que refresh no lo re-baje."""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body)
            item_id = data.get("id", "").strip()
            if not item_id:
                self._json_response(400, {"ok": False, "mensaje": "Falta 'id'"})
                return

            # 1) thumb
            thumbs_dir = os.path.join(DIR_TABLERO, "thumbs")
            if os.path.isdir(thumbs_dir):
                for fname in os.listdir(thumbs_dir):
                    if fname.startswith(item_id + "."):
                        try:
                            os.remove(os.path.join(thumbs_dir, fname))
                        except Exception:
                            pass

            # 2) datos.json
            datos_path = os.path.join(DIR_TABLERO, "datos.json")
            if os.path.isfile(datos_path):
                try:
                    with open(datos_path, "r", encoding="utf-8") as f:
                        datos = json.load(f)
                    datos["items"] = [it for it in datos.get("items", []) if it.get("id") != item_id]
                    datos["actualizado"] = datetime.now().isoformat()
                    self._escribir_json("datos.json", datos)
                except Exception:
                    pass

            # 3) eliminados.json (persistente)
            eliminados_path = os.path.join(DIR_TABLERO, "eliminados.json")
            eliminados = {"ids": []}
            if os.path.isfile(eliminados_path):
                try:
                    with open(eliminados_path, "r", encoding="utf-8") as f:
                        eliminados = json.load(f)
                    if "ids" not in eliminados or not isinstance(eliminados["ids"], list):
                        eliminados = {"ids": []}
                except Exception:
                    eliminados = {"ids": []}
            if item_id not in eliminados["ids"]:
                eliminados["ids"].append(item_id)
            eliminados["actualizado"] = datetime.now().isoformat()
            self._escribir_json("eliminados.json", eliminados)

            # 4) estado.json (quitar)
            estado_path = os.path.join(DIR_TABLERO, "estado.json")
            if os.path.isfile(estado_path):
                try:
                    with open(estado_path, "r", encoding="utf-8") as f:
                        estado = json.load(f)
                    if item_id in estado.get("items", {}):
                        del estado["items"][item_id]
                        estado["actualizado"] = datetime.now().isoformat()
                        self._escribir_json("estado.json", estado)
                except Exception:
                    pass

            self._json_response(200, {
                "ok": True,
                "mensaje": "Ejercicio eliminado de la lista local. El archivo en Drive se conserva."
            })
        except json.JSONDecodeError:
            self._json_response(400, {"ok": False, "mensaje": "JSON invalido"})
        except Exception as e:
            self._json_response(500, {"ok": False, "mensaje": "Error interno: %s" % str(e)})

    # ================================================================
    # HELPERS
    # ================================================================
    def _leer_estado(self):
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

    def _spawn_claude(self, prompt_relpath):
        """Invoca 'claude -p' en background con el prompt en prompt_relpath.
        Fire-and-forget: no aguarda el resultado. Devuelve (ok, mensaje)."""
        # project_root = D:/Proyectos/ActividadesEducativas/ResolucionActividadesEduten
        project_root = os.path.abspath(os.path.join(DIR_TABLERO, "..", ".."))
        prompt_path = os.path.join(project_root, prompt_relpath)

        if not os.path.isfile(prompt_path):
            return False, "no encontre %s" % prompt_relpath
        if not os.path.isfile(os.path.join(project_root, ".mcp.json")):
            return False, "no encontre .mcp.json"

        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt = f.read()
        except Exception as e:
            return False, "no pude leer prompt: %s" % str(e)

        creationflags = 0
        if hasattr(subprocess, "CREATE_NO_WINDOW"):
            creationflags = subprocess.CREATE_NO_WINDOW  # type: ignore

        sys.stderr.write("[spawn] claude -p (%s)\n" % prompt_relpath)

        try:
            subprocess.Popen(
                ["claude", "-p", "--permission-mode", "bypassPermissions", prompt],
                cwd=project_root,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=creationflags,
                shell=False,
                close_fds=True
            )
            return True, "claude arrancado"
        except FileNotFoundError:
            try:
                subprocess.Popen(
                    'claude -p --permission-mode bypassPermissions "%s"' % prompt.replace('"', '\\"'),
                    cwd=project_root,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=creationflags,
                    shell=True,
                    close_fds=True
                )
                return True, "claude arrancado (shell)"
            except Exception as e:
                return False, "no pude arrancar claude: %s" % str(e)
        except Exception as e:
            return False, "error spawn: %s" % str(e)


def main():
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
