import uuid
from flask import Flask, render_template, request, redirect, url_for, session, jsonify,flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'sreekrishneh'

# Function to connect to the database
def get_db_connection():
    conn = sqlite3.connect("sql.db")
    conn.row_factory = sqlite3.Row
    return conn

# List of all Indian states for dropdown
INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", 
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", 
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", 
    "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", 
    "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"
]

# Home Page
@app.route('/')
def home():
    return render_template("index.html")

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['username'] = username  
            return redirect(url_for('dashboard'))
        else:
            return render_template("login.html", error="Invalid credentials. Try again.")

    return render_template("login.html")

# Signup Page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'username' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        country = request.form['country']
        state = request.form['state']
        sex = request.form['sex']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO users (username, password, country, state, sex)
                VALUES (?, ?, ?, ?, ?)
            """, (username, password, country, state, sex))
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "Username already exists!"
        finally:
            conn.close()

    return render_template("signup.html")

# Dashboard Page
@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    
    

    username = session["username"]

    # Fetch planned trips from the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trips WHERE username = ?", (username,))
    planned_trips = cursor.fetchall()
    conn.close()

    return render_template("dashboard.html", planned_trips=planned_trips)
# Create Room
@app.route('/create_room', methods=['POST'])
def create_room():
    if 'username' not in session:
        return jsonify({"error": "Not logged in"}), 403  

    room_uuid = str(uuid.uuid4())  

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO rooms (room_id, created_by) VALUES (?, ?)", (room_uuid, session['username']))
    conn.commit()
    conn.close()

    return jsonify({"room_id": room_uuid})  

# Join Room
@app.route('/join_room', methods=['POST'])
def join_room():
    if 'username' not in session:
        return jsonify({"error": "Not logged in"}), 403  

    data = request.json
    room_id = data.get('room_id')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM rooms WHERE room_id = ?", (room_id,))
    room = cursor.fetchone()

    if not room:
        conn.close()
        return jsonify({"error": "Room not found"}), 404  

    cursor.execute("INSERT INTO room_members (room_id, username) VALUES (?, ?)", (room_id, session['username']))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Joined room successfully!"})

# Plan a Trip Page
@app.route('/plan_trip', methods=['GET', 'POST'])
def plan_trip():
    # if 'user_id' not in session:
    #     flash("Please log in first!", "error")
    #     return redirect(url_for('login'))
        
    if request.method == 'POST':
        try:
            # Get form data
            destination = request.form.get('destination')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            transport = request.form.get('transport')
            budget = request.form.get('budget')

            # Debugging: Print received data
            print(f"Received Data: {destination}, {start_date}, {end_date}, {transport}, {budget}")

            # Check if any required field is missing
            if not all([destination, start_date, end_date, transport, budget]):
                flash("Please fill in all fields!", "error")
                return render_template("plan_trip.html")

            # Insert data into trips table
            conn = get_db_connection()
            cursor = conn.cursor()
            print('cursor')
            cursor.execute("""
                INSERT INTO trips (username, destination, start_date, end_date, transport, budget) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (session['username'], destination, start_date, end_date, transport, budget))
            conn.commit()
            conn.close()

            flash("Trip planned successfully!", "success")
            return redirect(url_for('dashboard'))

        except Exception as e:
            print("Error:", e)
            flash("An error occurred while planning the trip.", "error")
            return render_template("plan_trip.html")

    return render_template("plan_trip.html")

# Chat Message Route
@app.route('/send_message', methods=['POST'])
def send_message():
    if 'username' not in session:
        return jsonify({"error": "Not logged in"}), 403

    data = request.json
    message_text = data.get('text')
    username = session['username']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (username, text) VALUES (?, ?)", (username, message_text))
    conn.commit()
    conn.close()

    return jsonify({"username": username, "text": message_text})

# Profile Page
@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (session['username'],))
    user = cursor.fetchone()
    conn.close()

    return render_template("profile.html", user=user)

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)