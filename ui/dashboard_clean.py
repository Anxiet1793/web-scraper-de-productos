# ui/dashboard.py

import flet as ft
import pandas as pd
from datetime import datetime, timedelta
from db.queries import find_documents
from utils.dataframe_tools import mongo_to_dataframe, clean_and_format_dataframe
from api.fetch_matches import (
    fetch_and_store_cs_all_data_hltv, 
    fetch_cs_players_hltv_only, 
    fetch_cs_teams_hltv_only, 
    fetch_cs_matches_hltv_only,
    fetch_cs_results_hltv_only
)

class Dashboard(ft.Column):
    """Dashboard principal para mostrar datos de Counter-Strike desde HLTV."""
    
    def __init__(self):
        super().__init__()
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.expand = True

        self.data_table = ft.DataTable(
            columns=[],
            rows=[],
            border=ft.border.all(2, ft.colors.BLUE_GREY_200),
            border_radius=ft.border_radius.all(10),
            vertical_lines=ft.border.BorderSide(1, ft.colors.BLUE_GREY_100),
            horizontal_lines=ft.border.BorderSide(1, ft.colors.BLUE_GREY_100),
            sort_column_index=0,
            sort_ascending=True,
            heading_row_color=ft.colors.BLUE_GREY_50,
            data_row_color={"hovered": ft.colors.BLUE_GREY_50},
            show_checkbox_column=False,
            divider_thickness=1,
            column_spacing=20,
        )

        self.progress_ring = ft.ProgressRing(width=50, height=50, stroke_width=5, visible=False)
        self.status_text = ft.Text("Cargando datos...", visible=False)

        self.controls = [
            ft.Text("🎮 CS:GO Stats Dashboard - HLTV Data", 
                   size=24, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_800),
            ft.Divider(),
            ft.Text("📡 Recolección de Datos HLTV", 
                   size=18, weight=ft.FontWeight.BOLD, color=ft.colors.ORANGE_600),
            ft.Row([
                ft.ElevatedButton(
                    "🚀 Recolectar Todos",
                    icon=ft.icons.DOWNLOAD_FOR_OFFLINE,
                    on_click=self.load_cs_all_data,
                    bgcolor=ft.colors.ORANGE_600,
                    color=ft.colors.WHITE,
                    tooltip="Obtiene equipos, jugadores y partidos desde HLTV"
                ),
                ft.ElevatedButton(
                    "👥 Jugadores",
                    icon=ft.icons.PERSON,
                    on_click=self.load_cs_players_data,
                    bgcolor=ft.colors.BLUE_600,
                    color=ft.colors.WHITE
                ),
                ft.ElevatedButton(
                    "🏆 Equipos",
                    icon=ft.icons.GROUPS,
                    on_click=self.load_cs_teams_data,
                    bgcolor=ft.colors.GREEN_600,
                    color=ft.colors.WHITE
                ),
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([
                ft.ElevatedButton(
                    "⚽ Partidos",
                    icon=ft.icons.SPORTS_ESPORTS,
                    on_click=self.load_cs_matches_data,
                    bgcolor=ft.colors.PURPLE_600,
                    color=ft.colors.WHITE
                ),
                ft.ElevatedButton(
                    "📊 Resultados",
                    icon=ft.icons.LEADERBOARD,
                    on_click=self.load_cs_results_data,
                    bgcolor=ft.colors.RED_600,
                    color=ft.colors.WHITE
                ),
                ft.ElevatedButton(
                    "🏅 Torneos",
                    icon=ft.icons.AUTO_AWESOME,
                    on_click=self.load_cs_tournaments_data,
                    bgcolor=ft.colors.AMBER_600,
                    color=ft.colors.WHITE
                ),
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([
                ft.ElevatedButton(
                    "📋 Ver Colecciones",
                    icon=ft.icons.VIEW_LIST,
                    on_click=self.view_cs_collections,
                    bgcolor=ft.colors.INDIGO_600,
                    color=ft.colors.WHITE
                ),
                ft.ElevatedButton(
                    "📤 Exportar CSV",
                    icon=ft.icons.FILE_DOWNLOAD,
                    on_click=self.export_to_csv,
                    bgcolor=ft.colors.TEAL_600,
                    color=ft.colors.WHITE
                ),
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(),
            ft.Stack([
                ft.Column([
                    self.progress_ring,
                    self.status_text
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                   alignment=ft.MainAxisAlignment.CENTER, expand=True),
                ft.Container(
                    content=self.data_table,
                    alignment=ft.alignment.center,
                    expand=True,
                    padding=10,
                    margin=10,
                    border_radius=ft.border_radius.all(10),
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=5,
                        color=ft.colors.BLACK26,
                        offset=ft.Offset(0, 3),
                    ),
                    bgcolor=ft.colors.WHITE
                ),
            ], expand=True)
        ]

    def did_mount(self):
        """Se llama cuando el componente se monta en la página."""
        self.load_cs_collection_data("cs_teams")  # Cargar equipos por defecto

    def _set_loading_state(self, loading=True, message=""):
        """Muestra/oculta el indicador de carga y el mensaje de estado."""
        self.progress_ring.visible = loading
        self.status_text.visible = loading
        self.status_text.value = message
        self.data_table.visible = not loading
        if hasattr(self, 'page') and self.page:
            self.page.update()

    def _update_data_table(self, df):
        """Actualiza las columnas y filas del DataTable con el DataFrame."""
        if df.empty:
            self.data_table.columns = []
            self.data_table.rows = []
            self.status_text.value = "No hay datos para mostrar."
            self.status_text.visible = True
            self.data_table.visible = False
            return

        # Crear columnas (excluir _id)
        columns = []
        for col in df.columns:
            if col == "_id":
                continue
            columns.append(
                ft.DataColumn(
                    ft.Text(col.replace('_', ' ').title(), weight=ft.FontWeight.BOLD)
                )
            )
        self.data_table.columns = columns

        # Crear filas
        rows = []
        for index, row in df.iterrows():
            cells = []
            for col in df.columns:
                if col == "_id":
                    continue
                cell_value = str(row[col]) if pd.notna(row[col]) else ""
                cells.append(ft.DataCell(ft.Text(cell_value[:50])))  # Limitar texto
            rows.append(ft.DataRow(cells))
        
        self.data_table.rows = rows
        self.data_table.visible = True
        self.status_text.visible = False
        if hasattr(self, 'page') and self.page:
            self.page.update()

    def export_to_csv(self, e):
        """Exporta los datos actuales a CSV."""
        self._set_loading_state(True, "Exportando a CSV...")
        try:
            # Exportar datos actuales de la tabla
            current_docs = find_documents()
            if current_docs:
                df = mongo_to_dataframe(current_docs)
                df = clean_and_format_dataframe(df)
                if '_id' in df.columns:
                    df = df.drop(columns=['_id'])
                
                filename = f"cs_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                df.to_csv(filename, index=False, encoding='utf-8')
                
                self.page.snack_bar = ft.SnackBar(
                    ft.Text(f"✅ Datos exportados a '{filename}'"),
                    open=True
                )
            else:
                self.page.snack_bar = ft.SnackBar(
                    ft.Text("⚠️ No hay datos para exportar"),
                    open=True
                )
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"❌ Error al exportar: {ex}"),
                open=True
            )
        finally:
            self._set_loading_state(False)

    # Funciones para Counter-Strike
    def load_cs_all_data(self, e):
        """Recolecta todos los datos de CS desde HLTV."""
        self._set_loading_state(True, "Recolectando datos de Counter-Strike...")
        try:
            success = fetch_and_store_cs_all_data_hltv()
            if success:
                self.load_cs_collection_data("cs_teams")
                self.page.snack_bar = ft.SnackBar(
                    ft.Text("✅ Datos de CS recolectados exitosamente!"),
                    open=True
                )
            else:
                self.page.snack_bar = ft.SnackBar(
                    ft.Text("❌ Error al recolectar datos de CS"),
                    open=True
                )
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"❌ Error: {ex}"),
                open=True
            )
        finally:
            self._set_loading_state(False)

    def load_cs_players_data(self, e):
        """Recolecta jugadores desde HLTV."""
        self._set_loading_state(True, "Recolectando jugadores...")
        try:
            success = fetch_cs_players_hltv_only()
            if success:
                self.load_cs_collection_data("cs_players")
                self.page.snack_bar = ft.SnackBar(
                    ft.Text("✅ Jugadores recolectados exitosamente!"),
                    open=True
                )
            else:
                self.page.snack_bar = ft.SnackBar(
                    ft.Text("❌ Error al recolectar jugadores"),
                    open=True
                )
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"❌ Error: {ex}"),
                open=True
            )
        finally:
            self._set_loading_state(False)

    def load_cs_teams_data(self, e):
        """Recolecta equipos desde HLTV."""
        self._set_loading_state(True, "Recolectando equipos...")
        try:
            success = fetch_cs_teams_hltv_only()
            if success:
                self.load_cs_collection_data("cs_teams")
                self.page.snack_bar = ft.SnackBar(
                    ft.Text("✅ Equipos recolectados exitosamente!"),
                    open=True
                )
            else:
                self.page.snack_bar = ft.SnackBar(
                    ft.Text("❌ Error al recolectar equipos"),
                    open=True
                )
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"❌ Error: {ex}"),
                open=True
            )
        finally:
            self._set_loading_state(False)

    def load_cs_matches_data(self, e):
        """Recolecta partidos desde HLTV."""
        self._set_loading_state(True, "Recolectando partidos...")
        try:
            success = fetch_cs_matches_hltv_only()
            if success:
                self.load_cs_collection_data("cs_matches")
                self.page.snack_bar = ft.SnackBar(
                    ft.Text("✅ Partidos recolectados exitosamente!"),
                    open=True
                )
            else:
                self.page.snack_bar = ft.SnackBar(
                    ft.Text("❌ Error al recolectar partidos"),
                    open=True
                )
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"❌ Error: {ex}"),
                open=True
            )
        finally:
            self._set_loading_state(False)

    def load_cs_results_data(self, e):
        """Recolecta resultados desde HLTV."""
        self._set_loading_state(True, "Recolectando resultados...")
        try:
            success = fetch_cs_results_hltv_only()
            if success:
                self.load_cs_collection_data("cs_results")
                self.page.snack_bar = ft.SnackBar(
                    ft.Text("✅ Resultados recolectados exitosamente!"),
                    open=True
                )
            else:
                self.page.snack_bar = ft.SnackBar(
                    ft.Text("❌ Error al recolectar resultados"),
                    open=True
                )
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"❌ Error: {ex}"),
                open=True
            )
        finally:
            self._set_loading_state(False)

    def load_cs_tournaments_data(self, e):
        """Genera datos de ejemplo de torneos."""
        self._set_loading_state(True, "Generando torneos de ejemplo...")
        try:
            sample_tournaments = [
                {
                    'name': 'IEM Katowice 2025',
                    'tier': 'S-Tier',
                    'prize_pool': 1000000,
                    'teams': 24,
                    'location': 'Katowice, Poland',
                    'start_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                    'end_date': (datetime.now() + timedelta(days=37)).strftime('%Y-%m-%d'),
                    'status': 'upcoming',
                    'source': 'sample'
                },
                {
                    'name': 'ESL Pro League S19',
                    'tier': 'A-Tier',
                    'prize_pool': 750000,
                    'teams': 16,
                    'location': 'Online',
                    'start_date': (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d'),
                    'end_date': (datetime.now() + timedelta(days=50)).strftime('%Y-%m-%d'),
                    'status': 'ongoing',
                    'source': 'sample'
                },
                {
                    'name': 'BLAST Premier Spring',
                    'tier': 'S-Tier',
                    'prize_pool': 600000,
                    'teams': 12,
                    'location': 'Copenhagen',
                    'start_date': (datetime.now() + timedelta(days=45)).strftime('%Y-%m-%d'),
                    'end_date': (datetime.now() + timedelta(days=52)).strftime('%Y-%m-%d'),
                    'status': 'upcoming',
                    'source': 'sample'
                }
            ]
            
            from db.queries import save_cs_data_to_collection
            success = save_cs_data_to_collection(sample_tournaments, "cs_tournaments")
            
            if success:
                self.load_cs_collection_data("cs_tournaments")
                self.page.snack_bar = ft.SnackBar(
                    ft.Text("✅ Torneos de ejemplo generados!"),
                    open=True
                )
            else:
                self.page.snack_bar = ft.SnackBar(
                    ft.Text("❌ Error al generar torneos"),
                    open=True
                )
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"❌ Error: {ex}"),
                open=True
            )
        finally:
            self._set_loading_state(False)

    def view_cs_collections(self, e):
        """Muestra diálogo para seleccionar colección de CS."""
        collections = [
            ("cs_players", "👥 Jugadores"),
            ("cs_teams", "🏆 Equipos"),
            ("cs_matches", "⚽ Partidos"),
            ("cs_results", "📊 Resultados"),
            ("cs_tournaments", "🏅 Torneos"),
            ("cs_transfers", "💼 Transferencias"),
            ("cs_weapons", "🔫 Armas"),
            ("cs_statistics", "📈 Estadísticas"),
            ("cs_patches", "🔧 Parches")
        ]
        
        def select_collection(collection_name):
            def handler(e):
                self.load_cs_collection_data(collection_name)
                self.page.dialog.open = False
                self.page.update()
            return handler
        
        buttons = []
        for col_name, display_name in collections:
            buttons.append(
                ft.ElevatedButton(
                    display_name,
                    on_click=select_collection(col_name),
                    width=200
                )
            )
        
        # Organizar en filas de 2
        button_rows = []
        for i in range(0, len(buttons), 2):
            row_buttons = buttons[i:i+2]
            button_rows.append(ft.Row(row_buttons, alignment=ft.MainAxisAlignment.CENTER))
        
        self.page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("🎮 Colecciones de Counter-Strike"),
            content=ft.Container(
                content=ft.Column(
                    button_rows + [
                        ft.Divider(),
                        ft.ElevatedButton(
                            "Cerrar",
                            on_click=lambda e: setattr(self.page.dialog, 'open', False) or self.page.update(),
                            bgcolor=ft.colors.GREY_400
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO
                ),
                width=500,
                height=400
            )
        )
        self.page.dialog.open = True
        self.page.update()

    def load_cs_collection_data(self, collection_name):
        """Carga y muestra datos de una colección específica."""
        self._set_loading_state(True, f"Cargando {collection_name}...")
        try:
            mongo_docs = find_documents(collection_name=collection_name)
            if not mongo_docs:
                self.status_text.value = f"No hay datos en '{collection_name}'"
                self.status_text.visible = True
                self.data_table.visible = False
                self._set_loading_state(False)
                return
            
            df = mongo_to_dataframe(mongo_docs)
            df = clean_and_format_dataframe(df)
            self._update_data_table(df)
            self._set_loading_state(False)
            
        except Exception as e:
            self._set_loading_state(False)
            self.status_text.value = f"Error al cargar {collection_name}: {e}"
            self.status_text.visible = True
            print(f"Error al cargar {collection_name}: {e}")
