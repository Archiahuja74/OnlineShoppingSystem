import mysql.connector
from datetime import datetime

# ------------------- Connect to Database -------------------
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Waheguruji@74',  # your MySQL password
    database='online_shopping'
)

cursor = conn.cursor()
print("Connected to database successfully!")

# ------------------- Functions -------------------

def register_or_login():
    email = input("\nEnter your email: ").strip()
    cursor.execute("SELECT customer_id FROM Customers WHERE email=%s", (email,))
    result = cursor.fetchone()
    
    if result:
        print("Email already registered. You can place an order or view orders.")
        return result[0], email
    else:
        print("--- Registration ---")
        name = input("Enter your name: ").strip()
        password = input("Enter your password: ").strip()
        address = input("Enter your address: ").strip()
        phone = input("Enter your phone number: ").strip()
        
        cursor.execute(
            "INSERT INTO Customers (name, email, password, address, phone) VALUES (%s,%s,%s,%s,%s)",
            (name, email, password, address, phone)
        )
        conn.commit()
        customer_id = cursor.lastrowid
        print("Registration successful!")
        return customer_id, email

def show_products():
    cursor.execute("SELECT product_id, name, description, price, stock_quantity FROM Products")
    products = cursor.fetchall()
    print("\n--- Available Products ---")
    for product in products:
        print(f"ID: {product[0]}, Name: {product[1]}, Description: {product[2]}, Price: {product[3]}, Stock: {product[4]}")

def place_order(customer_id):
    cart = {}  # key = product_id, value = [quantity, price]
    
    show_products()
    
    while True:
        try:
            product_id = int(input("\nEnter Product ID to buy (0 to finish): "))
        except ValueError:
            print("Please enter a valid number!")
            continue

        if product_id == 0:
            break

        try:
            quantity = int(input("Enter quantity: "))
        except ValueError:
            print("Please enter a valid number!")
            continue

        cursor.execute("SELECT price, stock_quantity FROM Products WHERE product_id=%s", (product_id,))
        product = cursor.fetchone()
        
        if product:
            price, stock = product
            if product_id in cart:
                if cart[product_id][0] + quantity > stock:
                    print(f"Sorry, not enough stock! You already have {cart[product_id][0]} in cart.")
                else:
                    cart[product_id][0] += quantity
                    print(f"Updated cart: Product ID {product_id}, Total Quantity {cart[product_id][0]}, Price {price}")
            else:
                if quantity > stock:
                    print("Sorry, not enough stock!")
                else:
                    cart[product_id] = [quantity, price]
                    print(f"Added to cart: Product ID {product_id}, Quantity {quantity}, Price {price}")
        else:
            print("Invalid product ID")
    
    if cart:
        total_amount = sum(qty * price for qty, price in cart.values())
        print(f"\nTotal amount for this order: {total_amount}")

        order_date = datetime.now()
        status = "Pending"

        cursor.execute(
            "INSERT INTO Orders (customer_id, order_date, total_amount, status) VALUES (%s,%s,%s,%s)",
            (customer_id, order_date, total_amount, status)
        )
        conn.commit()
        order_id = cursor.lastrowid

        for product_id, (quantity, price) in cart.items():
            cursor.execute(
                "INSERT INTO Order_Items (order_id, product_id, quantity, price) VALUES (%s,%s,%s,%s)",
                (order_id, product_id, quantity, price)
            )
            cursor.execute(
                "UPDATE Products SET stock_quantity = stock_quantity - %s WHERE product_id = %s",
                (quantity, product_id)
            )

        conn.commit()
        print("Order placed successfully!")

def view_orders(customer_id):
    cursor.execute("""
        SELECT o.order_id, o.order_date, o.total_amount, o.status, p.name, oi.quantity, oi.price
        FROM Orders o
        JOIN Order_Items oi ON o.order_id = oi.order_id
        JOIN Products p ON oi.product_id = p.product_id
        WHERE o.customer_id = %s
        ORDER BY o.order_id
    """, (customer_id,))

    orders = cursor.fetchall()

    if not orders:
        print("No orders found!")
        return

    print("\n--- Your Orders ---")
    current_order_id = None
    for order in orders:
        order_id, order_date, total_amount, status, product_name, quantity, price = order
        
        if order_id != current_order_id:
            if current_order_id is not None:
                print()  # space between orders
            print(f"Order ID: {order_id} | Date: {order_date} | Status: {status} | Total: {total_amount}")
            current_order_id = order_id
        
        print(f"   - Product: {product_name} | Quantity: {quantity} | Price: {price}")

