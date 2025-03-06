from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///logistics.db'
app.config['SECRET_KEY'] = 'your_secret_key_here'
db = SQLAlchemy(app)

# ---------------------------
# Models
# ---------------------------
class Shipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tracking_number = db.Column(db.String(50), unique=True, nullable=False)
    origin = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    estimated_delivery = db.Column(db.DateTime, nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=True)

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_type = db.Column(db.String(50), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    current_location = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    shipments = db.relationship('Shipment', backref='vehicle', lazy=True)

# ---------------------------
# Routes
# ---------------------------
@app.route('/')
def dashboard():
    shipments = Shipment.query.all()
    inventory = Inventory.query.all()
    vehicles = Vehicle.query.all()
    return render_template('dashboard.html', 
                           shipments=shipments,
                           inventory=inventory,
                           vehicles=vehicles)

@app.route('/shipments', methods=['GET', 'POST'])
def manage_shipments():
    if request.method == 'POST':
        tracking_number = request.form.get('tracking_number')
        origin = request.form.get('origin')
        destination = request.form.get('destination')
        status = request.form.get('status')
        departure_time_str = request.form.get('departure_time')
        estimated_delivery_str = request.form.get('estimated_delivery')
        
        try:
            departure_time = datetime.strptime(departure_time_str, '%Y-%m-%dT%H:%M')
            estimated_delivery = datetime.strptime(estimated_delivery_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid date/time format.', 'danger')
            return redirect(url_for('manage_shipments'))
        
        new_shipment = Shipment(
            tracking_number=tracking_number,
            origin=origin,
            destination=destination,
            status=status,
            departure_time=departure_time,
            estimated_delivery=estimated_delivery
        )
        db.session.add(new_shipment)
        db.session.commit()
        flash('New shipment added successfully!', 'success')
        return redirect(url_for('manage_shipments'))
    
    shipments = Shipment.query.all()
    return render_template('shipments.html', shipments=shipments)

@app.route('/inventory', methods=['GET', 'POST'])
def manage_inventory():
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        quantity = request.form.get('quantity')
        location = request.form.get('location')
        
        try:
            quantity = int(quantity)
        except ValueError:
            flash('Quantity must be a number.', 'danger')
            return redirect(url_for('manage_inventory'))
        
        new_item = Inventory(
            product_name=product_name,
            quantity=quantity,
            location=location
        )
        db.session.add(new_item)
        db.session.commit()
        flash('Inventory item added successfully!', 'success')
        return redirect(url_for('manage_inventory'))
    
    inventory = Inventory.query.all()
    return render_template('inventory.html', inventory=inventory)

@app.route('/vehicles', methods=['GET', 'POST'])
def manage_vehicles():
    if request.method == 'POST':
        vehicle_type = request.form.get('vehicle_type')
        capacity = request.form.get('capacity')
        current_location = request.form.get('current_location')
        status = request.form.get('status')
        
        try:
            capacity = int(capacity)
        except ValueError:
            flash('Capacity must be a number.', 'danger')
            return redirect(url_for('manage_vehicles'))
        
        new_vehicle = Vehicle(
            vehicle_type=vehicle_type,
            capacity=capacity,
            current_location=current_location,
            status=status
        )
        db.session.add(new_vehicle)
        db.session.commit()
        flash('Vehicle added successfully!', 'success')
        return redirect(url_for('manage_vehicles'))
    
    vehicles = Vehicle.query.all()
    return render_template('vehicles.html', vehicles=vehicles)

@app.route('/track/<tracking_number>')
def track_shipment(tracking_number):
    shipment = Shipment.query.filter_by(tracking_number=tracking_number).first_or_404()
    return render_template('tracking.html', shipment=shipment)

# ---------------------------
# Run the Application
# ---------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
