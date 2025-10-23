import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import psutil
import re

# --- Работа с базой данных ---
DB_NAME = "mac_addresses.db"

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

def get_all_macs(cursor):
    cursor.execute("SELECT mac_address, first_seen FROM macs")
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

# --- GUI ---
class MacApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MAC Address Collector")
        self.conn, self.cursor = init_db()
        
        self.tree = ttk.Treeview(root, columns=("MAC", "First Seen"), show='headings')
        self.tree.heading("MAC", text="MAC Address")
        self.tree.heading("First Seen", text="First Seen")
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        btn_frame = tk.Frame(root)
        btn_frame.pack(fill=tk.X)
        
        refresh_btn = tk.Button(btn_frame, text="Refresh MACs", command=self.refresh_macs)
        refresh_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        load_db_btn = tk.Button(btn_frame, text="Load from DB", command=self.load_db)
        load_db_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.load_db()
    
    def refresh_macs(self):
        macs = get_mac_addresses()
        new_count = 0
        for mac in macs:
            if save_mac(self.cursor, mac):
                new_count += 1
        self.conn.commit()
        messagebox.showinfo("Update", f"Найдено {len(macs)} MAC, добавлено новых: {new_count}")
        self.load_db()
    
    def load_db(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for mac, ts in get_all_macs(self.cursor):
            self.tree.insert("", tk.END, values=(mac, ts))

# --- Запуск приложения ---
if __name__ == "__main__":
    root = tk.Tk()
    app = MacApp(root)
    root.geometry("500x400")
    root.mainloop()
import sys
import re
import sqlite3
import psutil
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt6.QtGui import QColor

DB_NAME = "mac_addresses.db"

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
class MacApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MAC Address Collector")
        self.setGeometry(200, 200, 600, 400)

        self.conn, self.cursor = init_db()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Поиск
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по MAC...")
        self.search_input.textChanged.connect(self.filter_table)
        search_layout.addWidget(self.search_input)
        self.layout.addLayout(search_layout)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["MAC Address", "First Seen"])
        self.layout.addWidget(self.table)

        # Кнопки
        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Обновить MAC")
        self.refresh_btn.clicked.connect(self.refresh_macs)
        self.load_btn = QPushButton("Загрузить из БД")
        self.load_btn.clicked.connect(self.load_db)
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.load_btn)
        self.layout.addLayout(btn_layout)

        self.load_db()

    def refresh_macs(self):
        macs = get_mac_addresses()
        new_count = 0
        for mac in macs:
            if save_mac(self.cursor, mac):
                new_count += 1
        self.conn.commit()
        QMessageBox.information(self, "Обновление", f"Найдено {len(macs)} MAC, добавлено новых: {new_count}")
        self.load_db()

    def load_db(self):
        self.all_data = get_all_macs(self.cursor)
        self.display_table(self.all_data)

    def display_table(self, data):
        self.table.setRowCount(0)
        for row_idx, (mac, ts) in enumerate(data):
            self.table.insertRow(row_idx)
            mac_item = QTableWidgetItem(mac)
            ts_item = QTableWidgetItem(ts)
            # Цвет для новых MAC (например, последние 5)
            if row_idx < 5:
                mac_item.setBackground(QColor(200, 255, 200))
                ts_item.setBackground(QColor(200, 255, 200))
            self.table.setItem(row_idx, 0, mac_item)
            self.table.setItem(row_idx, 1, ts_item)

    def filter_table(self):
        query = self.search_input.text().upper()
        filtered = [row for row in self.all_data if query in row[0]]
        self.display_table(filtered)

# --- Запуск приложения ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MacApp()
    window.show()
    sys.exit(app.exec())
