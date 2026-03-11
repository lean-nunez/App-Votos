import sqlite3
conn = sqlite3.connect("votos_proa.db")
conn.execute("DELETE FROM votos")
conn.commit()
conn.close()
print("Base de datos reiniciada. Ya puedes volver a votar.")