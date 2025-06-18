# MiVet Login API  
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/TheLexa69/mivet-login-api)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/TheLexa69/mivet-login-api/actions) [![Python](https://img.shields.io/badge/python-3.10+-blue)](https://www.python.org/) [![Flask](https://img.shields.io/badge/flask-2.3.3-yellow)](https://flask.palletsprojects.com/) 
[![Docker](https://img.shields.io/badge/docker-ready-blue)](https://www.docker.com/)  

---

## Índice
- [📘 Supuesto](#supuesto)
- [⚙️ Arquitectura General](#arquitectura-general)
- [🧪 Manual Técnico para Desarrolladores](#manual-técnico-para-desarrolladores)
- [🚀 Endpoints y Funcionalidades](#endpoints-y-funcionalidades)
- [🧩 Modelo de Datos y Seguridad](#modelo-de-datos-y-seguridad)
- [🧑‍💻 Manual de Usuario](#manual-de-usuario)
- [💡 Conclusiones](#conclusiones)
- [⏱ Dedicación Estimada](#dedicación-estimada)

---

## Supuesto

Este microservicio forma parte del ecosistema **MiVet**, actuando como **servicio de autenticación y registro**. Se encarga de:

- Registro de usuarios (con mascotas asociadas).
- Inicio de sesión con emisión de JWT.
- Gestión de tokens persistentes en base de datos.
- Validación de roles y tipos de usuario.
- Documentación automática con Swagger (`/docs`).

---

## Arquitectura General

La API está desarrollada con **Flask** y utiliza:
- `Flask-RESTx`: documentación y estructura REST.
- `python-dotenv`: carga de configuración desde `.env`.
- `python-jose`: generación de tokens JWT.
- `MySQL`: motor de base de datos relacional.

### Flujo simplificado:
```
Cliente → /register → Crea Usuario + Mascotas + Token
Cliente → /login → Verifica credenciales + Emite nuevo Token
Cliente → Acceso protegido en otros servicios mediante JWT
```

---

## Manual Técnico para Desarrolladores

### Requisitos
- Python 3.10+
- MySQL 8+
- pip + venv (opcional)
- Docker (opcional)

### Variables de entorno
Al clonar el proyecto, copia `.env.example` y crea un `.env`:
```env
SECRET_KEY=clave
DB_HOST=localhost
DB_USER=root
DB_PASS=root
DB_NAME=database
DB_PORT=3306
```

### Instalación y ejecución local

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar app
python app.py
```

> Accede a la documentación Swagger en: [http://localhost:5000/docs](http://localhost:5000/docs)

### Docker (opcional)
```bash
docker build -t mivet-login-api .
docker run -p 5000:5000 mivet-login-api
```

---

## Endpoints y Funcionalidades

### `/login` (POST)
Autenticación de usuario.
- Verifica email y contraseña.
- Emite un token JWT válido por 24h.
- Almacena token en la tabla `Auth`.

**Body**:
```json
{
  "email": "user@mail.com",
  "contrasena": "1234"
}
```

**Respuesta**:
```json
{
  "success": true,
  "token": "<JWT>",
  "user_id": 5,
  "rol": "usuario",
  "tipo_usuario": "privado"
}
```

---

###  `/register` (POST)
Registra un nuevo usuario + mascotas asociadas.
- Verifica duplicado por correo.
- Inserta usuario, mascotas y entrada en tabla `Auth`.

**Body**:
```json
{
  "nombre": "Carlos",
  "correo": "carlos@mail.com",
  "contrasena": "1234",
  "tipo_usuario": "privado",
  "rol": "usuario",
  "mascotas": [
    {
      "tipo": "perro",
      "nombre": "Toby",
      "raza": "Labrador",
      "fecha_nac": "2021-03-05"
    }
  ]
}
```

**Respuesta**:
```json
{
  "success": true,
  "user_id": 7,
  "token": "<JWT>",
  "secret": "<clave privada>",
  "rol": "usuario",
  "tipo_usuario": "privado"
}
```

---

### `/status` y `/ping`
Endpoints de prueba:
- `/status`: para verificar estado general.
- `/ping`: retorna `{ message: "pong" }`.

---

## Modelo de Datos y Seguridad

### Entidades utilizadas:
- **`Usuario`**: nombre, correo, contraseña, rol, tipo.
- **`Mascota`**: tipo, nombre, raza, fecha_nac, id_usuario.
- **`Auth`**: token, secret, servicio, id_usuario.

### Seguridad
- Tokens JWT generados con `python-jose`.
- Incluyen: `user_id`, `rol`, `tipo_usuario` y `exp`.
- Validez de 24h.
- Se almacenan en `Auth` para trazabilidad o verificación futura.

---

## Manual de Usuario

- El usuario puede registrarse desde `/register`, adjuntando una o varias mascotas.
- Luego puede iniciar sesión desde `/login` y usar su token en otros microservicios (como `mivet-api`).
- Todos los tokens incluyen rol y tipo de usuario, lo que permite gestionar permisos desde otros servicios.

---

## Conclusiones

Este microservicio proporciona la capa de autenticación y registro del sistema MiVet. Está diseñado para ser liviano, seguro y fácil de integrar con otros servicios mediante JWT. Su enfoque REST y documentación integrada facilitan su adopción.

---

## Dedicación Estimada

Se invirtieron aproximadamente **25-30 horas** en la arquitectura, conexión a base de datos, JWT, validación de usuario y documentación Swagger.
