import json
from flask import Flask, json, Response, request, jsonify
from pymongo import MongoClient, DESCENDING
from pymongo.errors import ServerSelectionTimeoutError, OperationFailure
from bson import ObjectId
from datetime import datetime, timedelta
#from consultas import obtener_reservas_usuario, vehiculo_mas_reservado, usuarios_mas_cancelaciones

app = Flask(__name__)


class ConnectionMongoDB:
    def __init__(self, data):
        self.server = data['server']
        self.port = data['port']
        self.username = data['username']
        self.password = data['password']
        self.db = data['db']

    def getDB(self):
        mongoClient = MongoClient(
            "mongodb://" + str(self.username) + ":" + str(self.password) + "@" + str(self.server) + ":" + str(
                self.port) + "/?authMechanism=DEFAULT&authSource=" + str(self.db), serverSelectionTimeoutMS=500)

        try:
            if mongoClient.admin.command('ismaster')['ismaster']:
                return "Connected to the MongoDB Server!"
        except OperationFailure:
            return ("Database not found.")
        except ServerSelectionTimeoutError:
            return ("MongoDB Server is down.")


#credenciales de la base de datos
mongo_uri = "mongodb://root-crashell:password-crashell@cs_mongodb:27017/db_crashell"
client = MongoClient(mongo_uri)
db = client['db_crashell']
car_collection = db['vehiculos']
user_collection = db['usuarios']
booking_collection = db['reservas']



def obtener_reservas_usuario(usuario_id):
    """ Obtiene todas las reservas de un usuario específico. """
    reservas = list(booking_collection.find({"usuario_id": usuario_id}, {"_id": 0}))
    return reservas

def vehiculo_mas_reservado():
    """ Obtiene el vehículo más reservado en el último mes. """
    fecha_limite = datetime.utcnow() - timedelta(days=30)

    pipeline = [
        {"$match": {"fecha_inicio": {"$gte": fecha_limite}}},
        {"$group": {"_id": "$vehiculo_id", "total_reservas": {"$sum": 1}}},
        {"$sort": {"total_reservas": DESCENDING}},
        {"$limit": 1}
    ]

    resultado = list(booking_collection.aggregate(pipeline))
    return resultado[0] if resultado else {"message": "No hay reservas en el último mes"}

def usuarios_mas_cancelaciones():
    """ Obtiene los usuarios con más cancelaciones en el último mes. """
    fecha_limite = datetime.utcnow() - timedelta(days=30)

    pipeline = [
        {"$match": {"estado": "cancelada", "fecha_cancelacion": {"$gte": fecha_limite}}},
        {"$group": {"_id": "$usuario_id", "total_cancelaciones": {"$sum": 1}}},
        {"$sort": {"total_cancelaciones": DESCENDING}},
        {"$limit": 5}
    ]

    resultado = list(booking_collection.aggregate(pipeline))
    return resultado if resultado else {"message": "No hay cancelaciones en el último mes"}



# traer todos los vehiculos
@app.route('/vehiculos', methods=['GET'])
def get_vehiculos():
    vehiculos = list(car_collection.find())
    for vehiculo in vehiculos:
        vehiculo["_id"] = str(vehiculo["_id"])
    return Response(response=json.dumps(vehiculos), status=200, mimetype='application/json')

# traer todos los usuarios
@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    usuarios = list(db['usuarios'].find())
    for usuario in usuarios:
        usuario["_id"] = str(usuario["_id"])
    return Response(response=json.dumps(usuarios), status=200, mimetype='application/json')

#traer todas las reservas
@app.route('/reservas', methods=['GET'])
def get_reservas():
    reservas = list(db['reservas'].find())
    for reserva in reservas:
        reserva["_id"] = str(reserva["_id"])
    return Response(response=json.dumps(reservas), status=200, mimetype='application/json')

# crear usuario
'''
estructura del json
{ 
    usuario_id: "usuario_id_1", 
    nombre: "Juan Pérez", 
    email: "juan@example.com"
    }
'''
@app.route('/usuarios', methods=['POST'])
def create_usuario():
    # Obtener datos del usuario
    usuario_data = request.json
    usuario_id = usuario_data.get("usuario_id")
    nombre = usuario_data.get("nombre")
    email = usuario_data.get("email")

    # Crear usuario
    usuario = {
        "usuario_id": usuario_id,
        "nombre": nombre,
        "email": email,
        "historial_reservas": [],
        "penalizaciones": 0
    }
    user_collection.insert_one(usuario)
    usuario["_id"] = str(usuario["_id"])
    return jsonify({"message": "Usuario creado", "usuario": usuario})

