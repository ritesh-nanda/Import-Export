import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with a secure secret in production

# Set the MongoDB URI. You can set this via an environment variable or directly here.
app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "mongodb://localhost:27017/cargo")

mongo = PyMongo(app)
users_collection = mongo.db.users
cargo_collection = mongo.db.cargo

@app.route('/')
def index():
    if 'user_id' in session:
        # Retrieve all cargo shipments from MongoDB
        shipments = list(cargo_collection.find())
        return render_template("dashboard.html", shipments=shipments)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users_collection.find_one({"username": username})
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            return redirect(url_for('index'))
        flash("Invalid username or password", "danger")
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        if users_collection.find_one({"username": username}):
            flash("Username already exists", "danger")
            return redirect(url_for('register'))
        # Insert the new user into MongoDB
        new_user = {"username": username, "password": password}
        users_collection.insert_one(new_user)
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))
    return render_template("register.html")

@app.route('/add-cargo', methods=['GET', 'POST'])
def add_cargo():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        shipment_type = request.form['shipment_type']
        origin = request.form['origin']
        destination = request.form['destination']
        description = request.form['description']
        status = request.form['status']
        # Insert the cargo shipment record into MongoDB
        cargo_data = {
            "shipment_type": shipment_type,
            "origin": origin,
            "destination": destination,
            "description": description,
            "status": status
        }
        cargo_collection.insert_one(cargo_data)
        flash("Cargo shipment added successfully", "success")
        return redirect(url_for('index'))
    
    return render_template("add_cargo.html")

if __name__ == '__main__':
    app.run(debug=True)
