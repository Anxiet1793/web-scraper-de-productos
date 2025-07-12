# test_dashboard.py

import flet as ft
import sys
import os

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ui.rtx_dashboard import RTXDashboard

def main(page: ft.Page):
    """
    Aplicación de prueba para el dashboard RTX.
    """
    page.title = "🧪 Test RTX Dashboard"
    page.window_width = 1400
    page.window_height = 900
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO

    # Crear dashboard
    dashboard = RTXDashboard()
    dashboard.page = page  # Asignar referencia de la página
    
    # Agregar botones de prueba
    test_buttons = ft.Row([
        ft.ElevatedButton(
            "🧪 Test Estadísticas",
            on_click=dashboard.show_statistics,
            bgcolor=ft.colors.GREEN_600,
            color=ft.colors.WHITE
        ),
        ft.ElevatedButton(
            "🧪 Test Análisis Precios", 
            on_click=dashboard.show_price_analysis,
            bgcolor=ft.colors.ORANGE_600,
            color=ft.colors.WHITE
        ),
        ft.ElevatedButton(
            "🧪 Test Actualizar",
            on_click=dashboard.refresh_data,
            bgcolor=ft.colors.BLUE_600,
            color=ft.colors.WHITE
        ),
        ft.ElevatedButton(
            "🧪 Test Descargar CSV",
            on_click=dashboard.download_csv,
            bgcolor=ft.colors.PURPLE_600,
            color=ft.colors.WHITE
        )
    ], wrap=True)
    
    page.add(
        ft.Container(
            content=ft.Column([
                ft.Text("🧪 Dashboard de Prueba", size=24, weight=ft.FontWeight.BOLD),
                test_buttons,
                ft.Divider(),
                dashboard
            ]),
            padding=20
        )
    )
    
    page.update()

if __name__ == "__main__":
    print("🧪 Iniciando Dashboard de Prueba...")
    ft.app(target=main)
