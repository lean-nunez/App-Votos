from flask import Flask, render_template, request, jsonify
from correos_permitidos import VerificadorCorreo
from db import BaseDeDatos

app = Flask(__name__)

ADMIN_PASSWORD = "admin123"

verificador = VerificadorCorreo("correos_permitidos.txt")
db = BaseDeDatos()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/validar', methods=['POST'])
def validar():
    data = request.get_json()
    correo = data.get('correo', '').strip().lower()

    if not correo:
        return jsonify({"status": "error", "message": "Ingrese un correo válido."})
    if not verificador.correo_permitido(correo):
        return jsonify({"status": "error", "message": "El correo no pertenece al padrón."})
    if db.correo_ya_voto(correo):
        return jsonify({"status": "error", "message": "Este correo ya ha votado."})

    return jsonify({"status": "success"})

@app.route('/votar', methods=['POST'])
def votar():
    data = request.get_json()
    correo = data.get('correo', '').strip().lower()
    lista = data.get('lista')

    # Re-validación de seguridad en el servidor
    if not correo or not lista:
        return jsonify({"status": "error", "message": "Datos incompletos."})
    if not verificador.correo_permitido(correo):
        return jsonify({"status": "error", "message": "No autorizado."})
    if db.correo_ya_voto(correo):
        return jsonify({"status": "error", "message": "Ya votó."})

    if db.guardar_voto(correo, lista):
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Error al guardar el voto."})

@app.route('/admin_resultados', methods=['GET', 'POST'])
def admin_resultados():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            conteo_db = db.obtener_recuento()
            
            # Aseguramos que todas las listas aparezcan aunque tengan 0 votos
            conteo = {
                'LISTA AZUL': conteo_db.get('LISTA AZUL', 0),
                'LISTA NEGRA': conteo_db.get('LISTA NEGRA', 0),
                'VOTO EN BLANCO': conteo_db.get('VOTO EN BLANCO', 0)
            }
            
            participantes = db.obtener_participantes()
            return render_template(
                'resultados.html',
                conteo=conteo,
                participantes=participantes,
                autorizado=True
            )
        return render_template('resultados.html', error="Contraseña incorrecta", autorizado=False)
    
    return render_template('resultados.html', autorizado=False)

if __name__ == '__main__':
    app.run(debug=True)
