"""
Visualizador de recorrido de una tabla de numeros
====================================================

Interfaz limpia, moderna y ordenada, con explicaciones en lenguaje sencillo
(sin palabras tecnicas como "condicion", "booleano" o "iteracion").

Ejecutar:
    python ejemplo1.py
"""

import tkinter as tk
from tkinter import ttk

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
# Colores (tema claro, moderno)
# ----------------------------------------------------------------------

FONDO = "#eef0f5"
TARJETA = "#ffffff"
BORDE = "#e1e3ea"
SOMBRA = "#d7d9e3"

ACENTO = "#4b5bd1"          # azul-violeta: marca / casilla actual
ACENTO_OSCURO = "#3a47ab"   # hover del boton principal
ACENTO_SUAVE = "#eceefb"    # hover de botones secundarios / opciones

POSITIVO = "#1f9d75"        # verde: se cumple / se suma
POSITIVO_SUAVE = "#e3f5ee"
NEGATIVO = "#d1603a"        # naranja: no se cumple / se resta
NEGATIVO_SUAVE = "#fbece4"

TEXTO = "#242530"
TEXTO_SUAVE = "#6b6d7a"
TEXTO_CLARO = "#c7cbf5"

CASILLA_BASE = "#f1f2f7"

FUENTE_LOGO = ("Segoe UI", 14, "bold")
FUENTE_TITULO = ("Segoe UI", 17, "bold")
FUENTE_SUB = ("Segoe UI", 10)
FUENTE_BOTON = ("Segoe UI", 10, "bold")
FUENTE_CASILLA = ("Segoe UI", 15, "bold")
FUENTE_TEXTO = ("Segoe UI", 11)
FUENTE_RESULTADO = ("Segoe UI", 30, "bold")
FUENTE_INDICE = ("Segoe UI", 9, "bold")

