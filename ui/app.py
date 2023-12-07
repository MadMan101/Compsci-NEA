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

        # Categories list
        self.categories = []

        # Create GUI components
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        # Dashboard Page
        dashboard_page = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_page, text="Dashboard")

        # Categories Page
        categories_page = ttk.Frame(self.notebook)
        self.notebook.add(categories_page, text="Categories")

        # Category Info
        self.category_combobox = ttk.Combobox(categories_page, values=self.get_category_names(), state="readonly", width=20)
        self.category_combobox.grid(row=0, column=0, padx=10, pady=10)
        self.category_combobox["values"] = self.db.get_categories()
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
        ttk.Label(categories_page, text="Add Income").grid(row=6, column=0, pady=5, columnspan=2)

        ttk.Label(categories_page, text="Amount:").grid(row=7, column=0, pady=5)
        self.income_entry = ttk.Entry(categories_page, width=15)
        self.income_entry.grid(row=7, column=1, padx=10, pady=5)

        ttk.Button(categories_page, text="Add Income", command=self.add_income).grid(row=7, column=2, padx=10, pady=5)

        # Add Expense
        ttk.Label(categories_page, text="Add Expense").grid(row=6, column=3, pady=5, columnspan=2)

        ttk.Label(categories_page, text="Amount:").grid(row=7, column=3, pady=5)
        self.expense_entry = ttk.Entry(categories_page, width=15)
        self.expense_entry.grid(row=7, column=4, padx=10, pady=5)

        ttk.Button(categories_page, text="Add Expense", command=self.add_expense).grid(row=7, column=5, padx=10, pady=5)

        # Expenses Table (Simplified Representation)
        ttk.Label(categories_page, text="Expenses Table").grid(row=8, column=0, pady=10, columnspan=6)

        self.expenses_table = ttk.Treeview(categories_page, columns=("Amount", "Type"))
        self.expenses_table.heading("#0", text="Date")
        self.expenses_table.heading("Amount", text="Amount")
        self.expenses_table.heading("Type", text="Type")
        self.expenses_table.grid(row=9, column=0, columnspan=6, padx=10, pady=5)

        ttk.Label(dashboard_page, text="Pie Chart of Categories").pack(pady=10)

        # Dashboard Info
        ttk.Label(dashboard_page, text="Total Money Available:").pack(pady=5)
        ttk.Label(dashboard_page, text="Total Money Assigned:").pack(pady=5)

        # TODO: Add Pie Chart widget (you may use Matplotlib for this)

        # TODO: Display the total money available and total money assigned

    def see_all_expenses(self):
        # TODO: Implement displaying all expenses in the expenses_table
        pass

    def add_category(self):
        new_category_name = self.new_category_name_entry.get()
        new_budget_limit = self.new_budget_limit_entry.get()

        if new_category_name and new_budget_limit:
            new_category = Category(name=new_category_name, budget_limit=float(new_budget_limit))
            self.db.insert_category(new_category_name, new_budget_limit)
            self.categories.append(new_category)

            # Update Combobox
            self.category_combobox["values"] = self.db.get_categories()

            # Clear entry fields
            self.new_category_name_entry.delete(0, tk.END)
            self.new_budget_limit_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Input Error", "Please enter category name and budget limit.")

    def add_income(self):
        # TODO: Implement adding income
        pass

    def add_expense(self):
        print(self.category_combobox.current())
        selected_category_index = self.category_combobox.current()
        if selected_category_index != -1:
            selected_category = self.categories[selected_category_index]
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
            selected_category = self.categories[selected_category_index]

            # Update Category Info Labels
            self.category_info_labels[0]["text"] = f"{selected_category.budget_limit}"
            self.category_info_labels[1]["text"] = f"{selected_category.get_total_expenses()}"
            self.category_info_labels[2]["text"] = f"{selected_category.budget_limit - selected_category.get_total_expenses()}"
        else:
            messagebox.showwarning("Selection Error", "Please select a category.")

    def get_category_names(self):
        return [category.name for category in self.categories]
    
    def on_combobox_selected(self, event):
        self.show_category_info(self.category_combobox.current())
