import tkinter as tk
from tkinter import ttk, messagebox
from categories.category import Category
from expenses.expense import Expense
from databases.database import BudgetDatabase

class BudgetTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Budget Tracker App")

        self.db = BudgetDatabase()

        # Create login window
        self.login_window = tk.Toplevel(self.root)
        self.login_window.title("Login")
        self.login_window.geometry("400x250")

        # Login variables
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        # Login components
        ttk.Label(self.login_window, text="Username:").pack(pady=5)
        ttk.Entry(self.login_window, textvariable=self.username_var).pack(pady=5)

        ttk.Label(self.login_window, text="Password:").pack(pady=5)
        ttk.Entry(self.login_window, textvariable=self.password_var, show="*").pack(pady=5)

        ttk.Button(self.login_window, text="Login", command=self.login).pack(pady=10)
        ttk.Button(self.login_window, text="Register", command=self.register).pack(pady=5)
        
    def login(self):
        username = self.username_var.get()
        password = self.password_var.get()

        # Validate username and password (you may check against a database)
        if self.db.login(username, password,):
            self.login_window.destroy()  # Close login window
            self.initialise_app()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def register(self):
        username = self.username_var.get()
        password = self.password_var.get()

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

        

    def init_categories(self):
         # Categories Page
        categories_page = ttk.Frame(self.notebook)
        self.notebook.add(categories_page, text="Categories")

         # Category Info
        self.category_combobox = ttk.Combobox(categories_page, values=self.db.get_category_names(), state="readonly", width=20)
        self.category_combobox.grid(row=0, column=0, padx=10, pady=10)
        self.category_combobox["values"] = self.db.get_category_names()
        self.category_combobox.bind("<<ComboboxSelected>>", self.on_combobox_selected)

        ttk.Button(categories_page, text="See All Expenses", command=self.see_all_expenses).grid(row=0, column=1, padx=10, pady=10)

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

        ttk.Label(categories_page, text="Amount:").grid(row=7, column=0, pady=5)
        self.income_entry = ttk.Entry(categories_page, width=15)
        self.income_entry.grid(row=7, column=1, padx=10, pady=5)

        ttk.Button(categories_page, text="Add Expense", command=self.add_expense).grid(row=7, column=2, padx=10, pady=5)

        # Expenses Table (Simplified Representation)
        ttk.Label(categories_page, text="Expenses Table").grid(row=8, column=0, pady=10, columnspan=6)

        self.expenses_table = ttk.Treeview(categories_page, columns=("Amount", "Type"))
        self.expenses_table.heading("#0", text="Date")
        self.expenses_table.heading("Amount", text="Amount")
        self.expenses_table.heading("Type", text="Type")
        self.expenses_table.grid(row=9, column=0, columnspan=6, padx=10, pady=5)

    def init_dashboard(self):
        # Dashboard Page
        dashboard_page = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_page, text="Dashboard")

        ttk.Label(dashboard_page, text="Pie Chart of Categories").pack(pady=10)

        # Dashboard Info
        ttk.Label(dashboard_page, text="Total Money Available:").pack(pady=5)
        ttk.Label(dashboard_page, text="Total Money Assigned:").pack(pady=5)

        # TODO: Add Pie Chart widget (you may use Matplotlib for this)

        # TODO: Display the total money available and total money assigned

    def init_income(self):
         # Categories Page
        income_page = ttk.Frame(self.notebook)
        self.notebook.add(income_page, text="Income")

         # Category Info
        self.income_combobox = ttk.Combobox(income_page, values=self.db.get_category_names(), state="readonly", width=20)
        self.income_combobox.grid(row=0, column=0, padx=10, pady=10)
        self.income_combobox["values"] = self.db.get_income_names()
        self.income_combobox.bind("<<ComboboxSelected>>", self.on_combobox_selected)

        ttk.Button(income_page, text="See All Expenses", command=self.see_all_expenses).grid(row=0, column=1, padx=10, pady=10)

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

        ttk.Button(income_page, text="Add Source", command=self.add_category).grid(row=5, column=2, padx=10, pady=5)

        # Add Income
        ttk.Label(income_page, text="Add Income").grid(row=6, column=0, pady=5, columnspan=2)

        ttk.Label(income_page, text="Amount:").grid(row=7, column=0, pady=5)
        self.income_entry = ttk.Entry(income_page, width=15)
        self.income_entry.grid(row=7, column=1, padx=10, pady=5)

        ttk.Button(income_page, text="Add Income", command=self.add_expense).grid(row=7, column=2, padx=10, pady=5)

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
        # TODO: Implement adding income
        pass

    def add_expense(self):
        selected_category_index = self.category_combobox.current()
        selected_category = self.db.get_category(self.category_combobox.get())
        if selected_category_index != -1:
            expense_amount = self.expense_entry.get()

            if expense_amount:
                selected_category.add_expense(float(expense_amount))
                messagebox.showinfo("Expense Added", f"Expense of {expense_amount} added to {selected_category.name}")
                self.expense_entry.delete(0, tk.END)
                self.show_category_info(selected_category_index)
                # TODO: Update expenses_table
            else:
                messagebox.showwarning("Input Error", "Please enter expense amount.")
        else:
            messagebox.showwarning("Selection Error", "Please select a category.")

    def show_category_info(self, selected_category_index):
        if selected_category_index != -1:
            selected_category = self.db.get_category(self.category_combobox.get())

            # Update Category Info Labels
            self.category_info_labels[0]["text"] = f"{selected_category[2]}"
            self.category_info_labels[1]["text"] = f"{selected_category[3]}"
            self.category_info_labels[2]["text"] = f"{selected_category[2] - selected_category[3]}"
        else:
            messagebox.showwarning("Selection Error", "Please select a category.")
    
    def on_combobox_selected(self, event):
        self.show_category_info(self.category_combobox.current())
