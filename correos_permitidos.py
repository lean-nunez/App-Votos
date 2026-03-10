class VerificadorCorreo:
    def __init__(self, archivo_txt):
        with open(archivo_txt, "r") as f:
            self.correos_permitidos = set(line.strip() for line in f if line.strip())

    def correo_permitido(self, correo):
        return correo in self.correos_permitidos