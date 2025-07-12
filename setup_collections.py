# setup_collections.py

"""
Script para configurar las colecciones de MongoDB para el proyecto de gráficas RTX.
Ejecuta este script para verificar la conexión y crear las colecciones necesarias.
"""

from db.mongo_config import connect_to_mongodb, close_mongodb_connection
from datetime import datetime

def setup_rtx_collections():
    """Configura las colecciones necesarias para las gráficas RTX"""
    
    print("🔧 Configurando colecciones de MongoDB...")
    
    # Conectar a MongoDB
    db = connect_to_mongodb()
    if db is None:
        print("❌ No se pudo conectar a MongoDB")
        return False
    
    # Nombre de la colección principal
    collection_name = "rtx_graphics_cards_peru"
    
    try:
        # Verificar si la colección existe
        existing_collections = db.list_collection_names()
        
        if collection_name in existing_collections:
            print(f"✅ La colección '{collection_name}' ya existe")
            
            # Mostrar estadísticas
            collection = db[collection_name]
            doc_count = collection.count_documents({})
            print(f"📊 Documentos en la colección: {doc_count}")
            
            if doc_count > 0:
                # Mostrar algunos datos de ejemplo
                sample_doc = collection.find_one()
                print("📋 Estructura de documento de ejemplo:")
                for key, value in sample_doc.items():
                    if key != '_id':
                        print(f"   • {key}: {type(value).__name__}")
        
        else:
            print(f"⚠️ La colección '{collection_name}' no existe")
            print("🔨 Se creará automáticamente cuando insertes el primer documento")
            
            # Crear colección con documento de ejemplo (opcional)
            collection = db[collection_name]
            
            # Insertar documento de ejemplo para crear la colección
            example_doc = {
                "model_searched": "RTX 4070",
                "title": "Ejemplo - NVIDIA GeForce RTX 4070 Gaming",
                "price_text": "2,500",
                "price_numeric": 2500.0,
                "series": "RTX 40",
                "post_link": "https://mercadolibre.com.pe/ejemplo",
                "image_link": "https://example.com/image.jpg",
                "scraped_date": datetime.now().isoformat(),
                "country": "Peru",
                "source": "MercadoLibre",
                "_example": True  # Marca para identificar como ejemplo
            }
            
            result = collection.insert_one(example_doc)
            print(f"✅ Colección '{collection_name}' creada con documento de ejemplo")
            print(f"📄 ID del documento: {result.inserted_id}")
        
        # Crear índices para mejorar el rendimiento
        collection = db[collection_name]
        
        print("🔍 Creando índices...")
        
        # Índice en series (RTX 40, RTX 50)
        collection.create_index("series")
        print("   ✅ Índice en 'series' creado")
        
        # Índice en price_numeric para consultas de precio
        collection.create_index("price_numeric")
        print("   ✅ Índice en 'price_numeric' creado")
        
        # Índice en scraped_date para ordenar por fecha
        collection.create_index("scraped_date")
        print("   ✅ Índice en 'scraped_date' creado")
        
        # Índice en model_searched para búsquedas por modelo
        collection.create_index("model_searched")
        print("   ✅ Índice en 'model_searched' creado")
        
        # Índice compuesto para consultas complejas
        collection.create_index([("series", 1), ("price_numeric", -1)])
        print("   ✅ Índice compuesto 'series + price_numeric' creado")
        
        print("\n✅ Configuración de colecciones completada exitosamente!")
        
        # Mostrar información final
        print(f"\n📋 Información de la colección '{collection_name}':")
        print(f"   • Base de datos: {db.name}")
        print(f"   • Colección: {collection_name}")
        print(f"   • Documentos: {collection.count_documents({})}")
        print(f"   • Índices: {len(list(collection.list_indexes()))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error configurando colecciones: {e}")
        return False
    
    finally:
        close_mongodb_connection()

def clean_example_data():
    """Limpia los datos de ejemplo si existen"""
    print("🧹 Limpiando datos de ejemplo...")
    
    db = connect_to_mongodb()
    if db is None:
        print("❌ No se pudo conectar a MongoDB")
        return
    
    try:
        collection = db["rtx_graphics_cards_peru"]
        result = collection.delete_many({"_example": True})
        
        if result.deleted_count > 0:
            print(f"🗑️ {result.deleted_count} documentos de ejemplo eliminados")
        else:
            print("ℹ️ No se encontraron documentos de ejemplo para eliminar")
    
    except Exception as e:
        print(f"❌ Error limpiando datos de ejemplo: {e}")
    
    finally:
        close_mongodb_connection()

def show_collection_info():
    """Muestra información detallada de las colecciones"""
    print("📊 Información de colecciones...")
    
    db = connect_to_mongodb()
    if db is None:
        print("❌ No se pudo conectar a MongoDB")
        return
    
    try:
        collection_name = "rtx_graphics_cards_peru"
        collection = db[collection_name]
        
        print(f"\n📁 Colección: {collection_name}")
        print(f"📄 Total documentos: {collection.count_documents({})}")
        
        # Estadísticas por serie
        rtx40_count = collection.count_documents({"series": "RTX 40"})
        rtx50_count = collection.count_documents({"series": "RTX 50"})
        
        print(f"🔴 RTX Serie 40: {rtx40_count} productos")
        print(f"🟢 RTX Serie 50: {rtx50_count} productos")
        
        # Últimos productos agregados
        latest_products = list(collection.find({}).sort("scraped_date", -1).limit(5))
        
        if latest_products:
            print(f"\n🕐 Últimos 5 productos agregados:")
            for i, product in enumerate(latest_products, 1):
                model = product.get('model_searched', 'N/A')
                price = product.get('price_text', 'N/A')
                date = product.get('scraped_date', 'N/A')[:10] if product.get('scraped_date') else 'N/A'
                print(f"   {i}. {model} - {price} ({date})")
        
        # Índices
        indexes = list(collection.list_indexes())
        print(f"\n🔍 Índices ({len(indexes)}):")
        for idx in indexes:
            name = idx.get('name', 'unknown')
            key = idx.get('key', {})
            print(f"   • {name}: {dict(key)}")
    
    except Exception as e:
        print(f"❌ Error obteniendo información: {e}")
    
    finally:
        close_mongodb_connection()

if __name__ == "__main__":
    print("🎮 Configurador de Colecciones RTX")
    print("=" * 50)
    
    while True:
        print("\nOpciones:")
        print("1. 🔧 Configurar colecciones")
        print("2. 📊 Mostrar información")
        print("3. 🧹 Limpiar datos de ejemplo")
        print("4. 🚪 Salir")
        
        option = input("\nSelecciona una opción (1-4): ").strip()
        
        if option == "1":
            setup_rtx_collections()
        elif option == "2":
            show_collection_info()
        elif option == "3":
            clean_example_data()
        elif option == "4":
            print("👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción no válida")