# crear vehiculo
'''
estructura del json
{ 
    vehiculo_id: "vehiculo_id_1", 
    marca: "Toyota", 
    modelo: "Corolla",
    placa: "ABC123"
    }
'''
@app.route('/vehiculos', methods=['POST'])
def create_vehiculo():
    # Obtener datos del vehiculo
    vehiculo_data = request.json
    vehiculo_id = vehiculo_data.get("vehiculo_id")
    marca = vehiculo_data.get("marca")
    modelo = vehiculo_data.get("modelo")
    placa = vehiculo_data.get("placa")

    # Crear vehiculo
    vehiculo = {
        "vehiculo_id": vehiculo_id,
        "marca": marca,
        "modelo": modelo,
        "placa": placa
    }
    car_collection.insert_one(vehiculo)
    vehiculo["_id"] = str(vehiculo["_id"])
    return jsonify({"message": "Vehiculo creado", "vehiculo": vehiculo})


# crear una reserva
@app.route('/reservas', methods=['POST'])
def crear_reserva():
    try:
        data = request.json
        usuario_id = data.get("usuario_id")
        vehiculo_id = data.get("vehiculo_id")
        fecha_inicio = datetime.strptime(data.get("fecha_inicio"), "%Y-%m-%d")
        fecha_fin = datetime.strptime(data.get("fecha_fin"), "%Y-%m-%d")

        # Verificar si el usuario está penalizado
        usuario = users_collection.find_one({"_id": usuario_id})
        if usuario and "penalizacion_hasta" in usuario:
            if usuario["penalizacion_hasta"] > datetime.utcnow():
                return jsonify({"error": "Usuario penalizado, no puede hacer reservas hasta {}".format(usuario["penalizacion_hasta"])}), 403

        # Verificar si el vehículo está disponible en el rango de fechas
        conflicto = booking_collection.find_one({
            "vehiculo_id": vehiculo_id,
            "estado": "activa",
            "$or": [
                {"fecha_inicio": {"$lt": fecha_fin}, "fecha_fin": {"$gt": fecha_inicio}}
            ]
        })

        if conflicto:
            return jsonify({"error": "El vehículo ya está reservado en estas fechas"}), 400

        # Crear la reserva
        reserva = {
            "usuario_id": usuario_id,
            "vehiculo_id": vehiculo_id,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "estado": "activa"
        }
        booking_collection.insert_one(reserva)

        return jsonify({"message": "Reserva creada exitosamente"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/reservas/cancelar', methods=['POST'])
def cancelar_reserva():
    try:
        data = request.json
        reserva_id = data.get("reserva_id")
        motivo = data.get("motivo", "No especificado")

        # Buscar la reserva
        reserva = booking_collection.find_one({"_id": ObjectId(reserva_id)})

        if not reserva:
            return jsonify({"error": "Reserva no encontrada"}), 404

        if reserva.get("estado") == "cancelada":
            return jsonify({"message": "La reserva ya está cancelada"}), 400

        usuario_id = reserva["usuario_id"]

        # Obtener la fecha actual y calcular la fecha límite (últimos 7 días)
        fecha_actual = datetime.utcnow()
        fecha_limite = fecha_actual - timedelta(days=7)

        # Contar cancelaciones en los últimos 7 días
        cancelaciones_recientes = booking_collection.count_documents({
            "usuario_id": usuario_id,
            "estado": "cancelada",
            "fecha_cancelacion": {"$gte": fecha_limite}
        })

        # Aplicar penalización si ha cancelado más de 3 veces
        if cancelaciones_recientes >= 3:
            penalizacion_hasta = fecha_actual + timedelta(days=7)
            users_collection.update_one({"_id": usuario_id}, {"$set": {"penalizacion_hasta": penalizacion_hasta}})
            return jsonify({"message": "Reserva cancelada, pero el usuario ha sido penalizado por 7 días."}), 200

        # Cancelar la reserva y actualizar el estado
        booking_collection.update_one(
            {"_id": ObjectId(reserva_id)},
            {"$set": {"estado": "cancelada", "motivo_cancelacion": motivo, "fecha_cancelacion": fecha_actual}}
        )

        return jsonify({"message": "Reserva cancelada exitosamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/api')
def get_api():
    data = {
        "server": "cs_mongodb",
        "port": '27017',
        "username": "root-crashell",
        "password": "password-crashell",
        "db": "db_crashell"
    }

    response = ConnectionMongoDB(data).getDB()
    return Response(response=json.dumps(response), status=200, mimetype='application/json')


@app.route('/', methods=('GET', 'POST'))
def hello():
    return '<h1 style="background-color: #262626; color: white; padding: 20px; text-align:center;">Hello, Crashell!</h1>'


@app.route('/reservas/usuario/<usuario_id>', methods=['GET'])
def get_reservas_usuario(usuario_id):
    reservas = obtener_reservas_usuario(usuario_id)
    return jsonify(reservas), 200

@app.route('/reservas/vehiculo-mas-reservado', methods=['GET'])
def get_vehiculo_mas_reservado():
    vehiculo = vehiculo_mas_reservado()
    return jsonify(vehiculo), 200

@app.route('/reservas/usuarios-mas-cancelaciones', methods=['GET'])
def get_usuarios_mas_cancelaciones():
    usuarios = usuarios_mas_cancelaciones()
    return jsonify(usuarios), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)