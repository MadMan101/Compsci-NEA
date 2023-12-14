import sqlite3
from categories.category import Category

class BudgetDatabase:
    def __init__(self, db_file="budget_tracker.db"):
        self.conn = sqlite3.connect(db_file)
        self.create_tables()
        self.id = -1

    def create_tables(self):
        cursor = self.conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL,
                pass REAL NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT NOT NULL,
                budget REAL NOT NULL,
                spent REAL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS income_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS income (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                source TEXT NOT NULL,
                amount REAL NOT NULL,
                date DATE NOT NULL,
                income_type_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (income_type_id) REFERENCES income_types(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                goal_name TEXT NOT NULL,
                target_amount REAL NOT NULL,
                current_amount REAL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                category_id INTEGER,
                amount REAL NOT NULL,
                description TEXT,
                date_spent DATE NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        ''')

        self.conn.commit()

    #login sys
    def register_user(self, user, password):
        valid = False
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT pass FROM users WHERE user = ?", (user,))
        if len(cursor.fetchall()) == 0:
            cursor.execute("INSERT INTO users (user, pass) VALUES (?, ?)", (user, password))
            valid = True
        self.conn.commit()

        return valid

    def login(self, user, password):
        cursor = self.conn.cursor()
        cursor.execute("SELECT pass FROM users WHERE user = ?", (user,))
        pswd = cursor.fetchone()[0]
        cursor.execute("SELECT id FROM users WHERE user = ?", (user))
        self.id = cursor.fetchone()[0]
        return self.id if pswd == password else -1

    def insert_category(self, name, budget_limit):
        valid = False 

        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM categories WHERE name = ?", (name,))
        if len(cursor.fetchall()) == 0:
            cursor.execute("INSERT INTO categories (user_id, name, budget) VALUES (?, ?, ?)", (self.id, name, budget_limit))
            valid = True
        self.conn.commit()

        return valid
    
    def get_category(self, name):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM categories WHERE name = ?", (name,))
        id = cursor.fetchone()[0]
        cursor.execute("SELECT budget FROM categories WHERE id = ?", (id,))
        budget = cursor.fetchone()[0]
        cursor.execute("SELECT spent FROM categories WHERE id = ?", (id,))
        spent = cursor.fetchone()[0]

        return [id, name, budget, spent]
    
    def get_category_names(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM categories WHERE user_id = ?", (self.id,))
        return cursor.fetchall()

    def get_income_names(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM income_types WHERE user_id = ?", (self.id,))
        return cursor.fetchall()

    def get_id(self, name):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM categories WHERE name = ?", (name))
        return cursor.fetchall()
    
    def get_budget(self, id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT budget_limit FROM categories WHERE id = ?", (id))
        return cursor.fetchall()

    def insert_expense(self, category_id, amount):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO expenses (category_id, amount) VALUES (?, ?)", (category_id, amount))
        self.conn.commit()

    def get_expenses(self, category_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT amount FROM expenses WHERE category_id = ?", (category_id,))
        return cursor.fetchall()