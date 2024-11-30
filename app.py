from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
from functools import wraps
import json

from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

app.config['SECRET_KEY'] = 'abc123'

def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='labour'
        )
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

def generate_token(user_id):
    # Simple token generation without JWT
    timestamp = datetime.utcnow().timestamp()
    token = f"{user_id}:{timestamp}:{app.config['SECRET_KEY']}"
    return token

@app.route('/labours', methods=['GET'])
def get_labours():
    connection = create_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM labours"
        cursor.execute(query)
        labours = cursor.fetchall()
        return jsonify(labours), 200
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        connection.close()

@app.route('/labours', methods=['POST'])
def add_labour():
    connection = create_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = connection.cursor()
        id = request.json.get('id')
        name = request.json.get('name')
        group_id = request.json.get('group_id')
        site_id = request.json.get('site_id')
        daily_wage = request.json.get('daily_wage')
        working_hours = request.json.get('working_hours')
        category = request.json.get('category')
        
        if not all([id, name, group_id, site_id, daily_wage, working_hours, category]):
            return jsonify({"error": "All fields are required"}), 400
        
        query = "INSERT INTO labours (id, name, group_id, site_id, daily_wage, working_hours, category) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (id, name, group_id, site_id, daily_wage, working_hours, category))
        connection.commit()
        return jsonify({"id": id, "name": name, "group_id": group_id, "site_id": site_id, "daily_wage": float(daily_wage), "working_hours": int(working_hours), "category": category}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        connection.close()

@app.route('/sites', methods=['POST'])
def add_site():
    connection = create_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = connection.cursor()
        id = request.json['id']
        name = request.json['name']
        
        if not id or not name:
            return jsonify({"error": "ID and name are required"}), 400
        
        query = "INSERT INTO sites (id, name) VALUES (%s, %s)"
        cursor.execute(query, (id, name))
        connection.commit()
        return jsonify({"id": id, "name": name}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        connection.close()

@app.route('/sites', methods=['GET'])
def get_sites():
    connection = create_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM sites"
        cursor.execute(query)
        sites = cursor.fetchall()
        return jsonify(sites), 200
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        connection.close()

@app.route('/groups', methods=['POST'])
def add_group():
    connection = create_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = connection.cursor()
        id = request.json['id']
        name = request.json['name']
        
        if not id or not name:
            return jsonify({"error": "ID and name are required"}), 400
        
        query = "INSERT INTO `groups` (id, name) VALUES (%s, %s)"
        cursor.execute(query, (id, name))
        connection.commit()
        return jsonify({"id": id, "name": name}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        connection.close()

@app.route('/attendance', methods=['POST'])
def add_attendance():
    connection = create_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = connection.cursor()
        id = request.json['id']
        labour_id = request.json['labour_id']
        date = request.json['date']
        is_present = request.json['is_present']
        
        if not all([id, labour_id, date, is_present is not None]):
            return jsonify({"error": "All fields are required"}), 400
        
        query = "INSERT INTO attendance (id, labour_id, date, is_present) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (id, labour_id, date, is_present))
        connection.commit()
        return jsonify({"id": id, "labour_id": labour_id, "date": date, "is_present": bool(is_present)}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        connection.close()

@app.route('/payroll', methods=['POST'])
def add_payroll():
    connection = create_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = connection.cursor()
        id = request.json['id']
        labour_id = request.json['labour_id']
        amount = request.json['amount']
        date = request.json['date']
        
        if not all([id, labour_id, amount, date]):
            return jsonify({"error": "All fields are required"}), 400
        
        query = "INSERT INTO payroll (id, labour_id, amount, date) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (id, labour_id, float(amount), date))
        connection.commit()
        return jsonify({"id": id, "labour_id": labour_id, "amount": float(amount), "date": date}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        connection.close()

@app.route('/signup', methods=['POST'])
def signup():
    try:
        if not request.is_json:
            return jsonify({
                "status": "error", 
                "message": "Missing JSON in request"
            }), 400

        email = request.json.get('email')
        password = request.json.get('password')
        
        if not email or not password:
            return jsonify({
                "status": "error",
                "message": "Email and password are required"
            }), 400
            
        connection = create_connection()
        if connection is None:
            return jsonify({
                "status": "error",
                "message": "Database connection failed"
            }), 500
            
        cursor = connection.cursor(dictionary=True)
        
        # Check if user already exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({
                "status": "error",
                "message": "Email already registered"
            }), 400
            
        # Create new user
        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (email, password) VALUES (%s, %s)",
            (email, hashed_password)
        )
        connection.commit()
        
        # Get the created user
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        # Generate token
        token = generate_token(user['id'])
        
        return jsonify({
            "status": "success",
            "message": "User created successfully",
            "token": token
        }), 201
        
    except Exception as e:
        print(f"Signup error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@app.route('/login', methods=['POST'])
def login():
    try:
        if not request.is_json:
            return jsonify({
                "status": "error",
                "message": "Missing JSON in request"
            }), 400

        email = request.json.get('email')
        password = request.json.get('password')
        
        if not email or not password:
            return jsonify({
                "status": "error",
                "message": "Email and password are required"
            }), 400
        
        connection = create_connection()
        if connection is None:
            return jsonify({
                "status": "error",
                "message": "Database connection failed"
            }), 500
            
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user['password'], password):
            token = generate_token(user['id'])
            return jsonify({
                "status": "success",
                "message": "Login successful",
                "token": token
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Invalid email or password"
            }), 401
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@app.route('/user', methods=['GET'])
def get_user_info():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                "status": "error",
                "message": "No token provided"
            }), 401
            
        token = auth_header.split(' ')[1]
        try:
            # Simple token validation
            user_id = token.split(':')[0]
            
            connection = create_connection()
            cursor = connection.cursor(dictionary=True)
            query = "SELECT id, email FROM users WHERE id = %s"
            cursor.execute(query, (user_id,))
            user = cursor.fetchone()
            
            if user:
                return jsonify({
                    "status": "success",
                    "user": {
                        "id": user['id'],
                        "email": user['email'],
                        "name": user['email'].split('@')[0],
                        "initials": user['email'][0].upper()
                    }
                }), 200
            else:
                return jsonify({
                    "status": "error",
                    "message": "User not found"
                }), 404
                
        except Exception:
            return jsonify({
                "status": "error",
                "message": "Invalid token"
            }), 401
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

if __name__ == '__main__':
    app.run(debug=True)
