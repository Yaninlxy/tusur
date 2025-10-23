#!/usr/bin/env python3
"""
GUI MAC Scanner — обновлён: ARP-сканирование сети (scapy) + fallback (ping+ARP)

Изменения:
- Вместо получения MAC-адресов локальных интерфейсов (psutil) добавлена опция полноценного ARP-сканирования сети.
- Пользователь может указать CIDR (или автодетект сети). Поле ввода сети в GUI.
- Сканирование выполняется в фоновом потоке, чтобы GUI не блокировался.
- Поддержка scapy (если установлен и запущено от root) и fallback для Linux.

Сохранён остальной функционал: SQLite, скрытие строк, экспорт CSV, очистка базы по паролю.
"""

import sys
import re
import csv
import os
import sqlite3
import logging
import threading
import time
from datetime import datetime, timedelta
from collections import Counter
from ipaddress import ip_network, ip_address

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QComboBox, QFileDialog, QLabel, QDateEdit, QMessageBox, QHeaderView, QTextEdit, QInputDialog
)
from PyQt6.QtCore import Qt, QDate, QTimer
from PyQt6.QtGui import QColor, QBrush

# Try to import scapy
try:
    from scapy.all import srp, Ether, ARP, conf
    SCAPY_AVAILABLE = True
except Exception:
    SCAPY_AVAILABLE = False

DB_NAME = "mac_addresses.db"
SCAN_INTERVAL_MINUTES = 5
ADMIN_PASSWORD = "1234"  # Пример пароля для очистки базы

logging.basicConfig(filename="mac_changes.log", level=logging.INFO,
                    format="%(asctime)s - %(message)s")

# --- Работа с базой данных ---
def init_db():
    first_time = not os.path.exists(DB_NAME)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS macs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mac_address TEXT UNIQUE,
            ip_address TEXT,
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    if first_time:
        print("База данных не найдена. Создана новая пустая база.")
    return conn, cursor

def save_mac(cursor, mac, ip=None):
    try:
        cursor.execute("INSERT INTO macs (mac_address, ip_address) VALUES (?, ?)", (mac, ip))
        return True
    except sqlite3.IntegrityError:
        return False

def get_all_macs(cursor):
    cursor.execute("SELECT mac_address, ip_address, first_seen FROM macs ORDER BY first_seen DESC")
    return cursor.fetchall()

# --- Сканирование сети (ARP) ---
def detect_local_subnet(default_mask=24):
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        net = ip_network(f"{local_ip}/{default_mask}", strict=False)
        return str(net)
    except Exception:
        return None

def arp_scan_scapy(cidr, timeout=2, iface=None):
    """ARP scan using scapy. Returns list of (mac, ip)."""
    if not SCAPY_AVAILABLE:
        raise RuntimeError('Scapy not available')
    conf.verb = 0
    if iface:
        conf.iface = iface
    answered, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=cidr), timeout=timeout, retry=1)
    results = []
    for snd, rcv in answered:
        ip = rcv.psrc
        mac = rcv.hwsrc.lower()
        results.append((mac.upper(), ip))
    return results

def read_arp_table_linux():
    path = "/proc/net/arp"
    if not os.path.exists(path):
        return []
    res = []
    with open(path, "r", encoding="utf-8") as f:
        next(f)
        for line in f:
            parts = line.split()
            if len(parts) >= 4:
                ip = parts[0]
                mac = parts[3].lower()
                if mac != "00:00:00:00:00:00":
                    res.append((mac.upper(), ip))
    return res

