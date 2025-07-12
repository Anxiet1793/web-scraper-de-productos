# ui/rtx_dashboard.py

import flet as ft
import pandas as pd
from datetime import datetime
import sys
import os

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.mongo_config import connect_to_mongodb
from utils.dataframe_tools import mongo_to_dataframe, clean_and_format_dataframe

class RTXDashboard(ft.Container):
    def __init__(self):
        super().__init__()
        self.db = None
        self.collection = None
        self.df = pd.DataFrame()
        self.filtered_df = pd.DataFrame()
        self.current_filter = "Todas"  # Filtro actual
        
        # Configuración del container principal
        self.expand = True
        self.padding = 20
        
        # Inicializar conexión a MongoDB
        self.init_database()
        
        # Crear la interfaz
        self.content = self.build_interface()
        
        # No cargar datos automáticamente aquí - se hará desde main.py
        
    def init_database(self):
        """Inicializa la conexión a MongoDB"""
        try:
            self.db = connect_to_mongodb()
            if self.db is not None:
                self.collection = self.db["rtx_graphics_cards_peru"]
                print("✅ Conectado a la colección de gráficas RTX")
            else:
                print("❌ Error conectando a MongoDB")
        except Exception as e:
            print(f"❌ Error en init_database: {e}")
    
    def build_interface(self):
        """Construye la interfaz principal del dashboard"""
        return ft.Column(
            [
                # Título principal
                ft.Container(
                    content=ft.Text(
                        "🎮 Dashboard de Gráficas RTX - Perú",
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.BLUE_700
                    ),
                    alignment=ft.alignment.center,
                    padding=ft.padding.only(bottom=20)
                ),
                
                # Botones de control
                ft.Container(
                    content=ft.Row(
                        [
                            ft.ElevatedButton(
                                text="🔄 Actualizar Datos",
                                icon=ft.icons.REFRESH,
                                on_click=self.refresh_data,
                                bgcolor="#1976d2",
                                color="#ffffff"
                            ),
                            ft.Dropdown(
                                label="🔍 Filtrar por Serie",
                                width=200,
                                options=[
                                    ft.dropdown.Option("Todas"),
                                    ft.dropdown.Option("RTX 40"),
                                    ft.dropdown.Option("RTX 50"),
                                ],
                                value="Todas",
                                on_change=self.filter_by_series
                            ),
                            ft.ElevatedButton(
                                text="📊 Estadísticas",
                                icon=ft.icons.ANALYTICS,
                                on_click=self.show_statistics,
                                bgcolor="#388e3c",
                                color="#ffffff"
                            ),
                            ft.ElevatedButton(
                                text="💰 Análisis de Precios",
                                icon=ft.icons.ATTACH_MONEY,
                                on_click=self.show_price_analysis,
                                bgcolor="#f57c00",
                                color="#ffffff"
                            ),
                            ft.ElevatedButton(
                                text="📥 Descargar CSV",
                                icon=ft.icons.DOWNLOAD,
                                on_click=self.download_csv,
                                bgcolor="#7b1fa2",
                                color="#ffffff"
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
                        wrap=True
                    ),
                    padding=ft.padding.only(bottom=20)
                ),
                
                # Área de contenido principal
                ft.Container(
                    content=ft.Column(
                        [
                            self.create_stats_cards(),
                            self.create_data_table()
                        ],
                        spacing=20
                    ),
                    expand=True
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=10
        )
    
    def create_stats_cards(self):
        """Crea las tarjetas de estadísticas"""
        return ft.Container(
            content=ft.Row(
                [
                    self.create_stat_card("📦 Total Productos", "0", ft.colors.BLUE_100),
                    self.create_stat_card("🔴 RTX Serie 40", "0", ft.colors.RED_100),
                    self.create_stat_card("🟢 RTX Serie 50", "0", ft.colors.GREEN_100),
                    self.create_stat_card("💰 Precio Promedio", "S/ 0", ft.colors.ORANGE_100),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                wrap=True
            ),
            padding=ft.padding.only(bottom=20)
        )
    
    def create_stat_card(self, title, value, bg_color):
        """Crea una tarjeta de estadística individual"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(title, size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(value, size=24, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_700)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5
            ),
            width=200,
            height=100,
            bgcolor=bg_color,
            border_radius=10,
            padding=15,
            alignment=ft.alignment.center
        )
    
    def create_data_table(self):
        """Crea la tabla de datos"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("📋 Datos de Gráficas RTX", size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(
                        content=ft.DataTable(
                            columns=[
                                ft.DataColumn(ft.Text("Modelo", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Título", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Precio", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Serie", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Fecha", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
                            ],
                            rows=[],
                            border=ft.border.all(1, ft.colors.GREY_300),
                            border_radius=10,
                            vertical_lines=ft.border.BorderSide(1, ft.colors.GREY_200),
                            horizontal_lines=ft.border.BorderSide(1, ft.colors.GREY_200),
                        ),
                        height=400,
                        padding=10,
                        border=ft.border.all(1, ft.colors.GREY_300),
                        border_radius=10
                    )
                ],
                spacing=10
            )
        )
    
    def refresh_data(self, e):
        """Actualiza los datos desde MongoDB"""
        try:
            if self.collection is None:
                self.show_message("❌ Error: No hay conexión a la base de datos", "#f44336")
                return
            
            # Obtener datos de MongoDB
            cursor = self.collection.find({}).sort("scraped_date", -1).limit(1000)
            documents = list(cursor)
            
            if not documents:
                self.show_message("ℹ️ No hay datos en la base de datos. Ejecuta el scraper primero.", "#2196f3")
                return
            
            # Convertir a DataFrame
            self.df = mongo_to_dataframe(documents)
            
            # Aplicar filtro actual
            self.apply_current_filter()
            
            # Actualizar estadísticas
            self.update_statistics()
            
            # Actualizar tabla
            self.update_data_table()
            
            self.show_message(f"✅ Datos actualizados: {len(self.df)} productos cargados", "#4caf50")
            
        except Exception as e:
            self.show_message(f"❌ Error actualizando datos: {str(e)}", "#f44336")
    
    def auto_load_data(self):
        """Carga datos automáticamente al iniciar"""
        try:
            if self.collection is not None:
                print("🔄 Cargando datos automáticamente...")
                cursor = self.collection.find({}).sort("scraped_date", -1).limit(1000)
                documents = list(cursor)
                
                if documents:
                    self.df = mongo_to_dataframe(documents)
                    self.apply_current_filter()
                    print(f"✅ {len(self.df)} productos cargados automáticamente")
                else:
                    print("ℹ️ No hay datos en la base de datos")
        except Exception as e:
            print(f"❌ Error cargando datos automáticamente: {e}")
    
    def update_statistics(self):
        """Actualiza las tarjetas de estadísticas"""
        data_to_use = self.filtered_df if not self.filtered_df.empty else self.df
        
        if data_to_use.empty:
            return
        
        try:
            total_products = len(data_to_use)
            rtx40_count = len(data_to_use[data_to_use['series'] == 'RTX 40']) if 'series' in data_to_use.columns else 0
            rtx50_count = len(data_to_use[data_to_use['series'] == 'RTX 50']) if 'series' in data_to_use.columns else 0
            
            # Calcular precio promedio
            avg_price = 0
            if 'price_numeric' in data_to_use.columns:
                valid_prices = data_to_use[data_to_use['price_numeric'] > 0]['price_numeric']
                if len(valid_prices) > 0:
                    avg_price = valid_prices.mean()
            
            # Buscar las tarjetas y actualizar sus valores
            try:
                stats_container = self.content.controls[2].content.controls[0].content
                if hasattr(stats_container, 'controls'):
                    cards = stats_container.controls
                    if len(cards) >= 4:
                        cards[0].content.controls[1].value = str(total_products)
                        cards[1].content.controls[1].value = str(rtx40_count)
                        cards[2].content.controls[1].value = str(rtx50_count)
                        cards[3].content.controls[1].value = f"S/ {avg_price:,.0f}"
                
                self.update()
            except Exception as e:
                print(f"Error actualizando tarjetas de estadísticas: {e}")
            
        except Exception as e:
            print(f"Error calculando estadísticas: {e}")
    
    def update_data_table(self):
        """Actualiza la tabla de datos"""
        data_to_use = self.filtered_df if not self.filtered_df.empty else self.df
        
        if data_to_use.empty:
            return
        
        try:
            # Obtener la tabla
            table_container = self.content.controls[2].content.controls[1].content.controls[1].content
            data_table = table_container
            
            # Limpiar filas existentes
            data_table.rows.clear()
            
            # Agregar nuevas filas (limitamos a 50 para rendimiento)
            for idx, row in data_to_use.head(50).iterrows():
                # Formatear fecha
                scraped_date = row.get('scraped_date', '')
                if scraped_date:
                    try:
                        date_obj = datetime.fromisoformat(scraped_date.replace('Z', '+00:00'))
                        formatted_date = date_obj.strftime('%d/%m/%Y')
                    except:
                        formatted_date = scraped_date[:10]
                else:
                    formatted_date = 'N/A'
                
                # Crear fila
                data_table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(row.get('model_searched', 'N/A'))[:20])),
                            ft.DataCell(ft.Text(str(row.get('title', 'N/A'))[:30] + "...")),
                            ft.DataCell(ft.Text(str(row.get('price_text', 'N/A')))),
                            ft.DataCell(ft.Text(str(row.get('series', 'N/A')))),
                            ft.DataCell(ft.Text(formatted_date)),
                            ft.DataCell(
                                ft.IconButton(
                                    icon=ft.icons.OPEN_IN_NEW,
                                    tooltip="Ver en MercadoLibre",
                                    on_click=lambda e, url=row.get('post_link', ''): self.open_link(url)
                                )
                            )
                        ]
                    )
                )
            
            self.update()
            
        except Exception as e:
            print(f"Error actualizando tabla: {e}")
    
    def show_statistics(self, e):
        """Muestra estadísticas detalladas"""
        data_to_use = self.filtered_df if not self.filtered_df.empty else self.df
        
        if data_to_use.empty:
            self.show_message("ℹ️ No hay datos cargados. Actualiza primero.", ft.colors.BLUE)
            return
        
        try:
            # Estadísticas por modelo
            model_stats = data_to_use['model_searched'].value_counts().head(10)
            
            # Estadísticas de precios por serie
            price_stats = ""
            if 'price_numeric' in data_to_use.columns and 'series' in data_to_use.columns:
                for series in ['RTX 40', 'RTX 50']:
                    series_data = data_to_use[data_to_use['series'] == series]
                    if not series_data.empty:
                        valid_prices = series_data[series_data['price_numeric'] > 0]['price_numeric']
                        if len(valid_prices) > 0:
                            price_stats += f"\n{series}:\n"
                            price_stats += f"  • Precio mínimo: S/ {valid_prices.min():,.0f}\n"
                            price_stats += f"  • Precio máximo: S/ {valid_prices.max():,.0f}\n"
                            price_stats += f"  • Precio promedio: S/ {valid_prices.mean():,.0f}\n"
            
            filter_info = f" (Filtro: {self.current_filter})" if self.current_filter != "Todas" else ""
            stats_text = f"📊 Estadísticas{filter_info}\n\nTop 10 Modelos más encontrados:\n\n"
            for model, count in model_stats.items():
                stats_text += f"• {model}: {count} productos\n"
            
            stats_text += f"\n💰 Estadísticas de Precios:{price_stats}"
            
            # Mostrar en un diálogo
            self.show_dialog("📊 Estadísticas Detalladas", stats_text)
            
        except Exception as e:
            self.show_message(f"❌ Error calculando estadísticas: {str(e)}", "#f44336")
    
    def show_price_analysis(self, e):
        """Muestra análisis de precios"""
        data_to_use = self.filtered_df if not self.filtered_df.empty else self.df
        
        if data_to_use.empty:
            self.show_message("ℹ️ No hay datos cargados. Actualiza primero.", ft.colors.BLUE)
            return
        
        try:
            if 'price_numeric' not in data_to_use.columns:
                self.show_message("❌ No hay datos de precios disponibles", ft.colors.RED)
                return
            
            valid_df = data_to_use[data_to_use['price_numeric'] > 0]
            
            if valid_df.empty:
                self.show_message("❌ No hay precios válidos para analizar", ft.colors.RED)
                return
            
            # Análisis general
            filter_info = f" (Filtro: {self.current_filter})" if self.current_filter != "Todas" else ""
            analysis_text = f"💰 Análisis de Precios{filter_info}:\n\n"
            analysis_text += f"📦 Total productos con precio: {len(valid_df)}\n"
            analysis_text += f"💵 Precio mínimo: S/ {valid_df['price_numeric'].min():,.0f}\n"
            analysis_text += f"💵 Precio máximo: S/ {valid_df['price_numeric'].max():,.0f}\n"
            analysis_text += f"💵 Precio promedio: S/ {valid_df['price_numeric'].mean():,.0f}\n"
            analysis_text += f"💵 Precio mediano: S/ {valid_df['price_numeric'].median():,.0f}\n\n"
            
            # Rangos de precio
            analysis_text += "📈 Distribución por rangos:\n"
            ranges = [
                (0, 1000, "Menos de S/ 1,000"),
                (1000, 2000, "S/ 1,000 - S/ 2,000"),
                (2000, 3000, "S/ 2,000 - S/ 3,000"),
                (3000, 5000, "S/ 3,000 - S/ 5,000"),
                (5000, float('inf'), "Más de S/ 5,000")
            ]
            
            for min_price, max_price, label in ranges:
                count = len(valid_df[(valid_df['price_numeric'] >= min_price) & (valid_df['price_numeric'] < max_price)])
                percentage = (count / len(valid_df)) * 100
                analysis_text += f"• {label}: {count} productos ({percentage:.1f}%)\n"
            
            self.show_dialog("💰 Análisis de Precios", analysis_text)
            
        except Exception as e:
            self.show_message(f"❌ Error en análisis de precios: {str(e)}", ft.colors.RED)
    
    def filter_by_series(self, e):
        """Filtra los datos por serie de gráfica"""
        if e.control.value:
            self.current_filter = e.control.value
            self.apply_current_filter()
            self.update_statistics()
            self.update_data_table()
            
            filter_text = "todas las series" if self.current_filter == "Todas" else f"serie {self.current_filter}"
            self.show_message(f"🔍 Filtrado por {filter_text}: {len(self.filtered_df)} productos", "#2196f3")
    
    def apply_current_filter(self):
        """Aplica el filtro actual a los datos"""
        if self.df.empty:
            self.filtered_df = pd.DataFrame()
            return
            
        if self.current_filter == "Todas":
            self.filtered_df = self.df.copy()
        else:
            self.filtered_df = self.df[self.df['series'] == self.current_filter].copy()
    
    def download_csv(self, e):
        """Descarga los datos filtrados en formato CSV"""
        try:
            if self.filtered_df.empty:
                self.show_message("❌ No hay datos para descargar. Actualiza primero.", "#f44336")
                return
            
            # Crear directorio de descargas si no existe
            import os
            downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            
            # Nombre del archivo con timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filter_suffix = self.current_filter.replace(" ", "_").lower() if self.current_filter != "Todas" else "todas"
            filename = f"rtx_graphics_{filter_suffix}_{timestamp}.csv"
            filepath = os.path.join(downloads_dir, filename)
            
            # Preparar datos para exportar
            export_df = self.filtered_df.copy()
            
            # Renombrar columnas para mejor legibilidad
            column_mapping = {
                'model_searched': 'Modelo_Buscado',
                'title': 'Título',
                'price_text': 'Precio_Texto',
                'price_numeric': 'Precio_Numérico',
                'series': 'Serie',
                'post_link': 'Enlace_Producto',
                'image_link': 'Enlace_Imagen',
                'scraped_date': 'Fecha_Scraping',
                'country': 'País',
                'source': 'Fuente'
            }
            
            # Renombrar solo las columnas que existen
            existing_columns = {k: v for k, v in column_mapping.items() if k in export_df.columns}
            export_df = export_df.rename(columns=existing_columns)
            
            # Exportar a CSV
            export_df.to_csv(filepath, index=False, encoding='utf-8-sig', sep=';')
            
            # Mostrar mensaje de éxito
            filter_text = f" ({self.current_filter})" if self.current_filter != "Todas" else ""
            self.show_message(f"✅ Descarga exitosa: {len(export_df)} productos{filter_text} guardados en {filename}", "#4caf50")
            
            # Abrir carpeta de descargas (opcional)
            try:
                os.startfile(downloads_dir)
            except:
                pass  # No es crítico si no puede abrir la carpeta
                
        except Exception as e:
            self.show_message(f"❌ Error descargando CSV: {str(e)}", "#f44336")
    
    def open_link(self, url):
        """Abre un enlace en el navegador"""
        if url:
            import webbrowser
            webbrowser.open(url)
    
    def show_message(self, message, color):
        """Muestra un mensaje temporal"""
        print(f"DEBUG: show_message called with: {message}")
        try:
            if hasattr(self, 'page') and self.page is not None:
                snack = ft.SnackBar(content=ft.Text(message), bgcolor=color)
                self.page.snack_bar = snack
                snack.open = True
                self.page.update()
                print(f"DEBUG: SnackBar shown successfully")
            else:
                print(f"DEBUG: No page reference available")
                # Fallback: print to console
                print(f"MESSAGE: {message}")
        except Exception as e:
            print(f"DEBUG: Error showing message: {e}")
            print(f"MESSAGE: {message}")
    
    def show_dialog(self, title, content):
        """Muestra un diálogo con información"""
        print(f"DEBUG: show_dialog called with title: {title}")
        try:
            if hasattr(self, 'page') and self.page is not None:
                dialog = ft.AlertDialog(
                    title=ft.Text(title),
                    content=ft.Container(
                        content=ft.Text(content, selectable=True),
                        width=500,
                        height=400,
                        padding=10
                    ),
                    actions=[
                        ft.TextButton("Cerrar", on_click=lambda e: self.close_dialog())
                    ],
                    modal=True
                )
                self.page.dialog = dialog
                dialog.open = True
                self.page.update()
                print(f"DEBUG: Dialog shown successfully")
            else:
                print(f"DEBUG: No page reference available")
                # Fallback: print to console
                print(f"DIALOG - {title}:")
                print(content)
        except Exception as e:
            print(f"DEBUG: Error showing dialog: {e}")
            print(f"DIALOG - {title}:")
            print(content)
    
    def close_dialog(self):
        """Cierra el diálogo actual"""
        try:
            if hasattr(self, 'page') and self.page is not None and self.page.dialog:
                self.page.dialog.open = False
                self.page.update()
                print("DEBUG: Dialog closed successfully")
        except Exception as e:
            print(f"DEBUG: Error closing dialog: {e}")
