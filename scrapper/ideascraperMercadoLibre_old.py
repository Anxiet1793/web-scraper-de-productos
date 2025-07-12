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
        # Limpiar el nombre del producto
        cleaned_name = product_name.replace(" ", "-").lower()
        
        # Crear las URLs para scrapear con diferentes formatos
        base_search_url = f"{self.base_url}{cleaned_name}"
        urls = [base_search_url]
        
        # También probar con formato de búsqueda directo
        search_query = product_name.replace(" ", "%20")
        direct_search_url = f"https://listado.mercadolibre.com.pe/{search_query}"
        urls.append(direct_search_url)
        
        print(f"🔍 URLs a probar:")
        for url in urls:
            print(f"   • {url}")
        
        # Contador para este modelo
        model_count = 0
        
        # Iterar sobre cada URL
        for i, url in enumerate(urls, start=1):
            try:
                print(f"\n🌐 Probando URL {i}: {url}")
                
                # Headers para simular un navegador real
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                # Obtener el HTML de la página
                response = requests.get(url, headers=headers)
                print(f"📡 Código de respuesta: {response.status_code}")
                
                if response.status_code != 200:
                    print(f"❌ Error HTTP: {response.status_code}")
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Buscar diferentes clases de elementos de producto
                selectors = [
                    'li.ui-search-layout__item',
                    '.ui-search-result',
                    '.ui-search-results__item',
                    'div.ui-search-result__wrapper'
                ]
                
                content = []
                for selector in selectors:
                    found_content = soup.select(selector)
                    if found_content:
                        content = found_content
                        print(f"✅ Encontrado contenido con selector: {selector}")
                        break
                
                if not content:
                    print("🔍 Buscando cualquier elemento que contenga 'RTX'...")
                    # Buscar elementos que contengan RTX en el texto
                    all_elements = soup.find_all(text=lambda text: text and 'RTX' in text.upper())
                    print(f"📋 Elementos que contienen 'RTX': {len(all_elements)}")
                    
                    if len(all_elements) > 0:
                        print("🎯 Algunos textos encontrados:")
                        for j, element in enumerate(all_elements[:5]):
                            print(f"   {j+1}. {element.strip()[:100]}...")
                    
                    print(f"❌ No se encontraron productos en {url}")
                    continue
                
                print(f"📦 Productos encontrados en esta página: {len(content)}")
                
                # Iteración para scrapear posts
                for j, post in enumerate(content[:5]):  # Limitamos a 5 para debugging
                    try:
                        print(f"\n🔎 Procesando producto {j+1}...")
                        
                        # Buscar título de diferentes maneras
                        title = ""
                        title_selectors = ['h2', 'h3', '.ui-search-item__title']
                        for selector in title_selectors:
                            title_element = post.select_one(selector)
                            if title_element:
                                title = title_element.get_text(strip=True)
                                print(f"   📝 Título encontrado: {title[:50]}...")
                                break
                        
                        if not title:
                            print("   ❌ No se encontró título")
                            continue
                        
                        # Buscar precio de diferentes maneras
                        price = ""
                        price_selectors = [
                            '.andes-money-amount__fraction',
                            '.price-tag-fraction',
                            '.ui-search-price__part',
                            '[class*="price"]'
                        ]
                        
                        for selector in price_selectors:
                            price_element = post.select_one(selector)
                            if price_element:
                                price = price_element.get_text(strip=True)
                                print(f"   💰 Precio encontrado: {price}")
                                break
                        
                        if not price:
                            print("   ❌ No se encontró precio")
                            continue
                        
                        # Buscar enlace
                        link_element = post.find("a")
                        post_link = ""
                        if link_element and link_element.get("href"):
                            post_link = link_element["href"]
                            if not post_link.startswith('http'):
                                post_link = f"https://mercadolibre.com.pe{post_link}"
                            print(f"   🔗 Enlace: {post_link[:50]}...")
                        
                        # Buscar imagen
                        img_element = post.find("img")
                        img_link = ""
                        if img_element:
                            img_link = img_element.get("data-src", "") or img_element.get("src", "")
                            print(f"   🖼️ Imagen: {img_link[:50]}..." if img_link else "   ❌ Sin imagen")
                        
                        # Limpiar y procesar precio
                        price_clean = price.replace(",", "").replace(".", "").replace("S/", "").strip()
                        try:
                            price_numeric = float(price_clean)
                        except:
                            price_numeric = 0
                        
                        # Determinar serie de la gráfica
                        if "40" in product_name or "4060" in product_name or "4070" in product_name or "4080" in product_name or "4090" in product_name:
                            series = "RTX 40"
                        elif "50" in product_name or "5060" in product_name or "5070" in product_name or "5080" in product_name or "5090" in product_name:
                            series = "RTX 50"
                        else:
                            series = "RTX"
                        
                        # Guardar en un diccionario con más detalles
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
                        
                        # Guardar los diccionarios en la lista
                        self.data.append(post_data)
                        model_count += 1
                        
                        print(f"   ✅ Producto {model_count} guardado!")
                        
                    except Exception as e:
                        print(f"   ❌ Error procesando producto {j+1}: {e}")
                        continue
                        
            except Exception as e:
                print(f"❌ Error accediendo a la página {url}: {e}")
                continue
        
        print(f"\n📊 Productos encontrados para {product_name}: {model_count}")
        return model_count
                            continue
                        price = price_element.text.strip()
                        
                        # Obtener la URL del post
                        link_element = post.find("a")
                        if not link_element or not link_element.get("href"):
                            continue
                        post_link = link_element["href"]
                        
                        # Obtener la URL de la imagen
                        img_element = post.find("img")
                        img_link = ""
                        if img_element:
                            img_link = img_element.get("data-src", "") or img_element.get("src", "")
                        
                        # Limpiar y procesar precio
                        price_clean = price.replace(",", "").replace(".", "")
                        try:
                            price_numeric = float(price_clean)
                        except:
                            price_numeric = 0
                        
                        # Determinar serie de la gráfica
                        if "40" in product_name or "4060" in product_name or "4070" in product_name or "4080" in product_name or "4090" in product_name:
                            series = "RTX 40"
                        elif "50" in product_name or "5060" in product_name or "5070" in product_name or "5080" in product_name or "5090" in product_name:
                            series = "RTX 50"
                        else:
                            series = "RTX"
                        
                        # Guardar en un diccionario con más detalles
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
                        
                        # Guardar los diccionarios en la lista
                        self.data.append(post_data)
                        model_count += 1
                        
                    except Exception as e:
                        print(f"Error procesando un post: {e}")
                        continue
                        
            except Exception as e:
                print(f"Error accediendo a la página {url}: {e}")
                continue
        
        print(f"Productos encontrados para {product_name}: {model_count}")

    def scraping(self):
        # Mantener método original para compatibilidad
        product_name = input("\nProducto: ")
        self.scraping_single_model(product_name)

    def save_to_mongodb(self):
        """Guarda los datos scrapeados en MongoDB"""
        if not self.data:
            print("No hay datos para guardar en MongoDB.")
            return
        
        try:
            # Insertar todos los documentos
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
            
        # Crear directorio si no existe
        os.makedirs("data", exist_ok=True)
        
        # Exportar a archivo CSV
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
            
            # Estadísticas por serie
            rtx40_count = self.collection.count_documents({"series": "RTX 40"})
            rtx50_count = self.collection.count_documents({"series": "RTX 50"})
            
            print(f"📊 Productos RTX Serie 40: {rtx40_count}")
            print(f"📊 Productos RTX Serie 50: {rtx50_count}")
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
    
    def clear_collection(self):
        """Limpia toda la colección (usar con precaución)"""
        try:
            result = self.collection.delete_many({})
            print(f"🗑️ {result.deleted_count} documentos eliminados de la colección")
        except Exception as e:
            print(f"❌ Error limpiando colección: {e}")

if __name__ == "__main__":
    s = Scraper()
    
    # Opciones de uso
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
    
    # Cerrar conexión
    close_mongodb_connection()
    print("👋 Scraper finalizado.")