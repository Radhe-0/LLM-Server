from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import querys



app = Flask(__name__)


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data["email"]
    password = data["password"]
    print(f"\n\n{email}")

    conn = querys.conectar_mariadb()
    usuario_valido = querys.login(conn, email, password)

    if usuario_valido:
        return jsonify({"tipo": "login", "data": "credenciales correctas"})
    else:
        return jsonify({"tipo": "login", "data": "credenciales incorrectas"})


@app.route("/registro", methods=["POST"])
def registro():
    data = request.get_json()
    email = data["email"]
    password = data["password"]

    conn = querys.conectar_mariadb()
    registro_correcto = querys.nuevo_usuario(conn, email, password)
    print(registro_correcto)

    if registro_correcto:
        return jsonify({"tipo": "registro", "data": "registro exitoso"})
    else:
        return jsonify({"tipo": "registro", "data": "correo ya existente"})



if __name__ == "__main__":
    app.run(debug=True, port=5000)
