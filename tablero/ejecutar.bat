@echo off
REM ============================================================
REM  Tablero - explicaciones-1077
REM  Levanta el servidor local del tablero y abre el navegador.
REM  Tene Claude Code corriendo en este proyecto para que
REM  procese los ejercicios que selecciones.
REM ============================================================

title Tablero - explicaciones-1077

cd /d "%~dp0"

REM Abre el navegador apuntando al tablero. Si el server tarda
REM unos segundos en arrancar, refresca con F5.
start "" "http://127.0.0.1:8765/"

echo.
echo ============================================================
echo  Tablero corriendo en http://127.0.0.1:8765/
echo.
echo  IMPORTANTE:
echo    1. Tene Claude Code abierto en la carpeta del proyecto:
echo       D:\Proyectos\ActividadesEducativas\ResolucionActividadesEduten
echo.
echo    2. Decile UNA vez al arrancar: "inicia tablero"
echo       (eso hace que actualice los datos y empiece a vigilar
echo        tus selecciones).
echo.
echo    3. Despues, en el navegador, marca los ejercicios y dale
echo       "Resolver Ejercicio" - Claude los procesa solo.
echo.
echo  Para apagar todo: cerra esta ventana (o Ctrl+C).
echo ============================================================
echo.

python servidor.py

REM Si python no esta en el PATH o falla:
if errorlevel 1 (
    echo.
    echo ERROR: no se pudo arrancar el servidor.
    echo Verifica que Python este instalado y accesible como 'python'.
    pause
)
