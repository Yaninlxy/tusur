import sys
import re
import csv
import sqlite3
import psutil
import logging
from datetime import datetime, timedelta
from collections import Counter
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QComboBox, QFileDialog, QLabel, QDateEdit, QMessageBox, QHeaderView, QTextEdit
)
from PyQt6.QtCore import Qt, QDate, QTimer
from PyQt6.QtGui import QColor, QBrush

DB_NAME = "mac_addresses.db"
SCAN_INTERVAL_MINUTES = 5

logging.basicConfig(filename="mac_changes.log", level=logging.INFO,
                    format="%(asctime)s - %(message)s")

# --- Работа с базой данных ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS macs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mac_address TEXT UNIQUE,
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    return conn, cursor

def save_mac(cursor, mac):
    try:
        cursor.execute("INSERT INTO macs (mac_address) VALUES (?)", (mac,))
        return True
    except sqlite3.IntegrityError:
        return False

def delete_mac(cursor, mac):
    cursor.execute("DELETE FROM macs WHERE mac_address = ?", (mac,))

def update_mac(cursor, old_mac, new_mac):
    try:
        cursor.execute("UPDATE macs SET mac_address = ? WHERE mac_address = ?", (new_mac, old_mac))
        return True
    except sqlite3.IntegrityError:
        return False

def get_all_macs(cursor):
    cursor.execute("SELECT mac_address, first_seen FROM macs ORDER BY first_seen DESC")
    return cursor.fetchall()

# --- Получение MAC-адресов ---
def get_mac_addresses():
    mac_list = []
    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family.name == 'AF_LINK' or addr.family.name == 'AF_PACKET':
                mac = addr.address.upper()
                if re.match(r'([0-9A-F]{2}[:\-]){5}[0-9A-F]{2}', mac):
                    mac_list.append(mac)
    return mac_list

