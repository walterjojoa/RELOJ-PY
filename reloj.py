"""
Taller: Desarrollo de un Reloj con Python
Reloj analógico con frontend de escritorio (Tkinter), sin HTML ni CSS.

Funcionalidades extra:
  - Reloj digital y fecha en español
  - Alarma configurable (HH:MM) con aviso y sonido
  - Modo claro / modo oscuro

Solo usa la biblioteca estándar de Python: no requiere instalar nada con pip.
Ejecutar con:  python reloj.py
"""

import math                      # seno, coseno y radianes para ubicar las agujas
import tkinter as tk             # interfaz gráfica (frontend) incluida con Python
from datetime import datetime    # hora y fecha actuales

DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

TEMAS = {
    "claro": {"fondo": "#f4f6fb", "esfera": "#ffffff", "borde": "#1f2a44",
              "texto": "#1f2a44", "segundero": "#d62828", "boton": "#e3e7f1"},
    "oscuro": {"fondo": "#14161f", "esfera": "#1f2230", "borde": "#c9d1e8",
               "texto": "#e6e9f2", "segundero": "#ff5c5c", "boton": "#2b2f40"},
}

TAMANO = 400              # ancho y alto del lienzo en píxeles
CENTRO = TAMANO // 2      # centro del reloj
RADIO = 170               # radio de la esfera


