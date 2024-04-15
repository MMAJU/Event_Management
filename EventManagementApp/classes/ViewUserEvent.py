import sys
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QComboBox, QDateEdit, QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QHBoxLayout, QLabel, QSpinBox, QTimeEdit
from PyQt5.QtCore import QDate, QTime
from PyQt5.QtGui import QFont
import sqlite3
#from dotenv import load_dotenv
import os


def connect_to_database():
    try:
        conn = sqlite3.connect('event_management.db')
        return conn
    except sqlite3.Error as err:
        QMessageBox.warning(None, 'Error', f"SQLite Error: {err}")
        return None


class ViewUserEventsForm(QDialog):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setWindowTitle('View Event')
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ['Title', 'Description', 'Event Date', 'Event Time', 'Slots', 'Register'])
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.populate_events()

        # Filter Widgets
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Date:"))
        self.date_filter = QDateEdit()
        filter_layout.addWidget(self.date_filter)
        filter_layout.addWidget(QLabel("Title:"))
        self.title_filter = QLineEdit()
        filter_layout.addWidget(self.title_filter)
        filter_layout.addWidget(QLabel("Time:"))
        self.time_filter = QLineEdit()
        filter_layout.addWidget(self.time_filter)
        filter_button = QPushButton("Search")
        filter_button.clicked.connect(self.filter_events)
        filter_layout.addWidget(filter_button)
        layout.addLayout(filter_layout)

    def populate_events(self):
        conn = connect_to_database()
        if conn:
            try:
                cursor = conn.cursor()
                query = "SELECT event_id, title, description, event_date, event_time, slots FROM events"
                cursor.execute(query)
                events = cursor.fetchall()
                self.table.setRowCount(len(events))
                for row, event in enumerate(events):
                    for col, data in enumerate(event[1:]):
                        item = QTableWidgetItem(str(data))
                        self.table.setItem(row, col, item)
                    reg_button = QPushButton('Register')
                    reg_button.clicked.connect(
                        lambda checked, row=row, event_id=event[0]: self.reg_event(row, event_id))
                    self.table.setCellWidget(row, 5, reg_button)

            except sqlite3.Error as err:
                QMessageBox.warning(None, 'Error', f"SQLite Error: {err}")
            finally:
                cursor.close()
                conn.close()

    def reg_event(self, row, event_id):
        reply = QMessageBox.question(
            self, 'Confirmation', 'Are you sure you want to register for this event?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            conn = connect_to_database()
            if conn:
                try:
                    cursor = conn.cursor()
                    # Check if the user has already registered for the event
                    cursor.execute(
                        "SELECT * FROM users_event WHERE user_id = ? AND event_id = ?", (self.user_id, event_id))
                    if cursor.fetchone():
                        QMessageBox.warning(
                            self, 'Error', 'You have already registered for this event.')
                    else:
                        # Check if the event date has passed
                        cursor.execute(
                            "SELECT event_date FROM events WHERE event_id = ?", (event_id,))
                        event_date_str = cursor.fetchone()[0] # Fetch the date as a string
                        event_date = QDate.fromString(event_date_str, 'yyyy-MM-dd')  # Convert to QDate
                        if event_date < QDate.currentDate():
                            QMessageBox.warning(
                                self, 'Error', 'Event date has passed. Cannot register for past events.')
                        else:
                            # Insert the user_id and event_id into the user_event table
                            cursor.execute(
                                "INSERT INTO  users_event (user_id, event_id) VALUES (?, ?)", (self.user_id, event_id))
                            conn.commit()
                            QMessageBox.information(
                                self, 'Success', 'Event registered successfully.')
                except sqlite3.Error as err:
                    QMessageBox.warning(self, 'Error', f"SQLite Error: {err}")
                finally:
                    cursor.close()
                    conn.close()

    def filter_events(self):
        conn = connect_to_database()
        if conn:
            try:
                cursor = conn.cursor()
                query = "SELECT event_id, title, description, event_date, event_time, slots FROM events WHERE 1=1"
                filters = []
                if self.date_filter.date().isValid():
                    filters.append(
                        f"event_date = '{self.date_filter.date().toString('yyyy-MM-dd')}'")
                if self.title_filter.text():
                    filters.append(
                        f"title LIKE '%{self.title_filter.text()}%'")
                if self.time_filter.text():
                    filters.append(
                        f"event_time LIKE '%{self.time_filter.text()}%'")

                if filters:
                    query += " AND " + " AND ".join(filters)
                    print("Constructed SQL query:", query)

                cursor.execute(query)
                events = cursor.fetchall()
                self.table.setRowCount(len(events))
                for row, event in enumerate(events):
                    for col, data in enumerate(event[1:]):
                        item = QTableWidgetItem(str(data))
                        self.table.setItem(row, col, item)
                    reg_button = QPushButton('Register')
                    reg_button.clicked.connect(
                        lambda checked, row=row, event_id=event[0]: self.reg_event(row, event_id))
                    self.table.setCellWidget(row, 5, reg_button)

            except sqlite3.Error as err:
                QMessageBox.warning(None, 'Error', f"SQLite Error: {err}")
            finally:
                cursor.close()
                conn.close()