def ping_sweep_and_arp(cidr, timeout=1):
    """Ping sweep then read ARP table (Linux-only fallback). Returns list of (mac, ip)."""
    results = []
    try:
        net = ip_network(cidr)
    except Exception:
        return results
    # Ping hosts (serially). This can be slow for large networks.
    import subprocess
    for ip in net.hosts():
        subprocess.call(["ping", "-c", "1", "-W", str(timeout), str(ip)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.5)
    return read_arp_table_linux()

# --- GUI ---
class UltimateMacMonitor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ultimate MAC Monitor (ARP scan)")
        self.setGeometry(100, 100, 1000, 600)

        self.conn, self.cursor = init_db()
        self.all_data = []
        self.filtered_data = []

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # --- Сеть: ввод или автодетект ---
        net_layout = QHBoxLayout()
        self.net_input = QLineEdit()
        self.net_input.setPlaceholderText("CIDR сети (например 192.168.1.0/24) — если пусто, автодетект")
        autod = detect_local_subnet()
        if autod:
            self.net_input.setText(autod)
        net_layout.addWidget(QLabel("Сеть:"))
        net_layout.addWidget(self.net_input)
        self.layout.addLayout(net_layout)

        # --- Фильтры ---
        filter_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по MAC или IP...")
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
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["MAC Address", "IP Address", "First Seen"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.layout.addWidget(self.table)

        # --- Кнопки ---
        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Обновить MAC (сканировать сеть)")
        self.refresh_btn.clicked.connect(self.manual_scan)
        self.load_btn = QPushButton("Загрузить из БД")
        self.load_btn.clicked.connect(self.load_db)
        self.export_btn = QPushButton("Экспорт в CSV")
        self.export_btn.clicked.connect(self.export_csv)
        self.delete_btn = QPushButton("Скрыть выбранный MAC")
        self.delete_btn.clicked.connect(self.hide_selected_mac)
        self.clear_db_btn = QPushButton("Очистка базы (Пароль)")
        self.clear_db_btn.clicked.connect(self.clear_db_with_password)
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.load_btn)
        btn_layout.addWidget(self.export_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.clear_db_btn)
        self.layout.addLayout(btn_layout)

        # --- Статистика ---
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.layout.addWidget(self.stats_text)

        self.load_db()
        self.auto_scan_timer = QTimer()
        self.auto_scan_timer.timeout.connect(self.auto_scan)
        self.auto_scan_timer.start(SCAN_INTERVAL_MINUTES * 60 * 1000)

    # --- Сканирование ---
    def auto_scan(self):
        self.scan_and_notify(new_notification=False)

    def manual_scan(self):
        self.scan_and_notify(new_notification=True)

    def scan_and_notify(self, new_notification=False):
        # Запускаем скан в отдельном потоке
        cidr = self.net_input.text().strip() or None
        if cidr:
            try:
                cidr = str(ip_network(cidr, strict=False))
            except Exception as e:
                QMessageBox.warning(self, "Ошибка сети", f"Неверный CIDR: {e}")
                return
        else:
            cidr = detect_local_subnet()
            if not cidr:
                QMessageBox.warning(self, "Ошибка", "Не удалось определить сеть — укажите CIDR вручную.")
                return

        self.refresh_btn.setEnabled(False)
        self.stats_text.append(f"[{datetime.now().isoformat()}] Запуск сканирования {cidr} ...")

        def worker():
            try:
                results = []
                if SCAPY_AVAILABLE:
                    try:
                        results = arp_scan_scapy(cidr, timeout=2)
                    except Exception as e:
                        logging.info(f"Scapy scan failed: {e}")
                        results = []
                if not results:
                    results = ping_sweep_and_arp(cidr, timeout=1)
                # save to DB
                added = []
                for mac, ip in results:
                    if save_mac(self.cursor, mac, ip):
                        added.append((mac, ip))
                self.conn.commit()
                # schedule UI update in main thread
                QTimer.singleShot(0, lambda: finish(len(results), added))
            except Exception as e:
                logging.exception("scan worker error")
                QTimer.singleShot(0, lambda: QMessageBox.warning(self, "Ошибка", f"Ошибка при сканировании: {e}"))
                QTimer.singleShot(0, lambda: self.refresh_btn.setEnabled(True))

        def finish(total_found, added_list):
            if new_notification and added_list:
                msg = "Найдены новые устройства:\n" + "\n".join([f"{m} ({ip})" for m, ip in added_list])
                QMessageBox.information(self, "Новые MAC", msg)
            self.stats_text.append(f"Найдено {total_found} устройств, добавлено в БД: {len(added_list)}")
            self.load_db()
            self.refresh_btn.setEnabled(True)

        t = threading.Thread(target=worker, daemon=True)
        t.start()

    # --- Загрузка данных из базы ---
    def load_db(self):
        self.all_data = get_all_macs(self.cursor)
        # entries: (mac, ip, ts)
        self.filtered_data = [(row[0], row[1], row[2]) for row in self.all_data]
        self.apply_filters()

    # --- Фильтры ---
    def apply_filters(self):
        query = self.search_input.text().upper()
        status = self.status_filter.currentText()
        date_from = self.date_from.date().toPyDate()
        date_to = self.date_to.date().toPyDate()
        filtered = []
        for mac, ip, ts in self.filtered_data:
            ts_date = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").date()
            if query and (query not in mac and (not ip or query not in ip.upper())):
                continue
            if not (date_from <= ts_date <= date_to):
                continue
            if status == "Новые (после 1 дня)" and ts_date < datetime.now().date() - timedelta(days=1):
                continue
            if status == "Старые" and ts_date >= datetime.now().date() - timedelta(days=1):
                continue
            filtered.append((mac, ip, ts))
        self.display_table(filtered)

    # --- Отображение таблицы ---
    def display_table(self, data):
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        now = datetime.now()
        max_age = max(((now - datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")).days for _, _, ts in data), default=1)
        if max_age == 0:
            max_age = 1

        for row_idx, (mac, ip, ts) in enumerate(data):
            self.table.insertRow(row_idx)
            mac_item = QTableWidgetItem(mac)
            ip_item = QTableWidgetItem(ip or "-")
            ts_item = QTableWidgetItem(ts)
            ts_datetime = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            age_ratio = min(1.0, (now - ts_datetime).days / max_age)
            green = int(200 * (1 - age_ratio) + 220 * age_ratio)
            red_blue = int(0 * (1 - age_ratio) + 220 * age_ratio)
            bg_color = QColor(red_blue, green, red_blue)
            for it in (mac_item, ip_item, ts_item):
                it.setBackground(QBrush(bg_color))
                it.setForeground(QBrush(QColor(0,0,0)))
            self.table.setItem(row_idx, 0, mac_item)
            self.table.setItem(row_idx, 1, ip_item)
            self.table.setItem(row_idx, 2, ts_item)
        self.table.blockSignals(False)

    # --- Скрытие MAC из таблицы ---
    def hide_selected_mac(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Скрытие", "Выберите строку для скрытия!")
            return
        for idx in selected:
            mac = self.table.item(idx.row(), 0).text()
            self.filtered_data = [entry for entry in self.filtered_data if entry[0] != mac]
        self.apply_filters()

    # --- Очистка базы по паролю ---
    def clear_db_with_password(self):
        password, ok = QInputDialog.getText(self, "Очистка базы", "Введите пароль:", echo=QLineEdit.EchoMode.Password)
        if ok:
            if password == ADMIN_PASSWORD:
                reply = QMessageBox.question(self, "Подтверждение", "Вы действительно хотите очистить базу?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    self.cursor.execute("DELETE FROM macs")
                    self.conn.commit()
                    self.load_db()
                    QMessageBox.information(self, "Очистка", "База успешно очищена!")
            else:
                QMessageBox.warning(self, "Ошибка", "Неверный пароль!")

    # --- Экспорт CSV ---
    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить CSV", "", "CSV Files (*.csv)")
        if path:
            with open(path, "w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["MAC Address", "IP Address", "First Seen"])
                for row in range(self.table.rowCount()):
                    mac = self.table.item(row, 0).text()
                    ip = self.table.item(row, 1).text()
                    ts = self.table.item(row, 2).text()
                    writer.writerow([mac, ip, ts])
            QMessageBox.information(self, "Экспорт", "Данные успешно экспортированы!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UltimateMacMonitor()
    window.show()
    sys.exit(app.exec())
