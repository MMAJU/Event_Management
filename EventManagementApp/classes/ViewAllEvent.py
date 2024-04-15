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


class ViewEventsForm(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('View Event')
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ['Title', 'Description', 'Event Date', 'Event Time', 'Slots', 'Edit', 'Delete', 'Attendee List'])
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
                    edit_button = QPushButton('Edit')
                    edit_button.clicked.connect(
                        lambda checked, row=row, event_id=event[0]: self.edit_event(row, event_id))
                    self.table.setCellWidget(row, 5, edit_button)

                    delete_button = QPushButton('Delete')
                    delete_button.clicked.connect(
                        lambda checked, row=row, event_id=event[0]: self.delete_event(row, event_id))
                    self.table.setCellWidget(row, 6, delete_button)

                    atten_list_button = QPushButton('View list')
                    atten_list_button.clicked.connect(
                        lambda checked, row=row, event_id=event[0]: self.attendee_event(row, event_id))
                    self.table.setCellWidget(row, 7, atten_list_button)

            except sqlite3.Error as err:
                QMessageBox.warning(None, 'Error', f"SQLite Error: {err}")
                print("Full error message:", err)
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
                    # Debugging statement
                    print("Constructed SQL query:", query)

                cursor.execute(query)
                events = cursor.fetchall()
                self.table.setRowCount(len(events))
                for row, event in enumerate(events):
                    for col, data in enumerate(event[1:]):
                        item = QTableWidgetItem(str(data))
                        self.table.setItem(row, col, item)
                    edit_button = QPushButton('Edit')
                    edit_button.clicked.connect(
                        lambda checked, row=row, event_id=event[0]: self.edit_event(row, event_id))
                    self.table.setCellWidget(row, 5, edit_button)

                    delete_button = QPushButton('Delete')
                    delete_button.clicked.connect(
                        lambda checked, row=row, event_id=event[0]: self.delete_event(row, event_id))
                    self.table.setCellWidget(row, 6, delete_button)

                    atten_list_button = QPushButton('View list')
                    atten_list_button.clicked.connect(
                        lambda checked, row=row, event_id=event[0]: self.attendee_event(row, event_id))
                    self.table.setCellWidget(row, 7, atten_list_button)

            except sqlite3.Error as err:
                QMessageBox.warning(None, 'Error', f"SQLite Error: {err}")
            finally:
                cursor.close()
                conn.close()

    def delete_event(self, row, event_id):
        reply = QMessageBox.question(self, 'Confirmation', 'Are you sure you want to delete this event?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            conn = connect_to_database()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute(
                        "DELETE FROM events WHERE event_id = ?", (event_id,))
                    conn.commit()
                    QMessageBox.information(
                        self, 'Success', 'Event deleted successfully.')
                    self.populate_events()
                except sqlite3.Error as err:
                    QMessageBox.warning(
                        self, 'Error', f"SQLite Error: {err}")
                finally:
                    cursor.close()
                    conn.close()

    def attendee_event(self, row, event_id):
        conn = connect_to_database()
        if conn:
            try:
                cursor = conn.cursor()

                # Fetch user details based on user IDs stored in users_event table
                cursor.execute(
                    "SELECT u.username, u.email FROM users u JOIN users_event ue ON u.user_id = ue.user_id WHERE ue.event_id = ?", (event_id,))
                attendees = cursor.fetchall()

                # Display user names and emails in a table
                dialog = QDialog(self)
                dialog.setWindowTitle('Attendee List')
                layout = QVBoxLayout()
                table = QTableWidget()
                table.setColumnCount(2)
                table.setHorizontalHeaderLabels(['User Name', 'User Email'])

                for idx, attendee in enumerate(attendees):
                    table.insertRow(idx)
                    table.setItem(idx, 0, QTableWidgetItem(str(attendee[0])))
                    table.setItem(idx, 1, QTableWidgetItem(str(attendee[1])))

                layout.addWidget(table)

                total_attendees_label = QLabel(
                    f"Total Attendees: {len(attendees)}")
                layout.addWidget(total_attendees_label)

                dialog.setLayout(layout)
                dialog.exec_()

            except sqlite3.Error as err:
                QMessageBox.warning(None, 'Error', f"SQLite Error: {err}")
            finally:
                cursor.close()
                conn.close()

    def edit_event(self, row, event_id):
        edit_dialog = QDialog(self)
        edit_dialog.setWindowTitle('Edit Event')
        edit_dialog.setGeometry(200, 200, 400, 200)
        layout = QVBoxLayout()
        title_input = QLineEdit()
        description_input = QLineEdit()
        event_date_input = QDateEdit()
        event_time_input = QTimeEdit()
        slots_input = QSpinBox()

        conn = connect_to_database()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT title, description, event_date, event_time, slots FROM events WHERE event_id = ?", (event_id,))
                event_details = cursor.fetchone()
                if event_details:
                    title_input.setText(event_details[0])
                    description_input.setText(event_details[1])
                    event_date = QDate.fromString(
                        event_details[2], 'yyyy-MM-dd')
                    event_date_input.setDate(event_date)
                    event_time = QTime.fromString(event_details[3], 'HH:mm:ss')
                    event_time_input.setTime(event_time)
                    slots_input.setValue(int(event_details[4]))
            except sqlite3.Error as err:
                QMessageBox.warning(edit_dialog, 'Error',
                                    f"SQLite Error: {err}")
            finally:
                cursor.close()
                conn.close()

        layout.addWidget(title_input)
        layout.addWidget(description_input)
        layout.addWidget(event_date_input)
        layout.addWidget(event_time_input)
        layout.addWidget(slots_input)

        save_button = QPushButton('Save')
        save_button.clicked.connect(lambda: self.save_event(edit_dialog, event_id, title_input.text(),
                                                            description_input.text(), event_date_input.date().toString('yyyy-MM-dd'),
                                                            event_time_input.time().toString('HH:mm:ss'), slots_input.value()))
        layout.addWidget(save_button)

        edit_dialog.setLayout(layout)
        edit_dialog.exec_()

    def save_event(self, dialog, event_id, title, description, event_date, event_time, slots):
        conn = connect_to_database()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("UPDATE events SET title = ?, description = ?, event_date  = ?, event_time  = ?, slots  = ?  WHERE event_id  = ?", (
                    title, description, event_date, event_time, slots,  event_id))
                conn.commit()

                event_date_qdate = QDate.fromString(event_date, 'yyyy-MM-dd')

                # Check if event_date is in the past
                if event_date_qdate < QDate.currentDate():
                    QMessageBox.warning(dialog, 'Error', 'Event date cannot be in the past.')
                else:
                    QMessageBox.information(
                    dialog, 'Success', 'Event updated successfully.')
                    self.populate_events()
            except sqlite3.Error as err:
                QMessageBox.warning(dialog, 'Error', f"SQLite Error: {err}")
            finally:
                cursor.close()
                conn.close()
                dialog.close()
