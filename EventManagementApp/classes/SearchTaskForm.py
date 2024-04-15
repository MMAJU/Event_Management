import sys
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QComboBox, QDateEdit, QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QHBoxLayout, QLabel
from PyQt5.QtGui import QFont
import mysql.connector
from dotenv import load_dotenv
import os


def connect_to_database():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_DATABASE")
        )
        return conn
    except mysql.connector.Error as err:
        QMessageBox.warning(self, 'Error', f"MySQL Error: {err}")
        return None


class SearchTaskForm(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Search Task')
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        search_layout = QHBoxLayout()

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        search_layout.addWidget(self.date_edit)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('Task Name')
        search_layout.addWidget(self.name_input)

        self.user_input = QComboBox()  # Use QComboBox for dropdown
        self.populate_users()  # Fetch users and populate the dropdown
        search_layout.addWidget(self.user_input)

        search_button = QPushButton('Search')
        search_button.clicked.connect(self.search_task)
        search_layout.addWidget(search_button)

        layout.addLayout(search_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(['Title', 'Description'])
        layout.addWidget(self.table)

        self.setLayout(layout)

    def populate_users(self):
        # Fetch users from the database and populate the dropdown
        conn = connect_to_database()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id, username FROM users")
                users = cursor.fetchall()
                for user in users:
                    user_id, user_name = user
                    self.user_input.addItem(user_name, userData=user_id)
            except mysql.connector.Error as err:
                QMessageBox.warning(self, 'Error', f"MySQL Error: {err}")
            finally:
                cursor.close()
                conn.close()

    def search_task(self):
        selected_date = self.date_edit.date().toString('yyyy-MM-dd')
        task_name = self.name_input.text()
        assigned_user = self.user_input.currentData()

        conn = connect_to_database()
        if conn:
            try:
                cursor = conn.cursor()

                # Construct the SQL query based on the user's input
                query = "SELECT t.title, t.description FROM tasks t JOIN users u ON t.assigned_to = u.user_id WHERE 1=1"
                params = []

                if selected_date:
                    query += " AND DATE(t.task_date) = %s"
                    params.append(selected_date)
                if task_name:
                    query += " AND t.title LIKE %s"
                    params.append(f'%{task_name}%')
                if assigned_user:
                    query += " AND u.username LIKE %s"
                    params.append(f'%{assigned_user}%')

                cursor.execute(query, tuple(params))
                tasks = cursor.fetchall()
                if tasks:
                    self.display_results(tasks)
                else:
                    QMessageBox.information(
                        self, 'Search Results', 'No tasks found.')
            except mysql.connector.Error as err:
                QMessageBox.warning(self, 'Error', f"MySQL Error: {err}")
            finally:
                cursor.close()
                conn.close()

    def display_results(self, tasks):
        self.table.setRowCount(0)
        for row, task in enumerate(tasks):
            self.table.insertRow(row)
            for col, data in enumerate(task):
                self.table.setItem(row, col, QTableWidgetItem(str(data)))
