import customtkinter as ctk
import pandas as pd
import os
import sys
from tkinter import messagebox, simpledialog
from PIL import Image
import datetime

ctk.set_appearance_mode("dark")

COLOR_FONDO = "#1D3557"
COLOR_ROJO = "#E63946"
COLOR_AZUL = "#457B9D"
COLOR_BLANCO = "#F1FAEE"

ARCHIVO = "votos.xlsx"
ADMIN_PASSWORD = "admin123"


# ---------------- HEADER ----------------
class Header(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="x", pady=10, padx=20)

        cont = ctk.CTkFrame(self, fg_color="transparent")
        cont.pack(fill="x")

        try:
            img = Image.open("logo.png")
            img = img.resize((70, 70))
            self.logo = ctk.CTkImage(img)

            ctk.CTkLabel(cont, image=self.logo, text="").pack(side="left")
        except:
            ctk.CTkLabel(cont, text="PROA", font=("Arial Bold", 20)).pack(side="left")

        ctk.CTkLabel(
            cont,
            text="Escuela PROA Río Tercero",
            font=("Arial Bold", 20),
            text_color="white"
        ).pack(side="left", padx=10)

        ctk.CTkFrame(parent, height=2, fg_color="#A8DADC").pack(fill="x", padx=20)


# ---------------- BASE EXCEL ----------------
def cargar_datos():
    if not os.path.exists(ARCHIVO):
        df = pd.DataFrame(columns=["Nombre", "Correo", "Lista", "Fecha"])
        df.to_excel(ARCHIVO, index=False)
    return pd.read_excel(ARCHIVO)


def guardar_voto(nombre, correo, lista):
    df = cargar_datos()

    if correo in df["Correo"].values:
        return False

    nuevo = {
        "Nombre": nombre,
        "Correo": correo,
        "Lista": lista,
        "Fecha": datetime.datetime.now()
    }

    df = pd.concat([df, pd.DataFrame([nuevo])], ignore_index=True)
    df.to_excel(ARCHIVO, index=False)
    return True


# ---------------- APP ----------------
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Votación PROA")
        self.attributes("-fullscreen", True)
        self.configure(fg_color=COLOR_FONDO)

        self.bind("<Escape>", self.salir)
        self.bind_all("<Control-Shift-A>", self.admin)

        self.frame = None
        self.cambiar(Inicio)

    def cambiar(self, frame, datos=None):
        if self.frame:
            self.frame.destroy()

        self.frame = frame(self, self, datos) if datos else frame(self, self)
        self.frame.pack(expand=True, fill="both")

    def salir(self, event=None):
        pwd = simpledialog.askstring("Salir", "Clave:", show="*")
        if pwd == ADMIN_PASSWORD:
            sys.exit()

    def admin(self, event=None):
        pwd = simpledialog.askstring("Admin", "Clave:", show="*")
        if pwd == ADMIN_PASSWORD:
            self.cambiar(Admin)


# ---------------- INICIO ----------------
class Inicio(ctk.CTkFrame):
    def __init__(self, p, c):
        super().__init__(p, fg_color=COLOR_FONDO)

        Header(self)

        cont = ctk.CTkFrame(self, fg_color="transparent")
        cont.pack(expand=True)

        ctk.CTkLabel(
            cont,
            text="🗳️ ELECCIONES PROA",
            font=("Arial Black", 50),
            text_color=COLOR_BLANCO
        ).pack(pady=20)

        ctk.CTkButton(
            cont,
            text="COMENZAR",
            font=("Arial Bold", 30),
            fg_color=COLOR_ROJO,
            width=400,
            height=100,
            command=lambda: c.cambiar(Formulario)
        ).pack(pady=40)


# ---------------- FORMULARIO ----------------
class Formulario(ctk.CTkFrame):
    def __init__(self, p, c):
        super().__init__(p, fg_color=COLOR_FONDO)
        self.c = c

        Header(self)

        cont = ctk.CTkFrame(self, fg_color="transparent")
        cont.pack(expand=True)

        ctk.CTkLabel(cont, text="Identificación", font=("Arial Bold", 35)).pack(pady=30)

        self.nombre = ctk.CTkEntry(cont, placeholder_text="Nombre", width=400, height=50)
        self.nombre.pack(pady=10)

        self.correo = ctk.CTkEntry(cont, placeholder_text="Correo", width=400, height=50)
        self.correo.pack(pady=10)

        ctk.CTkButton(cont, text="Continuar", command=self.validar).pack(pady=30)

    def validar(self):
        nombre = self.nombre.get().strip()
        correo = self.correo.get().strip()

        if not nombre or not correo:
            messagebox.showerror("Error", "Completá todo")
            return

        df = cargar_datos()

        if correo in df["Correo"].values:
            messagebox.showwarning("Atención", "Ya votaste")
            return

        self.c.cambiar(Votacion, {"nombre": nombre, "correo": correo})


# ---------------- VOTACIÓN ----------------
class Votacion(ctk.CTkFrame):
    def __init__(self, p, c, d):
        super().__init__(p, fg_color=COLOR_FONDO)
        self.c = c
        self.d = d

        Header(self)

        ctk.CTkLabel(self, text="Elegí una opción", font=("Arial Bold", 35)).pack(pady=40)

        self.boton("🔴 Lista Roja", COLOR_ROJO)
        self.boton("🔵 Lista Azul", COLOR_AZUL)
        self.boton("⚪ Blanco", "gray")

    def boton(self, texto, color):
        ctk.CTkButton(
            self,
            text=texto,
            fg_color=color,
            width=500,
            height=100,
            command=lambda: self.votar(texto)
        ).pack(pady=20)

    def votar(self, lista):
        if messagebox.askyesno("Confirmar", f"Votar {lista}?"):

            ok = guardar_voto(self.d["nombre"], self.d["correo"], lista)

            if ok:
                self.c.cambiar(Final)
            else:
                messagebox.showerror("Error", "No se pudo guardar")


# ---------------- FINAL ----------------
class Final(ctk.CTkFrame):
    def __init__(self, p, c):
        super().__init__(p, fg_color=COLOR_FONDO)

        Header(self)

        ctk.CTkLabel(self, text="✅ VOTO REGISTRADO", font=("Arial Bold", 45)).pack(pady=200)

        self.after(2500, lambda: c.cambiar(Inicio))


# ---------------- ADMIN ----------------
class Admin(ctk.CTkFrame):
    def __init__(self, p, c):
        super().__init__(p, fg_color=COLOR_FONDO)

        Header(self)

        df = cargar_datos()

        ctk.CTkLabel(self, text="Panel Admin", font=("Arial Bold", 30)).pack(pady=30)

        ctk.CTkLabel(self, text=f"Total votos: {len(df)}", font=("Arial", 20)).pack(pady=10)

        ctk.CTkButton(self, text="Abrir Excel", command=self.abrir).pack(pady=10)
        ctk.CTkButton(self, text="Resetear", fg_color="red", command=self.reset).pack(pady=10)
        ctk.CTkButton(self, text="Volver", command=lambda: c.cambiar(Inicio)).pack(pady=20)

    def abrir(self):
        os.startfile(ARCHIVO)

    def reset(self):
        if messagebox.askyesno("Seguro?", "Borrar todo"):
            os.remove(ARCHIVO)
            cargar_datos()
            messagebox.showinfo("OK", "Reiniciado")


# ---------------- RUN ----------------
if __name__ == "__main__":
    app = App()
    app.mainloop()
