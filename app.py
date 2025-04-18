from flask import Flask, request
from flask_restx import Api, Resource, fields
import mysql.connector
import os
from dotenv import load_dotenv
from jose import jwt
from datetime import datetime, timedelta
import secrets

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
api = Api(app, doc='/docs', title="MiVet Login API", description="Gestión de login, registro y mascotas")

# -----------------------------
# CONFIGURACIÓN JWT
# -----------------------------
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 día

def crear_token_jwt(user_id, rol):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "user_id": user_id,
        "rol": rol,
        "exp": expire
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

# -----------------------------
# MODELOS PARA DOCUMENTACIÓN
# -----------------------------
mascota_model = api.model('Mascota', {
    'tipo': fields.String(required=True, description="Tipo de animal (perro, gato, exotico)"),
    'nombre': fields.String(required=True, description="Nombre de la mascota"),
    'raza': fields.String(required=True, description="Raza"),
    'fecha_nac': fields.String(required=True, description="Fecha de nacimiento (YYYY-MM-DD)")
})

login_model = api.model('LoginRequest', {
    'email': fields.String(required=True),
    'contrasena': fields.String(required=True)
})

register_model = api.model('RegisterRequest', {
    'nombre': fields.String(required=True),
    'correo': fields.String(required=True),
    'contrasena': fields.String(required=True),
    'tipo_usuario': fields.String(required=True),
    'rol': fields.String(required=True),
    'mascotas': fields.List(fields.Nested(mascota_model), required=True)
})

# -----------------------------
# CONEXIÓN MYSQL
# -----------------------------
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT"))
    )

# -----------------------------
# ENDPOINTS
# -----------------------------
@api.route('/ping')
class Ping(Resource):
    def get(self):
        return {"message": "pong"}

@api.route('/status')
class Status(Resource):
    def get(self):
        return {"status": "ok", "message": "API activa y funcionando."}

@api.route('/login')
class Login(Resource):
    @api.expect(login_model)
    def post(self):
        data = request.json
        email = data.get("email")
        contrasena = data.get("contrasena")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id, contrasena, rol FROM Usuario WHERE correo = %s AND contrasena = %s",
                       (email, contrasena))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if not user:
            return {"success": False, "message": "Credenciales inválidas"}, 401

        token = crear_token_jwt(user["id"], user["rol"])

        return {
            "success": True,
            "token": token,
            "user_id": user["id"],
            "rol": user["rol"]
        }

@api.route('/register')
class Register(Resource):
    @api.expect(register_model)
    def post(self):
        try:
            data = request.json
            nombre = data.get("nombre")
            correo = data.get("correo")
            contrasena = data.get("contrasena")
            tipo_usuario = data.get("tipo_usuario")
            rol = data.get("rol")
            mascotas = data.get("mascotas", [])

            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT id FROM Usuario WHERE correo = %s", (correo,))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return {"success": False, "message": "Este correo ya está registrado"}, 400

            # Crear usuario
            cursor.execute(
                "INSERT INTO Usuario (nombre, correo, contrasena, tipo_usuario, rol) VALUES (%s, %s, %s, %s, %s)",
                (nombre, correo, contrasena, tipo_usuario, rol)
            )
            conn.commit()
            user_id = cursor.lastrowid

            # Registrar mascotas
            for m in mascotas:
                cursor.execute(
                    "INSERT INTO Mascota (nombre, tipo, raza, fecha_nac, id_usuario) VALUES (%s, %s, %s, %s, %s)",
                    (m["nombre"], m["tipo"], m["raza"], m["fecha_nac"], user_id)
                )

            # Insertar en Auth
            token = crear_token_jwt(user_id, rol)
            user_secret = secrets.token_hex(16)

            cursor.execute(
                "INSERT INTO Auth (id_usuario, token, secret, service) VALUES (%s, %s, %s, %s)",
                (user_id, token, user_secret, "MiVet")
            )
            conn.commit()

            cursor.close()
            conn.close()

            return {
                "success": True,
                "message": "Usuario y mascotas registradas correctamente",
                "user_id": user_id,
                "token": token,
                "rol": rol,
                "secret": user_secret
            }

        except Exception as e:
            print("❌ Error en /register:", str(e))
            return {"success": False, "message": "Error interno del servidor: " + str(e)}, 500

# -----------------------------
# EJECUCIÓN LOCAL (opcional)
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)
