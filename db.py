import sqlite3
import hashlib

class BaseDeDatos:

    def __init__(self, db_name="votos.db"):
        self.db_name = db_name
        self.crear_tabla() # Esto DEBE ejecutarse primero.

    def _hash(self, correo):
        return hashlib.sha256(correo.strip().lower().encode()).hexdigest()

    def ejecutar(self, sql, params=(), fetch=False, one=False):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                
                if fetch:
                    # Forzamos a que devuelva una lista vacía si no hay datos
                    resultado = cursor.fetchall()
                    return resultado if resultado is not None else []
                
                if one:
                    return cursor.fetchone()
                    
                conn.commit()
                return True
        except Exception as e:
            print(f"Error DB en '{sql}':", e)
            if fetch:
                return []
            return None

    def crear_tabla(self):
        # Nos aseguramos de que la tabla exista sí o sí al iniciar
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS votos(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    correo_hash TEXT UNIQUE,
                    nombre TEXT,
                    lista TEXT,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
                conn.commit()
        except Exception as e:
            print("Error al crear la tabla inicial:", e)

    def guardar_voto(self, correo, nombre, lista):
        r = self.ejecutar(
            "INSERT INTO votos (correo_hash, nombre, lista) VALUES (?, ?, ?)",
            (self._hash(correo), nombre.strip(), lista)
        )
        return r is not None

    def ya_voto(self, correo):
        r = self.ejecutar(
            "SELECT 1 FROM votos WHERE correo_hash=?",
            (self._hash(correo),), one=True
        )
        return r is not None

    def votos_sin_lista(self):
        # No extrae la columna 'lista' para que no se guarde en el excel
        return self.ejecutar("SELECT nombre, fecha FROM votos ORDER BY fecha DESC", fetch=True)

    def votos_detallados(self):
        return self.ejecutar("SELECT nombre, lista, fecha FROM votos ORDER BY fecha DESC", fetch=True)

    def stats(self):
        return self.ejecutar(
            "SELECT lista, COUNT(*) FROM votos GROUP BY lista ORDER BY COUNT(*) DESC",
            fetch=True
        )

    def total(self):
        r = self.ejecutar("SELECT COUNT(*) FROM votos", one=True)
        return r[0] if r else 0

    def borrar_todo(self):
        self.ejecutar("DELETE FROM votos")
