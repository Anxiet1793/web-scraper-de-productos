# 🎮 Web Scraper de Gráficas RTX - Perú

Sistema completo de web scraping para gráficas RTX serie 40 y 50 en MercadoLibre Perú, con dashboard interactivo para visualización de datos.

## 📋 Estructura del Proyecto

```
web scraper de productos/
├── main.py                     # 🚀 Aplicación principal (Dashboard)
├── setup_collections.py        # 🔧 Configurador de MongoDB
├── scrapper/
│   └── ideascraperMercadoLibre.py  # 🕷️ Web scraper
├── db/
│   └── mongo_config.py         # 🗄️ Configuración MongoDB
├── ui/
│   └── rtx_dashboard.py        # 📊 Dashboard interactivo
└── utils/
    └── dataframe_tools.py      # 🛠️ Herramientas DataFrame
```

## 🗄️ Colecciones de MongoDB

### Colección Principal: `rtx_graphics_cards_peru`

**Estructura de documentos:**
```json
{
  "_id": ObjectId("..."),
  "model_searched": "RTX 4070",
  "title": "NVIDIA GeForce RTX 4070 Gaming X Trio 12GB",
  "price_text": "2,499",
  "price_numeric": 2499.0,
  "series": "RTX 40",
  "post_link": "https://mercadolibre.com.pe/...",
  "image_link": "https://http2.mlstatic.com/...",
  "scraped_date": "2025-07-11T10:30:00",
  "country": "Peru",
  "source": "MercadoLibre"
}
```

**Índices creados:**
- `series` - Para filtrar por RTX 40/50
- `price_numeric` - Para consultas de precio
- `scraped_date` - Para ordenar por fecha
- `model_searched` - Para búsquedas por modelo
- `series + price_numeric` - Índice compuesto

## 🚀 Instalación y Configuración

### 1. Dependencias requeridas:
```bash
pip install requests beautifulsoup4 pandas pymongo flet
```

### 2. Configurar MongoDB:
1. Edita `db/mongo_config.py` con tu URI de MongoDB
2. Ejecuta el configurador:
```bash
python setup_collections.py
```

## 📖 Instrucciones de Uso

### 1. 🔧 Configurar Base de Datos
```bash
python setup_collections.py
```
- Selecciona opción 1 para configurar colecciones
- Crea índices automáticamente
- Verifica la conexión

### 2. 🕷️ Ejecutar Web Scraper
```bash
python scrapper/ideascraperMercadoLibre.py
```

**Opciones disponibles:**
- **Opción 1**: Scrapear todas las gráficas RTX serie 40 y 50 automáticamente
- **Opción 2**: Scrapear un producto específico
- **Opción 3**: Ver estadísticas de la base de datos
- **Opción 4**: Limpiar toda la colección

**Modelos incluidos:**
- **RTX Serie 40**: 4060, 4060 Ti, 4070, 4070 Ti, 4080, 4090
- **RTX Serie 50**: 5060, 5060 Ti, 5070, 5070 Ti, 5080, 5090
- Variantes con y sin "GeForce"

### 3. 📊 Visualizar Dashboard
```bash
python main.py
```

**Características del Dashboard:**
- 📦 Estadísticas generales (total productos, por serie, precios)
- 📋 Tabla interactiva con todos los datos
- 💰 Análisis detallado de precios
- 🔄 Actualización en tiempo real
- 🔗 Enlaces directos a MercadoLibre

## 🎯 Funcionalidades

### Web Scraper (`ideascraperMercadoLibre.py`)
- ✅ Scraping automático de múltiples modelos RTX
- ✅ Manejo de errores robusto
- ✅ Limitación de páginas por modelo (rendimiento)
- ✅ Limpieza y procesamiento de precios
- ✅ Guardado directo en MongoDB
- ✅ Detección automática de series (40/50)

### Dashboard (`rtx_dashboard.py`)
- ✅ Interfaz moderna con Flet
- ✅ Tarjetas de estadísticas en tiempo real
- ✅ Tabla paginada con datos
- ✅ Análisis de precios por rangos
- ✅ Enlaces directos a productos
- ✅ Actualización automática desde MongoDB

### Herramientas de Datos (`dataframe_tools.py`)
- ✅ Conversión MongoDB ↔ DataFrame
- ✅ Limpieza automática de datos
- ✅ Formateo de tipos de datos
- ✅ Manejo de valores nulos

## 📊 Análisis Disponibles

### Estadísticas Básicas
- Total de productos encontrados
- Distribución por series (RTX 40 vs RTX 50)
- Precios promedio, mínimo y máximo
- Top modelos más encontrados

### Análisis de Precios
- Distribución por rangos de precio
- Estadísticas por serie
- Productos más caros/baratos
- Tendencias temporales

## 🔍 Búsquedas y Filtros

El sistema permite:
- Filtrar por serie (RTX 40/50)
- Buscar por modelo específico
- Ordenar por precio, fecha, relevancia
- Filtrar por rangos de precio

## 🛠️ Mantenimiento

### Limpiar datos duplicados:
```bash
python setup_collections.py
# Opción 3: Limpiar datos de ejemplo
```

### Ver estadísticas:
```bash
python setup_collections.py
# Opción 2: Mostrar información
```

### Backup de datos:
Los datos se almacenan en MongoDB Atlas con respaldo automático.

## ⚡ Rendimiento

- **Scraper**: ~10 páginas por modelo, ~500 productos máximo por modelo
- **Dashboard**: Carga hasta 1000 productos, tabla limitada a 50 para rendimiento
- **Base de datos**: Índices optimizados para consultas rápidas

## 🔒 Consideraciones

- **Rate limiting**: El scraper incluye manejo de errores para evitar bloqueos
- **Datos duplicados**: Posibles duplicados si se ejecuta múltiples veces
- **Actualización**: Los precios cambian constantemente en MercadoLibre

## 🐛 Solución de Problemas

### Error de conexión MongoDB:
1. Verifica la URI en `db/mongo_config.py`
2. Confirma acceso a internet
3. Ejecuta `python setup_collections.py` opción 2

### Dashboard no muestra datos:
1. Ejecuta el scraper primero
2. Verifica conexión a MongoDB
3. Usa "🔄 Actualizar Datos" en el dashboard

### Scraper no encuentra productos:
1. Verifica conexión a internet
2. MercadoLibre puede haber cambiado su estructura
3. Revisa los logs de error

## 📝 Notas

- Los datos se actualizan cada vez que ejecutas el scraper
- El dashboard se conecta en tiempo real a MongoDB
- Los precios están en soles peruanos (S/)
- Las fechas se almacenan en formato ISO

## 🤝 Contribuciones

Para mejorar el sistema:
1. Agregar más sitios de scraping
2. Implementar notificaciones de precios
3. Añadir gráficos y visualizaciones
4. Crear sistema de alertas
