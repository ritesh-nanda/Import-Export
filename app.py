from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this for production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cargo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models for User and Cargo shipment
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Cargo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shipment_type = db.Column(db.String(50))  # "import" or "export"
    origin = db.Column(db.String(100))
    destination = db.Column(db.String(100))
    description = db.Column(db.String(200))
    status = db.Column(db.String(50))  # e.g., "pending", "in transit", "delivered"

# Routes

@app.route('/')
def index():
    if 'user_id' in session:
        shipments = Cargo.query.all()
        return render_template("dashboard.html", shipments=shipments)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('index'))
        flash("Invalid username or password", "danger")
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Simple user registration (add validations as needed)
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        if User.query.filter_by(username=username).first():
            flash("Username already exists", "danger")
            return redirect(url_for('register'))
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
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
        new_cargo = Cargo(
            shipment_type=shipment_type,
            origin=origin,
            destination=destination,
            description=description,
            status=status
        )
        db.session.add(new_cargo)
        db.session.commit()
        flash("Cargo shipment added successfully", "success")
        return redirect(url_for('index'))
    
    return render_template("add_cargo.html")

# Update and delete routes would be built similarly

if __name__ == '__main__':
    # Create database tables if not exist
    db.create_all()
    app.run(debug=True)
