# Laboratorio 7 — Teoría de la Computación

Programa en Python para validar gramáticas y eliminar producciones ε, mostrando el procedimiento en la terminal. Utiliza el constructor y simulador de AFN del Proyecto 1 para validar cada línea mediante una expresión regular.

## Archivos del programa

| Archivo | Función |
| --- | --- |
| `main.py` | Lee las gramáticas, valida su formato y elimina producciones ε. |
| `AFN_Proy_1.py` | Construye el AFN a partir de la expresión regular y simula las líneas de entrada. |
| `entrada/gramatica1.txt` | Primera gramática del Problema 2. |
| `entrada/gramatica2.txt` | Segunda gramática del Problema 2. |

`main.py`, `AFN_Proy_1.py` y la carpeta `entrada` deben estar en la misma carpeta.

## Requisitos

- Python 3.
- Archivos de entrada guardados en UTF-8.

Se utilizan `itertools.product`, `itertools.count` y `pathlib.Path`, que pertenecen a la biblioteca estándar de Python. No es necesario instalar librerías externas.

## Ejecución

Abrir una terminal en la carpeta donde se encuentra `main.py` y ejecutar:

```bash
python main.py
```

El programa carga automáticamente los dos archivos de `entrada`. Si alguna línea tiene un formato inválido, muestra el archivo, el número de línea y el error, y detiene la ejecución antes de simplificar las gramáticas.

## Formato de las gramáticas

Cada línea contiene una producción. Las alternativas se separan con `|`:

```text
S -> 0A0 | 1B1 | BB
A -> C
B -> S | A
C -> S | ε
```

- La cabeza debe ser una sola letra mayúscula de `A` a `Z`.
- Se aceptan las flechas `->` y `→`.
- Los no terminales son letras mayúsculas; los terminales son letras minúsculas de `a` a `z` o dígitos de `0` a `9`.
- La cadena vacía se escribe `ε` o `ϵ`, como alternativa completa.
- Se permiten espacios y tabulaciones alrededor de la cabeza, la flecha y los separadores `|`. Los símbolos de cada cuerpo se escriben juntos.
- No se aceptan líneas en blanco ni alternativas vacías después de `|`.

Se toma como símbolo inicial la cabeza de la primera línea.

## Eliminación de producciones ε

1. **Paso 1: anulables.** Se encuentran los no terminales anulables por iteraciones, hasta que el conjunto deja de cambiar. También se muestran las producciones anulables.
2. **Paso 2: combinaciones.** Para cada cuerpo con `m` apariciones anulables, se generan los `2^m` casos posibles. Cada bit representa una aparición: `0` la conserva y `1` la elimina. Se descartan los cuerpos vacíos y se evitan alternativas repetidas.
3. **Paso 3: resultado.** Se muestra la gramática sin producciones ε.

Cada aparición se considera por separado. Por ejemplo, `BB` tiene dos posiciones anulables si `B` es anulable, por lo que genera cuatro casos.

Si el símbolo inicial es anulable, eliminar todas las producciones ε produce el lenguaje `L(G) − {ε}`. El programa lo indica al mostrar el resultado.

## Demostración de la validación

Para mostrar un error, se puede cambiar temporalmente una línea de un archivo de entrada por:

```text
S -> a |
```

La línea es inválida porque falta una alternativa después de `|`. Al ejecutar el programa, se informa el error y se detiene la ejecución. Después se restaura la producción original y se ejecuta nuevamente.

## Parte manual

El Problema 2 se entrega en un PDF dentro de una carpeta separada llamada `manual`. Debe incluir las tres gramáticas y el procedimiento para eliminar producciones ε, producciones unarias y símbolos inútiles, y convertir el resultado a Forma Normal de Chomsky.

## Video

**https://www.youtube.com/watch?v=vfGnJcGCgN0**

El video debe durar como máximo 10 minutos y mostrar la ejecución del programa, la eliminación de producciones ε y la validación al introducir errores en las producciones.