def cancel_order(customer_id):
    cursor.execute("""
        SELECT o.order_id, p.name, oi.quantity, oi.price, o.status
        FROM Orders o
        JOIN Order_Items oi ON o.order_id = oi.order_id
        JOIN Products p ON oi.product_id = p.product_id
        WHERE o.customer_id = %s AND o.status='Pending'
    """, (customer_id,))
    
    orders = cursor.fetchall()
    
    if not orders:
        print("No pending orders to cancel!")
        return
    
    print("\n--- Pending Orders ---")
    for order in orders:
        order_id, product_name, quantity, price, status = order
        print(f"Order ID: {order_id} | Product: {product_name} | Quantity: {quantity} | Price: {price} | Status: {status}")
    
    try:
        order_to_cancel = int(input("Enter Order ID to cancel: "))
    except ValueError:
        print("Invalid input!")
        return
    
    cursor.execute("SELECT order_id FROM Orders WHERE order_id=%s AND customer_id=%s AND status='Pending'",
                   (order_to_cancel, customer_id))
    result = cursor.fetchone()
    
    if result:
        cursor.execute("SELECT product_id, quantity FROM Order_Items WHERE order_id=%s", (order_to_cancel,))
        items = cursor.fetchall()
        for product_id, qty in items:
            cursor.execute("UPDATE Products SET stock_quantity = stock_quantity + %s WHERE product_id=%s", (qty, product_id))
        
        cursor.execute("DELETE FROM Order_Items WHERE order_id=%s", (order_to_cancel,))
        cursor.execute("DELETE FROM Orders WHERE order_id=%s", (order_to_cancel,))
        conn.commit()
        print(f"Order ID {order_to_cancel} cancelled successfully!")
    else:
        print("Order not found or cannot be cancelled!")

def update_order_status(customer_id):
    cursor.execute("""
        SELECT o.order_id, p.name, oi.quantity, oi.price, o.status
        FROM Orders o
        JOIN Order_Items oi ON o.order_id = oi.order_id
        JOIN Products p ON oi.product_id = p.product_id
        WHERE o.customer_id = %s AND o.status='Pending'
    """, (customer_id,))
    
    orders = cursor.fetchall()
    
    if not orders:
        print("No pending orders to update!")
        return
    
    print("\n--- Pending Orders ---")
    for order in orders:
        order_id, product_name, quantity, price, status = order
        print(f"Order ID: {order_id} | Product: {product_name} | Quantity: {quantity} | Price: {price} | Status: {status}")
    
    try:
        order_to_update = int(input("Enter Order ID to mark as Shipped: "))
    except ValueError:
        print("Invalid input!")
        return
    
    cursor.execute("SELECT order_id FROM Orders WHERE order_id=%s AND customer_id=%s AND status='Pending'",
                   (order_to_update, customer_id))
    result = cursor.fetchone()
    
    if result:
        cursor.execute("UPDATE Orders SET status='Shipped' WHERE order_id=%s", (order_to_update,))
        conn.commit()
        print(f"Order ID {order_to_update} status updated to Shipped!")
    else:
        print("Order not found or already shipped/cancelled!")

# ------------------- Main Menu -------------------
customer_id, email = register_or_login()

while True:
    print("\n--- MENU ---")
    print("1. Show Products")
    print("2. Place Order")
    print("3. View Orders")
    print("4. Cancel Order")
    print("5. Update Order Status")
    print("6. Exit")
    
    choice = input("Enter your choice: ").strip()
    
    if choice == '1':
        show_products()
    elif choice == '2':
        place_order(customer_id)
    elif choice == '3':
        view_orders(customer_id)
    elif choice == '4':
        cancel_order(customer_id)
    elif choice == '5':
        update_order_status(customer_id)
    elif choice == '6':
        print("Thank you for shopping with us!")
        break
    else:
        print("Invalid choice! Please enter 1-6.")

# ------------------- Close Connection -------------------
cursor.close()
conn.close()
