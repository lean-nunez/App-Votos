import os
import re

class VerificadorCorreo:

    def __init__(self, archivo="correos_permitidos.txt"):
        self.correos = set()

        if os.path.exists(archivo):
            try:
                with open(archivo, "r", encoding="utf-8") as f:
                    for linea in f:
                        correo = linea.strip().lower()
                        if correo:
                            self.correos.add(correo)
            except Exception as e:
                print("Error al leer archivo de correos:", e)

    def correo_permitido(self, correo):
        return correo.strip().lower() in self.correos

    def correo_valido(self, correo):
        # Regex estándar para validación de correos electrónicos
        patron = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(patron, correo.strip()) is not None
