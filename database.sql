CREATE DATABASE online_shopping;
USE online_shopping;

-- Customers table
CREATE TABLE Customers (
  customer_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50),
  email VARCHAR(50) UNIQUE,
  password VARCHAR(50),
  address VARCHAR(255),
  phone VARCHAR(15)
);

-- Categories table
CREATE TABLE Categories (
  category_id INT AUTO_INCREMENT PRIMARY KEY,
  category_name VARCHAR(50)
);

-- Products table
CREATE TABLE Products (
  product_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50),
  description TEXT,
  price DECIMAL(10,2),
  stock_quantity INT,
  category_id INT,
  FOREIGN KEY (category_id) REFERENCES Categories(category_id)
);

-- Orders table
CREATE TABLE Orders (
  order_id INT AUTO_INCREMENT PRIMARY KEY,
  customer_id INT,
  order_date DATETIME,
  total_amount DECIMAL(10,2),
  status VARCHAR(20),
  FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
);

-- Order_Items table
CREATE TABLE Order_Items (
  order_item_id INT AUTO_INCREMENT PRIMARY KEY,
  order_id INT,
  product_id INT,
  quantity INT,
  price DECIMAL(10,2),
  FOREIGN KEY (order_id) REFERENCES Orders(order_id),
  FOREIGN KEY (product_id) REFERENCES Products(product_id)
);

INSERT INTO Categories (category_name) VALUES ('Electronics'), ('Clothing');

INSERT INTO Products (name, description, price, stock_quantity, category_id)
VALUES
('Smartphone', 'Android 12, 128GB', 20000, 50, 1),
('Laptop', 'Intel i5, 8GB RAM', 45000, 30, 1),
('T-Shirt', 'Cotton, Medium', 500, 100, 2);

INSERT INTO Customers (name, email, password, address, phone)
VALUES ('Archi', 'archi@example.com', 'archi123', '123 Bangalore', '9876543210');

SELECT o.order_id, p.name, oi.quantity, oi.price, o.total_amount, o.status
FROM Orders o
JOIN Order_Items oi ON o.order_id = oi.order_id
JOIN Products p ON oi.product_id = p.product_id
WHERE o.customer_id = 3;

