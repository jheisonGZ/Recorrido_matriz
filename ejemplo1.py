"""
Visualizador de recorrido de una tabla de numeros
====================================================

Interfaz limpia y ordenada, con explicaciones en lenguaje sencillo
(sin palabras tecnicas como "condicion", "booleano" o "iteracion").

Ejecutar:
    python ejemplo1.py
"""

import tkinter as tk

# ----------------------------------------------------------------------
# La tabla de numeros (matriz)
# ----------------------------------------------------------------------

numeros = [
    [4, 3, 5, 8],
    [7, 10, 0, 14],
    [6, 0, 11, 0],
    [9, 3, 0, 0],
]

# ----------------------------------------------------------------------
# Colores (tema claro, limpio)
# ----------------------------------------------------------------------

FONDO = "#f5f6f8"
TARJETA = "#ffffff"
BORDE = "#e2e4ea"
ACENTO = "#4f5fce"       # azul-violeta para resaltar la casilla actual
POSITIVO = "#1f9d75"     # verde: se cumple / se suma
NEGATIVO = "#d1603a"     # naranja/rojo: no se cumple / se resta
TEXTO = "#242530"
TEXTO_SUAVE = "#6b6d7a"
CASILLA_BASE = "#eef0f5"

FUENTE_TITULO = ("Segoe UI", 16, "bold")
FUENTE_SUB = ("Segoe UI", 10)
FUENTE_BOTON = ("Segoe UI", 10, "bold")
FUENTE_CASILLA = ("Segoe UI", 16, "bold")
FUENTE_TEXTO = ("Segoe UI", 11)
FUENTE_RESULTADO = ("Segoe UI", 26, "bold")

OPCIONES = [
    "Opción 1: sumar una zona de la tabla",
    "Opción 2: contar según el tamaño del número",
    "Opción 3: sumar los números especiales",
]


# ----------------------------------------------------------------------
# Aca se calcula, casilla por casilla, que pasa con cada numero
# ----------------------------------------------------------------------

def construir_pasos(opcion):
    pasos = []
    resultado = 0
    for fila in range(4):
        for columna in range(4):
            numero = numeros[fila][columna]

            if opcion == 0:
                # se toma en cuenta la zona: filas 2-3, columnas 0-1
                se_toma_en_cuenta = (fila > 1 and columna < 2)
                explicacion = "¿Esta casilla esta dentro de la zona marcada (filas 2-3, columnas 0-1)?"
                if se_toma_en_cuenta:
                    resultado += numero
                    resumen = f"Si, entra en la zona. Se suma {numero}. Total: {resultado}"
                else:
                    resumen = "No entra en la zona, se deja igual."

            elif opcion == 1:
                # los numeros menores a 4 suman, los mayores a 4 restan, el 4 no se cuenta
                if numero < 4:
                    se_toma_en_cuenta = True
                    explicacion = "¿Este número es menor que 4?"
                    resultado += 1
                    resumen = f"Si, es menor que 4. Se suma 1. Total: {resultado}"
                elif numero > 4:
                    se_toma_en_cuenta = False
                    explicacion = "¿Este número es mayor que 4?"
                    resultado -= 1
                    resumen = f"No, es mayor que 4. Se resta 1. Total: {resultado}"
                else:
                    se_toma_en_cuenta = False
                    explicacion = "El número es 4, no se cuenta en esta opción."
                    resumen = "Es 4, se deja igual."

            else:
                # numeros cuyo residuo al dividir entre 3 es igual a 2
                se_toma_en_cuenta = (numero % 3 == 2)
                explicacion = "¿Al dividir este número entre 3, sobra 2?"
                if se_toma_en_cuenta:
                    resultado += numero
                    resumen = f"Si, sobra 2. Se suma {numero}. Total: {resultado}"
                else:
                    resumen = "No sobra 2, se deja igual."

            pasos.append({
                "fila": fila, "columna": columna, "numero": numero,
                "explicacion": explicacion, "se_toma_en_cuenta": se_toma_en_cuenta,
                "resumen": resumen, "resultado": resultado,
            })
    return pasos


# ----------------------------------------------------------------------
# Ventana principal
# ----------------------------------------------------------------------

