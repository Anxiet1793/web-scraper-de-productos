import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import sys
from datetime import datetime

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.mongo_config import connect_to_mongodb, close_mongodb_connection

class Scraper():

    def __init__(self):
        # Fijamos Perú como único país
        self.base_url = 'https://listado.mercadolibre.com.pe/'
        print("Scraper configurado para Perú")
        
        # Conectar a MongoDB
        self.db = connect_to_mongodb()
        if self.db is None:
            print("❌ Error: No se pudo conectar a MongoDB")
            sys.exit(1)
        
        # Nombre de la colección para gráficas RTX
        self.collection_name = "rtx_graphics_cards_peru"
        self.collection = self.db[self.collection_name]
        print(f"📁 Usando colección: {self.collection_name}")
        
        # Lista de gráficas RTX serie 40 y 50 a scrapear
        self.rtx_models = [
            # Serie RTX 40
            "RTX 4090", "RTX 4080", "RTX 4070 Ti", "RTX 4070", "RTX 4060 Ti", "RTX 4060",
            "GeForce RTX 4090", "GeForce RTX 4080", "GeForce RTX 4070 Ti", 
            "GeForce RTX 4070", "GeForce RTX 4060 Ti", "GeForce RTX 4060",
            # Serie RTX 50 (cuando estén disponibles)
            "RTX 5090", "RTX 5080", "RTX 5070 Ti", "RTX 5070", "RTX 5060 Ti", "RTX 5060",
            "GeForce RTX 5090", "GeForce RTX 5080", "GeForce RTX 5070 Ti", 
            "GeForce RTX 5070", "GeForce RTX 5060 Ti", "GeForce RTX 5060"
        ]
        
        # Lista para almacenar todos los datos
        self.data = []

    def scrape_all_rtx_models(self):
        """Scrapea todas las gráficas RTX serie 40 y 50"""
        print("Iniciando scraping de todas las gráficas RTX serie 40 y 50...")
        
        for model in self.rtx_models:
            print(f"\n=== Scrapeando: {model} ===")
            self.scraping_single_model(model)
            
        print(f"\nScraping completado. Total de productos encontrados: {len(self.data)}")

    def scraping_single_model(self, product_name):
        """Scrapea un modelo específico de gráfica"""
        # Crear URL de búsqueda
        search_query = product_name.replace(" ", "%20")
        url = f"https://listado.mercadolibre.com.pe/{search_query}"
        
        print(f"🔍 Buscando: {product_name}")
        print(f"🌐 URL: {url}")
        
        # Contador para este modelo
        model_count = 0
        
        try:
            # Headers para simular un navegador real
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Obtener el HTML de la página
            response = requests.get(url, headers=headers)
            print(f"📡 Código de respuesta: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Error HTTP: {response.status_code}")
                return model_count
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar elementos de producto con diferentes selectores
            content = soup.select('li.ui-search-layout__item')
            
            if not content:
                # Intentar con otros selectores
                content = soup.select('.ui-search-result')
                
            if not content:
                print(f"❌ No se encontraron productos para {product_name}")
                return model_count
            
            print(f"📦 Productos encontrados: {len(content)}")
            
            # Procesar máximo 10 productos por modelo
            for i, post in enumerate(content[:10]):
                try:
                    # Buscar título
                    title_element = post.select_one('.poly-component__title a')
                    if not title_element:
                        title_element = post.select_one('h2 a')
                    if not title_element:
                        title_element = post.select_one('.ui-search-item__title')
                    if not title_element:
                        title_element = post.select_one('a[class*="title"]')
                    
                    if title_element:
                        title = title_element.get_text(strip=True)
                        print(f"   📝 Título: {title[:50]}...")
                    else:
                        print("   ❌ No se encontró título")
                        continue
                    
                    # Buscar precio
                    price_element = post.select_one('.andes-money-amount__fraction')
                    if not price_element:
                        price_element = post.select_one('.price-tag-fraction')
                    if not price_element:
                        price_element = post.select_one('[class*="price"][class*="fraction"]')
                    
                    if price_element:
                        price = price_element.get_text(strip=True)
                        print(f"   💰 Precio: {price}")
                    else:
                        print("   ❌ No se encontró precio")
                        continue
                    
                    # Buscar enlace
                    link_element = post.select_one('.poly-component__title a')
                    if not link_element:
                        link_element = post.select_one('h2 a')
                    if not link_element:
                        link_element = post.select_one('a')
                    
                    post_link = ""
                    if link_element and link_element.get("href"):
                        post_link = link_element["href"]
                        if not post_link.startswith('http'):
                            post_link = f"https://mercadolibre.com.pe{post_link}"
                        print(f"   🔗 Enlace encontrado")
                    
                    # Buscar imagen
                    img_element = post.select_one('.poly-component__picture')
                    if not img_element:
                        img_element = post.select_one('img')
                    
                    img_link = ""
                    if img_element:
                        img_link = img_element.get("data-src", "") or img_element.get("src", "")
                        print(f"   🖼️ Imagen encontrada")
                    
                    # Procesar precio
                    price_clean = price.replace(",", "").replace(".", "").replace("S/", "").strip()
                    try:
                        price_numeric = float(price_clean)
                    except:
                        price_numeric = 0
                    
                    # Determinar serie
                    if any(x in product_name for x in ["40", "4060", "4070", "4080", "4090"]):
                        series = "RTX 40"
                    elif any(x in product_name for x in ["50", "5060", "5070", "5080", "5090"]):
                        series = "RTX 50"
                    else:
                        series = "RTX"
                    
                    # Crear documento
                    post_data = {
                        "model_searched": product_name,
                        "title": title,
                        "price_text": price,
                        "price_numeric": price_numeric,
                        "series": series,
                        "post_link": post_link,
                        "image_link": img_link,
                        "scraped_date": datetime.now().isoformat(),
                        "country": "Peru",
                        "source": "MercadoLibre"
                    }
                    
                    self.data.append(post_data)
                    model_count += 1
                    
                    print(f"   ✅ Producto {model_count}: {title[:50]}... - {price}")
                    
                except Exception as e:
                    print(f"   ❌ Error procesando producto {i+1}: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ Error accediendo a la página: {e}")
        
        print(f"📊 Total encontrados para {product_name}: {model_count}")
        return model_count

    def scraping(self):
        """Método para scraping manual"""
        product_name = input("\nProducto: ")
        self.scraping_single_model(product_name)

    def save_to_mongodb(self):
        """Guarda los datos scrapeados en MongoDB"""
        if not self.data:
            print("No hay datos para guardar en MongoDB.")
            return
        
        try:
            result = self.collection.insert_many(self.data)
            print(f"✅ {len(result.inserted_ids)} productos guardados en MongoDB")
            print(f"📁 Colección: {self.collection_name}")
            
            # Limpiar datos locales después de guardar
            self.data = []
            
        except Exception as e:
            print(f"❌ Error guardando en MongoDB: {e}")

    def export_to_csv(self):
        """Exporta los datos a un archivo CSV (método de respaldo)"""
        if not self.data:
            print("No hay datos para exportar.")
            return
            
        os.makedirs("data", exist_ok=True)
        
        df = pd.DataFrame(self.data)
        filename = "data/rtx_40_50_series_peru.csv"
        df.to_csv(filename, sep=";", index=False)
        print(f"Datos exportados a: {filename}")
        print(f"Total de productos exportados: {len(self.data)}")
    
    def get_collection_stats(self):
        """Muestra estadísticas de la colección"""
        try:
            total_docs = self.collection.count_documents({})
            print(f"📊 Total de productos en la base de datos: {total_docs}")
            
            rtx40_count = self.collection.count_documents({"series": "RTX 40"})
            rtx50_count = self.collection.count_documents({"series": "RTX 50"})
            
            print(f"📊 Productos RTX Serie 40: {rtx40_count}")
            print(f"📊 Productos RTX Serie 50: {rtx50_count}")
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
    
    def clear_collection(self):
        """Limpia toda la colección"""
        try:
            result = self.collection.delete_many({})
            print(f"🗑️ {result.deleted_count} documentos eliminados de la colección")
        except Exception as e:
            print(f"❌ Error limpiando colección: {e}")

