# explicaciones-1077

Sitio con explicaciones paso a paso de ejercicios de la plataforma Eduten, pensado para alumnos de primaria de la Escuela 1077 de Buenos Aires.

**Sitio publicado:** https://escuela1077buenosaires-edu.github.io/explicaciones-1077/

## Como funciona

1. El alumno sube una foto del ejercicio que no entiende (web app de subida).
2. La docente revisa los pedidos en un tablero local y elige cuales resolver.
3. Un motor local genera una ficha explicativa con tres bloques:
   - **La consigna** (re-redactada con palabras claras).
   - **Mira este ejemplo** (un ejercicio parecido pero mas facil, resuelto).
   - **Ahora el tuyo, paso a paso** (pasos cortos y numerados).
4. La ficha se publica en este sitio. **Ningun dato del alumno aparece publicado.**

## Estructura

```
docs/         <- lo unico que se publica como sitio (GitHub Pages)
plantilla/    <- plantilla base de las fichas
pipeline/     <- motor local de resolucion (no se publica)
tablero/      <- interfaz local de revision (no se publica)
local/        <- archivos privados (no versionados)
```

## Compatibilidad

El sitio funciona en navegadores modernos **y** en Internet Explorer 9 o superior (netbooks del programa Conectar Igualdad con Windows 7).