OPCIONES = [
    "Opción 1 · sumar una zona de la tabla",
    "Opción 2 · contar según el tamaño del número",
    "Opción 3 · sumar los números especiales",
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
# Utilidades de dibujo (esquinas redondeadas para un look mas moderno)
# ----------------------------------------------------------------------

def rectangulo_redondeado(canvas, x1, y1, x2, y2, radio=14, **kwargs):
    puntos = [
        x1 + radio, y1,
        x2 - radio, y1,
        x2, y1,
        x2, y1 + radio,
        x2, y2 - radio,
        x2, y2,
        x2 - radio, y2,
        x1 + radio, y2,
        x1, y2,
        x1, y2 - radio,
        x1, y1 + radio,
        x1, y1,
    ]
    return canvas.create_polygon(puntos, smooth=True, **kwargs)


class BotonRedondeado(tk.Canvas):
    """Boton con esquinas redondeadas, efecto hover y estado seleccionado."""

    def __init__(self, master, texto, comando=None, ancho=150, alto=46, radio=14,
                 fuente=FUENTE_BOTON, bg_normal=TARJETA, fg_normal=TEXTO,
                 bg_hover=None, fg_hover=None, bg_seleccionado=None, fg_seleccionado=None,
                 bg_fondo=FONDO, borde=BORDE):
        super().__init__(master, width=ancho, height=alto, bg=bg_fondo,
                          highlightthickness=0, cursor="hand2")
        self.ancho, self.alto, self.radio = ancho, alto, radio
        self.texto = texto
        self.comando = comando
        self.fuente = fuente
        self.bg_normal, self.fg_normal = bg_normal, fg_normal
        self.bg_hover = bg_hover or bg_normal
        self.fg_hover = fg_hover or fg_normal
        self.bg_seleccionado = bg_seleccionado or bg_normal
        self.fg_seleccionado = fg_seleccionado or fg_normal
        self.borde = borde
        self.seleccionado = False
        self.habilitado = True

        self._dibujar(self.bg_normal, self.fg_normal)
        self.bind("<Button-1>", self._al_hacer_click)
        self.bind("<Enter>", self._al_entrar)
        self.bind("<Leave>", self._al_salir)
        self.bind("<Configure>", self._al_redimensionar)

    def _colores_reposo(self):
        return (self.bg_seleccionado, self.fg_seleccionado) if self.seleccionado \
            else (self.bg_normal, self.fg_normal)

    def _dibujar(self, bg, fg):
        self.delete("all")
        borde = ACENTO if self.seleccionado else self.borde
        grosor = 2 if self.seleccionado else 1
        rectangulo_redondeado(self, 1, 1, self.ancho - 1, self.alto - 1, radio=self.radio,
                               fill=bg, outline=borde, width=grosor)
        self.create_text(self.ancho / 2, self.alto / 2, text=self.texto,
                          font=self.fuente, fill=fg)

    def _al_hacer_click(self, _evento=None):
        if self.habilitado and self.comando:
            self.comando()

    def _al_entrar(self, _evento=None):
        if self.habilitado and not self.seleccionado:
            self._dibujar(self.bg_hover, self.fg_hover)

    def _al_salir(self, _evento=None):
        self._dibujar(*self._colores_reposo())

    def _al_redimensionar(self, evento):
        self.ancho, self.alto = evento.width, evento.height
        self._dibujar(*self._colores_reposo())

    def establecer_texto(self, texto):
        self.texto = texto
        self._dibujar(*self._colores_reposo())

    def establecer_seleccionado(self, valor):
        self.seleccionado = valor
        self._dibujar(*self._colores_reposo())


class Casilla(tk.Canvas):
    """Una celda numerica de la tabla, con esquinas redondeadas."""

    ANCHO = 78
    ALTO = 78

    def __init__(self, master, numero):
        super().__init__(master, width=self.ANCHO, height=self.ALTO,
                          bg=TARJETA, highlightthickness=0)
        self.numero = numero
        self.set_estado(CASILLA_BASE, TEXTO, resaltado=False)

    def set_estado(self, color_fondo, color_texto, resaltado=False):
        self.delete("all")
        borde = ACENTO if resaltado else BORDE
        grosor = 3 if resaltado else 1
        rectangulo_redondeado(self, 3, 3, self.ANCHO - 3, self.ALTO - 3, radio=16,
                               fill=color_fondo, outline=borde, width=grosor)
        self.create_text(self.ANCHO / 2, self.ALTO / 2, text=str(self.numero),
                          font=FUENTE_CASILLA, fill=color_texto)


def chip_leyenda(parent, color, texto):
    contenedor = tk.Frame(parent, bg=TARJETA)
    tk.Canvas(contenedor, width=12, height=12, bg=TARJETA, highlightthickness=0) \
        .create_oval(1, 1, 11, 11, fill=color, outline=color)
    lienzo = tk.Canvas(contenedor, width=12, height=12, bg=TARJETA, highlightthickness=0)
    lienzo.create_oval(1, 1, 11, 11, fill=color, outline=color)
    lienzo.pack(side="left")
    tk.Label(contenedor, text=texto, font=("Segoe UI", 9), fg=TEXTO_SUAVE,
              bg=TARJETA).pack(side="left", padx=(6, 0))
    return contenedor


def crear_tarjeta(parent):
    """Frame con una sutil sombra (offset) para dar sensacion de elevacion."""
    sombra = tk.Frame(parent, bg=SOMBRA)
    interior = tk.Frame(sombra, bg=TARJETA, highlightbackground=BORDE, highlightthickness=1)
    interior.pack(padx=(0, 3), pady=(0, 3), fill="both", expand=True)
    return sombra, interior


# ----------------------------------------------------------------------
# Ventana principal
# ----------------------------------------------------------------------

class VisualizadorTabla(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Visualizador de recorrido de una tabla de números")
        self.configure(bg=FONDO)
        self.geometry("980x680")
        self.minsize(900, 640)

        self.todos_los_pasos = [construir_pasos(0), construir_pasos(1), construir_pasos(2)]
        self.opcion = 0
        self.paso = -1
        self.reproduciendo = False
        self.velocidad = 750
        self.tarea_pendiente = None

        self._configurar_estilos_ttk()
        self._crear_interfaz()
        self._elegir_opcion(0)

    # ------------------------------------------------------------------

    def _configurar_estilos_ttk(self):
        estilo = ttk.Style(self)
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass
        estilo.configure("Acento.Horizontal.TProgressbar",
                          troughcolor=CASILLA_BASE, background=ACENTO,
                          bordercolor=CASILLA_BASE, lightcolor=ACENTO,
                          darkcolor=ACENTO, thickness=8)

    def _crear_interfaz(self):
        # ---- barra superior -------------------------------------------------
        barra_superior = tk.Frame(self, bg=ACENTO, height=68)
        barra_superior.pack(fill="x", side="top")
        barra_superior.pack_propagate(False)

        bloque_titulo = tk.Frame(barra_superior, bg=ACENTO)
        bloque_titulo.pack(side="left", padx=24, pady=8)
        tk.Label(bloque_titulo, text="▦  Visualizador de tablas", font=FUENTE_LOGO,
                 fg="white", bg=ACENTO).pack(anchor="w")
        tk.Label(bloque_titulo, text="Recorrido paso a paso de una matriz numérica",
                 font=FUENTE_SUB, fg=TEXTO_CLARO, bg=ACENTO).pack(anchor="w")

        tk.Label(barra_superior, text="INTERACTIVO", font=("Segoe UI", 9, "bold"),
                 fg=ACENTO_OSCURO, bg="white", padx=10, pady=4).pack(side="right", padx=24)

        # ---- contenedor principal -------------------------------------------
        contenedor = tk.Frame(self, bg=FONDO)
        contenedor.pack(fill="both", expand=True, padx=24, pady=20)

        tk.Label(contenedor, text="¿Cómo se recorre esta tabla de números?",
                 font=FUENTE_TITULO, fg=TEXTO, bg=FONDO).pack(anchor="w")
        tk.Label(contenedor,
                 text="El programa revisa la tabla número por número, de izquierda a derecha y de arriba hacia abajo.",
                 font=FUENTE_SUB, fg=TEXTO_SUAVE, bg=FONDO).pack(anchor="w", pady=(2, 18))

        # ---- selector de opciones --------------------------------------------
        fila_opciones = tk.Frame(contenedor, bg=FONDO)
        fila_opciones.pack(fill="x", pady=(0, 18))
        for col in range(3):
            fila_opciones.columnconfigure(col, weight=1)

        self.botones_opcion = []
        for k, nombre in enumerate(OPCIONES):
            b = BotonRedondeado(fila_opciones, texto=nombre, ancho=300, alto=52,
                                 fuente=FUENTE_BOTON, bg_normal=TARJETA, fg_normal=TEXTO,
                                 bg_hover=ACENTO_SUAVE, fg_hover=ACENTO_OSCURO,
                                 bg_seleccionado=ACENTO, fg_seleccionado="white",
                                 bg_fondo=FONDO, comando=lambda k=k: self._elegir_opcion(k))
            b.grid(row=0, column=k, sticky="nsew", padx=(0 if k == 0 else 10, 0))
            self.botones_opcion.append(b)

        cuerpo = tk.Frame(contenedor, bg=FONDO)
        cuerpo.pack(fill="both", expand=True)

        # ---- tabla de numeros --------------------------------------------------
        sombra_tabla, panel_tabla = crear_tarjeta(cuerpo)
        sombra_tabla.pack(side="left", padx=(0, 18), anchor="n")
        interior_tabla = tk.Frame(panel_tabla, bg=TARJETA)
        interior_tabla.pack(padx=24, pady=22)

        tk.Label(interior_tabla, text="La tabla", font=FUENTE_BOTON,
                 fg=TEXTO_SUAVE, bg=TARJETA).grid(row=0, column=0, columnspan=5,
                                                    sticky="w", pady=(0, 12))

        # encabezados de columna
        tk.Label(interior_tabla, text="", bg=TARJETA, width=2).grid(row=1, column=0)
        for c in range(4):
            tk.Label(interior_tabla, text=str(c), font=FUENTE_INDICE,
                     fg=TEXTO_SUAVE, bg=TARJETA).grid(row=1, column=c + 1, pady=(0, 4))

        self.casillas = {}
        for f in range(4):
            tk.Label(interior_tabla, text=str(f), font=FUENTE_INDICE,
                     fg=TEXTO_SUAVE, bg=TARJETA).grid(row=f + 2, column=0, padx=(0, 4))
            for c in range(4):
                casilla = Casilla(interior_tabla, numeros[f][c])
                casilla.grid(row=f + 2, column=c + 1, padx=4, pady=4)
                self.casillas[(f, c)] = casilla

        tk.Label(interior_tabla, text="Fila = hacia abajo   ·   Columna = hacia la derecha",
                 font=("Segoe UI", 9), fg=TEXTO_SUAVE, bg=TARJETA).grid(
            row=6, column=0, columnspan=5, sticky="w", pady=(12, 0))

        leyenda = tk.Frame(interior_tabla, bg=TARJETA)
        leyenda.grid(row=7, column=0, columnspan=5, sticky="w", pady=(10, 0))
        chip_leyenda(leyenda, POSITIVO, "Se suma").pack(side="left", padx=(0, 14))
        chip_leyenda(leyenda, NEGATIVO, "Se resta").pack(side="left", padx=(0, 14))
        chip_leyenda(leyenda, ACENTO, "Casilla actual").pack(side="left")

        # ---- panel de estado ------------------------------------------------
        panel_derecho = tk.Frame(cuerpo, bg=FONDO)
        panel_derecho.pack(side="left", fill="both", expand=True, anchor="n")

        sombra_estado, tarjeta_estado = crear_tarjeta(panel_derecho)
        sombra_estado.pack(fill="x", pady=(0, 18))
        interior_estado = tk.Frame(tarjeta_estado, bg=TARJETA)
        interior_estado.pack(fill="x", padx=22, pady=20)

        cabecera_estado = tk.Frame(interior_estado, bg=TARJETA)
        cabecera_estado.pack(fill="x")
        self.etiqueta_paso = tk.Label(cabecera_estado, text="Casilla 0 de 16",
                                       font=FUENTE_SUB, fg=TEXTO_SUAVE, bg=TARJETA)
        self.etiqueta_paso.pack(side="left")

        self.barra_progreso = ttk.Progressbar(interior_estado, orient="horizontal",
                                               mode="determinate", maximum=16,
                                               style="Acento.Horizontal.TProgressbar")
        self.barra_progreso.pack(fill="x", pady=(8, 14))

        tk.Label(interior_estado, text="RESULTADO ACUMULADO", font=("Segoe UI", 9, "bold"),
                 fg=TEXTO_SUAVE, bg=TARJETA).pack(anchor="w")
        self.etiqueta_resultado = tk.Label(interior_estado, text="0", font=FUENTE_RESULTADO,
                                            fg=ACENTO, bg=TARJETA)
        self.etiqueta_resultado.pack(anchor="w", pady=(0, 12))

        separador = tk.Frame(interior_estado, bg=BORDE, height=1)
        separador.pack(fill="x", pady=(0, 12))

        self.etiqueta_explicacion = tk.Label(interior_estado, text="Presiona reproducir para empezar.",
                                              font=FUENTE_TEXTO, fg=TEXTO, bg=TARJETA,
                                              anchor="w", justify="left", wraplength=440)
        self.etiqueta_explicacion.pack(fill="x")

        self.etiqueta_resumen = tk.Label(interior_estado, text="", font=("Segoe UI", 11, "bold"),
                                          fg=POSITIVO, bg=TARJETA, anchor="w",
                                          justify="left", wraplength=440)
        self.etiqueta_resumen.pack(fill="x", pady=(8, 0))

        # ---- controles ----------------------------------------------------
        controles = tk.Frame(panel_derecho, bg=FONDO)
        controles.pack(fill="x", pady=(4, 0))

        BotonRedondeado(controles, texto="‹  Anterior", comando=self._paso_anterior,
                         ancho=118, alto=48, bg_normal=TARJETA, fg_normal=TEXTO,
                         bg_hover=ACENTO_SUAVE, fg_hover=ACENTO_OSCURO,
                         bg_fondo=FONDO).pack(side="left", padx=(0, 10))

        self.boton_reproducir = BotonRedondeado(
            controles, texto="▶  Reproducir", comando=self._alternar_reproduccion,
            ancho=160, alto=48, bg_normal=ACENTO, fg_normal="white",
            bg_hover=ACENTO_OSCURO, fg_hover="white", bg_fondo=FONDO)
        self.boton_reproducir.pack(side="left", padx=(0, 10))

        BotonRedondeado(controles, texto="Siguiente  ›", comando=self._paso_siguiente,
                         ancho=118, alto=48, bg_normal=TARJETA, fg_normal=TEXTO,
                         bg_hover=ACENTO_SUAVE, fg_hover=ACENTO_OSCURO,
                         bg_fondo=FONDO).pack(side="left", padx=(0, 10))

        BotonRedondeado(controles, texto="⟲  Reiniciar", comando=self._reiniciar,
                         ancho=126, alto=48, bg_normal=TARJETA, fg_normal=TEXTO,
                         bg_hover=ACENTO_SUAVE, fg_hover=ACENTO_OSCURO,
                         bg_fondo=FONDO).pack(side="left")

        tk.Label(self, text="Hecho con Python + Tkinter", font=("Segoe UI", 8),
                 fg=TEXTO_SUAVE, bg=FONDO).pack(side="bottom", pady=(0, 8))

    # ------------------------------------------------------------------

    def _elegir_opcion(self, k):
        self.opcion = k
        self.paso = -1
        self._detener()
        for i, b in enumerate(self.botones_opcion):
            b.establecer_seleccionado(i == k)
        self._limpiar_casillas()
        self._mostrar()

    def _limpiar_casillas(self):
        for casilla in self.casillas.values():
            casilla.set_estado(CASILLA_BASE, TEXTO, resaltado=False)

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
            self.boton_reproducir.establecer_texto("⏸  Pausar")
            self._siguiente_automatico()

    def _detener(self):
        self.reproduciendo = False
        self.boton_reproducir.establecer_texto("▶  Reproducir")
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
        self.barra_progreso["value"] = actual

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
                casilla.set_estado(POSITIVO, "white", resaltado=False)
            elif self.opcion == 1:
                casilla.set_estado(NEGATIVO, "white", resaltado=False)

        # casilla actual, resaltada
        s = pasos[self.paso]
        casilla = self.casillas[(s["fila"], s["columna"])]
        if s["se_toma_en_cuenta"]:
            color, color_texto = POSITIVO, "white"
        elif self.opcion == 1:
            color, color_texto = NEGATIVO, "white"
        else:
            color, color_texto = CASILLA_BASE, TEXTO
        casilla.set_estado(color, color_texto, resaltado=True)

        self.etiqueta_resultado.configure(text=str(s["resultado"]))
        self.etiqueta_explicacion.configure(
            text=f"Fila {s['fila']}, columna {s['columna']} → el número es {s['numero']}.\n{s['explicacion']}")
        self.etiqueta_resumen.configure(
            text=s["resumen"],
            fg=POSITIVO if s["se_toma_en_cuenta"] else (NEGATIVO if self.opcion == 1 else TEXTO_SUAVE))


if __name__ == "__main__":
    app = VisualizadorTabla()
    app.mainloop()
