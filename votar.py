import customtkinter as ctk
import pandas as pd
import os
import sys
from tkinter import messagebox, simpledialog
import winsound

from db import BaseDeDatos
from correos_permitidos import VerificadorCorreo

ctk.set_appearance_mode("dark")

# 🎨 COLORES DE LA BANDERA DE CÓRDOBA
COLOR_FONDO = "#1D3557"   # Azul
COLOR_ROJO = "#E63946"    # Rojo
COLOR_AZUL_BOTON = "#457B9D" 
COLOR_BLANCO = "#F1FAEE"  
COLOR_GRIS = "#1D3557"    

ADMIN_PASSWORD = "admin123"


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Sistema de Votación Escolar - Córdoba")
        
        # --- 🔒 PANTALLA COMPLETA TOTAL Y BLOQUEADA ---
        self.attributes("-fullscreen", True) # Fuerza el modo pantalla completa nativo
        self.resizable(False, False)

        # Vincular la tecla Escape para que pida contraseña antes de salir
        self.bind_all("<Escape>", self.intentar_salir_esc)
        
        # Bloquear que lo cierren con Alt+F4
        self.protocol("WM_DELETE_WINDOW", self.bloquear_salida_alt_f4)

        self.configure(fg_color=COLOR_FONDO)

        self.db = BaseDeDatos()
        self.verificador = VerificadorCorreo("correos_permitidos.txt")

        self.frame = None

        self.bind_all("<Control-Shift-A>", self.abrir_admin)

        self.cambiar(Inicio)

    def cambiar(self, frame, datos=None):
        if self.frame:
            self.frame.destroy()

        self.frame = frame(self, self, datos) if datos else frame(self, self)
        self.frame.pack(expand=True, fill="both")

    def intentar_salir_esc(self, event=None):
        # Al presionar ESC salta este cuadro. Si no ponen la clave, el programa no se cierra.
        pwd = simpledialog.askstring("Salir del Sistema", "Ingrese la contraseña de administrador para cerrar la aplicación:", show="*")
        
        if pwd == ADMIN_PASSWORD:
            sys.exit() 
        elif pwd is not None:
            messagebox.showerror("Error", "Contraseña incorrecta. El sistema continuará bloqueado.")

    def abrir_admin(self, event=None):
        pwd = simpledialog.askstring("Panel Administrador", "Ingrese la clave para ver estadísticas y exportar:", show="*")

        if pwd == ADMIN_PASSWORD:
            self.cambiar(Admin)
        elif pwd is not None:
            messagebox.showerror("Error", "Clave incorrecta")

    def bloquear_salida_alt_f4(self):
        messagebox.showwarning("Acceso Denegado", "Para cerrar la aplicación presione la tecla ESC e ingrese la contraseña de administrador.")


# ---------------- INICIO ----------------

class Inicio(ctk.CTkFrame):
    def __init__(self, p, c):
        super().__init__(p, fg_color=COLOR_FONDO)

        ctk.CTkLabel(
            self, 
            text="🗳️ SISTEMA DE VOTACIÓN", 
            font=("Arial Bold", 45), 
            text_color=COLOR_BLANCO
        ).pack(pady=(200, 50))

        ctk.CTkButton(
            self, 
            text="COMENZAR A VOTAR", 
            font=("Arial Bold", 26),
            fg_color=COLOR_ROJO,
            hover_color="#C22F3D",
            text_color="white",
            width=450,
            height=90,
            corner_radius=20,
            command=lambda: c.cambiar(Formulario)
        ).pack(pady=20)


# ---------------- FORMULARIO ----------------

