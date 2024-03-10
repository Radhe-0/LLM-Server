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


@app.route("/contactos", methods=["GET"])
def obtener_contactos():
    correo_electronico = request.args.get("correo_electronico")
    if correo_electronico:
        conn = querys.conectar_mariadb()
        contactos = querys.obtener_contactos_usuario(conn, correo_electronico)
        if contactos:
            return jsonify({"tipo": "obtener_contactos", "data": contactos})
        else:
            return jsonify({"tipo": "obtener_contactos", "data": "No se encontraron contactos para ese correo electrónico"})
    else:
        return jsonify({"tipo": "obtener contactos", "data": "Debe proporcionar un correo electrónico"})


@app.route("/obtener_foto", methods=["GET"])
def obtener_foto():
    email = request.args.get("email")
    if email:
        conn = querys.conectar_mariadb()
        imagenb64 = querys.obtener_foto_usuario(conn, email)
        if imagenb64:
            return jsonify({"tipo": "obtener_foto", "data": {"imagenb64": imagenb64}})
        else:
            return jsonify({"tipo": "obtener_foto", "data": "No se pudo obtener la foto de perfil para ese correo electrónico"}), 404
    else:
        return jsonify({"tipo": "obtener_foto", "data": "Debe proporcionar un correo electrónico"}), 400


@app.route("/actualizar_foto", methods=["POST"])
def actualizar_foto():
    data = request.get_json()
    email = data["email"]
    imagenb64 = data["imagenb64"]

    if email and imagenb64:
        conn = querys.conectar_mariadb()
        exito = querys.actualizar_foto(conn, email, imagenb64)
        foto = querys.obtener_foto_usuario(conn, email)

        if exito:
            return jsonify({"tipo": "actualizar_foto", "data": {"imagenb64": foto}})
        else:
            return jsonify({"tipo": "actualizar_foto", "data": "No se pudo actualizar la foto de perfil"}), 500
    else:
        return jsonify({"tipo": "actualizar_foto", "data": "Debe proporcionar un correo electrónico y la imagen en formato base64"}), 400



if __name__ == "__main__":
    app.run(debug=True, port=5000)
