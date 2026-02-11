CREATE DATABASE loan_management;
USE loan_management;

CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE loans (
    loan_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    amount DECIMAL(12, 2) NOT NULL,
    interest_rate DECIMAL(5, 2) NOT NULL,
    term_months INT NOT NULL,
    start_date DATE NOT NULL,
    status ENUM('Active', 'Paid', 'Defaulted') DEFAULT 'Active',
    purpose VARCHAR(100),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    loan_id INT,
    amount DECIMAL(12, 2) NOT NULL,
    payment_date DATE NOT NULL,
    payment_method ENUM('Cash', 'Bank Transfer', 'Check', 'Other'),
    FOREIGN KEY (loan_id) REFERENCES loans(loan_id)
);