class Formulario(ctk.CTkFrame):
    def __init__(self, p, c):
        super().__init__(p, fg_color=COLOR_FONDO)
        self.c = c

        ctk.CTkLabel(
            self, 
            text="REGISTRO DE ESTUDIANTE", 
            font=("Arial Bold", 35), 
            text_color=COLOR_BLANCO
        ).pack(pady=(120, 40))

        ctk.CTkLabel(self, text="Nombre Completo:", font=("Arial Bold", 18), text_color=COLOR_BLANCO).pack(pady=5)
        self.nombre = ctk.CTkEntry(self, width=400, height=50, font=("Arial", 16), fg_color="white", text_color="black")
        self.nombre.pack(pady=10)

        ctk.CTkLabel(self, text="Correo Electrónico Institucional:", font=("Arial Bold", 18), text_color=COLOR_BLANCO).pack(pady=5)
        self.correo = ctk.CTkEntry(self, width=400, height=50, font=("Arial", 16), fg_color="white", text_color="black")
        self.correo.pack(pady=10)

        ctk.CTkButton(
            self, 
            text="Validar y Continuar", 
            font=("Arial Bold", 22),
            fg_color=COLOR_ROJO,
            hover_color="#C22F3D",
            width=350,
            height=70,
            corner_radius=15,
            command=self.validar
        ).pack(pady=40)

    def validar(self):
        correo = self.correo.get().strip()
        nombre = self.nombre.get().strip()

        if not nombre:
            messagebox.showerror("Error", "Por favor ingresá tu nombre.")
            return

        if not self.c.verificador.correo_valido(correo):
            messagebox.showerror("Error", "El correo ingresado no es válido.")
            return

        if not self.c.verificador.correo_permitido(correo):
            messagebox.showerror("Error", "Este correo no está en el padrón de alumnos.")
            return

        if self.c.db.ya_voto(correo):
            messagebox.showwarning("Atención", "Este correo ya registró su voto.")
            return

        self.c.cambiar(Votacion, {"correo": correo, "nombre": nombre})


# ---------------- VOTACIÓN ----------------

class Votacion(ctk.CTkFrame):
    def __init__(self, p, c, d):
        super().__init__(p, fg_color=COLOR_FONDO)
        self.c = c
        self.d = d

        ctk.CTkLabel(
            self, 
            text=f"¡Hola {self.d['nombre']}! Elegí tu lista:", 
            font=("Arial Bold", 35), 
            text_color=COLOR_BLANCO
        ).pack(pady=(100, 40))

        self.btn("Lista Roja", COLOR_ROJO, "white")
        self.btn("Lista Azul", "#1D3557", "white", border_width=2, border_color="white")
        self.btn("Voto en Blanco", "white", COLOR_GRIS)

    def btn(self, texto, color, texto_col, border_width=0, border_color="white"):
        ctk.CTkButton(
            self,
            text=texto,
            font=("Arial Bold", 30),
            fg_color=color,
            text_color=texto_col,
            border_width=border_width,
            border_color=border_color,
            width=550,
            height=110,
            corner_radius=25,
            command=lambda: self.votar(texto)
        ).pack(pady=20)

    def votar(self, lista):
        if messagebox.askyesno("Confirmar Voto", f"¿Estás seguro de votar por: {lista}?"):

            ok = self.c.db.guardar_voto(
                self.d["correo"],
                self.d["nombre"],
                lista
            )

            if ok:
                try:
                    winsound.MessageBeep()
                except:
                    pass
                self.c.cambiar(Final)
            else:
                messagebox.showerror("Error", "No se pudo guardar el voto. Inténtalo de nuevo.")


# ---------------- FINAL ----------------

class Final(ctk.CTkFrame):
    def __init__(self, p, c):
        super().__init__(p, fg_color=COLOR_FONDO)

        ctk.CTkLabel(
            self, 
            text="✅ VOTO REGISTRADO", 
            font=("Arial Bold", 45), 
            text_color="green"
        ).pack(pady=(250, 30))

        ctk.CTkLabel(
            self, 
            text="Muchas gracias por participar en la jornada escolar.", 
            font=("Arial Bold", 24), 
            text_color=COLOR_BLANCO
        ).pack(pady=10)

        self.after(3000, lambda: c.cambiar(Inicio))


# ---------------- ADMINISTRACIÓN ----------------