class Reloj:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Reloj con Python")
        self.ventana.resizable(False, False)
        self.tema = "claro"
        self.alarma = None  # hora de la alarma como texto "HH:MM", o None

        # Lienzo donde se dibuja el reloj analógico
        self.canvas = tk.Canvas(ventana, width=TAMANO, height=TAMANO, highlightthickness=0)
        self.canvas.pack(padx=20, pady=(20, 10))

        # Reloj digital y fecha
        self.lbl_hora = tk.Label(ventana, font=("Consolas", 32, "bold"))
        self.lbl_hora.pack()
        self.lbl_fecha = tk.Label(ventana, font=("Segoe UI", 12))
        self.lbl_fecha.pack(pady=(0, 10))

        # Panel de alarma
        self.panel = tk.Frame(ventana)
        self.panel.pack(pady=5)
        self.lbl_alarma = tk.Label(self.panel, text="Alarma (HH:MM):", font=("Segoe UI", 11))
        self.lbl_alarma.grid(row=0, column=0, padx=5)
        self.entrada = tk.Entry(self.panel, width=7, font=("Consolas", 12), justify="center")
        self.entrada.grid(row=0, column=1, padx=5)
        self.entrada.bind("<Return>", lambda evento: self.activar_alarma())
        self.btn_activar = tk.Button(self.panel, text="Activar", command=self.activar_alarma,
                                     relief="flat", padx=10)
        self.btn_activar.grid(row=0, column=2, padx=5)
        self.btn_cancelar = tk.Button(self.panel, text="Cancelar", command=self.cancelar_alarma,
                                      relief="flat", padx=10)
        self.btn_cancelar.grid(row=0, column=3, padx=5)

        self.lbl_estado = tk.Label(ventana, text="Sin alarma", font=("Segoe UI", 10))
        self.lbl_estado.pack(pady=5)

        # Botón de cambio de tema
        self.btn_tema = tk.Button(ventana, text="Modo oscuro", command=self.cambiar_tema,
                                  relief="flat", padx=10)
        self.btn_tema.pack(pady=(5, 20))

        self.aplicar_tema()
        self.actualizar()

    # ---------- Tema ----------

    def aplicar_tema(self):
        c = TEMAS[self.tema]
        self.ventana.configure(bg=c["fondo"])
        self.panel.configure(bg=c["fondo"])
        for etiqueta in (self.lbl_hora, self.lbl_fecha, self.lbl_alarma, self.lbl_estado):
            etiqueta.configure(bg=c["fondo"], fg=c["texto"])
        for boton in (self.btn_activar, self.btn_cancelar, self.btn_tema):
            boton.configure(bg=c["boton"], fg=c["texto"],
                            activebackground=c["esfera"], activeforeground=c["texto"])
        self.entrada.configure(bg=c["esfera"], fg=c["texto"], insertbackground=c["texto"])
        self.canvas.configure(bg=c["fondo"])

    def cambiar_tema(self):
        self.tema = "oscuro" if self.tema == "claro" else "claro"
        self.btn_tema.configure(text="Modo claro" if self.tema == "oscuro" else "Modo oscuro")
        self.aplicar_tema()
        self.dibujar(datetime.now())

    # ---------- Dibujo del reloj ----------

    def punto(self, angulo, distancia):
        """Convierte un ángulo del reloj (0° = las 12, sentido horario) en coordenadas x, y.
        Se restan 90° porque en matemáticas el 0° apunta a la derecha, no hacia arriba."""
        radianes = math.radians(angulo - 90)
        return CENTRO + distancia * math.cos(radianes), CENTRO + distancia * math.sin(radianes)

    def aguja(self, angulo, largo, grosor, color):
        x, y = self.punto(angulo, largo)
        self.canvas.create_line(CENTRO, CENTRO, x, y, width=grosor, fill=color, capstyle="round")

    def dibujar(self, ahora):
        c = TEMAS[self.tema]
        self.canvas.delete("all")

        # Esfera
        self.canvas.create_oval(CENTRO - RADIO, CENTRO - RADIO, CENTRO + RADIO, CENTRO + RADIO,
                                fill=c["esfera"], outline=c["borde"], width=4)

        # Marcas: 60 minutos, más largas y gruesas cada 5
        for i in range(60):
            largo, grosor = (15, 3) if i % 5 == 0 else (7, 1)
            x1, y1 = self.punto(i * 6, RADIO - 8)
            x2, y2 = self.punto(i * 6, RADIO - 8 - largo)
            self.canvas.create_line(x1, y1, x2, y2, fill=c["borde"], width=grosor)

        # Números del 1 al 12 (cada número está a 30°)
        for numero in range(1, 13):
            x, y = self.punto(numero * 30, RADIO - 42)
            self.canvas.create_text(x, y, text=str(numero), fill=c["texto"],
                                    font=("Segoe UI", 18, "bold"))

        # Agujas: cada una avanza de forma proporcional a la unidad menor
        segundos = ahora.second
        minutos = ahora.minute + segundos / 60
        horas = ahora.hour % 12 + minutos / 60
        self.aguja(horas * 30, RADIO * 0.50, 7, c["borde"])       # 360° / 12 horas
        self.aguja(minutos * 6, RADIO * 0.75, 4, c["borde"])      # 360° / 60 minutos
        self.aguja(segundos * 6, RADIO * 0.85, 2, c["segundero"])  # 360° / 60 segundos

        # Eje central
        self.canvas.create_oval(CENTRO - 6, CENTRO - 6, CENTRO + 6, CENTRO + 6,
                                fill=c["segundero"], outline="")

    # ---------- Ciclo de actualización ----------

    def actualizar(self):
        ahora = datetime.now()
        self.dibujar(ahora)
        self.lbl_hora.configure(text=ahora.strftime("%H:%M:%S"))
        self.lbl_fecha.configure(
            text=f"{DIAS[ahora.weekday()]}, {ahora.day} de {MESES[ahora.month - 1]} de {ahora.year}")
        self.revisar_alarma(ahora)
        # Se vuelve a llamar justo al inicio del siguiente segundo
        self.ventana.after(1000 - ahora.microsecond // 1000, self.actualizar)

    # ---------- Alarma ----------

    def activar_alarma(self):
        texto = self.entrada.get().strip()
        try:
            hora = datetime.strptime(texto, "%H:%M")
        except ValueError:
            self.lbl_estado.configure(text="Formato inválido. Use HH:MM (ej. 07:30)",
                                      fg=TEMAS[self.tema]["segundero"])
            return
        self.alarma = hora.strftime("%H:%M")
        self.lbl_estado.configure(text=f"Alarma activada para las {self.alarma}",
                                  fg=TEMAS[self.tema]["texto"])

    def cancelar_alarma(self):
        self.alarma = None
        self.lbl_estado.configure(text="Sin alarma", fg=TEMAS[self.tema]["texto"])

    def revisar_alarma(self, ahora):
        if self.alarma and ahora.strftime("%H:%M") == self.alarma:
            hora = self.alarma
            self.cancelar_alarma()
            self.mostrar_aviso(hora)

    def mostrar_aviso(self, hora):
        """Ventana emergente que suena hasta que el usuario pulsa Detener."""
        c = TEMAS[self.tema]
        aviso = tk.Toplevel(self.ventana, bg=c["fondo"])
        aviso.title("Alarma")
        aviso.attributes("-topmost", True)
        tk.Label(aviso, text=f"¡Son las {hora}!", font=("Segoe UI", 20, "bold"),
                 bg=c["fondo"], fg=c["segundero"]).pack(padx=40, pady=(25, 15))
        tk.Button(aviso, text="Detener", command=aviso.destroy, relief="flat", padx=15,
                  bg=c["boton"], fg=c["texto"]).pack(pady=(0, 25))
        self.sonar(aviso)

    def sonar(self, aviso):
        if aviso.winfo_exists():
            self.ventana.bell()
            self.ventana.after(700, lambda: self.sonar(aviso))


if __name__ == "__main__":
    ventana = tk.Tk()
    Reloj(ventana)
    ventana.mainloop()
