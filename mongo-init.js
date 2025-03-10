db.createUser(
    {
        user: 'root-crashell',
        pwd: 'password-crashell',
        roles: [
            { role: "clusterMonitor", db: "admin" },
            { role: "dbOwner", db: "db_name" },
            { role: 'readWrite', db: 'db_crashell' }
        ]
    }
)

// Usar la base de datos que queremos
db = db.getSiblingDB("db_crashell");

// Crear colecciones con datos de prueba
db.usuarios.insertMany([
    { usuario_id: "usuario_id_1", nombre: "Juan Pérez", email: "juan@example.com", historial_reservas: [], penalizaciones: 0 },
    { usuario_id: "usuario_id_2", nombre: "María López", email: "maria@example.com", historial_reservas: [], penalizaciones: 0 }
]);

db.vehiculos.insertMany([
    { vehiculo_id: "vehiculo_id_1", tipo: "SUV", disponibilidad: true },
    { vehiculo_id: "vehiculo_id_2", tipo: "Sedán", disponibilidad: true }
]);

db.reservas.insertMany([]);