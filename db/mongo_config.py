# db/mongo_config.py

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# URI directa (reemplaza con tu propia URI si es distinta)
MONGO_URI = "mongodb+srv://gamys1793:GAMYS1793samuel@healthmobile.btbsqlw.mongodb.net/?retryWrites=true&w=majority&appName=HealthMobile"
DB_NAME = "MercadoLibre"  # Nombre de la base de datos

client = None
db = None

def connect_to_mongodb():
    """
    Establece la conexión con MongoDB Atlas.
    Retorna el objeto de la base de datos si la conexión es exitosa, None en caso contrario.
    """
    global client, db
    if client is not None and db is not None:
        print("Ya conectado a MongoDB.")
        return db

    try:
        client = MongoClient(MONGO_URI)
        # Comando ping para verificar la conexión
        client.admin.command('ping')
        db = client[DB_NAME]
        print(f"✅ Conexión exitosa a MongoDB Atlas. Base de datos: {DB_NAME}")
        return db
    except ConnectionFailure as e:
        print(f"❌ Error de conexión a MongoDB Atlas: {e}")
        return None
    except Exception as e:
        print(f"⚠️ Ocurrió un error inesperado al conectar a MongoDB: {e}")
        return None

def close_mongodb_connection():
    """Cierra la conexión con MongoDB."""
    global client, db
    if client is not None:
        client.close()
        print("🔒 Conexión a MongoDB cerrada.")
        client = None
        db = None

# Prueba directa si se ejecuta este archivo
if __name__ == "__main__":
    database = connect_to_mongodb()
    if database is not None:
        print(f"📂 Colecciones disponibles: {database.list_collection_names()}")
    close_mongodb_connection()
