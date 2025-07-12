# main.py

import flet as ft
from db.mongo_config import connect_to_mongodb, close_mongodb_connection
from ui.rtx_dashboard import RTXDashboard

def main(page: ft.Page):
    """
    Función principal de la aplicación Flet.
    Configura la página y añade el Dashboard de Gráficas RTX.
    """
    page.title = "🎮 RTX Graphics Dashboard - Perú"
    page.vertical_alignment = ft.CrossAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_width = 1400
    page.window_height = 900
    page.window_min_width = 800
    page.window_min_height = 600
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO
    page.auto_scroll = True

    # Conectar a MongoDB al iniciar la aplicación
    print("Intentando conectar a MongoDB...")
    db_instance = connect_to_mongodb()
    if db_instance is None:
        page.add(ft.Text("❌ Error: No se pudo conectar a la base de datos. Verifique su MONGO_URI.", color=ft.colors.RED_500))
        page.update()
        return

    # Verificar que existe la colección de RTX
    collection_name = "rtx_graphics_cards_peru"
    collections = db_instance.list_collection_names()
    
    if collection_name not in collections:
        print(f"⚠️ La colección '{collection_name}' no existe. Se creará automáticamente cuando agregues datos.")
    else:
        doc_count = db_instance[collection_name].count_documents({})
        print(f"✅ Colección '{collection_name}' encontrada con {doc_count} documentos.")

    # Crear una instancia del Dashboard RTX
    rtx_dashboard = RTXDashboard()
    rtx_dashboard.page = page  # Asignar referencia de la página ANTES de cargar datos
    
    # Cargar datos después de asignar la página
    if hasattr(rtx_dashboard, 'auto_load_data'):
        rtx_dashboard.auto_load_data()
        rtx_dashboard.update_statistics()  # Actualizar estadísticas después de cargar

    # Añadir el Dashboard a la página
    page.add(
        ft.Container(
            content=rtx_dashboard,
            expand=True,
            alignment=ft.alignment.center,
            padding=20
        )
    )

    # Función para manejar el cierre de la aplicación
    def on_page_close(e):
        print("Cerrando aplicación Flet y conexión a MongoDB...")
        close_mongodb_connection()
        page.window_destroy()

    page.on_window_event = on_page_close
    page.update()

if __name__ == "__main__":
    print("🚀 Iniciando Dashboard de Gráficas RTX...")
    print("📋 Características:")
    print("• ✅ Datos en tiempo real desde MongoDB")
    print("• 🔍 Filtros por serie RTX (40/50)")
    print("• 📥 Descarga de datos en CSV")
    print("• 📊 Estadísticas y análisis de precios")
    print("• 🔗 Enlaces directos a MercadoLibre")
    print()
    
    # Ejecutar como aplicación de escritorio por defecto
    ft.app(target=main)
    
    # Para ejecutar como una aplicación web en el navegador, usa:
    # ft.app(target=main, view=ft.WEB_BROWSER)