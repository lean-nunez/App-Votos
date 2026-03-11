import sqlite3

class BaseDeDatos:
    def __init__(self):
        self.db_name = "votos_proa.db"
        self.crear_tabla()

    def crear_tabla(self):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS votos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    correo TEXT UNIQUE NOT NULL,
                    lista TEXT NOT NULL,
                    fecha DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def guardar_voto(self, correo, lista):
        try:
            with sqlite3.connect(self.db_name) as conn:
                conn.execute(
                    "INSERT INTO votos (correo, lista) VALUES (?, ?)",
                    (correo, lista)
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def correo_ya_voto(self, correo):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.execute(
                "SELECT 1 FROM votos WHERE correo = ?",
                (correo,)
            )
            return cursor.fetchone() is not None

    def obtener_recuento(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.execute(
                "SELECT lista, COUNT(*) FROM votos GROUP BY lista"
            )
            return dict(cursor.fetchall())

    def obtener_participantes(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.execute(
                "SELECT correo, fecha FROM votos ORDER BY fecha DESC"
            )
            return cursor.fetchall()
