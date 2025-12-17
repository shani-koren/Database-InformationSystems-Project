from datetime import datetime, date
from flask import Flask, render_template, redirect, request, session, url_for, flash
from flask_session import Session
import mysql.connector
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Setting up SQL connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="mytau012"
)
cursor = mydb.cursor()


# Displaying the data with fetchall
cursor.execute("SELECT * from Cloth")
all_data = cursor.fetchall()


@app.route("/")
def homepage():
    if not session.get("email"):
        return redirect("/login")
    return redirect("/store")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        cursor.execute("SELECT * FROM user WHERE email = %s and password = %s;", (email, password))
        # Execute a query to retrieve all columns from the user table where the email and password match the provided credentials
        result = cursor.fetchall()
        if len(result) > 0:
            session['email'] = email # creating a session only if the user exists in the database
            user_data = result[0]  # Extract the first record from the query result (user's data)
            # Storing user details in the session based on the column order in the database
            session['email'] = user_data[0]
            session['name'] = user_data[1]
            session['gender'] = user_data[2]
            session['faculty'] = user_data[3]
            session['birth_date'] = user_data[4]
            session['is_admin'] = user_data[5]
            return redirect("/")
        else:
            return render_template("login.html", message = 'User doesnt exist') # Show login error message
    return render_template("login.html")  # Render login page

@app.route("/logout")
def logout():  # Clear session variables and redirect to login page
    session["email"] = None
    session["is_admin"] = None
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        new_email = request.form.get("email")
        new_password = request.form.get("password")
        new_name = request.form.get("name")
        new_gender = request.form.get("gender")
        new_faculty = request.form.get("faculty")
        new_date_of_birth = request.form.get("date_of_birth")
        try:
            # Convert the input date
            birthday = datetime.strptime(new_date_of_birth, "%Y-%m-%d")
            # checking if date is in the future
            if birthday.date() > date.today():
                return render_template('register.html', error="Invalid date format")
        except ValueError:
            return render_template('register.html', error="Invalid date format")
        new_is_admin = False # Default value for new users
        cursor.execute("SELECT * FROM user WHERE email = %s;", (new_email,))
        result = cursor.fetchall()
        # If the user already exists, redirect to login page
        if result:
            return render_template("login.html", message="User already exists")
        # Insert new user into the database
        cursor.execute(
            "INSERT INTO User(email, name, gender, faculty, date_of_birth, is_admin, password) VALUES (%s, %s, %s, %s, %s, %s, %s);",
            (new_email, new_name, new_gender, new_faculty, new_date_of_birth, new_is_admin, new_password)
        )

        mydb.commit()
        return redirect("/login") # Redirect to login page after successful registration
    return render_template("register.html")


@app.route("/store", methods=["GET", "POST"])
def store():
    if not session.get("email"):
        return redirect("/login") # Redirect unauthorized users

    is_admin = session.get("is_admin")
    email = session.get("email")
    # Filter items: show only in-stock item and campaign items first
    cursor.execute("SELECT * FROM Cloth WHERE quantity > 0 ORDER BY CAST(is_campaigned AS SIGNED) DESC", ())
    available_items = cursor.fetchall()

    if request.method == "POST":
        # Create a new transaction record
        cursor.execute("INSERT INTO Transaction(email) VALUES (%s)", (email,))
        transaction_id = cursor.lastrowid  # Get Transaction ID

        purchase_items = request.form.getlist("cloth_ID")  # Get selected items
        for item_id in purchase_items:
            qty = request.form.get(f"quantity-{item_id}")
            # Check if enough stock is available
            cursor.execute("SELECT quantity FROM Cloth WHERE cloth_ID = %s", (item_id,))
            result = cursor.fetchone()
            if result and result[0] >= int(qty):
                cursor.execute("UPDATE Cloth SET quantity = quantity - %s WHERE cloth_ID = %s", (qty, item_id))
                # Record the transaction details in the Transaction_details table
                cursor.execute(
                    "INSERT INTO Transaction_details(order_number, quantity, cloth_ID) VALUES (%s, %s, %s)",
                    (transaction_id, qty, item_id))
            else:
                print(f"Insufficient stock for item {item_id}")
                # Display error message if requested quantity exceeds available stock
        mydb.commit()
        return redirect("/store")
    return render_template("store.html", items=available_items, is_admin=is_admin)
    # Filter items: only in-stock and campaign items first


@app.route("/admin/manage_inventory", methods=["GET", "POST"])
def inventory_update():
    if not session.get("is_admin", False):  # Restrict access to admins only
        return redirect("/store")

    if request.method == "POST": # Getting data from the form
        action = request.form.get("action")
        if action == "add": # Adding a new item
            cloth_id = request.form.get("cloth_ID")
            cloth_name = request.form.get("cloth_name")
            quantity = int(request.form.get("quantity"))
            price = float(request.form.get("price"))
            # Handle image upload
            if 'path_image' in request.files:
                path_image = request.files['path_image']
                if path_image.filename != '':
                    filename = secure_filename(path_image.filename) # Secure filename
                    # Save the filename to your static folder
                    path_image.save(os.path.join(app.static_folder, filename))
                    # Store this filename in your database
                    path_image = filename  # Save filename in DB
            else:
                # Handle the case where no file was uploaded
                path_image = None
            cloth_description = request.form.get("cloth_description")
            is_campaigned = 1 if request.form.get("is_campaigned") == "on" else 0
            # Check if cloth id already exists
            cursor.execute("SELECT * FROM Cloth WHERE cloth_ID = %s;", (cloth_id,))
            result = cursor.fetchall()
            if result:
                return render_template("inventory_update.html", error="Cloth ID already exists")  # handle error
            # Insert new item into database
            cursor.execute("""
                INSERT INTO Cloth (cloth_ID, cloth_name, quantity, price, is_campaigned, path_image, cloth_description)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (cloth_id, cloth_name, quantity, price, is_campaigned, path_image, cloth_description ))
        elif action == "update":  # Update inventory quantity
            cloth_id = request.form.get("cloth_ID")
            quantity = int(request.form.get("quantity"))
            cursor.execute("""
                UPDATE Cloth
                SET quantity = %s
                WHERE cloth_ID = %s
            """, (quantity, cloth_id))
        mydb.commit()


    # Retrieve all items for inventory management
    cursor.execute("SELECT * FROM Cloth")
    items = cursor.fetchall()

    return render_template("inventory_update.html", items=items)




if __name__ == "__main__":
    try:
        app.run(debug=True)
    finally:
        cursor.close()
        mydb.close()
        print("connection closed")
