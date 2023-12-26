import sqlite3
from datetime import datetime
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
                pass REAL NOT NULL,
                funds REAL DEFAULT 0
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
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                category_id INTEGER,
                goal_id INTEGER,
                income_id INTEGER,
                amount REAL NOT NULL,
                description TEXT,
                date_spent DATE NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (category_id) REFERENCES categories(id)
                FOREIGN KEY (goal_id) REFERENCES goals(id),
                FOREIGN KEY (income_id) REFERENCES income_types(id),
                CHECK ((category_id IS NULL AND goal_id IS NOT NULL AND income_id IS NULL) OR (category_id IS NOT NULL AND goal_id IS NULL AND income_id IS NULL) OR (category_id IS NULL AND goal_id IS NULL AND income_id IS NOT NULL))
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
        cursor.execute("SELECT id FROM users WHERE user = ?", (user,))
        self.id = cursor.fetchone()[0]
        return self.id if pswd == password else -1

    def insert_category(self, name, budget_limit):
        valid = False 

        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM categories WHERE name = ? AND user_id = ?", (name, self.id,))
        if len(cursor.fetchall()) == 0:
            cursor.execute("INSERT INTO categories (user_id, name, budget) VALUES (?, ?, ?)", (self.id, name, budget_limit))
            valid = True
        self.conn.commit()

        return valid
    
    def insert_source(self, name):
        valid = False 

        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM income_types WHERE name = ? AND user_id = ?", (name, self.id,))
        if len(cursor.fetchall()) == 0:
            cursor.execute("INSERT INTO income_types (user_id, name) VALUES (?, ?)", (self.id, name,))
            valid = True
        self.conn.commit()

        return valid
    
    def get_category(self, name):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM categories WHERE name = ? AND user_id = ?", (name, self.id,))
        id = cursor.fetchone()[0]
        cursor.execute("SELECT budget FROM categories WHERE id = ?", (id,))
        budget = cursor.fetchone()[0]
        cursor.execute("SELECT spent FROM categories WHERE id = ?", (id,))
        spent = cursor.fetchone()[0]

        return [id, name, budget, spent]
    
    def get_income_type_id(self, name):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM income_types WHERE name = ? AND user_id = ?", (name, self.id,))
        return cursor.fetchone()[0]
    
    def add_expense(self, misc_id, amount, description="", goal=False):
        cursor = self.conn.cursor()

        if goal:

            cursor.execute("INSERT INTO expenses (user_id, goal_id, amount, description, date_spent) VALUES (?, ?, ?, ?, ?)", (self.id, misc_id, amount, description, datetime.now().date()))
            cursor.execute("UPDATE goals SET ")
        else:

            cursor.execute("INSERT INTO transactions (user_id, category_id, amount, description, date_spent) VALUES (?, ?, ?, ?, ?)", (self.id, misc_id, amount, description, datetime.now().date()))
            cursor.execute("UPDATE categories SET spent = spent + ? WHERE id = ?", (amount, misc_id,))
            cursor.execute("UPDATE users SET funds = funds - ? WHERE id = ?", (amount, self.id))
        
        self.conn.commit()

    def get_category_names(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM categories WHERE user_id = ?", (self.id,))
        results = cursor.fetchall()
        return [result[0] for result in results]

    def get_income_names(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM income_types WHERE user_id = ?", (self.id,))
        results = cursor.fetchall()
        return [result[0] for result in results]
    
    def get_funds(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT funds FROM users WHERE id = ?", (self.id,))
        return cursor.fetchone()[0]
    
    def add_income(self, income_id, amount, description):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO transactions (user_id, income_id, amount, description, date_spent) VALUES (?, ?, ?, ?, ?)", (self.id, income_id, amount, description, datetime.now().date()))
        cursor.execute("UPDATE users SET funds = funds + ? WHERE id = ?", (amount, self.id))
        self.conn.commit()

    def get_expenses(self, category_id):
        cursor = self.conn.cursor()

        cursor.execute('''
            SELECT date_spent, amount, description
            FROM transactions
            WHERE category_id = ? AND user_id = ?
        ''', (category_id, self.id,))

        expenses = cursor.fetchall()
        return expenses
    
    def get_transactions(self):
        cursor = self.conn.cursor()

        cursor.execute('''SELECT date_spent, amount, description, income_id FROM transactions  WHERE user_id = ?''', (self.id,))
        transactions = cursor.fetchall()

        cursor.execute("SELECT category_id, goal_id, income_id FROM transactions WHERE user_id = ?", (self.id,))
        ids = cursor.fetchall()

        types = []

        for id in ids:
            if id[0] is not None:
                cursor.execute("SELECT name FROm categories WHERE id = ?", (id[0],))
                types.append(cursor.fetchone())
            elif id[1] is not None:
                cursor.execute("SELECT name FROM goals WHERE id = ?", (id[1],))
                types.append(cursor.fetchone())
            else:
                cursor.execute("SELECT name FROM income_types WHERE id = ?", (id[2],))
                types.append(cursor.fetchone())

        mapped_transactions = []
        i = 0

        for transaction in transactions:
            income_id = transaction[3]
            if income_id is None:
                mapped_transactions.append([transaction[0], transaction[1] * -1, transaction[2], types[i]])
            else:
                mapped_transactions.append([transaction[0], transaction[1], transaction[2], types[i]])
            i = i + 1

        return mapped_transactions