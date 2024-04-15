from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QMessageBox
import sqlite3
import re  # Import the re module for regular expressions


class RegistrationForm(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('User Registration')
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Username')
        layout.addWidget(self.username_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText('Email')
        layout.addWidget(self.email_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Password')
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        register_button = QPushButton('Register')
        register_button.clicked.connect(self.register_user)
        layout.addWidget(register_button)

        self.setLayout(layout)

    def register_user(self):
        username = self.username_input.text()
        email = self.email_input.text()
        password = self.password_input.text()

        if not username.strip() or not email or not password:
            QMessageBox.warning(self, "Error", "Please fill in all fields.")
            return

        # Validate email format using regex
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            QMessageBox.warning(self, "Error", "Invalid email format.")
            return

        try:
            # Connect to SQLite database
            conn = sqlite3.connect('event_management.db')
            cursor = conn.cursor()

            # Check if username or email already exists
            cursor.execute(
                "SELECT * FROM users WHERE username=? OR email=?", (username, email))
            existing_user = cursor.fetchone()
            if existing_user:
                QMessageBox.warning(
                    self, 'Error', 'Username or email already exists.')
            else:
                # Insert new user into the database
                cursor.execute("INSERT INTO users (username, email, password, user_role) VALUES (?, ?, ?, ?)",
                               (username, email, password, 2))  # Assuming user_role 2 for regular users
                conn.commit()
                QMessageBox.information(
                    self, 'Registration', 'User registered successfully!')
                self.accept()  # Close the dialog after successful registration

            cursor.close()
            conn.close()
        except sqlite3.Error as err:
            print(f"SQLite Error: {err}")
