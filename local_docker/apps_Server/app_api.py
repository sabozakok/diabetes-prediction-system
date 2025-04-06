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
from flask import session

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
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "diabetes_db")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASS", "password")

# Configure session settings
app.config["SESSION_PERMANENT"] = True  # Make sessions persistent
app.config["SESSION_TYPE"] = "filesystem"  # Store sessions on the server
app.config["SESSION_COOKIE_HTTPONLY"] = True  # Protect against XSS attacks
app.config["SESSION_COOKIE_SECURE"] = False  # Set to True in production (requires HTTPS)
app.config["REMEMBER_COOKIE_DURATION"] = 86400 * 7  # Keep users logged in for 7 days

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
        self.id = str(id)  # Flask-Login expects string type
        self.username = username
        self.password = password


@login_manager.user_loader
def load_user(user_id):
    print("🔁 load_user called with ID:", user_id)  # Debug print

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, password FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user:
        print("✅ User found:", user)
        return User(user[0], user[1], user[2])
    else:
        print("❌ User not found")
        return None






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

# Home Page Route (Redirects to login if unauthenticated)
@app.route("/home")
@login_required
def home():
    return render_template("home.html")

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
    return render_template("Prediction.html", prediction=prediction, probability=probability)

#API
@app.route("/api/predict", methods=["POST"])
def api_predict():
    try:
        data = request.get_json()
        print("📥 Received data:", data)

        required_fields = [
            "Pregnancies", "Glucose", "BloodPressure", "SkinThickness",
            "Insulin", "BMI", "DiabetesPedigree", "Age"
        ]

        # Validate presence of JSON and required fields
        if not data:
            return jsonify({"error": "Missing JSON payload"}), 400

        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

        # Extract input values as floats
        input_data = [float(data[field]) for field in required_fields]

        # Predict
        input_array = np.array(input_data).reshape(1, -1)
        scaled_data = scaler.transform(input_array)
        prediction_prob = float(model.predict(scaled_data)[0][0])  # convert to native float
        prediction = int(prediction_prob > 0.5)
        probability = round(prediction_prob * 100, 2)

        # Save to DB if user_Id is provided
        user_id = data.get("user_Id")
        if user_id:
            try:
                save_prediction_to_db(input_data, prediction_prob, int(user_id))
            except Exception as e:
                print("⚠️ Failed to save prediction:", e)

        return jsonify({
            "prediction": prediction,
            "probability": probability
        })

    except Exception as e:
        print("❌ Prediction error:", str(e))
        return jsonify({"error": str(e)}), 400



# API: Login
@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, password FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    
    if user and bcrypt.check_password_hash(user[1], password):
        user_obj = User(user[0], username, user[1])
        login_user(user_obj, remember=True)
        session.permanent = True
        return jsonify({
            "success": True,
            "user_id": user[0],
            "username": username
        })

    return jsonify({"success": False, "message": "Invalid credentials!"})

@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json()

    full_name = data.get("full_name")
    phone = data.get("phone")
    email = data.get("email")
    username = data.get("username")
    password_raw = data.get("password")
    role = data.get("role")

    if not all([full_name, phone,email, username, password_raw, role]):
        return jsonify({"success": False, "message": "Missing required fields!"}), 400

    password = bcrypt.generate_password_hash(password_raw).decode("utf-8")

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO users (username, password, full_name, phone,email, role)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
        """, (username, password, full_name, phone,email, role))
        user_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        user_obj = User(user_id, username, password)
        login_user(user_obj)

        return jsonify({
            "success": True,
            "message": "Registration successful!",
            "user_id": user_id,
            "username": username
        }), 201

    except psycopg2.IntegrityError:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({"success": False, "message": "Username or phone already exists!"}), 409

    


# API: Logout
@app.route("/api/home_login_check", methods=["GET"])
def api_home_login_check():
    if current_user.is_authenticated:
        return jsonify({
            "logged_in": True,
            "username": current_user.username
        })
    return jsonify({"logged_in": False})

@app.route("/api/logout", methods=["GET"])
#@login_required
def api_logout():
    #logout_user()
    #session.clear()
    return jsonify({"success": True, "message": "Logged out successfully."})

@app.route("/debug/session")
def debug_session():
    return jsonify(dict(session))


@app.route("/api/current_user", methods=["GET"])
@login_required
def api_current_user():
    return jsonify({"id": current_user.id, "username": current_user.username})

@app.route("/api/history", methods=["GET"])
#@login_required
def api_history():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT users.id, predictions.created_at, pregnancies, glucose, blood_pressure, 
               skin_thickness, insulin, bmi, diabetes_pedigree, age, probability
        FROM predictions
        JOIN users ON predictions.patient_id = users.id
        ORDER BY predictions.created_at DESC
    """)
    history_data = cur.fetchall()
    cur.close()
    conn.close()

    history_records = [
        {
            "patient_id": record[0],
            "created_at": record[1].strftime("%Y-%m-%d %H:%M:%S"),
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

    return jsonify({"success": True, "history": history_records})

if __name__ == "__main__":
    create_users_table()
    create_predictions_table()
    app.run(host="0.0.0.0", port=5050, debug=True)
