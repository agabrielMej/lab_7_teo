from itertools import product
from pathlib import Path

from AFN_Proy_1 import regex_to_nfa, simulate_nfa


def crear_validador():
    letras = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    simbolos = letras + letras.lower() + "0123456789"
    cabeza = "(" + "|".join(letras) + ")"
    simbolo = "(" + "|".join(simbolos) + ")"
    espacio = "(\\ |\t)*"
    cuerpo = f"({simbolo}+|ϵ)"
    expresion = (
        f"{espacio}{cabeza}{espacio}(->|→){espacio}"
        f"{cuerpo}({espacio}\\|{espacio}{cuerpo})*{espacio}"
    )
    return regex_to_nfa(expresion)


def cargar_gramatica(ruta, validador):
    gramatica = {}

    with ruta.open("r", encoding="utf-8-sig") as archivo:
        for numero, linea in enumerate(archivo, start=1):
            linea = linea.rstrip("\r\n")
            aceptada, _ = simulate_nfa(validador, linea.replace("ε", "ϵ"))

            if not aceptada:
                raise ValueError(
                    f"{ruta.name}, línea {numero}: producción inválida {linea!r}. "
                    "Formato esperado: S -> 0A0 | 1B1 | BB | ε"
                )

            cabeza, cuerpos = linea.replace("→", "->").split("->")
            cabeza = cabeza.strip()
            gramatica.setdefault(cabeza, set())

            for cuerpo in cuerpos.split("|"):
                cuerpo = cuerpo.strip()
                gramatica[cabeza].add("" if cuerpo in {"ε", "ϵ"} else cuerpo)

    if not gramatica:
        raise ValueError(f"{ruta.name}: el archivo está vacío.")

    return gramatica


def mostrar_gramatica(gramatica):
    for cabeza, cuerpos in gramatica.items():
        if cuerpos:
            alternativas = " | ".join(cuerpo or "ε" for cuerpo in sorted(cuerpos))
            print(f"{cabeza} → {alternativas}")
        else:
            print(f"{cabeza}: sin producciones.")


def encontrar_anulables(gramatica):
    anulables = set()
    iteracion = 1

    print("\nPASO 1: ANULABLES")
    print("Conjunto inicial: ∅")

    while True:
        nuevos = set()
        print(f"\nIteración {iteracion}:")

        for cabeza, cuerpos in gramatica.items():
            if cabeza in anulables:
                continue

            for cuerpo in sorted(cuerpos):
                if all(simbolo in anulables for simbolo in cuerpo):
                    nuevos.add(cabeza)
                    print(f"{cabeza} → {cuerpo or 'ε'}")

        if not nuevos:
            print("Sin nuevos símbolos.")
            break

        anulables.update(nuevos)
        print("Anulables: {" + ", ".join(sorted(anulables)) + "}")
        iteracion += 1

    print("\nProducciones anulables:")
    producciones = [
        f"{cabeza} → {cuerpo or 'ε'}"
        for cabeza, cuerpos in gramatica.items()
        for cuerpo in sorted(cuerpos)
        if all(simbolo in anulables for simbolo in cuerpo)
    ]
    print("\n".join(producciones) if producciones else "Ninguna.")

    return anulables


def eliminar_epsilon(gramatica, anulables):
    resultado = {cabeza: set() for cabeza in gramatica}

    print("\nPASO 2: COMBINACIONES")
    print("Bits de izquierda a derecha: 0 = conservar; 1 = eliminar.")

    for cabeza, cuerpos in gramatica.items():
        for cuerpo in sorted(cuerpos):
            print(f"\nProducción: {cabeza} → {cuerpo or 'ε'}")

            if not cuerpo:
                print("Se elimina.")
                continue

            posiciones = [
                indice
                for indice, simbolo in enumerate(cuerpo)
                if simbolo in anulables
            ]
            m = len(posiciones)
            detalle = ", ".join(str(indice + 1) for indice in posiciones)

            print(f"Posiciones anulables: {detalle or 'ninguna'}")
            print(f"m = {m}; 2^{m} = {2 ** m} casos")

            for bits in product((0, 1), repeat=m):
                eliminadas = {
                    indice
                    for indice, bit in zip(posiciones, bits)
                    if bit == 1
                }
                nuevo = "".join(
                    simbolo
                    for indice, simbolo in enumerate(cuerpo)
                    if indice not in eliminadas
                )
                mascara = "".join(str(bit) for bit in bits) or "Único caso"

                if not nuevo:
                    estado = " (descartada)"
                elif nuevo in resultado[cabeza]:
                    estado = " (repetida)"
                else:
                    resultado[cabeza].add(nuevo)
                    estado = ""

                print(f"{mascara}: {nuevo or 'ε'}{estado}")

    return resultado


def principal():
    entrada = Path(__file__).resolve().parent / "entrada"
    rutas = [entrada / "gramatica1.txt", entrada / "gramatica2.txt"]

    print("VALIDACIÓN CON EL AFN DEL PROYECTO 1")

    try:
        validador = crear_validador()
        cargadas = [(ruta, cargar_gramatica(ruta, validador)) for ruta in rutas]
    except (OSError, UnicodeError, ValueError) as error:
        raise SystemExit(f"Ejecución detenida: {error}")

    print("Archivos válidos.")

    for ruta, gramatica in cargadas:
        print("\n" + "=" * 50)
        print(f"ARCHIVO: {ruta.name}")

        inicial = next(iter(gramatica))
        print(f"Símbolo inicial: {inicial}")

        print("\nGRAMÁTICA ORIGINAL")
        mostrar_gramatica(gramatica)

        anulables = encontrar_anulables(gramatica)
        resultado = eliminar_epsilon(gramatica, anulables)

        print("\nPASO 3: GRAMÁTICA SIN PRODUCCIONES ε")
        mostrar_gramatica(resultado)

        if inicial in anulables:
            print("\nLenguaje resultante: L(G) − {ε}.")


if __name__ == "__main__":
    principal()