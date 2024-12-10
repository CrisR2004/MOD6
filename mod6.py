from flask import Flask, request, render_template, redirect, url_for
import redis
import json

app = Flask(__name__)

# Configuración de la base de datos Redis
client = redis.Redis(host='localhost', port=6379, db=0)


# Ruta para la página principal que lista todas las recetas
@app.route('/')
def index():
    recetas = []
    for key in client.scan_iter("receta:*"):
        receta_id = key.decode().split(":")[1]
        receta_data = json.loads(client.get(key).decode())
        receta_data['id'] = receta_id
        recetas.append(receta_data)
    return render_template('index.html', recetas=recetas)


# Ruta para agregar una nueva receta
@app.route('/agregar', methods=['POST'])
def agregar_receta():
    nombre = request.form['nombre']
    ingredientes = request.form['ingredientes']
    pasos = request.form['pasos']
    receta_id = client.incr('receta_id')

    nueva_receta = {
        "nombre": nombre,
        "ingredientes": ingredientes,
        "pasos": pasos
    }

    client.set(f"receta:{receta_id}", json.dumps(nueva_receta))
    return redirect(url_for('index'))


# Ruta para ver una receta específica por ID
@app.route('/receta/<int:receta_id>')
def ver_receta(receta_id):
    receta_key = f"receta:{receta_id}"
    if client.exists(receta_key):
        receta = json.loads(client.get(receta_key).decode())
        return render_template('ver_receta.html', receta=receta, receta_id=receta_id)
    else:
        return "Receta no encontrada", 404


# Ruta para actualizar una receta
@app.route('/editar/<int:receta_id>', methods=['POST'])
def actualizar_receta(receta_id):
    receta_key = f"receta:{receta_id}"
    if client.exists(receta_key):
        nombre = request.form['nombre']
        ingredientes = request.form['ingredientes']
        pasos = request.form['pasos']

        receta_actualizada = {
            "nombre": nombre,
            "ingredientes": ingredientes,
            "pasos": pasos
        }

        client.set(receta_key, json.dumps(receta_actualizada))
        return redirect(url_for('index'))
    else:
        return "Receta no encontrada", 404


# Ruta para eliminar una receta
@app.route('/eliminar/<int:receta_id>', methods=['POST'])
def eliminar_receta(receta_id):
    receta_key = f"receta:{receta_id}"
    if client.exists(receta_key):
        client.delete(receta_key)
        return redirect(url_for('index'))
    else:
        return "Receta no encontrada", 404


# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)