class Admin(ctk.CTkFrame):
    def __init__(self, p, c):
        super().__init__(p, fg_color=COLOR_FONDO)
        self.c = c

        ctk.CTkLabel(
            self, 
            text="⚙️ PANEL DE ADMINISTRACIÓN", 
            font=("Arial Bold", 30), 
            text_color=COLOR_BLANCO
        ).pack(pady=(80, 20))

        self.label = ctk.CTkLabel(self, text="", font=("Arial Bold", 24), text_color=COLOR_BLANCO)
        self.label.pack(pady=10)

        self.crear_boton_admin("Actualizar Conteo", self.actualizar, COLOR_AZUL_BOTON)
        self.crear_boton_admin("Ver Detalle de Votantes", self.ver_votos, COLOR_AZUL_BOTON)
        self.crear_boton_admin("Ver Lista Ganadora", self.ganador, COLOR_AZUL_BOTON)
        self.crear_boton_admin("Exportar Excel (Sin revelar votos)", self.exportar, "green")
        self.crear_boton_admin("Borrar Base de Datos", self.borrar, COLOR_ROJO)
        self.crear_boton_admin("Volver a la pantalla de Inicio", lambda: self.c.cambiar(Inicio), "#6B7280")

        self.actualizar()

    def crear_boton_admin(self, texto, comando, color):
        ctk.CTkButton(
            self, 
            text=texto, 
            font=("Arial Bold", 18),
            fg_color=color,
            width=450,
            height=55,
            corner_radius=12,
            command=comando
        ).pack(pady=10)

    def actualizar(self):
        total = self.c.db.total()
        self.label.configure(text=f"Total votos emitidos: {total}")

    def ver_votos(self):
        datos = self.c.db.votos_detallados()

        if not datos:
            messagebox.showinfo("Info", "Aún no hay votos registrados.")
            return

        win = ctk.CTkToplevel(self)
        win.title("Votos Detallados")
        win.geometry("750x550")
        win.configure(fg_color=COLOR_FONDO)

        frame = ctk.CTkScrollableFrame(win, fg_color=COLOR_FONDO)
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(frame, text="Auditoría de Votos", font=("Arial Bold", 22), text_color=COLOR_BLANCO).pack(pady=10)

        for i, v in enumerate(datos, 1):
            ctk.CTkLabel(
                frame, 
                text=f"{i}. Alumno: {v[0]}  |  Votó a: {v[1]}  |  Fecha: {v[2]}",
                font=("Arial", 15),
                text_color=COLOR_BLANCO
            ).pack(anchor="w", pady=4)

    def ganador(self):
        stats = self.c.db.stats()

        if stats:
            g = stats[0]
            messagebox.showinfo("Resultados", f"La lista ganadora actualmente es:\n\n🎉 {g[0]} con {g[1]} votos.")
        else:
            messagebox.showinfo("Resultados", "Aún no hay votos para computar un ganador.")

    def exportar(self):
        datos = self.c.db.votos_sin_lista() 

        if not datos:
            messagebox.showwarning("Atención", "No hay datos para exportar.")
            return

        df = pd.DataFrame(datos, columns=["Nombre del Estudiante", "Fecha/Hora de Votación"])

        try:
            path = "votos_estudiantes.xlsx"
            df.to_excel(path, index=False)
            os.startfile(path)
            messagebox.showinfo("Éxito", f"Se exportó el archivo '{path}' sin revelar el voto.")
        except Exception as e:
            path_csv = "votos_estudiantes.csv"
            df.to_csv(path_csv, index=False)
            os.startfile(path_csv)
            messagebox.showinfo("Éxito", f"Se exportó el archivo '{path_csv}' sin revelar el voto.")

    def borrar(self):
        if messagebox.askyesno("⚠️ PELIGRO ⚠️", "¿Estás ABSOLUTAMENTE SEGURO de borrar todos los votos?\nEsta acción no se puede deshacer."):
            self.c.db.borrar_todo()
            self.actualizar()


if __name__ == "__main__":
    app = App()
    app.mainloop()
