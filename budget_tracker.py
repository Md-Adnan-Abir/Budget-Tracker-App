import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import datetime as dt

class BudgetTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Budget Tracker")
        self.root.geometry("800x600")  # Default window size set to larger dimensions
        self.data_file = "budget_data.csv"

        # Load existing data or create a new DataFrame
        try:
            self.data = pd.read_csv(self.data_file)
            if 'Date' in self.data.columns:
                self.data['Date'] = pd.to_datetime(self.data['Date'], errors='coerce')
        except FileNotFoundError:
            self.data = pd.DataFrame(columns=['Type', 'Category', 'Amount', 'Date'])

        # Track the current month
        self.current_month = dt.datetime.now().month

        # UI Elements
        self.setup_ui()
        self.update_overview()  # Ensure monthly data is updated on load

    def setup_ui(self):
        # Scrollable container for the home page
        container = ttk.Frame(self.root)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Frames
        overview_frame = ttk.LabelFrame(self.scrollable_frame, text="Overview", padding=(10, 10))
        overview_frame.pack(fill="x", padx=10, pady=10)

        input_frame = ttk.LabelFrame(self.scrollable_frame, text="Add Transaction", padding=(10, 10))
        input_frame.pack(fill="x", padx=10, pady=10)

        transaction_frame = ttk.LabelFrame(self.scrollable_frame, text="Transaction List", padding=(10, 10))
        transaction_frame.pack(fill="both", expand=True, padx=10, pady=10)

        detailed_view_frame = ttk.LabelFrame(self.scrollable_frame, text="Detailed View", padding=(10, 10))
        detailed_view_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Overview
        self.total_label = ttk.Label(overview_frame, text="Total Balance: $0", font=("Arial", 14, "bold"))
        self.total_label.pack(anchor="w")
        self.income_label = ttk.Label(overview_frame, text="Total Monthly Income: $0", font=("Arial", 12), foreground="green")
        self.income_label.pack(anchor="w")
        self.expense_label = ttk.Label(overview_frame, text="Total Monthly Expenses: $0", font=("Arial", 12), foreground="red")
        self.expense_label.pack(anchor="w")
        self.savings_label = ttk.Label(overview_frame, text="Total Savings: $0", font=("Arial", 12), foreground="blue")
        self.savings_label.pack(anchor="w")

        # Input fields
        ttk.Label(input_frame, text="Type:").grid(row=0, column=0, sticky="w", pady=5)
        self.type_var = tk.StringVar(value="Expense")
        ttk.Combobox(input_frame, textvariable=self.type_var, values=["Expense", "Income", "Saving"], state="readonly").grid(row=0, column=1, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Category:").grid(row=1, column=0, sticky="w", pady=5)
        self.category_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.category_var).grid(row=1, column=1, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Amount:").grid(row=2, column=0, sticky="w", pady=5)
        self.amount_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.amount_var).grid(row=2, column=1, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Date (YYYY-MM-DD):").grid(row=3, column=0, sticky="w", pady=5)
        self.date_var = tk.StringVar(value=dt.datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(input_frame, textvariable=self.date_var).grid(row=3, column=1, pady=5, sticky="ew")

        ttk.Button(input_frame, text="Add Transaction", command=self.add_transaction).grid(row=4, column=0, columnspan=2, pady=10)

        # Transaction list
        self.transaction_tree = ttk.Treeview(transaction_frame, columns=("Type", "Category", "Amount", "Date"), show="headings")
        self.transaction_tree.heading("Type", text="Type")
        self.transaction_tree.heading("Category", text="Category")
        self.transaction_tree.heading("Amount", text="Amount")
        self.transaction_tree.heading("Date", text="Date")
        self.transaction_tree.column("Amount", anchor="center")
        self.transaction_tree.pack(fill="both", expand=True)
        self.update_transaction_list()

        # Add tag colors for transaction types
        self.transaction_tree.tag_configure("income", foreground="green")
        self.transaction_tree.tag_configure("expense", foreground="red")
        self.transaction_tree.tag_configure("saving", foreground="blue")

        # Detailed view
        ttk.Button(detailed_view_frame, text="Earnings Details", command=self.show_earnings_options).pack(pady=5)
        ttk.Button(detailed_view_frame, text="Expenses Details", command=self.show_expenses_options).pack(pady=5)
        ttk.Button(detailed_view_frame, text="Savings Details", command=self.show_savings_options).pack(pady=5)

    def add_transaction(self):
        transaction_type = self.type_var.get()
        category = self.category_var.get()
        try:
            amount = float(self.amount_var.get())
        except ValueError:
            showinfo("Invalid Input", "Please enter a valid amount.")
            return

        try:
            date = pd.to_datetime(self.date_var.get())
        except ValueError:
            showinfo("Invalid Input", "Please enter a valid date in YYYY-MM-DD format.")
            return

        if not category:
            showinfo("Missing Input", "Please enter a category.")
            return

        new_transaction = pd.DataFrame([[transaction_type, category, amount, date]], columns=['Type', 'Category', 'Amount', 'Date'])
        self.data = pd.concat([self.data, new_transaction], ignore_index=True)

        if transaction_type == "Saving":
            # Deduct savings from total balance
            self.data = pd.concat([self.data, pd.DataFrame([["Expense", "Savings Deduction", amount, date]], columns=['Type', 'Category', 'Amount', 'Date'])], ignore_index=True)

        self.save_data()
        self.update_overview()
        self.update_transaction_list()
        showinfo("Success", "Transaction added successfully!")

    def save_data(self):
        self.data.to_csv(self.data_file, index=False)

    def update_overview(self):
        current_month = dt.datetime.now().month
        current_year = dt.datetime.now().year

        # Update current month if changed
        if self.current_month != current_month:
            self.current_month = current_month

        self.data['Date'] = pd.to_datetime(self.data['Date'], errors='coerce')  # Ensure all are datetime
        monthly_data = self.data[(self.data['Date'].dt.month == self.current_month) & (self.data['Date'].dt.year == current_year)]

        total_income = monthly_data[monthly_data['Type'] == "Income"]['Amount'].sum()
        total_expenses = monthly_data[monthly_data['Type'] == "Expense"]['Amount'].sum()
        total_savings = self.data[self.data['Type'] == "Saving"]['Amount'].sum()

        self.income_label.config(text=f"Total Monthly Income: ${total_income:.2f}")
        self.expense_label.config(text=f"Total Monthly Expenses: ${total_expenses:.2f}")
        self.total_label.config(text=f"Total Balance: ${total_income - total_expenses:.2f}")
        self.savings_label.config(text=f"Total Savings: ${total_savings:.2f}")

    def update_transaction_list(self):
        for row in self.transaction_tree.get_children():
            self.transaction_tree.delete(row)

        for _, row in self.data.iterrows():
            arrow = "↓" if row['Type'] == "Expense" else ("↑" if row['Type'] == "Income" else "→")
            tag = "expense" if row['Type'] == "Expense" else ("income" if row['Type'] == "Income" else "saving")
            self.transaction_tree.insert("", "end", values=(row['Type'], row['Category'], f"{row['Amount']} {arrow}", row['Date'].strftime("%Y-%m-%d")), tags=(tag,))

    def show_earnings_options(self):
        options_window = tk.Toplevel(self.root)
        options_window.geometry(f"{self.root.winfo_width()}x{self.root.winfo_height()}")
        options_window.title("Earnings Options")
        ttk.Button(options_window, text="Earnings Overview", command=lambda: self.show_line_graph("Income"), style="TButton").pack(pady=20)
        ttk.Button(options_window, text="Earnings Sources", command=lambda: self.show_pie_chart("Income"), style="TButton").pack(pady=20)

    def show_expenses_options(self):
        options_window = tk.Toplevel(self.root)
        options_window.geometry(f"{self.root.winfo_width()}x{self.root.winfo_height()}")
        options_window.title("Expenses Options")
        ttk.Button(options_window, text="Expenses Overview", command=lambda: self.show_line_graph("Expense"), style="TButton").pack(pady=20)
        ttk.Button(options_window, text="Expenses Categories", command=lambda: self.show_pie_chart("Expense"), style="TButton").pack(pady=20)

    def show_savings_options(self):
        options_window = tk.Toplevel(self.root)
        options_window.geometry(f"{self.root.winfo_width()}x{self.root.winfo_height()}")
        options_window.title("Savings Options")
        ttk.Button(options_window, text="Savings Overview", command=lambda: self.show_line_graph("Saving"), style="TButton").pack(pady=20)
        ttk.Button(options_window, text="Transfer Money", command=self.transfer_savings_to_balance, style="TButton").pack(pady=20)

    def transfer_savings_to_balance(self):
        transfer_window = tk.Toplevel(self.root)
        transfer_window.geometry("300x200")
        transfer_window.title("Transfer Savings")

        ttk.Label(transfer_window, text="Enter amount to transfer:").pack(pady=10)
        transfer_amount_var = tk.StringVar()
        ttk.Entry(transfer_window, textvariable=transfer_amount_var).pack(pady=10)

        def transfer():
            try:
                amount = float(transfer_amount_var.get())
                total_savings = self.data[self.data['Type'] == "Saving"]['Amount'].sum()

                if amount > total_savings:
                    showinfo("Error", "Insufficient savings.")
                else:
                    self.data = pd.concat([self.data, pd.DataFrame([["Income", "Savings Transfer", amount, dt.datetime.now()]], columns=['Type', 'Category', 'Amount', 'Date'])], ignore_index=True)
                    self.data = pd.concat([self.data, pd.DataFrame([["Saving", "Savings Reduction", -amount, dt.datetime.now()]], columns=['Type', 'Category', 'Amount', 'Date'])], ignore_index=True)
                    self.save_data()
                    self.update_overview()
                    self.update_transaction_list()
                    showinfo("Success", "Money transferred successfully!")
                    transfer_window.destroy()
            except ValueError:
                showinfo("Error", "Please enter a valid amount.")

        ttk.Button(transfer_window, text="Transfer", command=transfer).pack(pady=20)

    def show_line_graph(self, transaction_type):
        time_window = tk.Toplevel(self.root)
        time_window.geometry(f"{self.root.winfo_width()}x{self.root.winfo_height()}")
        time_window.title("Select Timeframe")

        def plot_timeframe(timeframe):
            if self.data.empty:
                showinfo("No Data", "No data available to visualize.")
                return

            filtered_data = self.data[self.data['Type'] == transaction_type]
            if timeframe == "Daily":
                aggregated = filtered_data.groupby('Date')['Amount'].sum()
                x_labels = aggregated.index.strftime('%Y-%m-%d')  # Show only dates
            elif timeframe == "Monthly":
                aggregated = filtered_data.groupby(filtered_data['Date'].dt.to_period('M'))['Amount'].sum()
                x_labels = aggregated.index.astype(str)
            elif timeframe == "Yearly":
                aggregated = filtered_data.groupby(filtered_data['Date'].dt.year)['Amount'].sum()
                x_labels = aggregated.index.astype(str)

            figure, ax = plt.subplots(figsize=(12, 8))
            ax.plot(x_labels, aggregated.values, marker='o')
            ax.set_title(f"{transaction_type} Overview ({timeframe})")
            ax.set_xlabel("Date")
            ax.set_ylabel("Amount")
            self.display_plot(figure)

        ttk.Button(time_window, text="Daily", command=lambda: plot_timeframe("Daily"), style="TButton").pack(pady=20)
        ttk.Button(time_window, text="Monthly", command=lambda: plot_timeframe("Monthly"), style="TButton").pack(pady=20)
        ttk.Button(time_window, text="Yearly", command=lambda: plot_timeframe("Yearly"), style="TButton").pack(pady=20)

    def show_pie_chart(self, transaction_type):
        time_window = tk.Toplevel(self.root)
        time_window.geometry(f"{self.root.winfo_width()}x{self.root.winfo_height()}")
        time_window.title("Select Timeframe")

        def plot_timeframe(timeframe):
            if self.data.empty:
                showinfo("No Data", "No data available to visualize.")
                return

            filtered_data = self.data[self.data['Type'] == transaction_type]
            if timeframe == "Daily":
                aggregated = filtered_data.groupby('Category')['Amount'].sum()
            elif timeframe == "Monthly":
                aggregated = filtered_data.groupby(filtered_data['Date'].dt.to_period('M'))['Amount'].sum()
            elif timeframe == "Yearly":
                aggregated = filtered_data.groupby('Category')['Amount'].sum()

            figure, ax = plt.subplots(figsize=(12, 8))
            ax.pie(aggregated, labels=aggregated.index.astype(str), autopct='%1.1f%%', startangle=90)
            ax.set_title(f"{transaction_type} Breakdown ({timeframe})")
            self.display_plot(figure)

        ttk.Button(time_window, text="Daily", command=lambda: plot_timeframe("Daily"), style="TButton").pack(pady=20)
        ttk.Button(time_window, text="Monthly", command=lambda: plot_timeframe("Monthly"), style="TButton").pack(pady=20)
        ttk.Button(time_window, text="Yearly", command=lambda: plot_timeframe("Yearly"), style="TButton").pack(pady=20)

    def display_plot(self, figure):
        plot_window = tk.Toplevel(self.root)
        plot_window.geometry(f"{self.root.winfo_width()}x{self.root.winfo_height()}")
        plot_window.title("Visualization")
        canvas = FigureCanvasTkAgg(figure, master=plot_window)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill="both", expand=True)
        canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = BudgetTrackerApp(root)
    root.mainloop()
