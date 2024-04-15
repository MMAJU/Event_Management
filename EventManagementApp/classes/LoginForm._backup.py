import tkinter as tk
from tkinter import messagebox
import mysql.connector
from argon2 import PasswordHasher  # Import PasswordHasher from argon2
from argon2.exceptions import InvalidHashError  # Import InvalidHashError
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()


class LoginForm:
    def __init__(self, master):
        self.master = master
        master.title("Task Management System - Login ")
        self.create_widgets()

    def create_widgets(self):
        self.label_email = tk.Label(self.master, text="Email:")
        self.label_email.config(font=("Arial", 12))
        self.label_email.pack(pady=5)

        self.entry_email = tk.Entry(self.master)
        self.entry_email.pack(pady=5)

        self.label_password = tk.Label(self.master, text="Password:")
        self.label_password.config(font=("Arial", 12))
        self.label_password.pack(pady=5)

        self.entry_password = tk.Entry(self.master, show="*")
        self.entry_password.pack(pady=5)

        self.button_signin = tk.Button(
            self.master, text="Sign In", command=self.signin_user)
        self.button_signin.pack(pady=10)

    def signin_user(self):
        email = self.entry_email.get()
        password = self.entry_password.get()

        try:
            # Establish database connection
            db_connection = mysql.connector.connect(
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_DATABASE")
            )
            cursor = db_connection.cursor()

            # Retrieve user data from the database
            cursor.execute(
                "SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
            user = cursor.fetchone()

            if user:
                # Verify the password using Argon2
                # ph = PasswordHasher()
                try:
                    if ph.verify(user[2], password):
                        messagebox.showinfo(
                            "Sign In Successful", "You have successfully signed in!")
                    else:
                        messagebox.showerror(
                            "Error", "Invalid email or password.")
                except InvalidHashError:
                    messagebox.showerror("Error", "Invalid hashed password.")
            else:
                messagebox.showerror("Error", "User not found.")

            # Close cursor and database connection
            cursor.close()
            db_connection.close()

        except mysql.connector.Error as err:
            # Display an error message if sign-in fails
            messagebox.showerror("Error", f"Sign in failed: {err}")


def main():
    root = tk.Tk()
    app = LoginForm(root)
    root.mainloop()


if __name__ == "__main__":
    main()
