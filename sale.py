import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.font import Font
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import os
import webbrowser

class SalesBillingSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Sales and Billing System")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f0f0f0")
        
        # Database connection parameters
        self.db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '1234',  # Enter your MySQL password here
            'database': 'sales_billing_db'
        }
        
        # Connect to database
        self.connection = self.connect_to_database()
        self.create_tables()
        
        # Custom fonts
        self.title_font = Font(family="Helvetica", size=18, weight="bold")
        self.label_font = Font(family="Helvetica", size=12)
        self.button_font = Font(family="Helvetica", size=12, weight="bold")
        
        # Colors
        self.primary_color = "#4e73df"
        self.secondary_color = "#2e59d9"
        self.accent_color = "#1cc88a"
        self.danger_color = "#e74a3b"
        
        # Create main container
        self.create_main_container()
        
        # Initialize variables
        self.current_user = "Admin"
        self.cart_items = []
        self.total_amount = 0.0
        
    def connect_to_database(self):
        """Establish connection to MySQL database"""
        try:
            connection = mysql.connector.connect(**self.db_config)
            if connection.is_connected():
                print("Connected to MySQL database")
                return connection
        except Error as e:
            messagebox.showerror("Database Error", f"Error connecting to MySQL: {e}")
            self.root.destroy()
    
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            cursor = self.connection.cursor()
            
            # Create products table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    product_id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    price DECIMAL(10, 2) NOT NULL,
                    quantity INT NOT NULL,
                    category VARCHAR(50),
                    barcode VARCHAR(50) UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create customers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100),
                    phone VARCHAR(20),
                    address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create invoices table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS invoices (
                    invoice_id INT AUTO_INCREMENT PRIMARY KEY,
                    customer_id INT,
                    invoice_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_amount DECIMAL(10, 2) NOT NULL,
                    discount DECIMAL(10, 2) DEFAULT 0,
                    tax DECIMAL(10, 2) DEFAULT 0,
                    payment_method VARCHAR(50),
                    status VARCHAR(20) DEFAULT 'Pending',
                    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
                )
            """)
            
            # Create invoice_items table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS invoice_items (
                    item_id INT AUTO_INCREMENT PRIMARY KEY,
                    invoice_id INT,
                    product_id INT,
                    quantity INT NOT NULL,
                    unit_price DECIMAL(10, 2) NOT NULL,
                    total_price DECIMAL(10, 2) NOT NULL,
                    FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id),
                    FOREIGN KEY (product_id) REFERENCES products(product_id)
                )
            """)
            
            self.connection.commit()
            cursor.close()
        except Error as e:
            messagebox.showerror("Database Error", f"Error creating tables: {e}")
    
    def create_main_container(self):
        """Create the main container with navigation and content frame"""
        # Main container
        self.main_container = tk.Frame(self.root, bg="#f8f9fc")
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Navigation sidebar
        self.create_sidebar()
        
        # Content frame
        self.content_frame = tk.Frame(self.main_container, bg="#f8f9fc")
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Show dashboard by default
        self.show_dashboard()
    
    def create_sidebar(self):
        """Create the navigation sidebar"""
        sidebar = tk.Frame(self.main_container, bg=self.primary_color, width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        
        # Logo/Title
        logo_frame = tk.Frame(sidebar, bg=self.secondary_color)
        logo_frame.pack(fill=tk.X)
        
        logo_label = tk.Label(logo_frame, text="SalesPro", font=self.title_font, 
                             bg=self.secondary_color, fg="white", padx=20, pady=20)
        logo_label.pack(fill=tk.X)
        
        # Navigation buttons
        nav_buttons = [
            ("Dashboard", self.show_dashboard),
            ("Products", self.show_products),
            ("Customers", self.show_customers),
            ("New Sale", self.show_new_sale),
            ("Sales History", self.show_sales_history),
            ("Reports", self.show_reports),
            ("Settings", self.show_settings)
        ]
        
        for text, command in nav_buttons:
            btn = tk.Button(sidebar, text=text, font=self.button_font, bg=self.primary_color, 
                           fg="white", bd=0, padx=20, pady=15, anchor="w", 
                           command=command, relief=tk.FLAT)
            btn.pack(fill=tk.X)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#3a56b7"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.primary_color))
        
        # Logout button
        logout_btn = tk.Button(sidebar, text="Logout", font=self.button_font, 
                              bg=self.danger_color, fg="white", bd=0, padx=20, pady=15, 
                              anchor="w", command=self.logout, relief=tk.FLAT)
        logout_btn.pack(side=tk.BOTTOM, fill=tk.X)
        logout_btn.bind("<Enter>", lambda e: logout_btn.config(bg="#c0392b"))
        logout_btn.bind("<Leave>", lambda e: logout_btn.config(bg=self.danger_color))
    
    def clear_content_frame(self):
        """Clear the content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        """Show dashboard content"""
        self.clear_content_frame()
        
        # Header
        header = tk.Frame(self.content_frame, bg="white")
        header.pack(fill=tk.X, padx=20, pady=20)
        
        title = tk.Label(header, text="Dashboard", font=self.title_font, bg="white")
        title.pack(side=tk.LEFT)
        
        # Dashboard cards
        cards_frame = tk.Frame(self.content_frame, bg="#f8f9fc")
        cards_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Card data
        cards = [
            {"title": "Total Sales", "value": "$12,345", "color": self.primary_color, "icon": "📊"},
            {"title": "Products", "value": "245", "color": self.accent_color, "icon": "📦"},
            {"title": "Customers", "value": "89", "color": "#36b9cc", "icon": "👥"},
            {"title": "Pending Orders", "value": "12", "color": "#f6c23e", "icon": "⏳"}
        ]
        
        for card in cards:
            card_frame = tk.Frame(cards_frame, bg="white", bd=1, relief=tk.RIDGE)
            card_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            icon = tk.Label(card_frame, text=card["icon"], font=("Arial", 24), bg="white")
            icon.pack(side=tk.LEFT, padx=15, pady=15)
            
            text_frame = tk.Frame(card_frame, bg="white")
            text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            title_label = tk.Label(text_frame, text=card["title"], font=self.label_font, 
                                 bg="white", fg="#858796")
            title_label.pack(anchor="w")
            
            value_label = tk.Label(text_frame, text=card["value"], font=("Helvetica", 20, "bold"), 
                                  bg="white", fg=card["color"])
            value_label.pack(anchor="w")
        
        # Recent Sales Table
        recent_sales_frame = tk.Frame(self.content_frame, bg="white", bd=1, relief=tk.RIDGE)
        recent_sales_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        table_title = tk.Label(recent_sales_frame, text="Recent Sales", font=self.label_font, 
                              bg="white", padx=10, pady=10)
        table_title.pack(anchor="w")
        
        # Create treeview
        columns = ("invoice_id", "customer", "date", "amount", "status")
        tree = ttk.Treeview(recent_sales_frame, columns=columns, show="headings", height=10)
        
        # Define headings
        tree.heading("invoice_id", text="Invoice ID")
        tree.heading("customer", text="Customer")
        tree.heading("date", text="Date")
        tree.heading("amount", text="Amount")
        tree.heading("status", text="Status")
        
        # Configure columns
        tree.column("invoice_id", width=100, anchor="center")
        tree.column("customer", width=200, anchor="w")
        tree.column("date", width=150, anchor="center")
        tree.column("amount", width=100, anchor="e")
        tree.column("status", width=100, anchor="center")
        
        # Add sample data (in a real app, fetch from database)
        sample_data = [
            ("INV-1001", "John Doe", "2023-05-15", "$125.00", "Paid"),
            ("INV-1000", "Jane Smith", "2023-05-14", "$89.50", "Paid"),
            ("INV-0999", "Acme Corp", "2023-05-13", "$1,245.75", "Pending"),
            ("INV-0998", "Bob Johnson", "2023-05-12", "$56.20", "Paid"),
            ("INV-0997", "Alice Brown", "2023-05-11", "$342.90", "Paid"),
        ]
        
        for data in sample_data:
            tree.insert("", tk.END, values=data)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(recent_sales_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def show_products(self):
        """Show products management"""
        self.clear_content_frame()
        
        # Header
        header = tk.Frame(self.content_frame, bg="white")
        header.pack(fill=tk.X, padx=20, pady=20)
        
        title = tk.Label(header, text="Product Management", font=self.title_font, bg="white")
        title.pack(side=tk.LEFT)
        
        # Add product button
        add_btn = tk.Button(header, text="Add Product", font=self.button_font, 
                          bg=self.accent_color, fg="white", command=self.show_add_product)
        add_btn.pack(side=tk.RIGHT, padx=10)
        
        # Search frame
        search_frame = tk.Frame(self.content_frame, bg="white", padx=10, pady=10)
        search_frame.pack(fill=tk.X, padx=20)
        
        search_label = tk.Label(search_frame, text="Search:", font=self.label_font, bg="white")
        search_label.pack(side=tk.LEFT)
        
        self.search_entry = tk.Entry(search_frame, font=self.label_font, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=10)
        
        search_btn = tk.Button(search_frame, text="Search", font=self.button_font, 
                             bg=self.primary_color, fg="white", command=self.search_products)
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # Products table
        table_frame = tk.Frame(self.content_frame, bg="white", bd=1, relief=tk.RIDGE)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create treeview
        columns = ("id", "name", "price", "quantity", "category", "actions")
        self.products_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Define headings
        self.products_tree.heading("id", text="ID")
        self.products_tree.heading("name", text="Name")
        self.products_tree.heading("price", text="Price")
        self.products_tree.heading("quantity", text="Qty")
        self.products_tree.heading("category", text="Category")
        self.products_tree.heading("actions", text="Actions")
        
        # Configure columns
        self.products_tree.column("id", width=50, anchor="center")
        self.products_tree.column("name", width=200, anchor="w")
        self.products_tree.column("price", width=100, anchor="e")
        self.products_tree.column("quantity", width=80, anchor="center")
        self.products_tree.column("category", width=150, anchor="w")
        self.products_tree.column("actions", width=150, anchor="center")
        
        # Add sample data (in a real app, fetch from database)
        sample_products = [
            (1, "Wireless Mouse", 24.99, 45, "Electronics"),
            (2, "Mechanical Keyboard", 89.99, 32, "Electronics"),
            (3, "Notebook", 4.99, 120, "Stationery"),
            (4, "Coffee Mug", 12.50, 65, "Home"),
            (5, "Bluetooth Speaker", 59.99, 28, "Electronics"),
        ]
        
        for product in sample_products:
            self.products_tree.insert("", tk.END, values=product + ("Edit | Delete",))
        
        self.products_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.products_tree.yview)
        self.products_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double click to edit
        self.products_tree.bind("<Double-1>", self.edit_product)
    
    def show_add_product(self):
        """Show add product dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Product")
        dialog.geometry("500x500")
        dialog.resizable(False, False)
        dialog.grab_set()
        
        # Form frame
        form_frame = tk.Frame(dialog, padx=20, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Form fields
        tk.Label(form_frame, text="Product Name:", font=self.label_font).grid(row=0, column=0, sticky="w", pady=5)
        name_entry = tk.Entry(form_frame, font=self.label_font, width=30)
        name_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=10)
        
        tk.Label(form_frame, text="Description:", font=self.label_font).grid(row=1, column=0, sticky="nw", pady=5)
        desc_text = tk.Text(form_frame, font=self.label_font, width=30, height=5)
        desc_text.grid(row=1, column=1, sticky="ew", pady=5, padx=10)
        
        tk.Label(form_frame, text="Price:", font=self.label_font).grid(row=2, column=0, sticky="w", pady=5)
        price_entry = tk.Entry(form_frame, font=self.label_font, width=30)
        price_entry.grid(row=2, column=1, sticky="ew", pady=5, padx=10)
        
        tk.Label(form_frame, text="Quantity:", font=self.label_font).grid(row=3, column=0, sticky="w", pady=5)
        qty_entry = tk.Entry(form_frame, font=self.label_font, width=30)
        qty_entry.grid(row=3, column=1, sticky="ew", pady=5, padx=10)
        
        tk.Label(form_frame, text="Category:", font=self.label_font).grid(row=4, column=0, sticky="w", pady=5)
        category_entry = tk.Entry(form_frame, font=self.label_font, width=30)
        category_entry.grid(row=4, column=1, sticky="ew", pady=5, padx=10)
        
        tk.Label(form_frame, text="Barcode:", font=self.label_font).grid(row=5, column=0, sticky="w", pady=5)
        barcode_entry = tk.Entry(form_frame, font=self.label_font, width=30)
        barcode_entry.grid(row=5, column=1, sticky="ew", pady=5, padx=10)
        
        # Button frame
        button_frame = tk.Frame(form_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        save_btn = tk.Button(button_frame, text="Save Product", font=self.button_font, 
                            bg=self.accent_color, fg="white", padx=20, pady=5,
                            command=lambda: self.save_product(
                                name_entry.get(),
                                desc_text.get("1.0", tk.END),
                                price_entry.get(),
                                qty_entry.get(),
                                category_entry.get(),
                                barcode_entry.get(),
                                dialog
                            ))
        save_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", font=self.button_font, 
                             bg="#858796", fg="white", padx=20, pady=5,
                             command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=10)
    
    def save_product(self, name, description, price, quantity, category, barcode, dialog):
        """Save product to database"""
        if not all([name, price, quantity]):
            messagebox.showerror("Error", "Please fill in all required fields")
            return
        
        try:
            cursor = self.connection.cursor()
            query = """
                INSERT INTO products (name, description, price, quantity, category, barcode)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (name, description, float(price), int(quantity), category, barcode))
            self.connection.commit()
            cursor.close()
            
            messagebox.showinfo("Success", "Product added successfully")
            dialog.destroy()
            self.show_products()  # Refresh product list
        except Error as e:
            messagebox.showerror("Database Error", f"Error saving product: {e}")
    
    def edit_product(self, event):
        """Edit product"""
        item = self.products_tree.selection()[0]
        product_data = self.products_tree.item(item, "values")
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Product")
        dialog.geometry("500x500")
        dialog.resizable(False, False)
        dialog.grab_set()
        
        # Form frame
        form_frame = tk.Frame(dialog, padx=20, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Form fields with existing data
        tk.Label(form_frame, text="Product Name:", font=self.label_font).grid(row=0, column=0, sticky="w", pady=5)
        name_entry = tk.Entry(form_frame, font=self.label_font, width=30)
        name_entry.insert(0, product_data[1])
        name_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=10)
        
        tk.Label(form_frame, text="Price:", font=self.label_font).grid(row=1, column=0, sticky="w", pady=5)
        price_entry = tk.Entry(form_frame, font=self.label_font, width=30)
        price_entry.insert(0, product_data[2])
        price_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=10)
        
        tk.Label(form_frame, text="Quantity:", font=self.label_font).grid(row=2, column=0, sticky="w", pady=5)
        qty_entry = tk.Entry(form_frame, font=self.label_font, width=30)
        qty_entry.insert(0, product_data[3])
        qty_entry.grid(row=2, column=1, sticky="ew", pady=5, padx=10)
        
        tk.Label(form_frame, text="Category:", font=self.label_font).grid(row=3, column=0, sticky="w", pady=5)
        category_entry = tk.Entry(form_frame, font=self.label_font, width=30)
        category_entry.insert(0, product_data[4])
        category_entry.grid(row=3, column=1, sticky="ew", pady=5, padx=10)
        
        # Button frame
        button_frame = tk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        update_btn = tk.Button(button_frame, text="Update", font=self.button_font, 
                             bg=self.accent_color, fg="white", padx=20, pady=5,
                             command=lambda: self.update_product(
                                 product_data[0],
                                 name_entry.get(),
                                 price_entry.get(),
                                 qty_entry.get(),
                                 category_entry.get(),
                                 dialog
                             ))
        update_btn.pack(side=tk.LEFT, padx=10)
        
        delete_btn = tk.Button(button_frame, text="Delete", font=self.button_font, 
                             bg=self.danger_color, fg="white", padx=20, pady=5,
                             command=lambda: self.delete_product(product_data[0], dialog))
        delete_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", font=self.button_font, 
                             bg="#858796", fg="white", padx=20, pady=5,
                             command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=10)
    
    def update_product(self, product_id, name, price, quantity, category, dialog):
        """Update product in database"""
        try:
            cursor = self.connection.cursor()
            query = """
                UPDATE products 
                SET name = %s, price = %s, quantity = %s, category = %s
                WHERE product_id = %s
            """
            cursor.execute(query, (name, float(price), int(quantity), category, product_id))
            self.connection.commit()
            cursor.close()
            
            messagebox.showinfo("Success", "Product updated successfully")
            dialog.destroy()
            self.show_products()  # Refresh product list
        except Error as e:
            messagebox.showerror("Database Error", f"Error updating product: {e}")
    
    def delete_product(self, product_id, dialog):
        """Delete product from database"""
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this product?"):
            try:
                cursor = self.connection.cursor()
                query = "DELETE FROM products WHERE product_id = %s"
                cursor.execute(query, (product_id,))
                self.connection.commit()
                cursor.close()
                
                messagebox.showinfo("Success", "Product deleted successfully")
                dialog.destroy()
                self.show_products()  # Refresh product list
            except Error as e:
                messagebox.showerror("Database Error", f"Error deleting product: {e}")
    
    def search_products(self):
        """Search products by name"""
        search_term = self.search_entry.get()
        if not search_term:
            return
        
        # In a real app, you would query the database with the search term
        messagebox.showinfo("Search", f"Searching for: {search_term}")
    
    def show_customers(self):
        """Show customers management"""
        self.clear_content_frame()
        
        # Header
        header = tk.Frame(self.content_frame, bg="white")
        header.pack(fill=tk.X, padx=20, pady=20)
        
        title = tk.Label(header, text="Customer Management", font=self.title_font, bg="white")
        title.pack(side=tk.LEFT)
        
        # Add customer button
        add_btn = tk.Button(header, text="Add Customer", font=self.button_font, 
                           bg=self.accent_color, fg="white", command=self.show_add_customer)
        add_btn.pack(side=tk.RIGHT, padx=10)
        
        # Customers table
        table_frame = tk.Frame(self.content_frame, bg="white", bd=1, relief=tk.RIDGE)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create treeview
        columns = ("id", "name", "email", "phone", "actions")
        self.customers_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Define headings
        self.customers_tree.heading("id", text="ID")
        self.customers_tree.heading("name", text="Name")
        self.customers_tree.heading("email", text="Email")
        self.customers_tree.heading("phone", text="Phone")
        self.customers_tree.heading("actions", text="Actions")
        
        # Configure columns
        self.customers_tree.column("id", width=50, anchor="center")
        self.customers_tree.column("name", width=200, anchor="w")
        self.customers_tree.column("email", width=200, anchor="w")
        self.customers_tree.column("phone", width=150, anchor="w")
        self.customers_tree.column("actions", width=150, anchor="center")
        
        # Add sample data (in a real app, fetch from database)
        sample_customers = [
            (1, "John Doe", "john@example.com", "555-1234"),
            (2, "Jane Smith", "jane@example.com", "555-5678"),
            (3, "Acme Corporation", "contact@acme.com", "555-9012"),
            (4, "Bob Johnson", "bob@example.com", "555-3456"),
            (5, "Alice Brown", "alice@example.com", "555-7890"),
        ]
        
        for customer in sample_customers:
            self.customers_tree.insert("", tk.END, values=customer + ("Edit | Delete",))
        
        self.customers_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.customers_tree.yview)
        self.customers_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double click to edit
        self.customers_tree.bind("<Double-1>", self.edit_customer)
    
    def show_add_customer(self):
        """Show add customer dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Customer")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        dialog.grab_set()
        
        # Form frame
        form_frame = tk.Frame(dialog, padx=20, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Form fields
        tk.Label(form_frame, text="Customer Name:", font=self.label_font).grid(row=0, column=0, sticky="w", pady=5)
        name_entry = tk.Entry(form_frame, font=self.label_font, width=30)
        name_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=10)
        
        tk.Label(form_frame, text="Email:", font=self.label_font).grid(row=1, column=0, sticky="w", pady=5)
        email_entry = tk.Entry(form_frame, font=self.label_font, width=30)
        email_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=10)
        
        tk.Label(form_frame, text="Phone:", font=self.label_font).grid(row=2, column=0, sticky="w", pady=5)
        phone_entry = tk.Entry(form_frame, font=self.label_font, width=30)
        phone_entry.grid(row=2, column=1, sticky="ew", pady=5, padx=10)
        
        tk.Label(form_frame, text="Address:", font=self.label_font).grid(row=3, column=0, sticky="nw", pady=5)
        address_text = tk.Text(form_frame, font=self.label_font, width=30, height=5)
        address_text.grid(row=3, column=1, sticky="ew", pady=5, padx=10)
        
        # Button frame
        button_frame = tk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        save_btn = tk.Button(button_frame, text="Save Customer", font=self.button_font, 
                           bg=self.accent_color, fg="white", padx=20, pady=5,
                           command=lambda: self.save_customer(
                               name_entry.get(),
                               email_entry.get(),
                               phone_entry.get(),
                               address_text.get("1.0", tk.END),
                               dialog
                           ))
        save_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", font=self.button_font, 
                             bg="#858796", fg="white", padx=20, pady=5,
                             command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=10)
    
    def save_customer(self, name, email, phone, address, dialog):
        """Save customer to database"""
        if not name:
            messagebox.showerror("Error", "Customer name is required")
            return
        
        try:
            cursor = self.connection.cursor()
            query = """
                INSERT INTO customers (name, email, phone, address)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (name, email, phone, address))
            self.connection.commit()
            cursor.close()
            
            messagebox.showinfo("Success", "Customer added successfully")
            dialog.destroy()
            self.show_customers()  # Refresh customer list
        except Error as e:
            messagebox.showerror("Database Error", f"Error saving customer: {e}")
    
    def edit_customer(self, event):
        """Edit customer"""
        item = self.customers_tree.selection()[0]
        customer_data = self.customers_tree.item(item, "values")
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Customer")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        dialog.grab_set()
        
        # Form frame
        form_frame = tk.Frame(dialog, padx=20, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Form fields with existing data
        tk.Label(form_frame, text="Customer Name:", font=self.label_font).grid(row=0, column=0, sticky="w", pady=5)
        name_entry = tk.Entry(form_frame, font=self.label_font, width=30)
        name_entry.insert(0, customer_data[1])
        name_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=10)
        
        tk.Label(form_frame, text="Email:", font=self.label_font).grid(row=1, column=0, sticky="w", pady=5)
        email_entry = tk.Entry(form_frame, font=self.label_font, width=30)
        email_entry.insert(0, customer_data[2])
        email_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=10)
        
        tk.Label(form_frame, text="Phone:", font=self.label_font).grid(row=2, column=0, sticky="w", pady=5)
        phone_entry = tk.Entry(form_frame, font=self.label_font, width=30)
        phone_entry.insert(0, customer_data[3])
        phone_entry.grid(row=2, column=1, sticky="ew", pady=5, padx=10)
        
        # Button frame
        button_frame = tk.Frame(form_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        update_btn = tk.Button(button_frame, text="Update", font=self.button_font, 
                             bg=self.accent_color, fg="white", padx=20, pady=5,
                             command=lambda: self.update_customer(
                                 customer_data[0],
                                 name_entry.get(),
                                 email_entry.get(),
                                 phone_entry.get(),
                                 dialog
                             ))
        update_btn.pack(side=tk.LEFT, padx=10)
        
        delete_btn = tk.Button(button_frame, text="Delete", font=self.button_font, 
                             bg=self.danger_color, fg="white", padx=20, pady=5,
                             command=lambda: self.delete_customer(customer_data[0], dialog))
        delete_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", font=self.button_font, 
                             bg="#858796", fg="white", padx=20, pady=5,
                             command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=10)
    
    def update_customer(self, customer_id, name, email, phone, dialog):
        """Update customer in database"""
        try:
            cursor = self.connection.cursor()
            query = """
                UPDATE customers 
                SET name = %s, email = %s, phone = %s
                WHERE customer_id = %s
            """
            cursor.execute(query, (name, email, phone, customer_id))
            self.connection.commit()
            cursor.close()
            
            messagebox.showinfo("Success", "Customer updated successfully")
            dialog.destroy()
            self.show_customers()  # Refresh customer list
        except Error as e:
            messagebox.showerror("Database Error", f"Error updating customer: {e}")
    
    def delete_customer(self, customer_id, dialog):
        """Delete customer from database"""
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this customer?"):
            try:
                cursor = self.connection.cursor()
                query = "DELETE FROM customers WHERE customer_id = %s"
                cursor.execute(query, (customer_id,))
                self.connection.commit()
                cursor.close()
                
                messagebox.showinfo("Success", "Customer deleted successfully")
                dialog.destroy()
                self.show_customers()  # Refresh customer list
            except Error as e:
                messagebox.showerror("Database Error", f"Error deleting customer: {e}")
    
    def show_new_sale(self):
        """Show new sale interface"""
        self.clear_content_frame()
        self.cart_items = []
        self.total_amount = 0.0
        
        # Header
        header = tk.Frame(self.content_frame, bg="white")
        header.pack(fill=tk.X, padx=20, pady=20)
        
        title = tk.Label(header, text="New Sale", font=self.title_font, bg="white")
        title.pack(side=tk.LEFT)
        
        # Main content frame
        content = tk.Frame(self.content_frame, bg="#f8f9fc")
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left frame - Product selection
        left_frame = tk.Frame(content, bg="white", bd=1, relief=tk.RIDGE)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=10)
        
        tk.Label(left_frame, text="Select Products", font=self.label_font, bg="white", padx=10, pady=10).pack(anchor="w")
        
        # Product search
        search_frame = tk.Frame(left_frame, bg="white", padx=10, pady=5)
        search_frame.pack(fill=tk.X)
        
        tk.Label(search_frame, text="Search:", font=self.label_font, bg="white").pack(side=tk.LEFT)
        
        self.product_search = tk.Entry(search_frame, font=self.label_font, width=30)
        self.product_search.pack(side=tk.LEFT, padx=10)
        self.product_search.bind("<Return>", self.search_product_for_sale)
        
        search_btn = tk.Button(search_frame, text="Search", font=self.button_font, 
                             bg=self.primary_color, fg="white", command=lambda: self.search_product_for_sale(None))
        search_btn.pack(side=tk.LEFT)
        
        # Products list
        products_frame = tk.Frame(left_frame, bg="white")
        products_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("id", "name", "price", "stock")
        self.products_sale_tree = ttk.Treeview(products_frame, columns=columns, show="headings", height=10)
        
        # Define headings
        self.products_sale_tree.heading("id", text="ID")
        self.products_sale_tree.heading("name", text="Name")
        self.products_sale_tree.heading("price", text="Price")
        self.products_sale_tree.heading("stock", text="In Stock")
        
        # Configure columns
        self.products_sale_tree.column("id", width=50, anchor="center")
        self.products_sale_tree.column("name", width=200, anchor="w")
        self.products_sale_tree.column("price", width=100, anchor="e")
        self.products_sale_tree.column("stock", width=80, anchor="center")
        
        # Add sample data (in a real app, fetch from database)
        sample_products = [
            (1, "Wireless Mouse", 24.99, 45),
            (2, "Mechanical Keyboard", 89.99, 32),
            (3, "Notebook", 4.99, 120),
            (4, "Coffee Mug", 12.50, 65),
            (5, "Bluetooth Speaker", 59.99, 28),
        ]
        
        for product in sample_products:
            self.products_sale_tree.insert("", tk.END, values=product)
        
        self.products_sale_tree.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(products_frame, orient=tk.VERTICAL, command=self.products_sale_tree.yview)
        self.products_sale_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add to cart button
        add_frame = tk.Frame(left_frame, bg="white", padx=10, pady=10)
        add_frame.pack(fill=tk.X)
        
        tk.Label(add_frame, text="Quantity:", font=self.label_font, bg="white").pack(side=tk.LEFT)
        
        self.quantity_entry = tk.Entry(add_frame, font=self.label_font, width=10)
        self.quantity_entry.pack(side=tk.LEFT, padx=10)
        self.quantity_entry.insert(0, "1")
        
        add_btn = tk.Button(add_frame, text="Add to Cart", font=self.button_font, 
                          bg=self.accent_color, fg="white", command=self.add_to_cart)
        add_btn.pack(side=tk.LEFT, padx=10)
        
        # Right frame - Cart and checkout
        right_frame = tk.Frame(content, bg="white", bd=1, relief=tk.RIDGE, width=350)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        right_frame.pack_propagate(False)
        
        tk.Label(right_frame, text="Shopping Cart", font=self.label_font, bg="white", padx=10, pady=10).pack(anchor="w")
        
        # Cart items
        cart_items_frame = tk.Frame(right_frame, bg="white")
        cart_items_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("name", "qty", "price", "total")
        self.cart_tree = ttk.Treeview(cart_items_frame, columns=columns, show="headings", height=10)
        
        # Define headings
        self.cart_tree.heading("name", text="Product")
        self.cart_tree.heading("qty", text="Qty")
        self.cart_tree.heading("price", text="Price")
        self.cart_tree.heading("total", text="Total")
        
        # Configure columns
        self.cart_tree.column("name", width=150, anchor="w")
        self.cart_tree.column("qty", width=50, anchor="center")
        self.cart_tree.column("price", width=80, anchor="e")
        self.cart_tree.column("total", width=80, anchor="e")
        
        self.cart_tree.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(cart_items_frame, orient=tk.VERTICAL, command=self.cart_tree.yview)
        self.cart_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Cart actions
        cart_actions_frame = tk.Frame(right_frame, bg="white", padx=10, pady=10)
        cart_actions_frame.pack(fill=tk.X)
        
        remove_btn = tk.Button(cart_actions_frame, text="Remove", font=self.button_font, 
                             bg=self.danger_color, fg="white", command=self.remove_from_cart)
        remove_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = tk.Button(cart_actions_frame, text="Clear Cart", font=self.button_font, 
                            bg="#858796", fg="white", command=self.clear_cart)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Customer selection
        customer_frame = tk.Frame(right_frame, bg="white", padx=10, pady=10)
        customer_frame.pack(fill=tk.X)
        
        tk.Label(customer_frame, text="Customer:", font=self.label_font, bg="white").pack(anchor="w")
        
        self.customer_var = tk.StringVar()
        self.customer_combobox = ttk.Combobox(customer_frame, textvariable=self.customer_var, 
                                             font=self.label_font, state="readonly")
        self.customer_combobox.pack(fill=tk.X, pady=5)
        
        # Set sample customers
        self.customer_combobox["values"] = ["Walk-in Customer", "John Doe", "Jane Smith", "Acme Corporation"]
        self.customer_combobox.current(0)
        
        # Payment method
        payment_frame = tk.Frame(right_frame, bg="white", padx=10, pady=10)
        payment_frame.pack(fill=tk.X)
        
        tk.Label(payment_frame, text="Payment Method:", font=self.label_font, bg="white").pack(anchor="w")
        
        self.payment_var = tk.StringVar()
        payment_options = ["Cash", "Credit Card", "Debit Card", "Bank Transfer"]
        
        for option in payment_options:
            rb = tk.Radiobutton(payment_frame, text=option, variable=self.payment_var, 
                               value=option, font=self.label_font, bg="white")
            rb.pack(anchor="w")
        
        self.payment_var.set("Cash")
        
        # Totals
        totals_frame = tk.Frame(right_frame, bg="white", padx=10, pady=10)
        totals_frame.pack(fill=tk.X)
        
        tk.Label(totals_frame, text="Subtotal:", font=self.label_font, bg="white").grid(row=0, column=0, sticky="e")
        self.subtotal_label = tk.Label(totals_frame, text="$0.00", font=self.label_font, bg="white")
        self.subtotal_label.grid(row=0, column=1, sticky="e", padx=10)
        
        tk.Label(totals_frame, text="Tax (10%):", font=self.label_font, bg="white").grid(row=1, column=0, sticky="e")
        self.tax_label = tk.Label(totals_frame, text="$0.00", font=self.label_font, bg="white")
        self.tax_label.grid(row=1, column=1, sticky="e", padx=10)
        
        tk.Label(totals_frame, text="Total:", font=self.label_font, bg="white").grid(row=2, column=0, sticky="e")
        self.total_label = tk.Label(totals_frame, text="$0.00", font=("Helvetica", 14, "bold"), bg="white")
        self.total_label.grid(row=2, column=1, sticky="e", padx=10)
        
        # Checkout button
        checkout_btn = tk.Button(right_frame, text="Complete Sale", font=self.button_font, 
                               bg=self.primary_color, fg="white", pady=10,
                               command=self.complete_sale)
        checkout_btn.pack(fill=tk.X, padx=10, pady=(0, 10))
    
    def search_product_for_sale(self, event):
        """Search product for sale"""
        search_term = self.product_search.get()
        if not search_term:
            return
        
        # In a real app, you would query the database with the search term
        messagebox.showinfo("Search", f"Searching for: {search_term}")
    
    def add_to_cart(self):
        """Add selected product to cart"""
        selected_item = self.products_sale_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a product first")
            return
        
        try:
            quantity = int(self.quantity_entry.get())
            if quantity <= 0:
                messagebox.showwarning("Warning", "Quantity must be greater than 0")
                return
        except ValueError:
            messagebox.showwarning("Warning", "Please enter a valid quantity")
            return
        
        product_data = self.products_sale_tree.item(selected_item[0], "values")
        product_id = product_data[0]
        product_name = product_data[1]
        price = float(product_data[2])
        stock = int(product_data[3])
        
        if quantity > stock:
            messagebox.showwarning("Warning", "Not enough stock available")
            return
        
        # Check if product already in cart
        for item in self.cart_items:
            if item["id"] == product_id:
                item["quantity"] += quantity
                item["total"] = item["quantity"] * price
                self.update_cart_display()
                return
        
        # Add new item to cart
        self.cart_items.append({
            "id": product_id,
            "name": product_name,
            "price": price,
            "quantity": quantity,
            "total": quantity * price
        })
        
        self.update_cart_display()
    
    def update_cart_display(self):
        """Update the cart display and totals"""
        # Clear current cart display
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        # Add items to cart display
        self.total_amount = 0.0
        for item in self.cart_items:
            self.cart_tree.insert("", tk.END, values=(
                item["name"],
                item["quantity"],
                f"${item['price']:.2f}",
                f"${item['total']:.2f}"
            ))
            self.total_amount += item["total"]
        
        # Update totals
        tax = self.total_amount * 0.10  # 10% tax
        subtotal = self.total_amount - tax
        
        self.subtotal_label.config(text=f"${subtotal:.2f}")
        self.tax_label.config(text=f"${tax:.2f}")
        self.total_label.config(text=f"${self.total_amount:.2f}")
    
    def remove_from_cart(self):
        """Remove selected item from cart"""
        selected_item = self.cart_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an item to remove")
            return
        
        item_index = self.cart_tree.index(selected_item[0])
        del self.cart_items[item_index]
        self.update_cart_display()
    
    def clear_cart(self):
        """Clear all items from cart"""
        if not self.cart_items:
            return
            
        if messagebox.askyesno("Confirm", "Are you sure you want to clear the cart?"):
            self.cart_items = []
            self.update_cart_display()
    
    def complete_sale(self):
        """Complete the sale and generate invoice"""
        if not self.cart_items:
            messagebox.showwarning("Warning", "Cart is empty")
            return
        
        customer = self.customer_var.get()
        payment_method = self.payment_var.get()
        
        try:
            cursor = self.connection.cursor()
            
            # Get customer ID (for walk-in customer, we might use a default ID or create a new record)
            customer_id = None
            if customer != "Walk-in Customer":
                # In a real app, you would query the database for the customer ID
                customer_id = 1  # Placeholder
            
            # Create invoice
            invoice_query = """
                INSERT INTO invoices (customer_id, total_amount, tax, payment_method, status)
                VALUES (%s, %s, %s, %s, %s)
            """
            tax = self.total_amount * 0.10
            subtotal = self.total_amount - tax
            
            cursor.execute(invoice_query, (
                customer_id,
                self.total_amount,
                tax,
                payment_method,
                "Paid"
            ))
            
            # Get the invoice ID
            invoice_id = cursor.lastrowid
            
            # Add invoice items
            for item in self.cart_items:
                item_query = """
                    INSERT INTO invoice_items (invoice_id, product_id, quantity, unit_price, total_price)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(item_query, (
                    invoice_id,
                    item["id"],
                    item["quantity"],
                    item["price"],
                    item["total"]
                ))
                
                # Update product stock
                update_query = "UPDATE products SET quantity = quantity - %s WHERE product_id = %s"
                cursor.execute(update_query, (item["quantity"], item["id"]))
            
            self.connection.commit()
            cursor.close()
            
            # Generate invoice
            self.generate_invoice(invoice_id, customer)
            
            # Clear cart
            self.cart_items = []
            self.update_cart_display()
            
            messagebox.showinfo("Success", f"Sale completed successfully! Invoice #{invoice_id}")
        except Error as e:
            messagebox.showerror("Database Error", f"Error completing sale: {e}")
    
    def generate_invoice(self, invoice_id, customer_name):
        """Generate invoice PDF or HTML"""
        # In a real app, you would generate a proper invoice document
        # This is just a placeholder that shows the invoice in a messagebox
        
        invoice_text = f"INVOICE #{invoice_id}\n"
        invoice_text += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        invoice_text += f"Customer: {customer_name}\n"
        invoice_text += f"Payment Method: {self.payment_var.get()}\n\n"
        invoice_text += "ITEMS:\n"
        
        for item in self.cart_items:
            invoice_text += f"{item['name']} x{item['quantity']} @ ${item['price']:.2f} = ${item['total']:.2f}\n"
        
        tax = self.total_amount * 0.10
        subtotal = self.total_amount - tax
        
        invoice_text += f"\nSubtotal: ${subtotal:.2f}\n"
        invoice_text += f"Tax (10%): ${tax:.2f}\n"
        invoice_text += f"TOTAL: ${self.total_amount:.2f}\n"
        
        messagebox.showinfo("Invoice", invoice_text)
    
    def show_sales_history(self):
        """Show sales history"""
        self.clear_content_frame()
        
        # Header
        header = tk.Frame(self.content_frame, bg="white")
        header.pack(fill=tk.X, padx=20, pady=20)
        
        title = tk.Label(header, text="Sales History", font=self.title_font, bg="white")
        title.pack(side=tk.LEFT)
        
        # Date range filter
        filter_frame = tk.Frame(self.content_frame, bg="white", padx=20, pady=10)
        filter_frame.pack(fill=tk.X)
        
        tk.Label(filter_frame, text="From:", font=self.label_font, bg="white").pack(side=tk.LEFT)
        self.from_date = tk.Entry(filter_frame, font=self.label_font, width=12)
        self.from_date.pack(side=tk.LEFT, padx=5)
        
        tk.Label(filter_frame, text="To:", font=self.label_font, bg="white").pack(side=tk.LEFT, padx=(10, 0))
        self.to_date = tk.Entry(filter_frame, font=self.label_font, width=12)
        self.to_date.pack(side=tk.LEFT, padx=5)
        
        filter_btn = tk.Button(filter_frame, text="Filter", font=self.button_font, 
                             bg=self.primary_color, fg="white", command=self.filter_sales)
        filter_btn.pack(side=tk.LEFT, padx=10)
        
        # Sales table
        table_frame = tk.Frame(self.content_frame, bg="white", bd=1, relief=tk.RIDGE)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create treeview
        columns = ("invoice_id", "date", "customer", "amount", "payment", "status", "actions")
        self.sales_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Define headings
        self.sales_tree.heading("invoice_id", text="Invoice #")
        self.sales_tree.heading("date", text="Date")
        self.sales_tree.heading("customer", text="Customer")
        self.sales_tree.heading("amount", text="Amount")
        self.sales_tree.heading("payment", text="Payment")
        self.sales_tree.heading("status", text="Status")
        self.sales_tree.heading("actions", text="Actions")
        
        # Configure columns
        self.sales_tree.column("invoice_id", width=80, anchor="center")
        self.sales_tree.column("date", width=120, anchor="center")
        self.sales_tree.column("customer", width=150, anchor="w")
        self.sales_tree.column("amount", width=100, anchor="e")
        self.sales_tree.column("payment", width=100, anchor="w")
        self.sales_tree.column("status", width=100, anchor="center")
        self.sales_tree.column("actions", width=100, anchor="center")
        
        # Add sample data (in a real app, fetch from database)
        sample_sales = [
            (1001, "2023-05-15 14:30", "John Doe", 125.00, "Cash", "Paid"),
            (1000, "2023-05-14 11:15", "Jane Smith", 89.50, "Credit Card", "Paid"),
            (999, "2023-05-13 16:45", "Acme Corp", 1245.75, "Bank Transfer", "Pending"),
            (998, "2023-05-12 09:20", "Bob Johnson", 56.20, "Cash", "Paid"),
            (997, "2023-05-11 13:10", "Alice Brown", 342.90, "Debit Card", "Paid"),
        ]
        
        for sale in sample_sales:
            self.sales_tree.insert("", tk.END, values=sale + ("View",))
        
        self.sales_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.sales_tree.yview)
        self.sales_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double click to view details
        self.sales_tree.bind("<Double-1>", self.view_sale_details)
    
    def filter_sales(self):
        """Filter sales by date range"""
        from_date = self.from_date.get()
        to_date = self.to_date.get()
        
        if not from_date or not to_date:
            messagebox.showwarning("Warning", "Please enter both from and to dates")
            return
        
        # In a real app, you would query the database with the date range
        messagebox.showinfo("Filter", f"Filtering sales from {from_date} to {to_date}")
    
    def view_sale_details(self, event):
        """View sale details"""
        item = self.sales_tree.selection()[0]
        sale_data = self.sales_tree.item(item, "values")
        invoice_id = sale_data[0]
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Invoice #{invoice_id} Details")
        dialog.geometry("800x600")
        dialog.grab_set()
        
        # Header
        header = tk.Frame(dialog, bg="white", padx=20, pady=20)
        header.pack(fill=tk.X)
        
        tk.Label(header, text=f"INVOICE #{invoice_id}", font=self.title_font, bg="white").pack(anchor="w")
        tk.Label(header, text=f"Date: {sale_data[1]}", font=self.label_font, bg="white").pack(anchor="w")
        tk.Label(header, text=f"Customer: {sale_data[2]}", font=self.label_font, bg="white").pack(anchor="w")
        tk.Label(header, text=f"Payment Method: {sale_data[4]}", font=self.label_font, bg="white").pack(anchor="w")
        tk.Label(header, text=f"Status: {sale_data[5]}", font=self.label_font, bg="white").pack(anchor="w")
        
        # Items table
        table_frame = tk.Frame(dialog, bg="white", bd=1, relief=tk.RIDGE)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create treeview
        columns = ("product", "qty", "price", "total")
        items_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        
        # Define headings
        items_tree.heading("product", text="Product")
        items_tree.heading("qty", text="Quantity")
        items_tree.heading("price", text="Unit Price")
        items_tree.heading("total", text="Total")
        
        # Configure columns
        items_tree.column("product", width=300, anchor="w")
        items_tree.column("qty", width=100, anchor="center")
        items_tree.column("price", width=100, anchor="e")
        items_tree.column("total", width=100, anchor="e")
        
        # Add sample data (in a real app, fetch from database)
        sample_items = [
            ("Wireless Mouse", 2, 24.99, 49.98),
            ("Mechanical Keyboard", 1, 89.99, 89.99),
            ("Notebook", 5, 4.99, 24.95),
        ]
        
        for item in sample_items:
            items_tree.insert("", tk.END, values=item)
        
        items_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=items_tree.yview)
        items_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Totals
        totals_frame = tk.Frame(dialog, bg="white", padx=20, pady=10)
        totals_frame.pack(fill=tk.X)
        
        tk.Label(totals_frame, text="Subtotal:", font=self.label_font, bg="white").grid(row=0, column=0, sticky="e")
        subtotal = float(sale_data[3]) * 0.9  # Assuming 10% tax
        tk.Label(totals_frame, text=f"${subtotal:.2f}", font=self.label_font, bg="white").grid(row=0, column=1, sticky="e", padx=10)
        
        tk.Label(totals_frame, text="Tax (10%):", font=self.label_font, bg="white").grid(row=1, column=0, sticky="e")
        tax = float(sale_data[3]) * 0.1
        tk.Label(totals_frame, text=f"${tax:.2f}", font=self.label_font, bg="white").grid(row=1, column=1, sticky="e", padx=10)
        
        tk.Label(totals_frame, text="Total:", font=self.label_font, bg="white").grid(row=2, column=0, sticky="e")
        tk.Label(totals_frame, text=f"${sale_data[3]}", font=("Helvetica", 14, "bold"), bg="white").grid(row=2, column=1, sticky="e", padx=10)
        
        # Buttons
        button_frame = tk.Frame(dialog, bg="white", padx=20, pady=10)
        button_frame.pack(fill=tk.X)
        
        print_btn = tk.Button(button_frame, text="Print Invoice", font=self.button_font, 
                            bg=self.primary_color, fg="white", padx=20,
                            command=lambda: self.print_invoice(invoice_id))
        print_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = tk.Button(button_frame, text="Close", font=self.button_font, 
                            bg="#858796", fg="white", padx=20,
                            command=dialog.destroy)
        close_btn.pack(side=tk.LEFT, padx=5)
    
    def print_invoice(self, invoice_id):
        """Print invoice (placeholder)"""
        messagebox.showinfo("Print", f"Printing invoice #{invoice_id}")
    
    def show_reports(self):
        """Show reports section"""
        self.clear_content_frame()
        
        # Header
        header = tk.Frame(self.content_frame, bg="white")
        header.pack(fill=tk.X, padx=20, pady=20)
        
        title = tk.Label(header, text="Reports", font=self.title_font, bg="white")
        title.pack(side=tk.LEFT)
        
        # Report options
        options_frame = tk.Frame(self.content_frame, bg="white", padx=20, pady=20)
        options_frame.pack(fill=tk.BOTH, expand=True)
        
        reports = [
            ("Sales Report", "Generate detailed sales report"),
            ("Inventory Report", "View current inventory status"),
            ("Customer Report", "Generate customer purchase history"),
            ("Revenue Report", "View revenue by period")
        ]
        
        for i, (title, desc) in enumerate(reports):
            card = tk.Frame(options_frame, bg="#f8f9fc", bd=1, relief=tk.RIDGE)
            card.grid(row=i//2, column=i%2, sticky="nsew", padx=10, pady=10)
            options_frame.grid_columnconfigure(i%2, weight=1)
            options_frame.grid_rowconfigure(i//2, weight=1)
            
            tk.Label(card, text=title, font=self.label_font, bg="#f8f9fc").pack(anchor="w", padx=10, pady=(10, 5))
            tk.Label(card, text=desc, font=("Helvetica", 10), bg="#f8f9fc", fg="#858796").pack(anchor="w", padx=10, pady=(0, 10))
            
            btn = tk.Button(card, text="Generate", font=self.button_font, 
                          bg=self.primary_color, fg="white",
                          command=lambda t=title: self.generate_report(t))
            btn.pack(side=tk.BOTTOM, anchor="e", padx=10, pady=10)
    
    def generate_report(self, report_type):
        """Generate report (placeholder)"""
        messagebox.showinfo("Report", f"Generating {report_type}")
    
    def show_settings(self):
        """Show settings section"""
        self.clear_content_frame()
        
        # Header
        header = tk.Frame(self.content_frame, bg="white")
        header.pack(fill=tk.X, padx=20, pady=20)
        
        title = tk.Label(header, text="Settings", font=self.title_font, bg="white")
        title.pack(side=tk.LEFT)
        
        # Settings form
        form_frame = tk.Frame(self.content_frame, bg="white", padx=20, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Database settings
        db_frame = tk.LabelFrame(form_frame, text="Database Settings", font=self.label_font, 
                                bg="white", padx=10, pady=10)
        db_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(db_frame, text="Host:", font=self.label_font, bg="white").grid(row=0, column=0, sticky="w", pady=5)
        host_entry = tk.Entry(db_frame, font=self.label_font, width=30)
        host_entry.insert(0, self.db_config["host"])
        host_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=10)
        
        tk.Label(db_frame, text="Username:", font=self.label_font, bg="white").grid(row=1, column=0, sticky="w", pady=5)
        user_entry = tk.Entry(db_frame, font=self.label_font, width=30)
        user_entry.insert(0, self.db_config["user"])
        user_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=10)
        
        tk.Label(db_frame, text="Password:", font=self.label_font, bg="white").grid(row=2, column=0, sticky="w", pady=5)
        pass_entry = tk.Entry(db_frame, font=self.label_font, width=30, show="*")
        pass_entry.insert(0, self.db_config["password"])
        pass_entry.grid(row=2, column=1, sticky="ew", pady=5, padx=10)
        
        tk.Label(db_frame, text="Database:", font=self.label_font, bg="white").grid(row=3, column=0, sticky="w", pady=5)
        db_entry = tk.Entry(db_frame, font=self.label_font, width=30)
        db_entry.insert(0, self.db_config["database"])
        db_entry.grid(row=3, column=1, sticky="ew", pady=5, padx=10)
        
        # Application settings
        app_frame = tk.LabelFrame(form_frame, text="Application Settings", font=self.label_font, 
                                bg="white", padx=10, pady=10)
        app_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(app_frame, text="Theme:", font=self.label_font, bg="white").grid(row=0, column=0, sticky="w", pady=5)
        theme_var = tk.StringVar(value="Light")
        theme_menu = ttk.Combobox(app_frame, textvariable=theme_var, 
                                values=["Light", "Dark"], font=self.label_font, state="readonly")
        theme_menu.grid(row=0, column=1, sticky="ew", pady=5, padx=10)
        
        tk.Label(app_frame, text="Default Tax Rate (%):", font=self.label_font, bg="white").grid(row=1, column=0, sticky="w", pady=5)
        tax_entry = tk.Entry(app_frame, font=self.label_font, width=30)
        tax_entry.insert(0, "10")
        tax_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=10)
        
        # Save button
        save_btn = tk.Button(form_frame, text="Save Settings", font=self.button_font, 
                           bg=self.accent_color, fg="white", padx=20, pady=5,
                           command=lambda: self.save_settings(
                               host_entry.get(),
                               user_entry.get(),
                               pass_entry.get(),
                               db_entry.get(),
                               theme_var.get(),
                               tax_entry.get()
                           ))
        save_btn.pack(side=tk.RIGHT, pady=20)
    
    def save_settings(self, host, user, password, database, theme, tax_rate):
        """Save application settings"""
        try:
            # Update database config
            self.db_config = {
                'host': host,
                'user': user,
                'password': password,
                'database': database
            }
            
            # Reconnect with new settings
            if self.connection and self.connection.is_connected():
                self.connection.close()
            
            self.connection = self.connect_to_database()
            
            messagebox.showinfo("Success", "Settings saved successfully")
        except Error as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def logout(self):
        """Logout from the system"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            if self.connection and self.connection.is_connected():
                self.connection.close()
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SalesBillingSystem(root)
    root.mainloop()