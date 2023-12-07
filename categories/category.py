class Category:
    def __init__(self, name, budget_limit):
        self.name = name
        self.budget_limit = budget_limit

    def add_expense(self, amount):
        self.expenses.append(amount)

    def get_total_expenses(self):
        return sum(self.expenses)
