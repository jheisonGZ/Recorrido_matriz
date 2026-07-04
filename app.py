import json
from flask import Flask, render_template, request

app = Flask(__name__)

numeros = [
    [4, 3, 5, 8],
    [7, 10, 0, 14],
    [6, 0, 11, 4],
    [9, 3, 0, 0],
]

OPCIONES = [
    "Opción 1: sumar una zona de la tabla",
    "Opción 2: contar según el tamaño del número",
    "Opción 3: sumar los números especiales",
]

OPCIONES_PARA_TEMPLATE = [(i, texto) for i, texto in enumerate(OPCIONES)]


def construir_pasos(opcion):
    pasos = []
    resultado = 0
    for fila in range(4):
        for columna in range(4):
            numero = numeros[fila][columna]

            if opcion == 0:
                se_toma_en_cuenta = (fila > 1 and columna < 2)
                explicacion = "¿Esta casilla está dentro de la zona marcada (filas 2-3, columnas 0-1)?"
                if se_toma_en_cuenta:
                    resultado += numero
                    resumen = f"Sí, entra en la zona. Se suma {numero}. Total: {resultado}"
                else:
                    resumen = "No entra en la zona, se deja igual."
            elif opcion == 1:
                if numero < 4:
                    se_toma_en_cuenta = True
                    resultado += 1
                    explicacion = "¿Este número es menor que 4?"
                    resumen = f"Sí, es menor que 4. Se suma 1. Total: {resultado}"
                elif numero > 4:
                    se_toma_en_cuenta = False
                    resultado -= 1
                    explicacion = "¿Este número es mayor que 4?"
                    resumen = f"Sí, es mayor que 4. Se resta 1. Total: {resultado}"
                else:
                    se_toma_en_cuenta = False
                    explicacion = "El número es 4, no se cuenta en esta opción."
                    resumen = "Es 4, se deja igual."
            else:
                se_toma_en_cuenta = (numero % 3 == 2)
                explicacion = "¿Al dividir este número entre 3, sobra 2?"
                if se_toma_en_cuenta:
                    resultado += numero
                    resumen = f"Sí, sobra 2. Se suma {numero}. Total: {resultado}"
                else:
                    resumen = "No sobra 2, se deja igual."

            pasos.append({
                "fila": fila,
                "columna": columna,
                "numero": numero,
                "explicacion": explicacion,
                "se_toma_en_cuenta": se_toma_en_cuenta,
                "resumen": resumen,
                "resultado": resultado,
            })
    return pasos


def estado_casillas(opcion, paso, pasos):
    estados = {}
    for indice, paso_actual in enumerate(pasos):
        llave = (paso_actual["fila"], paso_actual["columna"])
        if indice < paso:
            if paso_actual["se_toma_en_cuenta"]:
                estados[llave] = "pasado-positivo"
            elif opcion == 1:
                estados[llave] = "pasado-negativo"
            else:
                estados[llave] = "pasado-neutral"
        elif indice == paso:
            estados[llave] = "actual"
    return estados


@app.route("/update-matrix", methods=["POST"])
def update_matrix():
    global numeros
    nueva_matriz = []
    for fila in range(4):
        fila_valores = []
        for columna in range(4):
            nombre = f"celda-{fila}-{columna}"
            valor = request.form.get(nombre, "0").strip()
            try:
                fila_valores.append(int(valor))
            except ValueError:
                fila_valores.append(0)
        nueva_matriz.append(fila_valores)
    numeros = nueva_matriz
    return render_template(
        "index.html",
        numeros=numeros,
        opciones=OPCIONES_PARA_TEMPLATE,
        opcion=0,
        paso=-1,
        pasos=construir_pasos(0),
        pasos_json=json.dumps(construir_pasos(0)),
        estado_casillas=estado_casillas(0, -1, construir_pasos(0)),
    )


@app.route("/")
def index():
    opcion = int(request.args.get("opcion", 0))
    paso = int(request.args.get("paso", -1))

    if not 0 <= opcion < len(OPCIONES):
        opcion = 0
    if paso < -1:
        paso = -1

    pasos = construir_pasos(opcion)
    if paso >= len(pasos):
        paso = len(pasos) - 1

    return render_template(
        "index.html",
        numeros=numeros,
        opciones=OPCIONES_PARA_TEMPLATE,
        opcion=opcion,
        paso=paso,
        pasos=pasos,
        pasos_json=json.dumps(pasos),
        estado_casillas=estado_casillas(opcion, paso, pasos),
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
