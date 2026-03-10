import customtkinter as ctk
from PIL import Image
from correos_permitidos import VerificadorCorreo
from db import BaseDeDatos

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Voto Electronico - PRoA")
        self.attributes("-fullscreen", True)
        self.bind("<Control-Shift-Q>", lambda event: self.attributes("-fullscreen", False))
        self.bind("<Control-Shift-F>", self.mostrar_conteo)
        self.geometry("800x600")
        self.resizable(False, False)
        self.iconbitmap("./code/assets/logo_proa.ico")

        self.verificador_correo = VerificadorCorreo("code/correos_permitidos.txt")
        self.db = BaseDeDatos()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Voto Electronico - PRoA")
        self.attributes("-fullscreen", True)
        self.bind("<Control-Shift-Q>", lambda event: self.attributes("-fullscreen", False))
        self.geometry("800x600")
        self.resizable(False, False)
        self.iconbitmap("./code/assets/logo_proa.ico")

        self.verificador_correo = VerificadorCorreo("code/correos_permitidos.txt")
        self.db = BaseDeDatos()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frames = {}

        for F in (Inicio, Formulario, Final):
            if F == Formulario:
                frame = F(self, self.cambiar_frame, self.verificador_correo, self.db)
            else:
                frame = F(self, self.cambiar_frame)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.cambiar_frame(Inicio)

    def cambiar_frame(self, frame_class, *args, **kwargs):
        if frame_class not in self.frames:
            if frame_class == Votacion:
                frame = frame_class(self, self.cambiar_frame, *args, **kwargs)
            else:
                frame = frame_class(self, self.cambiar_frame)
            self.frames[frame_class] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        frame = self.frames[frame_class]
        frame.tkraise()

class Inicio(ctk.CTkFrame):
    def __init__(self, parent, cambiar_frame):
        super().__init__(parent)
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)
        self.grid_columnconfigure((0), weight=1)

        self.titulo = ctk.CTkLabel(self, text="Voto Electronico - PRoA", font=("Arial", 30))
        self.titulo.grid(row=0, column=0, pady=10)

        self.logo = ctk.CTkImage(Image.open("./code/assets/images/logo_proa.png"), size=(250, 250))
        self.logo_label = ctk.CTkLabel(self, text="", image=self.logo)
        self.logo_label.grid(row=1, column=0, pady=10)

        self.boton_iniciar = ctk.CTkButton(self, text="Iniciar Votación", height=50, width=150, command=lambda: cambiar_frame(Formulario))
        self.boton_iniciar.grid(row=3, column=0, pady=10)

class Formulario(ctk.CTkFrame):
    def __init__(self, master, cambiar_frame, verificador_correo, db):
        super().__init__(master)
        self.verificador_correo = verificador_correo
        self.cambiar_frame = cambiar_frame
        self.db = db

        self.grid_rowconfigure((0, 1, 2), weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.max_caracteres = 50

        self.titulo = ctk.CTkLabel(self, text="Formulario de Inscripción", font=("Arial", 30))
        self.titulo.grid(row=0, column=0, pady=10)

        self.correo_entry = ctk.CTkEntry(self, placeholder_text="Ingrese su correo electrónico", width=500, height=50, font=("Arial", 20), text_color="black", fg_color="white", validate="key", validatecommand=(self.register(self.validar_caracteres), "%P"))
        self.correo_entry.grid(row=1, column=0)

        self.boton_enviar = ctk.CTkButton(self, text="Enviar", height=50, width=150, command=self.validar_formulario)
        self.boton_enviar.grid(row=2, column=0, pady=20)

    def validar_caracteres(self, texto):
        if len(texto) > self.max_caracteres:
            return False
        return True

    def validar_formulario(self):
        correo = self.correo_entry.get().strip()

        if not correo:
            self.mostrar_error("Todos los campos son obligatorios.")
            return

        if not self.verificador_correo.correo_permitido(correo):
            self.mostrar_error("Este correo no está permitido para votar.")
            return
        
        if self.db.correo_ya_voto(correo):
            self.mostrar_error("Este correo ya ha sido usado para votar.")
            return

        datos_formulario = {
            "correo": correo
        }

        self.cambiar_frame(Votacion, datos_formulario)

    def mostrar_error(self, mensaje):
        error_label = ctk.CTkLabel(self, text=mensaje, text_color="red", font=("Arial", 16))
        error_label.grid(row=5, column=0, columnspan=3, pady=10)

class Votacion(ctk.CTkFrame):
    def __init__(self, parent, cambiar_frame, datos_formulario):
        super().__init__(parent)
        self.parent = parent
        self.cambiar_frame = cambiar_frame
        self.datos_formulario = datos_formulario
        self.db = parent.db  # así accedés a la instancia de BaseDeDatos

        ctk.CTkLabel(self, text="Elegí tu lista").pack(pady=20)

        self.boton_lista1 = ctk.CTkButton(self, height=50, width=150, text="Lista Azul",font=("Arial", 30),command=lambda: self.votar("Lista Azul"))
        self.boton_lista1.place(relx=0.3, rely=0.5, anchor="center")

        self.boton_lista2 = ctk.CTkButton(self, height=50, width=150, text="Lista Negra",fg_color="black", hover_color="black",font=("Arial", 30),command=lambda: self.votar("Lista Negra"))
        self.boton_lista2.place(relx=0.7, rely=0.5, anchor="center")

        self.boton_lista3 = ctk.CTkButton (self, height=50, width=200, text="Voto en Blanco", fg_color="white", hover_color="gray", font=("Arial", 30), text_color="black",command=lambda: self.votar("Voto en Blanco"))
        self.boton_lista3.place(relx=0.5, rely=0.7, anchor="center")

    def votar(self, lista):
        correo = self.datos_formulario["correo"].strip()

        self.db.guardar_voto(correo, lista) 
        self.master.frames[Final].mostrar()


class Final(ctk.CTkFrame):
    def __init__(self, parent, cambiar_frame):
        super().__init__(parent)
        self.cambiar_frame = cambiar_frame

        self.grid_rowconfigure((0, 1), weight=1)
        self.grid_columnconfigure((0), weight=1)

        self.titulo = ctk.CTkLabel(self, text="¡Gracias por votar!", font=("Arial", 30))
        self.titulo.grid(row=0, column=0, pady=10)

        self.gatito = ctk.CTkImage(Image.open("./code/assets/images/gatito.png"), size=(400, 400))
        self.gatito_label = ctk.CTkLabel(self, text="", image=self.gatito)
        self.gatito_label.grid(row=1, column=0, pady=10)

    def mostrar(self):
        self.tkraise()
        self.after(5000, lambda: self.cambiar_frame(Inicio))

if __name__ == "__main__":
    app = App()
    app.mainloop()