class VisualizadorTabla(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Visualizador de recorrido de una tabla de números")
        self.configure(bg=FONDO)
        self.geometry("940x600")
        self.minsize(860, 580)

        self.todos_los_pasos = [construir_pasos(0), construir_pasos(1), construir_pasos(2)]
        self.opcion = 0
        self.paso = -1
        self.reproduciendo = False
        self.velocidad = 750
        self.tarea_pendiente = None

        self._crear_interfaz()
        self._elegir_opcion(0)

    # ------------------------------------------------------------------

    def _crear_interfaz(self):
        contenedor = tk.Frame(self, bg=FONDO)
        contenedor.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(contenedor, text="¿Cómo se recorre esta tabla de números?",
                 font=FUENTE_TITULO, fg=TEXTO, bg=FONDO).pack(anchor="w")
        tk.Label(contenedor,
                 text="El programa revisa la tabla número por número, de izquierda a derecha y de arriba hacia abajo.",
                 font=FUENTE_SUB, fg=TEXTO_SUAVE, bg=FONDO).pack(anchor="w", pady=(2, 16))

        fila_opciones = tk.Frame(contenedor, bg=FONDO)
        fila_opciones.pack(fill="x", pady=(0, 16))
        self.botones_opcion = []
        for k, nombre in enumerate(OPCIONES):
            b = tk.Button(fila_opciones, text=nombre, font=FUENTE_BOTON,
                          bg=TARJETA, fg=TEXTO, relief="flat", bd=0,
                          highlightbackground=BORDE, highlightthickness=1,
                          padx=10, pady=12, cursor="hand2",
                          command=lambda k=k: self._elegir_opcion(k))
            b.pack(side="left", fill="x", expand=True, padx=(0 if k == 0 else 10, 0))
            self.botones_opcion.append(b)

        cuerpo = tk.Frame(contenedor, bg=FONDO)
        cuerpo.pack(fill="both", expand=True)

        # tabla de numeros
        panel_tabla = tk.Frame(cuerpo, bg=TARJETA, highlightbackground=BORDE,
                                highlightthickness=1)
        panel_tabla.pack(side="left", padx=(0, 16))
        interior_tabla = tk.Frame(panel_tabla, bg=TARJETA)
        interior_tabla.pack(padx=24, pady=24)

        tk.Label(interior_tabla, text="La tabla", font=FUENTE_BOTON,
                 fg=TEXTO_SUAVE, bg=TARJETA).grid(row=0, column=0, columnspan=4,
                                                    sticky="w", pady=(0, 10))

        self.casillas = {}
        for f in range(4):
            for c in range(4):
                casilla = tk.Label(interior_tabla, text=str(numeros[f][c]),
                                    font=FUENTE_CASILLA, width=3, height=1,
                                    bg=CASILLA_BASE, fg=TEXTO)
                casilla.grid(row=f + 1, column=c, padx=5, pady=5, ipady=8)
                self.casillas[(f, c)] = casilla

        tk.Label(interior_tabla, text="Fila = hacia abajo   ·   Columna = hacia la derecha",
                 font=("Segoe UI", 9), fg=TEXTO_SUAVE, bg=TARJETA).grid(
            row=5, column=0, columnspan=4, sticky="w", pady=(10, 0))

        # panel de estado
        panel_derecho = tk.Frame(cuerpo, bg=FONDO)
        panel_derecho.pack(side="left", fill="both", expand=True)

        tarjeta_estado = tk.Frame(panel_derecho, bg=TARJETA, highlightbackground=BORDE,
                                   highlightthickness=1)
        tarjeta_estado.pack(fill="x", pady=(0, 16))
        interior_estado = tk.Frame(tarjeta_estado, bg=TARJETA)
        interior_estado.pack(fill="x", padx=20, pady=16)

        self.etiqueta_paso = tk.Label(interior_estado, text="Casilla 0 de 16",
                                       font=FUENTE_SUB, fg=TEXTO_SUAVE, bg=TARJETA)
        self.etiqueta_paso.pack(anchor="w")

        self.etiqueta_resultado = tk.Label(interior_estado, text="0", font=FUENTE_RESULTADO,
                                            fg=ACENTO, bg=TARJETA)
        self.etiqueta_resultado.pack(anchor="w", pady=(2, 10))

        self.etiqueta_explicacion = tk.Label(interior_estado, text="Presiona reproducir para empezar.",
                                              font=FUENTE_TEXTO, fg=TEXTO, bg=TARJETA,
                                              anchor="w", justify="left", wraplength=440)
        self.etiqueta_explicacion.pack(fill="x")

        self.etiqueta_resumen = tk.Label(interior_estado, text="", font=("Segoe UI", 11, "bold"),
                                          fg=POSITIVO, bg=TARJETA, anchor="w",
                                          justify="left", wraplength=440)
        self.etiqueta_resumen.pack(fill="x", pady=(8, 0))

        # controles
        controles = tk.Frame(panel_derecho, bg=FONDO)
        controles.pack(fill="x", pady=(4, 0))

        estilo_boton = dict(font=FUENTE_BOTON, bg=TARJETA, fg=TEXTO,
                            relief="flat", bd=0, highlightbackground=BORDE,
                            highlightthickness=1, padx=14, pady=10, cursor="hand2")

        tk.Button(controles, text="Anterior", command=self._paso_anterior,
                  **estilo_boton).pack(side="left", padx=(0, 8))
        self.boton_reproducir = tk.Button(controles, text="Reproducir", command=self._alternar_reproduccion,
                                           font=FUENTE_BOTON, bg=ACENTO, fg="white",
                                           relief="flat", bd=0, padx=18, pady=10, cursor="hand2")
        self.boton_reproducir.pack(side="left", padx=(0, 8))
        tk.Button(controles, text="Siguiente", command=self._paso_siguiente,
                  **estilo_boton).pack(side="left", padx=(0, 8))
        tk.Button(controles, text="Reiniciar", command=self._reiniciar,
                  **estilo_boton).pack(side="left")

    # ------------------------------------------------------------------

    def _elegir_opcion(self, k):
        self.opcion = k
        self.paso = -1
        self._detener()
        for i, b in enumerate(self.botones_opcion):
            if i == k:
                b.configure(bg=ACENTO, fg="white")
            else:
                b.configure(bg=TARJETA, fg=TEXTO)
        self._limpiar_casillas()
        self._mostrar()

    def _limpiar_casillas(self):
        for casilla in self.casillas.values():
            casilla.configure(bg=CASILLA_BASE, fg=TEXTO, highlightthickness=0)

    def _pasos_actuales(self):
        return self.todos_los_pasos[self.opcion]

    def _paso_siguiente(self):
        pasos = self._pasos_actuales()
        if self.paso < len(pasos) - 1:
            self.paso += 1
            self._mostrar()
        else:
            self._detener()

    def _paso_anterior(self):
        if self.paso > -1:
            self.paso -= 1
            self._mostrar()

    def _reiniciar(self):
        self._detener()
        self.paso = -1
        self._limpiar_casillas()
        self._mostrar()

    def _alternar_reproduccion(self):
        if self.reproduciendo:
            self._detener()
        else:
            self.reproduciendo = True
            self.boton_reproducir.configure(text="Pausar")
            self._siguiente_automatico()

    def _detener(self):
        self.reproduciendo = False
        self.boton_reproducir.configure(text="Reproducir")
        if self.tarea_pendiente is not None:
            self.after_cancel(self.tarea_pendiente)
            self.tarea_pendiente = None

    def _siguiente_automatico(self):
        if not self.reproduciendo:
            return
        pasos = self._pasos_actuales()
        if self.paso < len(pasos) - 1:
            self.paso += 1
            self._mostrar()
            self.tarea_pendiente = self.after(self.velocidad, self._siguiente_automatico)
        else:
            self._detener()

    # ------------------------------------------------------------------

    def _mostrar(self):
        pasos = self._pasos_actuales()
        self._limpiar_casillas()

        total = len(pasos)
        actual = self.paso + 1 if self.paso >= 0 else 0
        self.etiqueta_paso.configure(text=f"Casilla {actual} de {total}")

        if self.paso < 0:
            self.etiqueta_resultado.configure(text="0")
            self.etiqueta_explicacion.configure(text="Presiona reproducir para empezar.")
            self.etiqueta_resumen.configure(text="")
            return

        # casillas ya revisadas, en un tono mas suave
        for p in range(self.paso):
            s = pasos[p]
            casilla = self.casillas[(s["fila"], s["columna"])]
            if s["se_toma_en_cuenta"]:
                casilla.configure(bg=POSITIVO, fg="white")
            elif self.opcion == 1:
                casilla.configure(bg=NEGATIVO, fg="white")

        # casilla actual, resaltada
        s = pasos[self.paso]
        casilla = self.casillas[(s["fila"], s["columna"])]
        color = POSITIVO if s["se_toma_en_cuenta"] else (NEGATIVO if self.opcion == 1 else CASILLA_BASE)
        color_texto = "white" if (s["se_toma_en_cuenta"] or self.opcion == 1) else TEXTO
        casilla.configure(bg=color, fg=color_texto,
                          highlightbackground=ACENTO, highlightthickness=3)

        self.etiqueta_resultado.configure(text=str(s["resultado"]))
        self.etiqueta_explicacion.configure(
            text=f"Fila {s['fila']}, columna {s['columna']} → el número es {s['numero']}.\n{s['explicacion']}")
        self.etiqueta_resumen.configure(
            text=s["resumen"],
            fg=POSITIVO if s["se_toma_en_cuenta"] else (NEGATIVO if self.opcion == 1 else TEXTO_SUAVE))


if __name__ == "__main__":
    app = VisualizadorTabla()
    app.mainloop()