class VerificadorCorreo:
    def __init__(self, archivo_txt):
        self.correos_permitidos = set()
        try:
            with open(archivo_txt, "r", encoding="utf-8") as f:
                # Usamos strip() para eliminar espacios y saltos de línea
                self.correos_permitidos = {
                    line.strip().lower()
                    for line in f
                    if line.strip()
                }
        except FileNotFoundError:
            print("Error: No se encontró el archivo de correos.")

    def correo_permitido(self, correo):
        return correo.strip().lower() in self.correos_permitidos
