# AI-Powered Diabetes Prediction & Monitoring System

A distributed, real-time application for predicting and monitoring diabetes risk using machine learning and secure API-based architecture.

## 🧠 Features

- Real-time diabetes risk prediction using a pre-trained deep learning model.
- Multi-user role support (Doctor & Patient).
- Prediction history tracking and filtering.
- Role-based authentication and authorization.
- Containerized deployment using Docker Compose.
- Load balancing with NGINX.
- Scalable PostgreSQL database with PgBouncer.

---

This project is a distributed, containerized system for predicting and monitoring diabetes using a machine learning model and real-time APIs. It includes:
•	- Flask backend with ML inference
•	- PostgreSQL database with PgBouncer for pooling
•	- NGINX load balancer across multiple backend instances
•	- Docker Compose for orchestration

Folder Structure
----------------
.
├── app.py                 # Main Flask application
├── app_api.py                 # Main Flask application
├── docker-compose.yml     # Docker Compose config for full system
├── Dockerfile             # Container build for Flask API
├── nginx.conf             # Load balancing configuration for NGINX
├── requirements.txt       # Python dependencies
├── diabetes_model.h5      # Trained deep learning model
├── scaler.pkl             # Data standardization scaler
└── templates/             # Frontend HTML files 

How to Run Locally (Using Docker)
---------------------------------
Prerequisites:
•	- Docker desktop & Docker Compose installed (https://docs.docker.com/get-docker/)

Step 1: Download or Clone the Project
-------------------------------------
Open CMD
If on GitHub:
git clone https://github.com/your-username/diabetes-prediction-system.git
cd diabetes-prediction-system
cd local_docker
If on local directory:
Cd to application directory 
Example: 
Cd ...\local_docker\apps_Server

Step 2: Ensure Required Files Exist
-----------------------------------
Make sure these files are present in the root directory:
•	- app.py
•	- app_api.py                 
•	- Dockerfile
•	- docker-compose.yml
•	- nginx.conf
•	- diabetes_model.h5
•	- scaler.pkl
•	- requirements.txt
•	- templates/ 
-	index.html
-	login.html
-	register.html
-	history.html
-	prediction.html
-	patients.html
-	doctors.html

Step 3: Run the System
----------------------
docker-compose up –build
After complete run:
docker exec -it postgres-master psql -U admin -d diabetes_db
ALTER USER admin WITH PASSWORD 'password';
postgres -c password_encryption=md5
\q
This will:
•	- Build multiple Flask backends (backend1, backend2, backend3)
•	- Start PostgreSQL and PgBouncer
•	- Launch NGINX as load balancer
•	- Expose the app on: http://localhost:8080
•	- Expose the app api on: http://localhost:5051

Component Overview
------------------
Component     | Port  | Description
--------------|-------|-----------------------------
NGINX         | 8080  | Load-balanced entry point
Flask APPS     | 5001–5003 | Multiple backend instances
Flask API          5051   application rest api
PostgreSQL    | 5432  | Database server
PgBouncer     | 6432  | Connection pooling for Postgres

Usage
-----
•	- Open browser to http://localhost:8080
•	- Register or login as doctor
•	- Navigate to prediction form
•	- Input patient values → get real-time diabetes risk prediction
•	- Check prediction history and export results

Testing
-------
Tests are handled through Flask routes and manual inputs:
•	- Validate ML output via /Predict
•	- Check resilience by stopping a backend container:
docker stop backend2
•	- System continues functioning via NGINX failover

Security Notes
--------------
•	- Passwords are hashed using Flask-Bcrypt
•	- Session-managed routes with Flask-Login
•	- Backend secured behind NGINX reverse proxy
•	- Environment variables handle DB credentials

Cleaning Up
-----------
To stop and remove all containers:
docker-compose down -v

Run Locally Using Visual Studio Code (VS Code)
Follow these steps to set up and run the application locally using Visual Studio Code:
Step 1: Install VS Code and Python & PostgreSQL server

1. Download and install Visual Studio Code from: https://code.visualstudio.com/
2. Install Python from: https://www.python.org/downloads/
3. Open VS Code and install the Python extension from Microsoft (search "Python" in Extensions).
4. Install PostgreSQL server
Create postgresql database diabetes_db
 Create  admin user with password - password

Step 2: Create and Activate Virtual Environment

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

Step 3: Install Required Modules

Make sure `requirements.txt` is present in the root directory, then run:
pip install -r requirements.txt

Step 4: Run the Application

Run the Flask app using the integrated terminal:
python app.py

Then open your browser and go to: http://localhost:5000
Run the Flask api app using the integrated terminal:
python app_api.py

Then open your browser and go to: http://localhost:5050

You now have the project running locally through VS Code with Python.
 
Deploy on Amazon EC2 with Docker
Follow these steps to deploy the application on an Amazon EC2 instance using Docker and Docker Compose.

Step 1: Launch 4 EC2 Instances

EC2-HOST1	Backend 1
EC2-HOST1	Backend 2
EC2-DB	Postgresql database
EC2-LB1	Load Balancer


1. Log in to your AWS Management Console.
2. Go to EC2 Dashboard > Launch Instance.
3. Choose Ubuntu 22.04 LTS (or compatible).
4. Select an instance type (e.g., t2.micro for testing).
5. Configure security group to allow:
   - Port 22 (SSH)
   - Port 8080 (NGINX load balancer)
6. Launch the instance and note the public IP address.

Step 2: Connect to the Instance via SSH

Use a terminal or PowerShell to SSH into the instance:
ssh -i /path/to/your-key.pem ubuntu@your-ec2-public-ip

Step 3: Install Docker and Docker Compose

# Update and install Docker
sudo apt update && sudo apt install docker.io -y

# Enable and start Docker
sudo systemctl enable docker
sudo systemctl start docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
sudo usermod -aG docker $USER
newgrp docker
Step 4: Clone the Project

login to  WinScp and move each node project files

Step 5: Configure and Run

Ensure the following are present in the root:
- docker-compose.yml
- Dockerfile
- nginx.conf
- app.py
- requirements.txt
- diabetes_model.h5
- scaler.pkl

Then run:
sudo docker-compose up --build -d

Step 6: Access the Application

Open your browser and go to:
http://your-ec2-public-ip:8080

Your application should now be live and load balanced across containers, served through NGINX.

