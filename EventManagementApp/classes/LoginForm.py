import os
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QMessageBox
import sqlite3


class LoginForm(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Login')
        self.setGeometry(100, 100, 300, 150)

        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Email')
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Password')
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        login_button = QPushButton('Login')
        login_button.clicked.connect(self.login)
        layout.addWidget(login_button)

        self.setLayout(layout)

    def login(self):
        email = self.username_input.text()
        password = self.password_input.text()

        # Connect to SQLite database
        conn = sqlite3.connect('event_management.db')
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            QMessageBox.information(self, 'Login', 'Login successful!')
            self.accept()  # Close the dialog if login successful
        else:
            QMessageBox.warning(
                self, 'Login', 'Invalid Login email or password')
