import customtkinter as ctk
import pandas as pd
import os
import sys
import hashlib
from tkinter import messagebox, simpledialog
import winsound
import time

from db import BaseDeDatos
from correos_permitidos import VerificadorCorreo

ctk.set_appearance_mode("dark")

COLOR_FONDO = "#1D3557"
COLOR_ROJO = "#E63946"
COLOR_AZUL = "#457B9D"
COLOR_BLANCO = "#F1FAEE"

ADMIN_PASSWORD = "admin123"

# 🔐 Hashear correo (privacidad)
def hash_correo(correo):
    return hashlib.sha256(correo.encode()).hexdigest()


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("🗳️ Votación PROA Río Tercero")

        self.attributes("-fullscreen", True)
        self.bind_all("<Escape>", self.intentar_salir_esc)
        self.protocol("WM_DELETE_WINDOW", self.bloquear_salida_alt_f4)

        self.configure(fg_color=COLOR_FONDO)

        self.db = BaseDeDatos()
        self.verificador = VerificadorCorreo("correos_permitidos.txt")

        self.frame = None
        self.intentos_admin = 0

        self.bind_all("<Control-Shift-A>", self.abrir_admin)

        self.cambiar(Inicio)

    def cambiar(self, frame, datos=None):
        if self.frame:
            self.frame.destroy()

        self.frame = frame(self, self, datos) if datos else frame(self, self)
        self.frame.pack(expand=True, fill="both")

    def intentar_salir_esc(self, event=None):
        pwd = simpledialog.askstring("Salir", "Clave admin:", show="*")
        if pwd == ADMIN_PASSWORD:
            sys.exit()
        elif pwd:
            messagebox.showerror("Error", "Incorrecta")

    def abrir_admin(self, event=None):
        pwd = simpledialog.askstring("Admin", "Clave:", show="*")

        if pwd == ADMIN_PASSWORD:
            self.intentos_admin = 0
            self.cambiar(Admin)
        else:
            self.intentos_admin += 1
            messagebox.showerror("Error", "Clave incorrecta")

            if self.intentos_admin >= 3:
                messagebox.showwarning("Bloqueado", "Demasiados intentos")
                time.sleep(2)
                self.intentos_admin = 0

    def bloquear_salida_alt_f4(self):
        messagebox.showwarning("Bloqueado", "Usá ESC + clave admin")


# ---------------- INICIO ----------------

class Inicio(ctk.CTkFrame):
    def __init__(self, p, c):
        super().__init__(p, fg_color=COLOR_FONDO)

        ctk.CTkLabel(self, text="🗳️ ELECCIONES PROA",
                     font=("Arial Black", 50),
                     text_color=COLOR_BLANCO).pack(pady=200)

        ctk.CTkButton(
            self,
            text="INICIAR VOTACIÓN",
            font=("Arial Bold", 26),
            fg_color=COLOR_ROJO,
            width=400,
            height=80,
            command=lambda: c.cambiar(Formulario)
        ).pack()


# ---------------- FORMULARIO ----------------

class Formulario(ctk.CTkFrame):
    def __init__(self, p, c):
        super().__init__(p, fg_color=COLOR_FONDO)
        self.c = c

        ctk.CTkLabel(self, text="Identificación",
                     font=("Arial Bold", 35),
                     text_color=COLOR_BLANCO).pack(pady=80)

        self.nombre = ctk.CTkEntry(self, placeholder_text="Nombre completo", width=400)
        self.nombre.pack(pady=10)

        self.correo = ctk.CTkEntry(self, placeholder_text="Correo institucional", width=400)
        self.correo.pack(pady=10)

        ctk.CTkButton(self, text="Continuar",
                      fg_color=COLOR_ROJO,
                      command=self.validar).pack(pady=30)

    def validar(self):
        nombre = self.nombre.get().strip()
        correo = self.correo.get().strip()

        if not nombre or not correo:
            messagebox.showerror("Error", "Completá todos los campos")
            return

        if not self.c.verificador.correo_permitido(correo):
            messagebox.showerror("Error", "Correo no autorizado")
            return

        correo_hash = hash_correo(correo)

        if self.c.db.ya_voto(correo_hash):
            messagebox.showwarning("Atención", "Ya votaste")
            return

        self.c.cambiar(Votacion, {"correo": correo_hash, "nombre": nombre})


# ---------------- VOTACIÓN ----------------

class Votacion(ctk.CTkFrame):
    def __init__(self, p, c, d):
        super().__init__(p, fg_color=COLOR_FONDO)
        self.c = c
        self.d = d
        self.votado = False

        ctk.CTkLabel(self,
                     text=f"{d['nombre']}, elegí lista",
                     font=("Arial Bold", 30),
                     text_color=COLOR_BLANCO).pack(pady=60)

        self.crear_boton("Lista Roja", COLOR_ROJO)
        self.crear_boton("Lista Azul", COLOR_AZUL)
        self.crear_boton("Blanco", "gray")

    def crear_boton(self, texto, color):
        ctk.CTkButton(
            self,
            text=texto,
            fg_color=color,
            width=500,
            height=100,
            command=lambda: self.votar(texto)
        ).pack(pady=20)

    def votar(self, lista):

        if self.votado:
            return

        confirmacion = messagebox.askyesno("Confirmar", f"Votar {lista}?")

        if not confirmacion:
            return

        doble = messagebox.askyesno("Confirmación FINAL", "¿Seguro seguro?")

        if not doble:
            return

        self.votado = True

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
            messagebox.showerror("Error", "No se guardó")


# ---------------- FINAL ----------------

class Final(ctk.CTkFrame):
    def __init__(self, p, c):
        super().__init__(p, fg_color=COLOR_FONDO)

        ctk.CTkLabel(self,
                     text="✅ VOTO REGISTRADO",
                     font=("Arial Bold", 45),
                     text_color="green").pack(pady=200)

        self.after(2500, lambda: c.cambiar(Inicio))


# ---------------- ADMIN ----------------

class Admin(ctk.CTkFrame):
    def __init__(self, p, c):
        super().__init__(p, fg_color=COLOR_FONDO)
        self.c = c

        ctk.CTkLabel(self, text="ADMIN",
                     font=("Arial Bold", 30),
                     text_color=COLOR_BLANCO).pack(pady=40)

        self.label = ctk.CTkLabel(self, text="", font=("Arial", 20))
        self.label.pack()

        ctk.CTkButton(self, text="Actualizar", command=self.actualizar).pack(pady=10)
        ctk.CTkButton(self, text="Exportar", command=self.exportar).pack(pady=10)
        ctk.CTkButton(self, text="Reset", fg_color="red", command=self.borrar).pack(pady=10)

        self.actualizar()

    def actualizar(self):
        self.label.configure(text=f"Votos: {self.c.db.total()}")

    def exportar(self):
        datos = self.c.db.votos_sin_lista()

        df = pd.DataFrame(datos, columns=["Nombre", "Fecha"])
        df.to_excel("votos.xlsx", index=False)

        messagebox.showinfo("OK", "Exportado")

    def borrar(self):
        if messagebox.askyesno("Seguro?", "Borrar TODO"):
            self.c.db.borrar_todo()
            self.actualizar()


if __name__ == "__main__":
    app = App()
    app.mainloop()
