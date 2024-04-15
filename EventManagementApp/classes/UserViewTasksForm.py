import sys
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QComboBox, QDateEdit, QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QHBoxLayout, QLabel
from PyQt5.QtGui import QFont
import sqlite3
import os


def connect_to_database():
    try:
        conn = sqlite3.connect('event_management.db')
        return conn
    except sqlite3.Error as err:
        QMessageBox.warning(self, 'Error', f"SQLite Error: {err}")
        return None


class UserViewTasksForm(QDialog):
    def __init__(self, user_id):
        super().__init__()
        self.setWindowTitle('User View Tasks')
        self.setGeometry(100, 100, 600, 400)
        self.user_id = user_id  # Store the user ID

        layout = QVBoxLayout()

        search_layout = QHBoxLayout()
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        search_layout.addWidget(self.date_edit)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText('Task Title')
        search_layout.addWidget(self.title_input)

        self.status_input = QLineEdit()
        self.status_input.setPlaceholderText('Task Status')
        search_layout.addWidget(self.status_input)

        search_button = QPushButton('Search')
        search_button.clicked.connect(self.search_tasks)
        search_layout.addWidget(search_button)

        layout.addLayout(search_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)  # Update column count
        self.table.setHorizontalHeaderLabels(
            ['Title', 'Description', 'Assigned User', 'Status', 'Comment', 'Edit'])  # Add status and comment columns
        layout.addWidget(self.table)

        self.setLayout(layout)

        self.populate_tasks()

    def populate_tasks(self):
        conn = connect_to_database()
        if conn:
            try:
                cursor = conn.cursor()
                if self.user_id:
                    cursor.execute(
                        "SELECT t.task_id, t.title, t.description, u.username, t.status, t.comment FROM tasks t LEFT JOIN users u ON t.assigned_to = u.user_id WHERE t.assigned_to = ?", (self.user_id,))
                else:
                    cursor.execute(
                        "SELECT t.task_id, t.title, t.description, u.username, t.status, t.comment FROM tasks t LEFT JOIN users u ON t.assigned_to = u.user_id")
                tasks = cursor.fetchall()
                self.table.setRowCount(len(tasks))
                for row, task in enumerate(tasks):
                    for col, data in enumerate(task[1:]):
                        item = QTableWidgetItem(str(data))
                        self.table.setItem(row, col, item)
                    edit_button = QPushButton('Edit')
                    edit_button.clicked.connect(
                        lambda checked, row=row, task_id=task[0]: self.edit_task(row, task_id))
                    self.table.setCellWidget(
                        row, 5, edit_button)  # Update column index
            except sqlite3.Error as err:
                QMessageBox.warning(self, 'Error', f"SQLite Error: {err}")
            finally:
                cursor.close()
                conn.close()

    def search_tasks(self):
        selected_date = self.date_edit.date().toString('yyyy-MM-dd')
        task_title = self.title_input.text()
        task_status = self.status_input.text()

        conn = connect_to_database()
        if conn:
            try:
                cursor = conn.cursor()
                query = "SELECT t.task_id, t.title, t.description, u.username, t.status, t.comment FROM tasks t LEFT JOIN users u ON t.assigned_to = u.user_id WHERE t.assigned_to = ?"
                params = [self.user_id]

                if selected_date:
                    query += " AND DATE(t.task_date) = ?"
                    params.append(selected_date)

                if task_title:
                    query += " AND t.title LIKE ?"
                    params.append(f'%{task_title}%')
                if task_status:
                    query += " AND t.status LIKE ?"
                    params.append(f'%{task_status}%')

                cursor.execute(query, params)
                tasks = cursor.fetchall()
                self.display_tasks(tasks)
            except sqlite3.Error as err:
                QMessageBox.warning(self, 'Error', f"SQLite Error: {err}")
            finally:
                cursor.close()
                conn.close()

    def display_tasks(self, tasks):
        self.table.setRowCount(0)
        for row, task in enumerate(tasks):
            self.table.insertRow(row)
            for col, data in enumerate(task[1:]):
                self.table.setItem(row, col, QTableWidgetItem(str(data)))
            edit_button = QPushButton('Edit')
            edit_button.clicked.connect(
                lambda checked, row=row, task_id=task[0]: self.edit_task(row, task_id))
            self.table.setCellWidget(
                row, 5, edit_button)  # Update column index

    def edit_task(self, row, task_id):
        edit_dialog = QDialog(self)
        edit_dialog.setWindowTitle('Edit Task')
        edit_dialog.setGeometry(200, 200, 400, 200)

        layout = QVBoxLayout()

        title_input = QLineEdit()
        description_input = QLineEdit()
        assigned_user_input = QLineEdit()  # Define assigned_user_input here
        status_input = QComboBox()  # Add status input field
        # Example status options
        status_input.addItems(["Ongoing", "Completed", "Pending"])
        comment_input = QLineEdit()  # Add comment input field

        # Fetch task details from the database and populate the input fields
        conn = connect_to_database()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT title, description, assigned_to, status, comment FROM tasks WHERE task_id = ?", (task_id,))
                task_details = cursor.fetchone()
                if task_details:
                    title_input.setText(task_details[0])
                    description_input.setText(task_details[1])
                    # You may need to fetch user name here instead of ID
                    assigned_user_input.setText(str(task_details[2]))
                    status_input.setCurrentText(
                        task_details[3])  # Set current status
                    comment_input.setText(task_details[4])  # Set comment
            except sqlite3.Error as err:
                QMessageBox.warning(edit_dialog, 'Error',
                                    f"SQLite Error: {err}")
            finally:
                cursor.close()
                conn.close()

        layout.addWidget(title_input)
        layout.addWidget(description_input)
        layout.addWidget(assigned_user_input)
        layout.addWidget(status_input)
        layout.addWidget(comment_input)

        save_button = QPushButton('Save')
        save_button.clicked.connect(lambda: self.save_task(edit_dialog, task_id, title_input.text(
        ), description_input.text(), assigned_user_input.text(), status_input.currentText(), comment_input.text()))
        layout.addWidget(save_button)

        edit_dialog.setLayout(layout)
        edit_dialog.exec_()

    def save_task(self, dialog, task_id, title, description, assigned_user, status, comment):
        # Update task details in the database
        conn = connect_to_database()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("UPDATE tasks SET title = ?, description = ?, assigned_to = ?, status = ?, comment = ? WHERE task_id = ?", (
                    title, description, assigned_user, status, comment, task_id))
                conn.commit()
                QMessageBox.information(
                    dialog, 'Success', 'Task updated successfully.')
                self.populate_tasks()  # Refresh task list
            except sqlite3.Error as err:
                QMessageBox.warning(dialog, 'Error', f"SQLite Error: {err}")
            finally:
                cursor.close()
                conn.close()
                dialog.close()



