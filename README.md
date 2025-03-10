# API de Reservas de Vehículos

## 👨‍💻 Desarrollo Realizado Por  

**Ing. Juan Sebastián Gómez Díaz**  
*Ingeniero de Sistemas y Computación*  
📍 *Universidad Tecnológica de Pereira*  

Este proyecto es una API REST desarrollada en Python con Flask y MongoDB como base de datos NoSQL. Permite gestionar reservas de vehículos, asegurando que no haya reservas solapadas y aplicando penalizaciones a usuarios que cancelen excesivamente.

---

## 🛠️ Requisitos Previos

Antes de ejecutar la aplicación, asegúrate de tener instalados:
- **Docker** y **Docker Compose**
- **MongoDB**

---

## ♻️ Instalación y Ejecución con Docker

### 1. Clonar el Repositorio
```sh
   git clone https://github.com/SebaxtriUTP/Parqueadero-MONGO-FLASK.git
   cd Parqueadero-MONGO-FLASK
```

### 2. Configuración de Variables de Entorno

Crea y actualiza el archivo `.env` con los siguientes valores:

```bash
WEB_HOST=cs_api

MONGO_HOST=cs_mongodb
MONGO_PORT=27017
MONGO_USER=root-crashell
MONGO_PASS=password-crashell
MONGO_DB=db_crashell
```

Adicionalmente, el archivo `mongo-init.js` contiene la configuración de usuario y roles en MongoDB:

```javascript
db.createUser(
    {
        user: 'root-crashell',
        pwd: 'password-crashell',
        roles: [
            { role: "clusterMonitor", db: "admin" },
            { role: "dbOwner", db: "db_crashell" },
            { role: 'readWrite', db: 'db_crashell' }
        ]
    }
)
```

### 3. Iniciar los Contenedores
Ejecuta el siguiente comando para levantar la API Flask y la base de datos MongoDB:
```sh
docker compose up -d
```

Para monitorear los logs de los servicios:
```sh
docker logs -f cs_mongodb  # Logs de MongoDB
docker logs -f cs_api       # Logs de Flask API
```

Accede a la consola de MongoDB con:
```sh
docker exec -it cs_mongodb mongosh -u root-crashell -p password-crashell --authenticationDatabase admin
```

La API estará disponible en: `http://localhost:5000`

---

## 🌐 Endpoints

### 1. Obtener todas las reservas
```http
GET http://localhost:5000/reservas
```

### 2. Obtener todos los usuarios
```http
GET http://localhost:5000/usuarios
```

### 3. Obtener todos los vehículos
```http
GET http://localhost:5000/vehiculos
```

### 4. Crear un usuario
```http
POST http://localhost:5000/usuarios
```
**Ejemplo de JSON:**
```json
{
    "usuario_id": "usuario_id_3",
    "nombre": "Sebastian",
    "email": "sebastian@gmail.com"
}
```

### 5. Crear un vehículo
```http
POST http://localhost:5000/vehiculos
```
**Ejemplo de JSON:**
```json
{
    "vehiculo_id": "vehiculo_id_4",
    "marca": "Toyota",
    "modelo": "Fortuner",
    "placa": "PPT234",
    "disponibilidad": true,
    "tipo": "SUV"
}
```

### 6. Crear una reserva
```http
POST http://localhost:5000/reservas
```
**Ejemplo de JSON:**
```json
{
    "usuario_id": "usuario_id_3",
    "vehiculo_id": "vehiculo_id_3",
    "fecha_inicio": "2025-03-10T10:00:00",
    "fecha_fin": "2025-03-12T18:00:00"
}
```

### 7. Cancelar una reserva
```http
POST http://localhost:5000/reservas/cancelar
```
**Ejemplo de JSON:**
```json
{
  "reserva_id": "789",
  "motivo": "Cambio de planes"
}
```

---

## 🛠️ Lógica de Penalización

- Si un usuario cancela más de **3 veces en una semana**, se le penaliza por **7 días** y no podrá realizar nuevas reservas durante ese tiempo.
- Antes de aceptar una nueva reserva, se verifica si el usuario está penalizado.
- Se evita la doble reserva de un mismo vehículo en el mismo rango de fechas.

---

## ✨ Consultas Avanzadas en PyMongo

**1. Obtener todas las reservas de un usuario**
```python
obtener_reservas_usuario(usuario_id)
```

**2. Obtener el vehículo más reservado en el último mes**
```python
vehiculo_mas_reservado()
```

**3. Obtener los usuarios con más cancelaciones en el último mes**
```python
usuarios_mas_cancelaciones()
```

---

## 🌐 Arquitectura y Estructura de Archivos
```
/Parqueadero-MONGO-FLASK
│── app
    │── app.py              # Código principal de la API
    │── consultas.py        # Módulo con consultas a MongoDB
    │── Dockerfile          # Imagen de la API Flask
    │── requirements.txt    # Dependencias del proyecto
│── docker-compose.yml  # Configuración de Docker
│── mongo-init.js       # Script de inicialización de MongoDB
│── README.md           # Documentación
```

---

## 🛠️ Notas Adicionales
- La API maneja validaciones de fechas para evitar conflictos en reservas.
- Se implementa un sistema de penalización si un usuario cancela más de 3 veces en una semana.
- Puedes probar la API con herramientas como **Postman** o **cURL**.

---

### 🚀 Ahora estás listo para probar la API y realizar reservas de vehículos de manera eficiente. ¡Buena suerte! 🚗💨

