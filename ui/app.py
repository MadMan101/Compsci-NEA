import tkinter as tk
from tkinter import ttk, messagebox
from categories.category import Category
from expenses.expense import Expense
from databases.database import BudgetDatabase
import configparser

class BudgetTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Budget Tracker App")

        self.db = BudgetDatabase()

        # Load saved credentials
        saved_credentials = self.load_saved_credentials()

        # Create login window
        self.login_window = tk.Toplevel(self.root)
        self.login_window.title("Login")
        self.login_window.geometry("400x250")
        self.login_window.attributes("-topmost", True)

        # Login variables
        self.username_var = saved_credentials.get("username", "")

        # Login components
        ttk.Label(self.login_window, text="Username:").pack(pady=5)
        self.user_entry = ttk.Entry(self.login_window)
        self.user_entry.pack(pady=5)

        ttk.Label(self.login_window, text="Password:").pack(pady=5)
        self.pass_entry = ttk.Entry(self.login_window, show="*")
        self.pass_entry.pack(pady=5)

        # Create a frame to contain the login buttons
        button_frame = ttk.Frame(self.login_window)
        button_frame.pack(pady=10)

        # Login and Login as User buttons
        ttk.Button(button_frame, text="Login", command=self.login).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Login as " + self.username_var, command=self.login_as_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.login_window, text="Register", command=self.register).pack(pady=10)

    def login(self):
        username = self.user_entry.get()
        password = hash(self.pass_entry.get())

        config = configparser.ConfigParser()
        config["Credentials"] = {"username": username, "password": password}
        with open("credentials.ini", "w") as configfile:
            config.write(configfile)

        if self.db.login(username, password,):
            self.login_window.destroy()  # Close login window
            self.initialise_app()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def logout(self):
        # Load saved credentials
        saved_credentials = self.load_saved_credentials()

        self.root.destroy()

        root = tk.Tk()
        self.__init__(root)
        root.mainloop()


    def login_as_user(self):
        saved_credentials = self.load_saved_credentials()

        username = saved_credentials.get("username", "")
        password = saved_credentials.get("password", "")

        if self.db.login(username, password,):
            self.login_window.destroy()  # Close login window
            self.initialise_app()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def load_saved_credentials(self):
        import os

        # Load saved credentials from a configuration file
        config = configparser.ConfigParser()
        
        if os.path.exists("credentials.ini"):
            try:
                config.read("credentials.ini")
                credentials = dict(config["Credentials"])
                
                return credentials
            except configparser.Error as e:
                print("Error loading credentials:", e)
                return {}
        else:
            print("Credentials file does not exist. Creating a new one.")
            # Create a new credentials file
            with open("credentials.ini", "w") as configfile:
                config.add_section("Credentials")
                config.set("Credentials", "username", "")
                config.set("Credentials", "password", "")
                config.write(configfile)

            return {}

    def register(self):
        username = self.user_entry.get()
        password = hash(self.pass_entry.get())

        if username:
            if self.db.register_user(username, password) == False:
                messagebox.showwarning("Register Error", "This username is taken, please choose another")
            else:
                messagebox.showinfo("Registered", "You have successfuly registered")

    def initialise_app(self):
        # Create GUI components
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        self.init_dashboard()

        self.init_categories()

        self.init_income()

        self.show_transactions()

    def init_categories(self):
         # Categories Page
        categories_page = ttk.Frame(self.notebook)
        self.notebook.add(categories_page, text="Categories")

         # Category Info
        self.category_combobox = ttk.Combobox(categories_page, values=self.db.get_category_names(), state="readonly", width=20)
        self.category_combobox.grid(row=0, column=0, padx=10, pady=10)
        self.category_combobox["values"] = self.db.get_category_names()
        self.category_combobox.bind("<<ComboboxSelected>>", self.on_combobox_selected)

        ttk.Label(categories_page, text="Category Info").grid(row=1, column=0, pady=5, columnspan=2)

        ttk.Label(categories_page, text="Budget Limit:").grid(row=2, column=0, pady=5)
        ttk.Label(categories_page, text="Total Expenses:").grid(row=2, column=1, pady=5)
        ttk.Label(categories_page, text="Remaining:").grid(row=2, column=2, pady=5)

        self.category_info_labels = [
            ttk.Label(categories_page, text=""),
            ttk.Label(categories_page, text=""),
            ttk.Label(categories_page, text="")
        ]

        for i, label in enumerate(self.category_info_labels):
            label.grid(row=3, column=i, pady=5)

        # Add New Category
        ttk.Label(categories_page, text="Add New Category").grid(row=4, column=0, pady=5, columnspan=2)

        ttk.Label(categories_page, text="Name:").grid(row=5, column=0, pady=5)
        self.new_category_name_entry = ttk.Entry(categories_page, width=15)
        self.new_category_name_entry.grid(row=5, column=1, padx=10, pady=5)

        ttk.Label(categories_page, text="Budget Limit:").grid(row=5, column=2, pady=5)
        self.new_budget_limit_entry = ttk.Entry(categories_page, width=10)
        self.new_budget_limit_entry.grid(row=5, column=3, padx=10, pady=5)

        ttk.Button(categories_page, text="Add Category", command=self.add_category).grid(row=5, column=4, padx=10, pady=5)

        # Add Income
        ttk.Label(categories_page, text="Add Expense").grid(row=6, column=0, pady=5, columnspan=2)

        ttk.Label(categories_page, text="Description (optional) :").grid(row=7, column=0, pady=5)
        self.category_name_entry = ttk.Entry(categories_page, width=15)
        self.category_name_entry.grid(row=7, column=1, padx=10, pady=5)

        ttk.Label(categories_page, text="Amount:").grid(row=7, column=2, pady=5)
        self.category_expense_entry = ttk.Entry(categories_page, width=15)
        self.category_expense_entry.grid(row=7, column=3, padx=10, pady=5)

        ttk.Button(categories_page, text="Add Expense", command=self.add_expense).grid(row=7, column=4, padx=10, pady=5)

        # Expenses Table (Simplified Representation)
        ttk.Label(categories_page, text="Expenses Table").grid(row=8, column=0, pady=10, columnspan=6)

        self.expenses_table = ttk.Treeview(categories_page, columns=("Date", "Amount", "Description"), show="headings")
        self.expenses_table.heading("Date", text="Date")
        self.expenses_table.heading("Amount", text="Amount")
        self.expenses_table.heading("Description", text="Description")
        self.expenses_table.grid(row=9, column=0, columnspan=6, padx=10, pady=5)

    def init_dashboard(self):
        # Dashboard Page
        dashboard_page = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_page, text="Dashboard")
        
        # Logout button
        logout_button = ttk.Button(dashboard_page, text="Logout", command=self.logout)
        logout_button.pack(side=tk.TOP, anchor=tk.NE, padx=10, pady=5)

        ttk.Label(dashboard_page, text="Pie Chart of Categories").pack(pady=10)

        # Dashboard Info
        ttk.Label(dashboard_page, text="Total Money Available:").pack(pady=5)
        self.funds_text = ttk.Label(dashboard_page, text="asd")
        self.funds_text.pack(pady=5)
        ttk.Label(dashboard_page, text="Total Money Assigned:").pack(pady=5)

        self.show_dashboard_info()

        # TODO: Add Pie Chart widget (you may use Matplotlib for this)

        # TODO: Display the total money available and total money assigned

        self.transaction_table = ttk.Treeview(dashboard_page, columns=("Date", "Categories", "Amount", "Description"), show="headings")
        self.transaction_table.heading("Date", text="Date")
        self.transaction_table.heading("Categories", text="Categories")
        self.transaction_table.heading("Amount", text="Amount")
        self.transaction_table.heading("Description", text="Description")
        self.transaction_table.pack(pady=10)

    def init_income(self):
         # Categories Page
        income_page = ttk.Frame(self.notebook)
        self.notebook.add(income_page, text="Income")

         # Category Info
        self.income_combobox = ttk.Combobox(income_page, values=self.db.get_income_names(), state="readonly", width=20)
        self.income_combobox.grid(row=0, column=0, padx=10, pady=10)
        self.income_combobox["values"] = self.db.get_income_names()
        self.income_combobox.bind("<<ComboboxSelected>>", self.on_combobox_income_selected)

        ttk.Label(income_page, text="Category Info").grid(row=1, column=0, pady=5, columnspan=2)

        ttk.Label(income_page, text="Income:").grid(row=2, column=0, pady=5)
        ttk.Label(income_page, text="Total Income:").grid(row=2, column=1, pady=5)
        ttk.Label(income_page, text="Percentage of total income:").grid(row=2, column=2, pady=5)

        self.income_info_labels = [
            ttk.Label(income_page, text=""),
            ttk.Label(income_page, text=""),
            ttk.Label(income_page, text="")
        ]

        for i, label in enumerate(self.income_info_labels):
            label.grid(row=3, column=i, pady=5)

        # Add New Category
        ttk.Label(income_page, text="Add New Income Source").grid(row=4, column=0, pady=5, columnspan=2)

        ttk.Label(income_page, text="Name:").grid(row=5, column=0, pady=5)
        self.new_income_name_entry = ttk.Entry(income_page, width=15)
        self.new_income_name_entry.grid(row=5, column=1, padx=10, pady=5)

        ttk.Button(income_page, text="Add Source", command=self.add_source).grid(row=5, column=2, padx=10, pady=5)

        # Add Income
        ttk.Label(income_page, text="Add Income").grid(row=6, column=0, pady=5, columnspan=2)

        ttk.Label(income_page, text="Description (optional) :").grid(row=7, column=0, pady=5)
        self.income_name_entry = ttk.Entry(income_page, width=15)
        self.income_name_entry.grid(row=7, column=1, padx=10, pady=5)

        ttk.Label(income_page, text="Amount:").grid(row=7, column=2, pady=5)
        self.income_amount_entry = ttk.Entry(income_page, width=15)
        self.income_amount_entry.grid(row=7, column=3, padx=10, pady=5)

        ttk.Button(income_page, text="Add Income", command=self.add_income).grid(row=7, column=4, padx=10, pady=5)

    def see_all_expenses(self):
        # TODO: Implement displaying all expenses in the expenses_table
        pass

    def add_category(self):
        new_category_name = self.new_category_name_entry.get()
        new_budget_limit = self.new_budget_limit_entry.get()

        if new_category_name and new_budget_limit:
            if self.db.insert_category(new_category_name, new_budget_limit) == False:
                messagebox.showerror("Category Error", "This category name already exists please choose another")

            # Update Combobox
            self.category_combobox["values"] = self.db.get_category_names()

            # Clear entry fields
            self.new_category_name_entry.delete(0, tk.END)
            self.new_budget_limit_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Input Error", "Please enter category name and budget limit.")

    def add_income(self):
        selected_category_index = self.income_combobox.current()
        income_name = self.income_name_entry.get()
        income_amount = self.income_amount_entry.get()

        income_id = self.db.get_income_type_id(self.income_combobox.get())

        if selected_category_index != -1:
            if income_amount:
                self.db.add_income(income_id, income_amount, income_name)

                messagebox.showinfo("Income Added", f"Income of {income_amount} added to {self.income_combobox.get()}")

                self.income_name_entry.delete(0, tk.END)
                self.income_amount_entry.delete(0, tk.END)
                
                self.show_dashboard_info()
                self.show_transactions()
            else:
                messagebox.showwarning("Input Error", "Please enter income amount")
        else:
            messagebox.showwarning("Selection Error", "Please select a category")

    def add_source(self): 
        new_source_name = self.new_income_name_entry.get()

        if new_source_name:
            if self.db.insert_source(new_source_name) == False:
                messagebox.showerror("Source Error", "This income type name already exists please choose another")
            
            self.income_combobox["values"] = self.db.get_income_names()

            self.new_income_name_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Input Error", "Please enter an income type name.")

    def add_expense(self):
        selected_category_index = self.category_combobox.current()
        selected_category = self.db.get_category(self.category_combobox.get())

        if selected_category_index != -1:
            expense_amount = self.category_expense_entry.get()
            expense_description = self.category_name_entry.get()

            if expense_amount:
                self.db.add_expense(selected_category[0], expense_amount, expense_description)
                messagebox.showinfo("Expense Added", f"Expense of {expense_amount} added to {selected_category[1]}")
                self.category_expense_entry.delete(0, tk.END)
                self.show_category_info(selected_category_index)
                # TODO: Update expenses_table
            else:
                messagebox.showwarning("Input Error", "Please enter expense amount.")
        else:
            messagebox.showwarning("Selection Error", "Please select a category.")

        self.show_dashboard_info()
        self.show_transactions()

    def show_category_info(self, selected_category_index):
        if selected_category_index != -1:
            selected_category = self.db.get_category(self.category_combobox.get())

            # Update Category Info Labels
            self.category_info_labels[0]["text"] = f"{selected_category[2]}"
            self.category_info_labels[1]["text"] = f"{selected_category[3]}"
            self.category_info_labels[2]["text"] = f"{selected_category[2] - selected_category[3]}"
        else:
            messagebox.showwarning("Selection Error", "Please select a category.")

    def show_income_info(self, selected_category_index):
        print(0)

    def show_dashboard_info(self):
        self.funds_text["text"] = self.db.get_funds()
    
    def on_combobox_selected(self, event):
        self.show_category_info(self.category_combobox.current())

        self.show_expenses(self.db.get_category(self.category_combobox.get())[0])

    def on_combobox_income_selected(self, event):
        self.show_income_info(self.income_combobox.current())

    def show_expenses(self, category_id):
        # Clear existing entries in the expenses_table
        for item in self.expenses_table.get_children():
            self.expenses_table.delete(item)

        # Fetch expenses for the selected category from the database
        expenses = self.db.get_expenses(category_id)

        # Insert expenses into the expenses_table
        for expense in expenses:
            self.expenses_table.insert("", 0, values=(expense[0], expense[1], expense[2],))

    def show_transactions(self):
        # Clear existing entries in the expenses_table
        for item in self.transaction_table.get_children():
            self.transaction_table.delete(item)

        # Fetch expenses for the selected category from the database
        expenses = self.db.get_transactions()

        # Insert expenses into the expenses_table
        for expense in expenses:
            self.transaction_table.insert("", 0, values=(expense[0], expense[3], expense[1], expense[2]))

    def hash(input_string):
        hash_value = 5381

        for char in input_string:
            hash_value = (hash_value * 33) ^ ord(char)

        # Apply additional mixing steps (XOR and bit shifting)
        hash_value = (hash_value ^ (hash_value >> 15)) * 2654435761 & 0xFFFFFFFF
        hash_value = (hash_value ^ (hash_value >> 13)) * 2654435761 & 0xFFFFFFFF
        hash_value = hash_value ^ (hash_value >> 16)

        return hash_value