if __name__ == "__main__":
    s = Scraper()
    
    print("\n=== Scraper de Gráficas RTX Serie 40 y 50 - Perú ===")
    print("1. Scrapear todas las gráficas RTX serie 40 y 50 automáticamente")
    print("2. Scrapear un producto específico")
    print("3. Ver estadísticas de la base de datos")
    print("4. Limpiar toda la colección (⚠️ CUIDADO)")
    
    opcion = input("\nSelecciona una opción (1-4): ").strip()
    
    if opcion == "1":
        s.scrape_all_rtx_models()
        s.save_to_mongodb()
        s.get_collection_stats()
    elif opcion == "2":
        s.scraping()
        s.save_to_mongodb()
        s.get_collection_stats()
    elif opcion == "3":
        s.get_collection_stats()
    elif opcion == "4":
        confirm = input("⚠️ ¿Estás seguro de que quieres limpiar toda la colección? (si/no): ").lower()
        if confirm == "si":
            s.clear_collection()
        else:
            print("Operación cancelada.")
    else:
        print("Opción no válida. Scrapeando todas las gráficas RTX por defecto...")
        s.scrape_all_rtx_models()
        s.save_to_mongodb()
        s.get_collection_stats()
    
    close_mongodb_connection()
    print("👋 Scraper finalizado.")
