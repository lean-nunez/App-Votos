import sqlite3

class BaseDeDatos:
    def __init__(self):
        self.conn = sqlite3.connect("votos.db")
        self.crear_tabla()

    def crear_tabla(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS votos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    correo TEXT UNIQUE,
                    lista TEXT
                )
            """)

    def guardar_voto(self, correo, lista):
        try:
            with self.conn:
                self.conn.execute(
                    "INSERT INTO votos (correo, lista) VALUES (?, ?)",
                    (correo, lista)
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def contar_votos(self):
        with self.conn:
            cursor = self.conn.execute("SELECT lista, COUNT(*) FROM votos GROUP BY lista")
            return cursor.fetchall()

    def correo_ya_voto(self, correo):
        cursor = self.conn.execute("SELECT 1 FROM votos WHERE correo = ?", (correo,))
        return cursor.fetchone() is not None