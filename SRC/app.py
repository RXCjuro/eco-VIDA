import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import bcrypt
import jwt
import datetime

app = Flask(__name__)
CORS(app)

# ==========================================
# CONFIGURACIÓN
# ==========================================

MONGO_URI = os.getenv("MONGO_URI")
SECRET_KEY = os.getenv("SECRET_KEY", "clave-secreta-ecovida")

# ==========================================
# CONEXIÓN CON MONGODB
# ==========================================

if not MONGO_URI:
    print("ERROR: No existe la variable MONGO_URI")
    client = None
    db = None
    usuarios = None
else:
    try:
        client = MongoClient(MONGO_URI)
        db = client["ecovida_db"]
        usuarios = db["usuarios"]

        print("Conexión con MongoDB correcta")

    except Exception as error:
        print("Error de conexión con MongoDB:", error)
        client = None
        db = None
        usuarios = None


# ==========================================
# REGISTRAR USUARIO
# ==========================================

@app.route("/api/registro", methods=["POST"])
def registrar_usuario():

    if usuarios is None:
        return jsonify({
            "error": "MongoDB no está conectado"
        }), 500

    datos = request.get_json()

    nombre = datos.get("nombre")
    correo = datos.get("correo")
    contrasena = datos.get("contrasena")

    if not nombre or not correo or not contrasena:
        return jsonify({
            "error": "Todos los campos son obligatorios"
        }), 400

    # Convertimos el correo a minúsculas
    correo = correo.lower().strip()

    # Verificar si ya existe
    usuario_existente = usuarios.find_one({
        "correo": correo
    })

    if usuario_existente:
        return jsonify({
            "error": "El correo ya está registrado"
        }), 400

    # Encriptar contraseña
    password_encriptada = bcrypt.hashpw(
        contrasena.encode("utf-8"),
        bcrypt.gensalt()
    )

    nuevo_usuario = {
        "nombre": nombre,
        "correo": correo,
        "contrasena": password_encriptada.decode("utf-8"),
        "rol": "usuario"
    }

    resultado = usuarios.insert_one(nuevo_usuario)

    return jsonify({
        "mensaje": "Usuario registrado correctamente",
        "usuario": {
            "id": str(resultado.inserted_id),
            "nombre": nombre,
            "correo": correo,
            "rol": "usuario"
        }
    }), 201


# ==========================================
# LOGIN
# ==========================================

@app.route("/api/login", methods=["POST"])
def iniciar_sesion():

    if usuarios is None:
        return jsonify({
            "error": "MongoDB no está conectado"
        }), 500

    datos = request.get_json()

    correo = datos.get("correo")
    contrasena = datos.get("contrasena")

    if not correo or not contrasena:
        return jsonify({
            "error": "Correo y contraseña son obligatorios"
        }), 400

    correo = correo.lower().strip()

    # Buscar usuario
    usuario = usuarios.find_one({
        "correo": correo
    })

    if not usuario:
        return jsonify({
            "error": "Correo o contraseña incorrectos"
        }), 401

    # Verificar contraseña
    password_correcta = bcrypt.checkpw(
        contrasena.encode("utf-8"),
        usuario["contrasena"].encode("utf-8")
    )

    if not password_correcta:
        return jsonify({
            "error": "Correo o contraseña incorrectos"
        }), 401

    # Crear token
    token = jwt.encode(
        {
            "id": str(usuario["_id"]),
            "correo": usuario["correo"],
            "rol": usuario.get("rol", "usuario"),
            "exp": datetime.datetime.now(datetime.timezone.utc)
                    + datetime.timedelta(hours=2)
        },
        SECRET_KEY,
        algorithm="HS256"
    )

    return jsonify({
        "mensaje": "Inicio de sesión correcto",
        "token": token,
        "usuario": {
            "id": str(usuario["_id"]),
            "nombre": usuario["nombre"],
            "correo": usuario["correo"],
            "rol": usuario.get("rol", "usuario")
        }
    }), 200


# ==========================================
# PRUEBA
# ==========================================

@app.route("/")
def inicio():
    return jsonify({
        "mensaje": "API de EcoVida funcionando"
    })


# ==========================================
# EJECUTAR SERVIDOR
# ==========================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        debug=True
    )