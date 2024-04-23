import tkinter as tk
from tkinter import ttk, messagebox
from databases.database import BudgetDatabase
import configparser
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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

        self.reset_value = 0.0

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
                return {}
        else:
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

        # Expenses Table 
        ttk.Label(categories_page, text="Expenses Table").grid(row=8, column=0, pady=10, columnspan=6)

        self.expenses_table = ttk.Treeview(categories_page, columns=("Date", "Amount", "Description"), show="headings")
        self.expenses_table.heading("Date", text="Date")
        self.expenses_table.heading("Amount", text="Amount")
        self.expenses_table.heading("Description", text="Description")
        self.expenses_table.grid(row=9, column=0, columnspan=6, padx=10, pady=5)

        reset_button = ttk.Button(categories_page, text="New Period", command=self.reset)
        reset_button.grid(row=0, column=5, sticky=tk.NE, padx=10, pady=5)

    def init_dashboard(self):
        # Dashboard Page
        dashboard_page = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_page, text="Dashboard")
        
        # Logout button
        logout_button = ttk.Button(dashboard_page, text="Logout", command=self.logout)
        logout_button.pack(side=tk.TOP, anchor=tk.NE, padx=10, pady=5)

        graphs_button = ttk.Button(dashboard_page, text="Show Graphs", command=self.show_graphs_popup)
        graphs_button.pack(side=tk.TOP, anchor=tk.NE, padx=10, pady=5)

        ttk.Label(dashboard_page, text="Pie Chart of Categories").pack(pady=10)

        # Dashboard Info
        ttk.Label(dashboard_page, text="Total Money Available:").pack(pady=5)
        self.funds_text = ttk.Label(dashboard_page, text="asd")
        self.funds_text.pack(pady=5)
        ttk.Label(dashboard_page, text="Total Money Assigned:").pack(pady=5)

        self.show_dashboard_info()

        self.transaction_table = ttk.Treeview(dashboard_page, columns=("ID", "Date", "Categories", "Amount", "Description"), show="headings")
        self.transaction_table.heading("ID", text="ID")
        self.transaction_table.heading("Date", text="Date")
        self.transaction_table.heading("Categories", text="Categories")
        self.transaction_table.heading("Amount", text="Amount")
        self.transaction_table.heading("Description", text="Description")
        self.transaction_table.pack(pady=10)

        self.transaction_table.column("ID", width=1, stretch=tk.NO)

        delete_button = ttk.Button(dashboard_page, text="Delete entry", command=self.delete_entry)
        delete_button.pack(side=tk.LEFT, anchor=tk.NE, padx=10, pady=5)

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

        # Expenses Table
        ttk.Label(income_page, text="Income Table").grid(row=8, column=0, pady=10, columnspan=6)

        self.income_table = ttk.Treeview(income_page, columns=("Date", "Amount", "Description"), show="headings")
        self.income_table.heading("Date", text="Date")
        self.income_table.heading("Amount", text="Amount")
        self.income_table.heading("Description", text="Description")
        self.income_table.grid(row=9, column=0, columnspan=6, padx=10, pady=5)

    def reset(self):
        self.db.new_reset()
        self.show_all()
        self.show_category_info()
        self.show_expenses()

    def show_graphs_popup(self):
        popup_window = tk.Tk()
        popup_window.title("Graphs")
        popup_window.geometry("600x600")

        canvas = tk.Canvas(popup_window)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(popup_window, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)

        graph_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=graph_frame, anchor="nw")

        exPieInfo = self.db.expenses_pie()

        fig1, ax1 = plt.subplots()
        ax1.pie(exPieInfo[0], labels=exPieInfo[1], autopct='%1.1f%%')
        ax1.set_title("Expense Categories")

        canvas1 = FigureCanvasTkAgg(fig1, master=graph_frame)
        canvas1.draw()
        canvas1.get_tk_widget().pack()

        inPieInfo = self.db.income_pie()

        fig3, ax3 = plt.subplots()
        ax3.pie(inPieInfo[0], labels=inPieInfo[1], autopct='%1.1f%%')
        ax3.set_title("Income Categories")

        canvas3 = FigureCanvasTkAgg(fig3, master=graph_frame)
        canvas3.draw()
        canvas3.get_tk_widget().pack()

        graph_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        popup_window.mainloop()

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

    def delete_entry(self):
        selected_item = self.transaction_table.selection()
        id = self.transaction_table.item(selected_item, "values")[0]
        amount = self.transaction_table.item(selected_item, "values")[3]
        
        self.db.delete_transaction(id, float(amount))

        self.show_all()

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
                
                self.show_all()
                self.show_income()
                self.show_income_info()
            else:
                messagebox.showwarning("Input Error", "Please enter income amount")
        else:
            messagebox.showwarning("Selection Error", "Please select a category")
        self.show_all()
        self.show_income()
        self.show_income_info()

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
                self.category_name_entry.delete(0, tk.END)
                self.show_all()
                self.show_expenses()
                self.show_category_info()
            else:
                messagebox.showwarning("Input Error", "Please enter expense amount.")
        else:
            messagebox.showwarning("Selection Error", "Please select a category.")

        self.show_all()
        self.show_expenses()
        self.show_category_info()

    def show_income_info(self, selected_category_index):
        print(0)
    
    def on_combobox_selected(self, event):
        self.show_category_info()

        self.show_expenses()

    def on_combobox_income_selected(self, event):
        self.show_income_info()

        self.show_income()
        
    def show_all(self):
        self.show_dashboard_info()
        self.show_transactions()
        
    def show_dashboard_info(self):
        self.funds_text["text"] = self.db.get_funds()

    def show_expenses(self):
        category_id = self.db.get_category(self.category_combobox.get())[0]

        # Clear existing entries in the expenses_table
        for item in self.expenses_table.get_children():
            self.expenses_table.delete(item)

        # Fetch expenses for the selected category from the database
        expenses = self.db.get_expenses(category_id)

        # Insert expenses into the expenses_table
        for expense in expenses:
            self.expenses_table.insert("", 0, values=(expense[0], expense[1], expense[2],))

    def show_income(self):
        category_id = self.db.get_income(self.income_combobox.get())[0]

        # Clear existing entries in the income_table
        for item in self.income_table.get_children():
            self.income_table.delete(item)

        # Fetch expenses for the selected category from the database
        expenses = self.db.get_incomes(category_id)

        # Insert expenses into the income_table
        for expense in expenses:
            self.income_table.insert("", 0, values=(expense[0], expense[1], expense[2],))

    def show_transactions(self):
        # Clear existing entries in the expenses_table
        for item in self.transaction_table.get_children():
            self.transaction_table.delete(item)

        # Fetch expenses for the selected category from the database
        expenses = self.db.get_transactions()

        # Insert expenses into the expenses_table
        for expense in expenses:
            self.transaction_table.insert("", 0, values=(expense[4], expense[0], expense[3], expense[1], expense[2]))

    def show_category_info(self):
        selected_category_index = self.db.get_category(self.category_combobox.get())

        if selected_category_index != -1:
            selected_category = self.db.get_category(self.category_combobox.get())

            # Update Category Info Labels
            self.category_info_labels[0]["text"] = f"{selected_category[2]}"
            self.category_info_labels[1]["text"] = selected_category[3] - selected_category[4]
            self.category_info_labels[2]["text"] = selected_category[2] - selected_category[3] + selected_category[4]
        else:
            messagebox.showwarning("Selection Error", "Please select a category.")

    def show_income_info(self):
        selected_category_index = self.db.get_income(self.income_combobox.get())

        if selected_category_index != -1:
            selected_category = self.db.get_income(self.income_combobox.get())

            # Update Category Info Labels
            self.income_info_labels[0]["text"] = round(selected_category[3],3)
            self.income_info_labels[1]["text"] = round(selected_category[2], 3)
            if selected_category[2] != 0:
                self.income_info_labels[2]["text"] = round((selected_category[3] * 100) / selected_category[2], 3)
            else:
                self.income_info_labels[2]["text"] = 0.0
        else:
            messagebox.showwarning("Selection Error", "Please select a category.")

    def hash(input_string):
        hash_value = 5381

        for char in input_string:
            hash_value = (hash_value * 33) ^ ord(char)

        hash_value = (hash_value ^ (hash_value >> 15)) * 2654435761 & 0xFFFFFFFF
        hash_value = (hash_value ^ (hash_value >> 13)) * 2654435761 & 0xFFFFFFFF
        hash_value = hash_value ^ (hash_value >> 16)

        return hash_value