# --- PyQt GUI ---
class UltimateMacMonitor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ultimate MAC Monitor (Smooth Gradient)")
        self.setGeometry(100, 100, 950, 600)

        self.conn, self.cursor = init_db()
        self.all_data = []

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # --- Фильтры ---
        filter_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по MAC...")
        self.search_input.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.search_input)

        self.status_filter = QComboBox()
        self.status_filter.addItems(["Все", "Новые (после 1 дня)", "Старые"])
        self.status_filter.currentIndexChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.status_filter)

        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_from.dateChanged.connect(self.apply_filters)
        filter_layout.addWidget(QLabel("С даты:"))
        filter_layout.addWidget(self.date_from)

        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.dateChanged.connect(self.apply_filters)
        filter_layout.addWidget(QLabel("По дату:"))
        filter_layout.addWidget(self.date_to)

        self.layout.addLayout(filter_layout)

        # --- Таблица ---
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["MAC Address", "First Seen"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemChanged.connect(self.item_changed)
        self.layout.addWidget(self.table)

        # --- Кнопки ---
        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Обновить MAC")
        self.refresh_btn.clicked.connect(self.manual_scan)
        self.load_btn = QPushButton("Загрузить из БД")
        self.load_btn.clicked.connect(self.load_db)
        self.export_btn = QPushButton("Экспорт в CSV")
        self.export_btn.clicked.connect(self.export_csv)
        self.delete_btn = QPushButton("Удалить выбранный MAC")
        self.delete_btn.clicked.connect(self.delete_selected_mac)
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.load_btn)
        btn_layout.addWidget(self.export_btn)
        btn_layout.addWidget(self.delete_btn)
        self.layout.addLayout(btn_layout)

        # --- Статистика ---
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.layout.addWidget(self.stats_text)

        self.load_db()
        self.auto_scan_timer = QTimer()
        self.auto_scan_timer.timeout.connect(self.auto_scan)
        self.auto_scan_timer.start(SCAN_INTERVAL_MINUTES * 60 * 1000)

    # --- Авто-сканирование ---
    def auto_scan(self):
        self.scan_and_notify(new_notification=True)

    def manual_scan(self):
        self.scan_and_notify(new_notification=True)

    def scan_and_notify(self, new_notification=False):
        current_macs = get_mac_addresses()
        added_macs = []
        for mac in current_macs:
            if save_mac(self.cursor, mac):
                added_macs.append(mac)
                logging.info(f"Добавлен новый MAC: {mac}")
        self.conn.commit()
        if new_notification and added_macs:
            QMessageBox.information(self, "Новые MAC", "Найдены новые MAC:\n" + "\n".join(added_macs))
        self.load_db()

    def load_db(self):
        self.all_data = get_all_macs(self.cursor)
        self.apply_filters()
        self.update_stats()

    def apply_filters(self):
        query = self.search_input.text().upper()
        status = self.status_filter.currentText()
        date_from = self.date_from.date().toPyDate()
        date_to = self.date_to.date().toPyDate()
        filtered = []
        for mac, ts in self.all_data:
            ts_date = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").date()
            if query not in mac:
                continue
            if not (date_from <= ts_date <= date_to):
                continue
            if status == "Новые (после 1 дня)" and ts_date < datetime.now().date() - timedelta(days=1):
                continue
            if status == "Старые" and ts_date >= datetime.now().date() - timedelta(days=1):
                continue
            filtered.append((mac, ts))
        self.display_table(filtered)
        self.update_stats(filtered)

    def display_table(self, data):
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        now = datetime.now()

        # защитимся от пустой таблицы
        max_age = max(((now - datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")).days for _, ts in data), default=1)
        if max_age == 0:
            max_age = 1  # защита от деления на ноль

        for row_idx, (mac, ts) in enumerate(data):
            self.table.insertRow(row_idx)
            mac_item = QTableWidgetItem(mac)
            ts_item = QTableWidgetItem(ts)

            ts_datetime = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            age_ratio = min(1.0, (now - ts_datetime).days / max_age)

            # плавный градиент: зеленый -> серый
            green = int(200 * (1 - age_ratio) + 220 * age_ratio)
            red_blue = int(0 * (1 - age_ratio) + 220 * age_ratio)
            bg_color = QColor(red_blue, green, red_blue)
            text_color = QColor(0, 0, 0)

            mac_item.setBackground(QBrush(bg_color))
            ts_item.setBackground(QBrush(bg_color))
            mac_item.setForeground(QBrush(text_color))
            ts_item.setForeground(QBrush(text_color))

            self.table.setItem(row_idx, 0, mac_item)
            self.table.setItem(row_idx, 1, ts_item)

        self.table.blockSignals(False)

    def item_changed(self, item):
        row = item.row()
        col = item.column()
        old_mac = self.all_data[row][0]
        new_mac = self.table.item(row, 0).text()
        if col == 0 and old_mac != new_mac:
            if update_mac(self.cursor, old_mac, new_mac):
                logging.info(f"MAC изменён: {old_mac} -> {new_mac}")
                self.conn.commit()
                self.load_db()
            else:
                QMessageBox.warning(self, "Ошибка", "MAC уже существует в базе!")
                self.load_db()

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить CSV", "", "CSV Files (*.csv)")
        if path:
            with open(path, "w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["MAC Address", "First Seen"])
                for row in range(self.table.rowCount()):
                    mac = self.table.item(row, 0).text()
                    ts = self.table.item(row, 1).text()
                    writer.writerow([mac, ts])
            QMessageBox.information(self, "Экспорт", "Данные успешно экспортированы!")

    def delete_selected_mac(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Удаление", "Выберите строку для удаления!")
            return
        for idx in selected:
            mac = self.table.item(idx.row(), 0).text()
            delete_mac(self.cursor, mac)
            logging.info(f"Удалён MAC: {mac}")
        self.conn.commit()
        self.load_db()
        QMessageBox.information(self, "Удаление", "Выбранные MAC удалены!")

    def update_stats(self, data=None):
        if data is None:
            data = self.all_data
        counter = Counter(datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").date() for _, ts in data)
        stats_lines = [f"{date}: {count} MAC" for date, count in sorted(counter.items())]
        self.stats_text.setPlainText("\n".join(stats_lines))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UltimateMacMonitor()
    window.show()
    sys.exit(app.exec())
