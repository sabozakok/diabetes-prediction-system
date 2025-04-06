from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import joblib
import os
import psycopg2
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_cors import CORS  # Import Flask-CORS

app = Flask(__name__, template_folder="templates")
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Allows CORS only for /predict
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")  # Use an environment variable
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# Load the scaler and model
scaler_path = "scaler.pkl"
model_path = "diabetes_model.h5"

if not os.path.exists(scaler_path) or not os.path.exists(model_path):
    raise FileNotFoundError("Required files are missing: Ensure 'scaler.pkl' and 'diabetes_model.h5' exist.")

scaler = joblib.load(scaler_path)
model = load_model(model_path)

# Database connection
DB_HOST = os.getenv("DB_HOST", "postgres-db")
DB_NAME = os.getenv("DB_NAME", "diabetes_db")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASS", "password")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

def create_users_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            role TEXT CHECK (role IN ('doctor', 'patient')) NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def create_predictions_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id SERIAL PRIMARY KEY, 
            patient_id INTEGER REFERENCES users(id),  
            pregnancies FLOAT,
            glucose FLOAT,
            blood_pressure FLOAT,
            skin_thickness FLOAT,
            insulin FLOAT,
            bmi FLOAT,
            diabetes_pedigree FLOAT,
            age FLOAT,
            probability FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def save_prediction_to_db(data, prediction_prob, user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Convert numpy float32 values to native Python float
    data = [float(value) for value in data]
    prediction_prob = float(prediction_prob)

    cur.execute("""
        INSERT INTO predictions (patient_id, pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, diabetes_pedigree, age, probability)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (user_id, *data, prediction_prob))
    
    conn.commit()
    cur.close()
    conn.close()

def predict(data):
    # Transform input using the scaler
    data = np.array(data).reshape(1, -1)
    data = scaler.transform(data)

    # Make prediction
    prediction_prob = model.predict(data)[0][0]
    return prediction_prob


# Define User class for authentication
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, password FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return User(*user) if user else None

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form["full_name"]
        phone = request.form["phone"]
        email = request.form["email"]
        username = request.form["username"]
        password = bcrypt.generate_password_hash(request.form["password"]).decode('utf-8')
        role = request.form["role"]

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO users (username, password, full_name, phone,email, role) 
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
            """, (username, password, full_name, phone,email, role))
            user_id = cur.fetchone()[0]
            conn.commit()
            login_user(User(user_id, username, password))
            return redirect(url_for("home"))
        except psycopg2.IntegrityError:
            conn.rollback()
            flash("Username or phone number already exists!", "danger")
        cur.close()
        conn.close()
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, password FROM users WHERE username = %s AND role = 'doctor'", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user and bcrypt.check_password_hash(user[1], password):
            login_user(User(user[0], username, user[1]))
            return redirect(url_for("home"))
        flash("Invalid credentials!", "danger")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/")
#@login_required
def home():
    return render_template("index.html")

@app.route("/patients")
@login_required
def patients():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, full_name, role, phone FROM users WHERE role = 'patient'")
    patients_list = cur.fetchall()
    cur.close()
    conn.close()
    
    patients_records = [
        {
            "id": patient[0],
            "name": patient[1],
            "phone": patient[3],
        }
        for patient in patients_list
    ]
    
    return render_template("patients.html", patients=patients_records)

@app.route("/doctors")
@login_required
def doctors():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, full_name, role, phone FROM users WHERE role = 'doctor'")
    doctors_list = cur.fetchall()
    cur.close()
    conn.close()
    
    doctors_records = [
        {
            "id": doctor[0],
            "name": doctor[1],
            "phone": doctor[3]
        }
        for doctor in doctors_list
    ]
    
    return render_template("doctors.html", doctors=doctors_records)

@app.route("/prediction")
@login_required
def prediction():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, full_name FROM users WHERE role = 'patient'")
    patients_list = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template("prediction.html", patients=patients_list)

@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, full_name FROM users WHERE role = 'patient'")
    patients_list = cur.fetchall()
    
    selected_patient = request.form.get("patient_id")
    query = """
        SELECT users.full_name, predictions.created_at, pregnancies, glucose, blood_pressure, 
               skin_thickness, insulin, bmi, diabetes_pedigree, age, probability
        FROM predictions
        JOIN users ON predictions.patient_id = users.id
    """
    params = []
    
    if selected_patient:
        query += " WHERE predictions.patient_id = %s"
        params.append(selected_patient)
    
    query += " ORDER BY predictions.created_at DESC"
    cur.execute(query, tuple(params))
    history_data = cur.fetchall()
    cur.close()
    conn.close()
    
    history_records = [
        {
            "patient_name": record[0],
            "created_at": record[1],
            "pregnancies": record[2],
            "glucose": record[3],
            "blood_pressure": record[4],
            "skin_thickness": record[5],
            "insulin": record[6],
            "bmi": record[7],
            "diabetes_pedigree": record[8],
            "age": record[9],
            "probability": round(record[10] * 100, 2)
        }
        for record in history_data
    ]
    
    return render_template("history.html", history=history_records, patients=patients_list, selected_patient=selected_patient)

@app.route("/Predict", methods=["GET", "POST"])
@login_required
def Predict():
    prediction = None
    probability = None
    
    if request.method == "POST":
        try:
            data = [                
                float(request.form.get("Pregnancies")),
                float(request.form.get("Glucose")),
                float(request.form.get("BloodPressure")),
                float(request.form.get("SkinThickness")),
                float(request.form.get("Insulin")),
                float(request.form.get("BMI")),
                float(request.form.get("DiabetesPedigree")),
                float(request.form.get("Age"))
            ]
            
            
            prediction_prob = predict(data)
            prediction = int(prediction_prob > 0.5)
            probability = round(prediction_prob * 100, 2)
            # Save to database
            save_prediction_to_db(data, prediction_prob,int(request.form.get("PatientSelect")))
        except Exception as e:
            flash(str(e), "danger")   
    return render_template("prediction.html", prediction=prediction, probability=probability)

if __name__ == "__main__":
    create_users_table()
    create_predictions_table()
    app.run(host="0.0.0.0", port=5000, debug=True)
