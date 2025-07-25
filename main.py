import sys
import matplotlib
matplotlib.use("Qt5Agg")
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QHBoxLayout, QLabel, QTableWidget, QScrollArea, QDialog
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

# Project files
from report1 import generate_summary
from report2 import generate_profitability_report
from report3 import generate_time_analysis
from report4 import generate_inventory_analysis

from chart1 import draw_profit_bar_chart, get_profit_chart_pixmap
from chart2 import draw_profit_pie_chart, get_profit_pie_pixmap
from chart3 import draw_inventory_bar_chart, get_inventory_chart_pixmap
from chart4 import draw_sold_percentage_pie_chart, get_sold_percentage_pie_pixmap
from chart5 import draw_sales_line_chart, get_sales_line_chart_pixmap
from chart6 import draw_sales_bar_chart, get_sales_bar_chart_pixmap
from chart7 import draw_sales_share_pie_chart, get_sales_share_pie_pixmap

from read_me import show_readme
from file import create_database, load_csv_and_insert, display_existing_data


def show_scrollable_dialog(parent, title, content):
    dialog = QDialog(parent)
    dialog.setWindowTitle(title)
    dialog.resize(600, 500)
    layout = QVBoxLayout(dialog)
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)

    label = QLabel(content)
    label.setWordWrap(True)

    scroll_content = QWidget()
    content_layout = QVBoxLayout(scroll_content)
    content_layout.addWidget(label)

    scroll.setWidget(scroll_content)
    layout.addWidget(scroll)
    dialog.exec_()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📊 Dashboard zur Verwaltung von Verkäufen und Einkäufen")
        self.resize(1300, 700)
        # self.setMinimumSize(1300, 600)
        self.db_name = "sales.db"
        create_database(self.db_name)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QHBoxLayout(self.central_widget)

        # 📦 Schaltflächenfeld mit Bildlaufleiste
        self.button_scroll = QScrollArea()
        self.button_scroll.setWidgetResizable(True)
        self.button_container = QWidget()
        self.button_layout = QVBoxLayout(self.button_container)

        self.add_buttons()
        self.button_scroll.setWidget(self.button_container)
        self.button_scroll.setFixedWidth(int(0.22 * self.width()))
        main_layout.addWidget(self.button_scroll)

        # 📊 Analyseinhalt-Panel
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)

        # Abschnitt für Analyseinhalte
        self.analysis_label = QLabel("📊 Analytisches Dashboard für Verkaufs- und Einkaufsdaten \n(Bitte lesen Sie vor der Nutzung der Anwendung das Benutzerhandbuch.)")
        self.analysis_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.scroll_layout.addWidget(self.analysis_label)

        self.table_widget = QTableWidget()
        self.scroll_layout.addWidget(self.table_widget)

        self.report_label = QLabel()
        self.report_label.setWordWrap(True)
        self.scroll_layout.addWidget(self.report_label)

        self.profit_label = QLabel()
        self.profit_label.setWordWrap(True)
        self.scroll_layout.addWidget(self.profit_label)

        self.time_label = QLabel()
        self.time_label.setWordWrap(True)
        self.scroll_layout.addWidget(self.time_label)

        self.inventory_label = QLabel()
        self.inventory_label.setWordWrap(True)
        self.scroll_layout.addWidget(self.inventory_label)

        # Diagrammbereich
        self.chart_label = QLabel(); self.chart_label.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(self.chart_label)

        self.pie_chart_label = QLabel(); self.pie_chart_label.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(self.pie_chart_label)

        self.inventory_chart_label = QLabel(); self.inventory_chart_label.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(self.inventory_chart_label)

        self.sold_percentage_chart_label = QLabel(); self.sold_percentage_chart_label.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(self.sold_percentage_chart_label)

        self.sales_line_chart_label = QLabel(); self.sales_line_chart_label.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(self.sales_line_chart_label)

        self.sales_bar_chart_label = QLabel(); self.sales_bar_chart_label.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(self.sales_bar_chart_label)

        self.sales_share_chart_label = QLabel(); self.sales_share_chart_label.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(self.sales_share_chart_label)

        self.refresh_dashboard()

    def add_buttons(self):
        # Hauptschaltflächen des Projekts
        self.load_csv_button = QPushButton("📁 CSV laden")
        self.load_csv_button.clicked.connect(self.load_csv)
        self.button_layout.addWidget(self.load_csv_button)

        self.report_button = QPushButton("📊 Allgemeiner Datenbericht")
        self.report_button.clicked.connect(self.show_report_popup)
        self.button_layout.addWidget(self.report_button)

        self.profit_button = QPushButton("💹 Rentabilitätsbericht")
        self.profit_button.clicked.connect(self.show_profit_popup)
        self.button_layout.addWidget(self.profit_button)

        self.time_button = QPushButton("📅 Zeitreihenanalyse")
        self.time_button.clicked.connect(self.show_time_popup)
        self.button_layout.addWidget(self.time_button)

        self.inventory_button = QPushButton("📦 Bestandsanalyse")
        self.inventory_button.clicked.connect(self.show_inventory_popup)
        self.button_layout.addWidget(self.inventory_button)

        # Diagramme
        self.chart_button = QPushButton("📉 Rentabilitätsdiagramm")
        self.chart_button.clicked.connect(draw_profit_bar_chart)
        self.button_layout.addWidget(self.chart_button)

        self.pie_chart_button = QPushButton("🥧 Kreisdiagramm zur Rentabilität")
        self.pie_chart_button.clicked.connect(draw_profit_pie_chart)
        self.button_layout.addWidget(self.pie_chart_button)

        self.inventory_chart_button = QPushButton("📦 Bestandsdiagramm")
        self.inventory_chart_button.clicked.connect(draw_inventory_bar_chart)
        self.button_layout.addWidget(self.inventory_chart_button)

        self.sold_percent_button = QPushButton("📊 Produktumsatzanteil")
        self.sold_percent_button.clicked.connect(draw_sold_percentage_pie_chart)
        self.button_layout.addWidget(self.sold_percent_button)

        self.sales_line_button = QPushButton("📈 Verkaufs-Liniendiagramm")
        self.sales_line_button.clicked.connect(draw_sales_line_chart)
        self.button_layout.addWidget(self.sales_line_button)

        self.sales_bar_button = QPushButton("📦 Verkaufs-Balkendiagramm")
        self.sales_bar_button.clicked.connect(draw_sales_bar_chart)
        self.button_layout.addWidget(self.sales_bar_button)

        self.sales_share_button = QPushButton("🥧 Produktumsatzanteilsdiagramm")
        self.sales_share_button.clicked.connect(draw_sales_share_pie_chart)
        self.button_layout.addWidget(self.sales_share_button)

        # Hilfe-Schaltfläche
        self.help_button = QPushButton("📘 Leitfaden")
        self.help_button.clicked.connect(lambda: show_readme(self))
        self.button_layout.addWidget(self.help_button)

        self.exit_button = QPushButton("❌ Beenden")
        self.exit_button.clicked.connect(QApplication.quit)
        self.button_layout.addWidget(self.exit_button)

    def refresh_dashboard(self):
        display_existing_data(self.db_name, self.table_widget)
        self.update_summary()
        self.update_profitability()
        self.update_time_analysis()
        self.update_inventory_analysis()
        self.update_chart_image()
        self.update_pie_chart_image()
        self.update_inventory_chart_image()
        self.update_sold_percentage_chart_image()
        self.update_sales_line_chart_image()
        self.update_sales_bar_chart_image()
        self.update_sales_share_chart_image()

    def load_csv(self):
        load_csv_and_insert(self, self.db_name, self.table_widget)
        self.refresh_dashboard()

    def update_summary(self):
        self.report_label.setText(generate_summary())

    def update_profitability(self):
        self.profit_label.setText(generate_profitability_report())

    def update_time_analysis(self):
        self.time_label.setText(generate_time_analysis())

    def update_inventory_analysis(self):
        self.inventory_label.setText(generate_inventory_analysis())

    def update_chart_image(self):
        pixmap = get_profit_chart_pixmap()
        if pixmap:
            self.chart_label.setPixmap(pixmap)

    def update_pie_chart_image(self):
        pixmap = get_profit_pie_pixmap()
        if pixmap:
            self.pie_chart_label.setPixmap(pixmap)

    def update_inventory_chart_image(self):
        pixmap = get_inventory_chart_pixmap()
        if pixmap:
            self.inventory_chart_label.setPixmap(pixmap)

    def update_sold_percentage_chart_image(self):
        pixmap = get_sold_percentage_pie_pixmap()
        if pixmap:
            self.sold_percentage_chart_label.setPixmap(pixmap)

    def update_sales_line_chart_image(self):
        pixmap = get_sales_line_chart_pixmap()
        if pixmap:
            self.sales_line_chart_label.setPixmap(pixmap)

    def update_sales_bar_chart_image(self):
        pixmap = get_sales_bar_chart_pixmap()
        if pixmap:
            self.sales_bar_chart_label.setPixmap(pixmap)

    def update_sales_share_chart_image(self):
        pixmap = get_sales_share_pie_pixmap()
        if pixmap:
            self.sales_share_chart_label.setPixmap(pixmap)

    def show_report_popup(self):
        show_scrollable_dialog(self, "📊 Numerischer Bericht" , generate_summary())

    def show_profit_popup(self):
        show_scrollable_dialog(self, "💹 Rentabilitätsbericht", generate_profitability_report())

    def show_time_popup(self):
        show_scrollable_dialog(self, "📈 Zeitreihenanalyse" , generate_time_analysis())

    def show_inventory_popup(self):
        show_scrollable_dialog(self, "📦 Bestandsanalyse", generate_inventory_analysis())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        with open("style.css", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print(f"⚠️ Fehler beim Laden des Stils: {e}")

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

# pyinstaller --onefile --windowed --add-data "style.css;." --icon=icon.ico main.py
# pyinstaller --onefile --windowed --add-data "style.css;." --icon=icon.ico main.py