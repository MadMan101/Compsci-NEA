import sqlite3
from categories.category import Category

class BudgetDatabase:
    def __init__(self, db_file="budget_tracker.db"):
        self.conn = sqlite3.connect(db_file)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                budget_limit REAL NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                amount REAL NOT NULL,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')

        self.conn.commit()

    def insert_category(self, name, budget_limit):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO categories (name, budget_limit) VALUES (?, ?)", (name, budget_limit))
        self.conn.commit()

    def get_categories(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM categories")
        return cursor.fetchall()

    def get_category_names(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM categories")
        return cursor.fetchall()

    def insert_expense(self, category_id, amount):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO expenses (category_id, amount) VALUES (?, ?)", (category_id, amount))
        self.conn.commit()

    def get_expenses(self, category_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT amount FROM expenses WHERE category_id = ?", (category_id,))
        return cursor.fetchall()