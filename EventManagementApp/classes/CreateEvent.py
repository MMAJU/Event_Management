import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QTextEdit, QComboBox, QMessageBox, QDateEdit, QSpinBox, QTimeEdit
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
        print(f"SQLite Error: {err}")
        return None


class CreateEventForm(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Create Event')
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        layout.addWidget(QLabel('Event Title'))
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText('Event Title')
        layout.addWidget(self.title_input)

        layout.addWidget(QLabel('Event Description'))
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText('Event Description')
        layout.addWidget(self.description_input)

        layout.addWidget(QLabel('Event Date'))
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat('yyyy-MM-dd')
        self.date_input.setDate(QDate.currentDate())
        layout.addWidget(self.date_input)

        layout.addWidget(QLabel('Event Time'))
        self.time_input = QTimeEdit()
        self.time_input.setDisplayFormat('HH:mm')
        self.time_input.setMinimumTime(QTime(0, 0))
        self.time_input.setMaximumTime(QTime(23, 59))
        layout.addWidget(self.time_input)

        layout.addWidget(QLabel('Total Number of Slots'))
        self.number_input = QSpinBox()
        self.number_input.setMinimum(0)
        self.number_input.setMaximum(100)
        self.number_input.setToolTip('Number of Slots')
        layout.addWidget(self.number_input)

        submit_button = QPushButton('Create Event')
        submit_button.clicked.connect(self.create_event)
        layout.addWidget(submit_button)

        self.setLayout(layout)

    def create_event(self):
        title = self.title_input.text()
        description = self.description_input.text()
        event_date = self.date_input.date().toString('yyyy-MM-dd')
        event_time = self.time_input.time().toString('HH:mm')
        number_of_slots = self.number_input.value()

        if not title or not description or not event_date or not event_time or not number_of_slots:
            QMessageBox.warning(self, 'Error', 'Please fill in all fields')
            return

        conn = connect_to_database()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO events (title, description, event_date, event_time, slots) VALUES (?, ?, ?, ?, ?)",
                               (title, description, event_date, event_time, number_of_slots))
                conn.commit()
                QMessageBox.information(
                    self, 'Success', 'Event created and assigned successfully!')
                self.accept()
            except sqlite3.Error as err:
                QMessageBox.warning(self, 'Error', f"SQLite Error: {err}")
            finally:
                cursor.close()
                conn.close()
