import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QMessageBox
from PyQt5.QtGui import QIcon
from classes.RegistrationForm import RegistrationForm
from classes.LoginForm import LoginForm
from classes.CreateEvent import CreateEventForm
from classes.SearchTaskForm import SearchTaskForm
from classes.ViewAllEvent import ViewEventsForm
from classes.ViewUserEvent import ViewUserEventsForm
from classes.UserViewTasksForm import UserViewTasksForm
import sqlite3
import os


def create_database():
    conn = sqlite3.connect('event_management.db')
    cursor = conn.cursor()

    # Create tables if they don't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        email TEXT NOT NULL UNIQUE,
        password TEXT,
        user_role INTEGER DEFAULT 2 NOT NULL
        )
    ''')

    # Check if admin user already exists
    cursor.execute('SELECT * FROM users WHERE user_role = 1 LIMIT 1')
    admin_user = cursor.fetchone()
    if not admin_user:
        cursor.execute('''
            INSERT INTO users (username, email, password, user_role) VALUES (?, ?, ?,?)
        ''', ('Izuzu','ff@gmail.com', '123456', 1))  # Assuming admin user_role is 1
        print("Admin user created successfully!")

    # Create events table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        event_date DATE,
        event_time TEXT,
        slots INTEGER
        )
    ''')
    # Create users_event table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users_event (
        user_event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        event_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users (user_id),
        FOREIGN KEY (event_id) REFERENCES events (event_id)
        )
    ''')

    conn.commit()
    conn.close()


class EventManagementGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Event Management System')
        self.setGeometry(100, 100, 600, 400)
        self.setWindowIcon(QIcon('icon.png'))

        self.login_action = QAction('Login', self)
        self.login_action.triggered.connect(self.show_login_form)
        self.register_action = QAction('Register', self)
        self.register_action.triggered.connect(self.show_registration_form)
        self.create_event_action = QAction('Create Event', self)
        self.create_event_action.triggered.connect(self.create_event)
        self.view_event_action = QAction('View Event', self)
        self.view_event_action.triggered.connect(self.view_task)
        self.search_event_action = QAction('Search Event', self)
        self.search_event_action.triggered.connect(self.search_task)
        self.update_task_action = QAction('Register for Event', self)
        self.update_task_action.triggered.connect(self.update_task)

        self.view_user_event_action = QAction('View All Event', self)
        self.view_user_event_action.triggered.connect(self.view_user_event)

        self.taskee_task_action = QAction('View My Event', self)
        self.taskee_task_action.triggered.connect(self.taskee_task)

        self.menubar = self.menuBar()
        self.file_menu = self.menubar.addMenu('Menu')

        self.show_login_form()

    def show_login_form(self):
        print("Showing login form")
        login_dialog = LoginForm()
        if login_dialog.exec_() == LoginForm.Accepted:
            username = login_dialog.username_input.text()
            password = login_dialog.password_input.text()

            print("Username:", username)
            print("Password:", password)

            try:
                conn = sqlite3.connect('event_management.db')
                if conn:
                    print("Connected to database successfully!")
                else:
                    print("Failed to connect to database!")

                cursor = conn.cursor()
                cursor.execute(
                    "SELECT user_id, user_role FROM users WHERE email=? AND password=?", (username, password))
                

                row = cursor.fetchone()
                print("Row retrieved from database:", row)
                if row:
                    self.user_id, user_role = row
                    self.update_menu_visibility(user_role)
                else:
                    QMessageBox.warning(
                        self, 'Error', 'Invalid username or password')
                cursor.close()
                conn.close()
            except sqlite3.Error as err:
                QMessageBox.warning(self, 'Error', f"SQLite Error: {err}")

    def show_registration_form(self):
        registration_dialog = RegistrationForm()
        if registration_dialog.exec_() == RegistrationForm.Accepted:
            username = registration_dialog.username_input.text()
            password = registration_dialog.password_input.text()

            try:
                conn = sqlite3.connect('event_management.db')
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (email, password) VALUES (?, ?)", (username, password))
                conn.commit()
                QMessageBox.information(
                    self, 'Success', 'User registered successfully!')
                cursor.close()
                conn.close()
            except sqlite3.Error as err:
                QMessageBox.warning(self, 'Error', f"SQLite Error: {err}")

    def update_menu_visibility(self, user_role):
        self.file_menu.clear()

        logout_action = QAction('Logout', self)
        logout_action.triggered.connect(self.logout)
        self.file_menu.addAction(logout_action)

        if user_role == 1:
            self.file_menu.addAction(self.register_action)
            self.file_menu.addAction(self.create_event_action)
            self.file_menu.addAction(self.view_event_action)
            self.file_menu.addAction(self.search_event_action)
        elif user_role == 2:
            self.file_menu.addAction(self.view_user_event_action)
            #self.file_menu.addAction(self.taskee_task_action)

    def logout(self):
        self.user_id = None
        self.show_login_form()

    def create_event(self):
        create_event_form = CreateEventForm()
        create_event_form.exec_()

    def view_task(self):
        view_event_form = ViewEventsForm()
        view_event_form.exec_()

    def view_user_event(self):
        view_user_event_form = ViewUserEventsForm(user_id=self.user_id)
        view_user_event_form.exec_()

    def search_task(self):
        search_task_form = SearchTaskForm()
        search_task_form.exec_()

    def update_task(self):
        QMessageBox.information(
            self, 'Update Task', 'Update Task functionality will be implemented here')

    def taskee_task(self):
        user_view_task_form = UserViewTasksForm(user_id=self.user_id)
        user_view_task_form.exec_()


if __name__ == '__main__':
    create_database()
    app = QApplication(sys.argv)
    window = EventManagementGUI()
    window.show()
    sys.exit(app.exec_())
