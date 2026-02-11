import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import tkinter.font as tkFont

class LoanManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Loan Management System")
        self.root.geometry("1200x700")
        self.root.configure(bg='#f0f0f0')
        
        # Custom font
        self.title_font = tkFont.Font(family="Helvetica", size=16, weight="bold")
        self.label_font = tkFont.Font(family="Helvetica", size=10)
        self.button_font = tkFont.Font(family="Helvetica", size=10, weight="bold")
        
        # Database connection
        self.connection = self.create_db_connection()
        
        # Create main containers
        self.create_header()
        self.create_main_content()
        self.create_footer()
        
        # Initialize UI
        self.show_dashboard()
    
    def create_db_connection(self):
        try:
            connection = mysql.connector.connect(
                host='localhost',
                user='root',  # Replace with your MySQL username
                password='1234',  # Replace with your MySQL password
                database='loan_management'
            )
            return connection
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to connect to database: {e}")
            return None
    
    def create_header(self):
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        header_frame.pack(fill='x', side='top')
        
        title_label = tk.Label(header_frame, text="Loan Management System", font=self.title_font, 
                              bg='#2c3e50', fg='white', padx=20)
        title_label.pack(side='left')
        
        # Navigation buttons
        nav_frame = tk.Frame(header_frame, bg='#2c3e50')
        nav_frame.pack(side='right', padx=20)
        
        buttons = [
            ("Dashboard", self.show_dashboard),
            ("Customers", self.show_customers),
            ("Loans", self.show_loans),
            ("Payments", self.show_payments),
            ("Reports", self.show_reports)
        ]
        
        for text, command in buttons:
            btn = tk.Button(nav_frame, text=text, font=self.button_font, 
                           bg='#3498db', fg='white', bd=0, padx=10,
                           command=command)
            btn.pack(side='left', padx=5)
    
    def create_main_content(self):
        self.main_frame = tk.Frame(self.root, bg='#f0f0f0')
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    def create_footer(self):
        footer_frame = tk.Frame(self.root, bg='#2c3e50', height=40)
        footer_frame.pack(fill='x', side='bottom')
        
        footer_label = tk.Label(footer_frame, text="© 2023 Loan Management System | Developed with Python & MySQL", 
                                font=('Helvetica', 8), bg='#2c3e50', fg='white')
        footer_label.pack(pady=10)
    
    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        self.clear_main_frame()
        
        # Dashboard title
        title_label = tk.Label(self.main_frame, text="Dashboard", font=self.title_font, bg='#f0f0f0')
        title_label.pack(pady=(0, 20), anchor='w')
        
        # Stats cards
        stats_frame = tk.Frame(self.main_frame, bg='#f0f0f0')
        stats_frame.pack(fill='x', pady=(0, 20))
        
        stats = [
            ("Total Loans", self.get_total_loans(), "#3498db"),
            ("Active Loans", self.get_active_loans(), "#2ecc71"),
            ("Total Customers", self.get_total_customers(), "#e74c3c"),
            ("Total Payments", self.get_total_payments(), "#9b59b6")
        ]
        
        for i, (title, value, color) in enumerate(stats):
            card = tk.Frame(stats_frame, bg=color, width=200, height=100, 
                           highlightbackground="#ddd", highlightthickness=1)
            card.grid(row=0, column=i, padx=10)
            
            title_label = tk.Label(card, text=title, font=self.label_font, 
                                  bg=color, fg='white')
            title_label.pack(pady=(10, 0))
            
            value_label = tk.Label(card, text=value, font=('Helvetica', 24, 'bold'), 
                                  bg=color, fg='white')
            value_label.pack(pady=(10, 10))
        
        # Recent activity
        activity_frame = tk.LabelFrame(self.main_frame, text="Recent Loans", 
                                      font=self.label_font, bg='#f0f0f0')
        activity_frame.pack(fill='both', expand=True)
        
        columns = ("Loan ID", "Customer", "Amount", "Start Date", "Status")
        self.recent_loans_tree = ttk.Treeview(activity_frame, columns=columns, show='headings')
        
        for col in columns:
            self.recent_loans_tree.heading(col, text=col)
            self.recent_loans_tree.column(col, width=120)
        
        self.recent_loans_tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Populate recent loans
        self.populate_recent_loans()
    
    def get_total_loans(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM loans")
            return cursor.fetchone()[0]
        except Error as e:
            messagebox.showerror("Error", f"Failed to fetch total loans: {e}")
            return "Error"
    
    def get_active_loans(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM loans WHERE status='Active'")
            return cursor.fetchone()[0]
        except Error as e:
            messagebox.showerror("Error", f"Failed to fetch active loans: {e}")
            return "Error"
    
    def get_total_customers(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM customers")
            return cursor.fetchone()[0]
        except Error as e:
            messagebox.showerror("Error", f"Failed to fetch total customers: {e}")
            return "Error"
    
    def get_total_payments(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT SUM(amount) FROM payments")
            result = cursor.fetchone()[0]
            return f"${result:,.2f}" if result else "$0.00"
        except Error as e:
            messagebox.showerror("Error", f"Failed to fetch total payments: {e}")
            return "Error"
    
    def populate_recent_loans(self):
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT l.loan_id, CONCAT(c.first_name, ' ', c.last_name) as customer, 
                       l.amount, l.start_date, l.status
                FROM loans l
                JOIN customers c ON l.customer_id = c.customer_id
                ORDER BY l.start_date DESC
                LIMIT 10
            """
            cursor.execute(query)
            loans = cursor.fetchall()
            
            for loan in loans:
                self.recent_loans_tree.insert("", "end", values=(
                    loan['loan_id'],
                    loan['customer'],
                    f"${loan['amount']:,.2f}",
                    loan['start_date'].strftime('%Y-%m-%d'),
                    loan['status']
                ))
        except Error as e:
            messagebox.showerror("Error", f"Failed to fetch recent loans: {e}")
    
    def show_customers(self):
        self.clear_main_frame()
        
        # Customers title and buttons
        title_frame = tk.Frame(self.main_frame, bg='#f0f0f0')
        title_frame.pack(fill='x', pady=(0, 20))
        
        title_label = tk.Label(title_frame, text="Customer Management", font=self.title_font, bg='#f0f0f0')
        title_label.pack(side='left')
        
        button_frame = tk.Frame(title_frame, bg='#f0f0f0')
        button_frame.pack(side='right')
        
        add_btn = tk.Button(button_frame, text="Add Customer", font=self.button_font,
                           bg='#2ecc71', fg='white', command=self.show_add_customer)
        add_btn.pack(side='left', padx=5)
        
        # Search frame
        search_frame = tk.Frame(self.main_frame, bg='#f0f0f0')
        search_frame.pack(fill='x', pady=(0, 10))
        
        search_label = tk.Label(search_frame, text="Search:", font=self.label_font, bg='#f0f0f0')
        search_label.pack(side='left')
        
        self.customer_search_entry = tk.Entry(search_frame, font=self.label_font, width=40)
        self.customer_search_entry.pack(side='left', padx=5)
        
        search_btn = tk.Button(search_frame, text="Search", font=self.button_font,
                             bg='#3498db', fg='white', command=self.search_customers)
        search_btn.pack(side='left', padx=5)
        
        # Customers table
        table_frame = tk.Frame(self.main_frame, bg='#f0f0f0')
        table_frame.pack(fill='both', expand=True)
        
        columns = ("ID", "First Name", "Last Name", "Email", "Phone", "Actions")
        self.customers_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        for col in columns:
            self.customers_tree.heading(col, text=col)
            self.customers_tree.column(col, width=120)
        
        self.customers_tree.pack(fill='both', expand=True)
        
        # Add action buttons to each row
        self.customers_tree.bind('<Double-1>', self.edit_customer)
        
        # Populate customers
        self.populate_customers()
    
    def populate_customers(self):
        try:
            # Clear existing data
            for row in self.customers_tree.get_children():
                self.customers_tree.delete(row)
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM customers ORDER BY last_name, first_name")
            customers = cursor.fetchall()
            
            for customer in customers:
                self.customers_tree.insert("", "end", values=(
                    customer['customer_id'],
                    customer['first_name'],
                    customer['last_name'],
                    customer['email'],
                    customer['phone'],
                    "Edit | Delete"
                ))
        except Error as e:
            messagebox.showerror("Error", f"Failed to fetch customers: {e}")
    
    def show_add_customer(self):
        self.customer_form_window = tk.Toplevel(self.root)
        self.customer_form_window.title("Add New Customer")
        self.customer_form_window.geometry("500x400")
        
        form_frame = tk.Frame(self.customer_form_window, padx=20, pady=20)
        form_frame.pack(fill='both', expand=True)
        
        tk.Label(form_frame, text="First Name:").grid(row=0, column=0, sticky='e', pady=5)
        self.first_name_entry = tk.Entry(form_frame, width=30)
        self.first_name_entry.grid(row=0, column=1, pady=5)
        
        tk.Label(form_frame, text="Last Name:").grid(row=1, column=0, sticky='e', pady=5)
        self.last_name_entry = tk.Entry(form_frame, width=30)
        self.last_name_entry.grid(row=1, column=1, pady=5)
        
        tk.Label(form_frame, text="Email:").grid(row=2, column=0, sticky='e', pady=5)
        self.email_entry = tk.Entry(form_frame, width=30)
        self.email_entry.grid(row=2, column=1, pady=5)
        
        tk.Label(form_frame, text="Phone:").grid(row=3, column=0, sticky='e', pady=5)
        self.phone_entry = tk.Entry(form_frame, width=30)
        self.phone_entry.grid(row=3, column=1, pady=5)
        
        tk.Label(form_frame, text="Address:").grid(row=4, column=0, sticky='ne', pady=5)
        self.address_text = tk.Text(form_frame, width=30, height=5)
        self.address_text.grid(row=4, column=1, pady=5)
        
        button_frame = tk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        save_btn = tk.Button(button_frame, text="Save", width=10, 
                            command=self.save_customer)
        save_btn.pack(side='left', padx=10)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", width=10,
                             command=self.customer_form_window.destroy)
        cancel_btn.pack(side='left', padx=10)
    
    def save_customer(self):
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()
        email = self.email_entry.get()
        phone = self.phone_entry.get()
        address = self.address_text.get("1.0", "end-1c")
        
        if not first_name or not last_name:
            messagebox.showerror("Error", "First name and last name are required!")
            return
        
        try:
            cursor = self.connection.cursor()
            query = """
                INSERT INTO customers (first_name, last_name, email, phone, address)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (first_name, last_name, email, phone, address))
            self.connection.commit()
            messagebox.showinfo("Success", "Customer added successfully!")
            self.customer_form_window.destroy()
            self.populate_customers()
        except Error as e:
            messagebox.showerror("Error", f"Failed to add customer: {e}")
    
    def edit_customer(self, event):
        selected_item = self.customers_tree.focus()
        if not selected_item:
            return
        
        item_data = self.customers_tree.item(selected_item)
        customer_id = item_data['values'][0]
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (customer_id,))
            customer = cursor.fetchone()
            
            if customer:
                self.show_edit_customer_form(customer)
        except Error as e:
            messagebox.showerror("Error", f"Failed to fetch customer: {e}")
    
    def show_edit_customer_form(self, customer):
        self.edit_customer_window = tk.Toplevel(self.root)
        self.edit_customer_window.title("Edit Customer")
        self.edit_customer_window.geometry("500x400")
        
        form_frame = tk.Frame(self.edit_customer_window, padx=20, pady=20)
        form_frame.pack(fill='both', expand=True)
        
        tk.Label(form_frame, text="First Name:").grid(row=0, column=0, sticky='e', pady=5)
        self.edit_first_name_entry = tk.Entry(form_frame, width=30)
        self.edit_first_name_entry.grid(row=0, column=1, pady=5)
        self.edit_first_name_entry.insert(0, customer['first_name'])
        
        tk.Label(form_frame, text="Last Name:").grid(row=1, column=0, sticky='e', pady=5)
        self.edit_last_name_entry = tk.Entry(form_frame, width=30)
        self.edit_last_name_entry.grid(row=1, column=1, pady=5)
        self.edit_last_name_entry.insert(0, customer['last_name'])
        
        tk.Label(form_frame, text="Email:").grid(row=2, column=0, sticky='e', pady=5)
        self.edit_email_entry = tk.Entry(form_frame, width=30)
        self.edit_email_entry.grid(row=2, column=1, pady=5)
        self.edit_email_entry.insert(0, customer['email'])
        
        tk.Label(form_frame, text="Phone:").grid(row=3, column=0, sticky='e', pady=5)
        self.edit_phone_entry = tk.Entry(form_frame, width=30)
        self.edit_phone_entry.grid(row=3, column=1, pady=5)
        self.edit_phone_entry.insert(0, customer['phone'])
        
        tk.Label(form_frame, text="Address:").grid(row=4, column=0, sticky='ne', pady=5)
        self.edit_address_text = tk.Text(form_frame, width=30, height=5)
        self.edit_address_text.grid(row=4, column=1, pady=5)
        self.edit_address_text.insert("1.0", customer['address'] if customer['address'] else "")
        
        button_frame = tk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        update_btn = tk.Button(button_frame, text="Update", width=10, 
                             command=lambda: self.update_customer(customer['customer_id']))
        update_btn.pack(side='left', padx=10)
        
        delete_btn = tk.Button(button_frame, text="Delete", width=10,
                             command=lambda: self.delete_customer(customer['customer_id']))
        delete_btn.pack(side='left', padx=10)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", width=10,
                             command=self.edit_customer_window.destroy)
        cancel_btn.pack(side='left', padx=10)
    
    def update_customer(self, customer_id):
        first_name = self.edit_first_name_entry.get()
        last_name = self.edit_last_name_entry.get()
        email = self.edit_email_entry.get()
        phone = self.edit_phone_entry.get()
        address = self.edit_address_text.get("1.0", "end-1c")
        
        if not first_name or not last_name:
            messagebox.showerror("Error", "First name and last name are required!")
            return
        
        try:
            cursor = self.connection.cursor()
            query = """
                UPDATE customers 
                SET first_name = %s, last_name = %s, email = %s, phone = %s, address = %s
                WHERE customer_id = %s
            """
            cursor.execute(query, (first_name, last_name, email, phone, address, customer_id))
            self.connection.commit()
            messagebox.showinfo("Success", "Customer updated successfully!")
            self.edit_customer_window.destroy()
            self.populate_customers()
        except Error as e:
            messagebox.showerror("Error", f"Failed to update customer: {e}")
    
    def delete_customer(self, customer_id):
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this customer?"):
            try:
                cursor = self.connection.cursor()
                cursor.execute("DELETE FROM customers WHERE customer_id = %s", (customer_id,))
                self.connection.commit()
                messagebox.showinfo("Success", "Customer deleted successfully!")
                self.edit_customer_window.destroy()
                self.populate_customers()
            except Error as e:
                messagebox.showerror("Error", f"Failed to delete customer: {e}")
    
    def search_customers(self):
        search_term = self.customer_search_entry.get()
        
        try:
            # Clear existing data
            for row in self.customers_tree.get_children():
                self.customers_tree.delete(row)
            
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT * FROM customers 
                WHERE first_name LIKE %s OR last_name LIKE %s OR email LIKE %s OR phone LIKE %s
                ORDER BY last_name, first_name
            """
            cursor.execute(query, (f"%{search_term}%", f"%{search_term}%", 
                                 f"%{search_term}%", f"%{search_term}%"))
            customers = cursor.fetchall()
            
            for customer in customers:
                self.customers_tree.insert("", "end", values=(
                    customer['customer_id'],
                    customer['first_name'],
                    customer['last_name'],
                    customer['email'],
                    customer['phone'],
                    "Edit | Delete"
                ))
        except Error as e:
            messagebox.showerror("Error", f"Failed to search customers: {e}")
    
    def show_loans(self):
        self.clear_main_frame()
        
        # Loans title and buttons
        title_frame = tk.Frame(self.main_frame, bg='#f0f0f0')
        title_frame.pack(fill='x', pady=(0, 20))
        
        title_label = tk.Label(title_frame, text="Loan Management", font=self.title_font, bg='#f0f0f0')
        title_label.pack(side='left')
        
        button_frame = tk.Frame(title_frame, bg='#f0f0f0')
        button_frame.pack(side='right')
        
        add_btn = tk.Button(button_frame, text="Add Loan", font=self.button_font,
                           bg='#2ecc71', fg='white', command=self.show_add_loan)
        add_btn.pack(side='left', padx=5)
        
        # Search frame
        search_frame = tk.Frame(self.main_frame, bg='#f0f0f0')
        search_frame.pack(fill='x', pady=(0, 10))
        
        search_label = tk.Label(search_frame, text="Search:", font=self.label_font, bg='#f0f0f0')
        search_label.pack(side='left')
        
        self.loan_search_entry = tk.Entry(search_frame, font=self.label_font, width=40)
        self.loan_search_entry.pack(side='left', padx=5)
        
        search_btn = tk.Button(search_frame, text="Search", font=self.button_font,
                             bg='#3498db', fg='white', command=self.search_loans)
        search_btn.pack(side='left', padx=5)
        
        # Loans table
        table_frame = tk.Frame(self.main_frame, bg='#f0f0f0')
        table_frame.pack(fill='both', expand=True)
        
        columns = ("ID", "Customer", "Amount", "Interest", "Term", "Start Date", "Status", "Actions")
        self.loans_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        for col in columns:
            self.loans_tree.heading(col, text=col)
            self.loans_tree.column(col, width=100)
        
        self.loans_tree.pack(fill='both', expand=True)
        
        # Add action buttons to each row
        self.loans_tree.bind('<Double-1>', self.edit_loan)
        
        # Populate loans
        self.populate_loans()
    
    def populate_loans(self):
        try:
            # Clear existing data
            for row in self.loans_tree.get_children():
                self.loans_tree.delete(row)
            
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT l.loan_id, CONCAT(c.first_name, ' ', c.last_name) as customer, 
                       l.amount, l.interest_rate, l.term_months, l.start_date, l.status
                FROM loans l
                JOIN customers c ON l.customer_id = c.customer_id
                ORDER BY l.start_date DESC
            """
            cursor.execute(query)
            loans = cursor.fetchall()
            
            for loan in loans:
                self.loans_tree.insert("", "end", values=(
                    loan['loan_id'],
                    loan['customer'],
                    f"${loan['amount']:,.2f}",
                    f"{loan['interest_rate']}%",
                    f"{loan['term_months']} months",
                    loan['start_date'].strftime('%Y-%m-%d'),
                    loan['status'],
                    "Edit | Payments"
                ))
        except Error as e:
            messagebox.showerror("Error", f"Failed to fetch loans: {e}")
    
    def show_add_loan(self):
        self.loan_form_window = tk.Toplevel(self.root)
        self.loan_form_window.title("Add New Loan")
        self.loan_form_window.geometry("600x500")
        
        form_frame = tk.Frame(self.loan_form_window, padx=20, pady=20)
        form_frame.pack(fill='both', expand=True)
        
        # Customer selection
        tk.Label(form_frame, text="Customer:").grid(row=0, column=0, sticky='e', pady=5)
        self.customer_var = tk.StringVar()
        self.customer_dropdown = ttk.Combobox(form_frame, textvariable=self.customer_var, width=40)
        self.customer_dropdown.grid(row=0, column=1, pady=5)
        
        # Populate customers
        self.populate_customer_dropdown()
        
        # Loan amount
        tk.Label(form_frame, text="Loan Amount:").grid(row=1, column=0, sticky='e', pady=5)
        self.amount_entry = tk.Entry(form_frame, width=30)
        self.amount_entry.grid(row=1, column=1, pady=5)
        
        # Interest rate
        tk.Label(form_frame, text="Interest Rate (%):").grid(row=2, column=0, sticky='e', pady=5)
        self.interest_entry = tk.Entry(form_frame, width=30)
        self.interest_entry.grid(row=2, column=1, pady=5)
        
        # Term (months)
        tk.Label(form_frame, text="Term (months):").grid(row=3, column=0, sticky='e', pady=5)
        self.term_entry = tk.Entry(form_frame, width=30)
        self.term_entry.grid(row=3, column=1, pady=5)
        
        # Start date
        tk.Label(form_frame, text="Start Date (YYYY-MM-DD):").grid(row=4, column=0, sticky='e', pady=5)
        self.start_date_entry = tk.Entry(form_frame, width=30)
        self.start_date_entry.grid(row=4, column=1, pady=5)
        self.start_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        # Purpose
        tk.Label(form_frame, text="Purpose:").grid(row=5, column=0, sticky='e', pady=5)
        self.purpose_entry = tk.Entry(form_frame, width=30)
        self.purpose_entry.grid(row=5, column=1, pady=5)
        
        # Status
        tk.Label(form_frame, text="Status:").grid(row=6, column=0, sticky='e', pady=5)
        self.status_var = tk.StringVar(value="Active")
        status_options = ["Active", "Paid", "Defaulted"]
        self.status_dropdown = ttk.Combobox(form_frame, textvariable=self.status_var, 
                                          values=status_options, width=27)
        self.status_dropdown.grid(row=6, column=1, pady=5)
        
        button_frame = tk.Frame(form_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        save_btn = tk.Button(button_frame, text="Save", width=10, 
                            command=self.save_loan)
        save_btn.pack(side='left', padx=10)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", width=10,
                             command=self.loan_form_window.destroy)
        cancel_btn.pack(side='left', padx=10)
    
    def populate_customer_dropdown(self):
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT customer_id, first_name, last_name FROM customers ORDER BY last_name, first_name")
            customers = cursor.fetchall()
            
            customer_list = []
            self.customer_id_map = {}
            
            for customer in customers:
                display_name = f"{customer['last_name']}, {customer['first_name']} (ID: {customer['customer_id']})"
                customer_list.append(display_name)
                self.customer_id_map[display_name] = customer['customer_id']
            
            self.customer_dropdown['values'] = customer_list
        except Error as e:
            messagebox.showerror("Error", f"Failed to fetch customers: {e}")
    
    def save_loan(self):
        customer_display = self.customer_var.get()
        amount = self.amount_entry.get()
        interest_rate = self.interest_entry.get()
        term_months = self.term_entry.get()
        start_date = self.start_date_entry.get()
        purpose = self.purpose_entry.get()
        status = self.status_var.get()
        
        if not customer_display or not amount or not interest_rate or not term_months or not start_date:
            messagebox.showerror("Error", "Please fill all required fields!")
            return
        
        try:
            customer_id = self.customer_id_map[customer_display]
            amount = float(amount)
            interest_rate = float(interest_rate)
            term_months = int(term_months)
            
            cursor = self.connection.cursor()
            query = """
                INSERT INTO loans (customer_id, amount, interest_rate, term_months, start_date, status, purpose)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (customer_id, amount, interest_rate, term_months, 
                                 start_date, status, purpose))
            self.connection.commit()
            messagebox.showinfo("Success", "Loan added successfully!")
            self.loan_form_window.destroy()
            self.populate_loans()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for amount, interest rate, and term!")
        except Error as e:
            messagebox.showerror("Error", f"Failed to add loan: {e}")
    
    def edit_loan(self, event):
        selected_item = self.loans_tree.focus()
        if not selected_item:
            return
        
        item_data = self.loans_tree.item(selected_item)
        loan_id = item_data['values'][0]
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT l.*, CONCAT(c.first_name, ' ', c.last_name) as customer_name
                FROM loans l
                JOIN customers c ON l.customer_id = c.customer_id
                WHERE l.loan_id = %s
            """
            cursor.execute(query, (loan_id,))
            loan = cursor.fetchone()
            
            if loan:
                self.show_edit_loan_form(loan)
        except Error as e:
            messagebox.showerror("Error", f"Failed to fetch loan: {e}")
    
    def show_edit_loan_form(self, loan):
        self.edit_loan_window = tk.Toplevel(self.root)
        self.edit_loan_window.title("Edit Loan")
        self.edit_loan_window.geometry("600x500")
        
        form_frame = tk.Frame(self.edit_loan_window, padx=20, pady=20)
        form_frame.pack(fill='both', expand=True)
        
        # Customer display (read-only)
        tk.Label(form_frame, text="Customer:").grid(row=0, column=0, sticky='e', pady=5)
        customer_label = tk.Label(form_frame, text=loan['customer_name'])
        customer_label.grid(row=0, column=1, pady=5, sticky='w')
        
        # Loan amount
        tk.Label(form_frame, text="Loan Amount:").grid(row=1, column=0, sticky='e', pady=5)
        self.edit_amount_entry = tk.Entry(form_frame, width=30)
        self.edit_amount_entry.grid(row=1, column=1, pady=5)
        self.edit_amount_entry.insert(0, loan['amount'])
        
        # Interest rate
        tk.Label(form_frame, text="Interest Rate (%):").grid(row=2, column=0, sticky='e', pady=5)
        self.edit_interest_entry = tk.Entry(form_frame, width=30)
        self.edit_interest_entry.grid(row=2, column=1, pady=5)
        self.edit_interest_entry.insert(0, loan['interest_rate'])
        
        # Term (months)
        tk.Label(form_frame, text="Term (months):").grid(row=3, column=0, sticky='e', pady=5)
        self.edit_term_entry = tk.Entry(form_frame, width=30)
        self.edit_term_entry.grid(row=3, column=1, pady=5)
        self.edit_term_entry.insert(0, loan['term_months'])
        
        # Start date
        tk.Label(form_frame, text="Start Date (YYYY-MM-DD):").grid(row=4, column=0, sticky='e', pady=5)
        self.edit_start_date_entry = tk.Entry(form_frame, width=30)
        self.edit_start_date_entry.grid(row=4, column=1, pady=5)
        self.edit_start_date_entry.insert(0, loan['start_date'].strftime('%Y-%m-%d'))
        
        # Purpose
        tk.Label(form_frame, text="Purpose:").grid(row=5, column=0, sticky='e', pady=5)
        self.edit_purpose_entry = tk.Entry(form_frame, width=30)
        self.edit_purpose_entry.grid(row=5, column=1, pady=5)
        self.edit_purpose_entry.insert(0, loan['purpose'] if loan['purpose'] else "")
        
        # Status
        tk.Label(form_frame, text="Status:").grid(row=6, column=0, sticky='e', pady=5)
        self.edit_status_var = tk.StringVar(value=loan['status'])
        status_options = ["Active", "Paid", "Defaulted"]
        self.edit_status_dropdown = ttk.Combobox(form_frame, textvariable=self.edit_status_var, 
                                               values=status_options, width=27)
        self.edit_status_dropdown.grid(row=6, column=1, pady=5)
        
        button_frame = tk.Frame(form_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        update_btn = tk.Button(button_frame, text="Update", width=10, 
                             command=lambda: self.update_loan(loan['loan_id']))
        update_btn.pack(side='left', padx=10)
        
        payments_btn = tk.Button(button_frame, text="View Payments", width=12,
                               command=lambda: self.show_loan_payments(loan['loan_id']))
        payments_btn.pack(side='left', padx=10)
        
        add_payment_btn = tk.Button(button_frame, text="Add Payment", width=12,
                                  command=lambda: self.show_add_payment(loan['loan_id']))
        add_payment_btn.pack(side='left', padx=10)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", width=10,
                             command=self.edit_loan_window.destroy)
        cancel_btn.pack(side='left', padx=10)
    
    def update_loan(self, loan_id):
        amount = self.edit_amount_entry.get()
        interest_rate = self.edit_interest_entry.get()
        term_months = self.edit_term_entry.get()
        start_date = self.edit_start_date_entry.get()
        purpose = self.edit_purpose_entry.get()
        status = self.edit_status_var.get()
        
        if not amount or not interest_rate or not term_months or not start_date:
            messagebox.showerror("Error", "Please fill all required fields!")
            return
        
        try:
            amount = float(amount)
            interest_rate = float(interest_rate)
            term_months = int(term_months)
            
            cursor = self.connection.cursor()
            query = """
                UPDATE loans 
                SET amount = %s, interest_rate = %s, term_months = %s, 
                    start_date = %s, purpose = %s, status = %s
                WHERE loan_id = %s
            """
            cursor.execute(query, (amount, interest_rate, term_months, 
                                 start_date, purpose, status, loan_id))
            self.connection.commit()
            messagebox.showinfo("Success", "Loan updated successfully!")
            self.edit_loan_window.destroy()
            self.populate_loans()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for amount, interest rate, and term!")
        except Error as e:
            messagebox.showerror("Error", f"Failed to update loan: {e}")
    
    def search_loans(self):
        search_term = self.loan_search_entry.get()
        
        try:
            # Clear existing data
            for row in self.loans_tree.get_children():
                self.loans_tree.delete(row)
            
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT l.loan_id, CONCAT(c.first_name, ' ', c.last_name) as customer, 
                       l.amount, l.interest_rate, l.term_months, l.start_date, l.status
                FROM loans l
                JOIN customers c ON l.customer_id = c.customer_id
                WHERE CONCAT(c.first_name, ' ', c.last_name) LIKE %s 
                   OR l.status LIKE %s
                   OR l.loan_id LIKE %s
                ORDER BY l.start_date DESC
            """
            cursor.execute(query, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
            loans = cursor.fetchall()
            
            for loan in loans:
                self.loans_tree.insert("", "end", values=(
                    loan['loan_id'],
                    loan['customer'],
                    f"${loan['amount']:,.2f}",
                    f"{loan['interest_rate']}%",
                    f"{loan['term_months']} months",
                    loan['start_date'].strftime('%Y-%m-%d'),
                    loan['status'],
                    "Edit | Payments"
                ))
        except Error as e:
            messagebox.showerror("Error", f"Failed to search loans: {e}")
    
    def show_payments(self):
        self.clear_main_frame()
        
        # Payments title
        title_label = tk.Label(self.main_frame, text="Payment Management", font=self.title_font, bg='#f0f0f0')
        title_label.pack(pady=(0, 20), anchor='w')
        
        # Stats frame
        stats_frame = tk.Frame(self.main_frame, bg='#f0f0f0')
        stats_frame.pack(fill='x', pady=(0, 20))
        
        # Recent payments table
        table_frame = tk.Frame(self.main_frame, bg='#f0f0f0')
        table_frame.pack(fill='both', expand=True)
        
        columns = ("ID", "Loan ID", "Customer", "Amount", "Date", "Method")
        self.payments_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        for col in columns:
            self.payments_tree.heading(col, text=col)
            self.payments_tree.column(col, width=120)
        
        self.payments_tree.pack(fill='both', expand=True)
        
        # Populate payments
        self.populate_recent_payments()
    
    def populate_recent_payments(self):
        try:
            # Clear existing data
            for row in self.payments_tree.get_children():
                self.payments_tree.delete(row)
            
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT p.payment_id, p.loan_id, 
                       CONCAT(c.first_name, ' ', c.last_name) as customer,
                       p.amount, p.payment_date, p.payment_method
                FROM payments p
                JOIN loans l ON p.loan_id = l.loan_id
                JOIN customers c ON l.customer_id = c.customer_id
                ORDER BY p.payment_date DESC
                LIMIT 50
            """
            cursor.execute(query)
            payments = cursor.fetchall()
            
            for payment in payments:
                self.payments_tree.insert("", "end", values=(
                    payment['payment_id'],
                    payment['loan_id'],
                    payment['customer'],
                    f"${payment['amount']:,.2f}",
                    payment['payment_date'].strftime('%Y-%m-%d'),
                    payment['payment_method']
                ))
        except Error as e:
            messagebox.showerror("Error", f"Failed to fetch payments: {e}")
    
    def show_loan_payments(self, loan_id):
        self.payments_window = tk.Toplevel(self.root)
        self.payments_window.title(f"Payments for Loan #{loan_id}")
        self.payments_window.geometry("800x500")
        
        main_frame = tk.Frame(self.payments_window, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Get loan details
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT l.*, CONCAT(c.first_name, ' ', c.last_name) as customer_name
                FROM loans l
                JOIN customers c ON l.customer_id = c.customer_id
                WHERE l.loan_id = %s
            """
            cursor.execute(query, (loan_id,))
            loan = cursor.fetchone()
            
            if loan:
                # Loan summary
                summary_frame = tk.LabelFrame(main_frame, text="Loan Summary", padx=10, pady=10)
                summary_frame.pack(fill='x', pady=(0, 20))
                
                tk.Label(summary_frame, text=f"Customer: {loan['customer_name']}").pack(anchor='w')
                tk.Label(summary_frame, text=f"Amount: ${loan['amount']:,.2f}").pack(anchor='w')
                tk.Label(summary_frame, text=f"Interest Rate: {loan['interest_rate']}%").pack(anchor='w')
                tk.Label(summary_frame, text=f"Term: {loan['term_months']} months").pack(anchor='w')
                tk.Label(summary_frame, text=f"Status: {loan['status']}").pack(anchor='w')
                
                # Payments table
                table_frame = tk.Frame(main_frame)
                table_frame.pack(fill='both', expand=True)
                
                columns = ("ID", "Amount", "Date", "Method")
                self.loan_payments_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
                
                for col in columns:
                    self.loan_payments_tree.heading(col, text=col)
                    self.loan_payments_tree.column(col, width=120)
                
                self.loan_payments_tree.pack(fill='both', expand=True)
                
                # Populate payments for this loan
                self.populate_loan_payments(loan_id)
                
                # Add payment button
                add_payment_btn = tk.Button(main_frame, text="Add Payment", 
                                          command=lambda: self.show_add_payment(loan_id))
                add_payment_btn.pack(pady=(10, 0))
        except Error as e:
            messagebox.showerror("Error", f"Failed to fetch loan details: {e}")
    
    def populate_loan_payments(self, loan_id):
        try:
            # Clear existing data
            for row in self.loan_payments_tree.get_children():
                self.loan_payments_tree.delete(row)
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM payments 
                WHERE loan_id = %s
                ORDER BY payment_date DESC
            """, (loan_id,))
            payments = cursor.fetchall()
            
            for payment in payments:
                self.loan_payments_tree.insert("", "end", values=(
                    payment['payment_id'],
                    f"${payment['amount']:,.2f}",
                    payment['payment_date'].strftime('%Y-%m-%d'),
                    payment['payment_method']
                ))
        except Error as e:
            messagebox.showerror("Error", f"Failed to fetch payments: {e}")
    
    def show_add_payment(self, loan_id):
        self.add_payment_window = tk.Toplevel(self.root)
        self.add_payment_window.title(f"Add Payment for Loan #{loan_id}")
        self.add_payment_window.geometry("400x300")
        
        form_frame = tk.Frame(self.add_payment_window, padx=20, pady=20)
        form_frame.pack(fill='both', expand=True)
        
        tk.Label(form_frame, text="Amount:").grid(row=0, column=0, sticky='e', pady=5)
        self.payment_amount_entry = tk.Entry(form_frame, width=30)
        self.payment_amount_entry.grid(row=0, column=1, pady=5)
        
        tk.Label(form_frame, text="Date (YYYY-MM-DD):").grid(row=1, column=0, sticky='e', pady=5)
        self.payment_date_entry = tk.Entry(form_frame, width=30)
        self.payment_date_entry.grid(row=1, column=1, pady=5)
        self.payment_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        tk.Label(form_frame, text="Method:").grid(row=2, column=0, sticky='e', pady=5)
        self.payment_method_var = tk.StringVar(value="Bank Transfer")
        method_options = ["Cash", "Bank Transfer", "Check", "Other"]
        self.payment_method_dropdown = ttk.Combobox(form_frame, textvariable=self.payment_method_var, 
                                                  values=method_options, width=27)
        self.payment_method_dropdown.grid(row=2, column=1, pady=5)
        
        button_frame = tk.Frame(form_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        save_btn = tk.Button(button_frame, text="Save", width=10, 
                            command=lambda: self.save_payment(loan_id))
        save_btn.pack(side='left', padx=10)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", width=10,
                             command=self.add_payment_window.destroy)
        cancel_btn.pack(side='left', padx=10)
    
    def save_payment(self, loan_id):
        amount = self.payment_amount_entry.get()
        payment_date = self.payment_date_entry.get()
        payment_method = self.payment_method_var.get()
        
        if not amount or not payment_date:
            messagebox.showerror("Error", "Amount and date are required!")
            return
        
        try:
            amount = float(amount)
            
            cursor = self.connection.cursor()
            query = """
                INSERT INTO payments (loan_id, amount, payment_date, payment_method)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (loan_id, amount, payment_date, payment_method))
            self.connection.commit()
            messagebox.showinfo("Success", "Payment added successfully!")
            
            self.add_payment_window.destroy()
            
            # Refresh payments view if it's open
            if hasattr(self, 'payments_window') and self.payments_window.winfo_exists():
                self.populate_loan_payments(loan_id)
            
            # Refresh dashboard
            self.show_dashboard()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for amount!")
        except Error as e:
            messagebox.showerror("Error", f"Failed to add payment: {e}")
    
    def show_reports(self):
        self.clear_main_frame()
        
        # Reports title
        title_label = tk.Label(self.main_frame, text="Reports", font=self.title_font, bg='#f0f0f0')
        title_label.pack(pady=(0, 20), anchor='w')
        
        # Report options
        options_frame = tk.Frame(self.main_frame, bg='#f0f0f0')
        options_frame.pack(fill='x', pady=(0, 20))
        
        report_types = [
            ("Loan Status Summary", self.generate_loan_status_report),
            ("Monthly Payments", self.generate_monthly_payments_report),
            ("Customer Loan Summary", self.generate_customer_loan_report)
        ]
        
        for i, (text, command) in enumerate(report_types):
            btn = tk.Button(options_frame, text=text, font=self.button_font,
                           bg='#3498db', fg='white', width=20, command=command)
            btn.grid(row=0, column=i, padx=10)
        
        # Report display area
        self.report_text = tk.Text(self.main_frame, wrap=tk.WORD, width=80, height=20)
        self.report_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Export button
        export_btn = tk.Button(self.main_frame, text="Export to File", font=self.button_font,
                             bg='#2ecc71', fg='white', command=self.export_report)
        export_btn.pack(pady=(10, 0))
    
    def generate_loan_status_report(self):
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT status, COUNT(*) as count, SUM(amount) as total_amount
                FROM loans
                GROUP BY status
            """
            cursor.execute(query)
            results = cursor.fetchall()
            
            report = "=== Loan Status Summary ===\n\n"
            report += f"{'Status':<15} {'Count':>10} {'Total Amount':>15}\n"
            report += "-" * 42 + "\n"
            
            for row in results:
                report += f"{row['status']:<15} {row['count']:>10} ${row['total_amount']:>14,.2f}\n"
            
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(tk.END, report)
        except Error as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")
    
    def generate_monthly_payments_report(self):
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT 
                    DATE_FORMAT(payment_date, '%Y-%m') as month,
                    COUNT(*) as payment_count,
                    SUM(amount) as total_payments
                FROM payments
                GROUP BY DATE_FORMAT(payment_date, '%Y-%m')
                ORDER BY month
            """
            cursor.execute(query)
            results = cursor.fetchall()
            
            report = "=== Monthly Payments Report ===\n\n"
            report += f"{'Month':<10} {'Payments':>10} {'Total Amount':>15}\n"
            report += "-" * 37 + "\n"
            
            for row in results:
                report += f"{row['month']:<10} {row['payment_count']:>10} ${row['total_payments']:>14,.2f}\n"
            
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(tk.END, report)
        except Error as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")
    
    def generate_customer_loan_report(self):
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT 
                    c.customer_id,
                    CONCAT(c.first_name, ' ', c.last_name) as customer_name,
                    COUNT(l.loan_id) as loan_count,
                    SUM(l.amount) as total_loans
                FROM customers c
                LEFT JOIN loans l ON c.customer_id = l.customer_id
                GROUP BY c.customer_id, customer_name
                ORDER BY total_loans DESC
            """
            cursor.execute(query)
            results = cursor.fetchall()
            
            report = "=== Customer Loan Summary ===\n\n"
            report += f"{'Customer ID':<12} {'Customer Name':<25} {'Loans':>10} {'Total Amount':>15}\n"
            report += "-" * 64 + "\n"
            
            for row in results:
                loan_count = row['loan_count'] if row['loan_count'] else 0
                total_loans = row['total_loans'] if row['total_loans'] else 0
                report += f"{row['customer_id']:<12} {row['customer_name'][:24]:<25} {loan_count:>10} ${total_loans:>14,.2f}\n"
            
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(tk.END, report)
        except Error as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")
    
    def export_report(self):
        report_content = self.report_text.get(1.0, tk.END)
        if not report_content.strip():
            messagebox.showwarning("Warning", "No report content to export!")
            return
        
        from datetime import datetime
        import os
        
        # Create reports directory if it doesn't exist
        if not os.path.exists("reports"):
            os.makedirs("reports")
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reports/report_{timestamp}.txt"
        
        try:
            with open(filename, 'w') as f:
                f.write(report_content)
            messagebox.showinfo("Success", f"Report exported successfully to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export report: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LoanManagementSystem(root)
    root.mainloop()