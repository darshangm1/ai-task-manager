import sqlite3
import json
import os
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, session, render_template
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from openai import OpenAI

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

app = Flask(__name__)
app.secret_key = "supersecretkey"

CORS(
    app,
    supports_credentials=True,
    origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ]
)

# Email configuration (for demo - users should set their own)
EMAIL_ENABLED = False  # Set to True and configure below to enable emails
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your-email@gmail.com"  # Change this
SENDER_PASSWORD = "your-app-password"  # Use Gmail App Password

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            profile_picture TEXT,
            streak INTEGER DEFAULT 0,
            last_task_date TEXT
        )
    """)
    
    # Add columns to users table if they don't exist
    c.execute("PRAGMA table_info(users)")
    user_columns = {row[1] for row in c.fetchall()}
    
    if 'profile_picture' not in user_columns:
        c.execute("ALTER TABLE users ADD COLUMN profile_picture TEXT")
    if 'streak' not in user_columns:
        c.execute("ALTER TABLE users ADD COLUMN streak INTEGER DEFAULT 0")
    if 'last_task_date' not in user_columns:
        c.execute("ALTER TABLE users ADD COLUMN last_task_date TEXT")

    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            task TEXT,
            date TEXT,
            time TEXT,
            priority TEXT,
            completed INTEGER,
            created_at TIMESTAMP,
            category TEXT
        )
    """)

    c.execute("PRAGMA table_info(tasks)")
    existing_columns = {row[1] for row in c.fetchall()}

    required_columns = {
        "user_id": "INTEGER",
        "task": "TEXT",
        "date": "TEXT",
        "time": "TEXT",
        "priority": "TEXT",
        "completed": "INTEGER",
        "created_at": "TIMESTAMP",
        "category": "TEXT"
    }

    for column_name, column_type in required_columns.items():
        if column_name not in existing_columns:
            c.execute(f"ALTER TABLE tasks ADD COLUMN {column_name} {column_type}")

    conn.commit()
    conn.close()

init_db()

def parse_task_fallback(text):
    txt = (text or "").strip()
    lowered = txt.lower()

    priority = "Medium"
    if any(word in lowered for word in ["urgent", "important", "asap", "meeting", "exam"]):
        priority = "High"
    elif any(word in lowered for word in ["watch", "buy", "check", "casual"]):
        priority = "Low"

    # Detect category
    category = "Personal"
    if any(word in lowered for word in ["work", "meeting", "report", "project", "email", "office", "client"]):
        category = "Work"
    elif any(word in lowered for word in ["study", "homework", "exam", "research", "learn", "class", "assignment"]):
        category = "Study"
    elif any(word in lowered for word in ["gym", "exercise", "doctor", "health", "workout", "medicine", "fitness"]):
        category = "Health"
    elif any(word in lowered for word in ["shopping", "family", "friend", "hobby", "buy", "personal"]):
        category = "Personal"

    time_match = re.search(r"\b(\d{1,2}(:\d{2})?\s?(am|pm|a\.m\.|p\.m\.)?)\b", lowered)
    time_val = time_match.group(1) if time_match else ""

    date_val = ""
    if "today" in lowered:
        date_val = "today"
    elif "tomorrow" in lowered:
        date_val = "tomorrow"

    task_val = txt
    for token in ["today", "tomorrow"]:
        task_val = re.sub(rf"\b{token}\b", "", task_val, flags=re.IGNORECASE)
    if time_match:
        task_val = task_val.replace(time_match.group(0), "")
    task_val = re.sub(r"\s+", " ", task_val).strip(" -,.\t\n")
    if not task_val:
        task_val = txt or "New Task"

    return {
        "task": task_val,
        "date": date_val,
        "time": time_val,
        "priority": priority,
        "category": category
    }

# ---------- SERVE HTML FILES ----------
@app.route("/")
def index():
    return render_template("login.html")

@app.route("/login.html")
def login_page():
    return render_template("login.html")

@app.route("/signup.html")
def signup_page():
    return render_template("signup.html")

@app.route("/dashboard.html")
def dashboard_page():
    return render_template("dashboard.html")

# ---------- SIGNUP ----------
@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    name = data["name"]
    email = data["email"]
    password = generate_password_hash(data["password"])

    try:
        conn = sqlite3.connect("tasks.db")
        c = conn.cursor()
        c.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, password)
        )
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except:
        return jsonify({"error": "Email already exists"}), 400

# ---------- LOGIN ----------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data["email"]
    password = data["password"]

    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("SELECT id, name, password FROM users WHERE email=?", (email,))
    user = c.fetchone()
    conn.close()

    if user and check_password_hash(user[2], password):
        session["user_id"] = user[0]
        session["name"] = user[1]
        return jsonify({"success": True, "name": user[1]})
    else:
        return jsonify({"error": "Invalid credentials"}), 401

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return jsonify({"success": True})

# ---------- CURRENT USER ----------
@app.route("/me")
def me():
    if "user_id" not in session:
        return jsonify({"logged_in": False})
    
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("SELECT name, email, profile_picture, streak FROM users WHERE id=?", (session["user_id"],))
    row = c.fetchone()
    conn.close()
    
    if row:
        return jsonify({
            "logged_in": True,
            "name": row[0],
            "email": row[1],
            "profile_picture": row[2],
            "streak": row[3] if row[3] else 0
        })
    return jsonify({"logged_in": True, "name": session["name"]})

# ---------- AI TASK ----------
@app.route("/ai", methods=["POST"])
def ai():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    text = (request.json or {}).get("text", "").strip()
    if not text:
        return jsonify({"error": "Please enter or speak a task first"}), 400

    prompt = f"""
You are a smart task assistant.

Extract task, date, time, priority and category from this sentence:

"{text}"

Rules:
- Priority must be one of: High, Medium, Low
- urgent, important, asap, meeting, exam → High
- normal work → Medium
- casual like watch, buy, check → Low
- Category must be one of: Work, Personal, Study, Health
- Work: meetings, reports, projects, email
- Study: homework, exam, research, learn
- Health: gym, exercise, doctor, medicine
- Personal: shopping, family, friends, hobby

Reply ONLY in valid JSON:
{{
  "task": "",
  "date": "",
  "time": "",
  "priority": "High | Medium | Low",
  "category": "Work | Personal | Study | Health"
}}
"""

    data = None
    try:
        if client is not None:
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=prompt
            )
            raw = response.output[0].content[0].text
            raw = raw.replace("```json", "").replace("```", "").strip()
            data = json.loads(raw)
    except Exception:
        data = None

    if not data:
        data = parse_task_fallback(text)

    # Ensure category exists
    if 'category' not in data or not data['category']:
        data['category'] = 'Personal'

    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO tasks (user_id, task, date, time, priority, category) VALUES (?, ?, ?, ?, ?, ?)",
        (session["user_id"], data["task"], data["date"], data["time"], data["priority"], data["category"])
    )
    conn.commit()
    conn.close()

    return jsonify({"result": data, "source": "ai" if client else "fallback"})

# ---------- GET TASKS ----------
@app.route("/tasks")
def tasks():
    if "user_id" not in session:
        return jsonify([])

    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute(
        "SELECT id, task, date, time, priority, completed, category FROM tasks WHERE user_id=? ORDER BY completed ASC, id DESC",
        (session["user_id"],)
    )
    rows = c.fetchall()
    conn.close()

    return jsonify([
        {
            "id": r[0],
            "task": r[1],
            "date": r[2],
            "time": r[3],
            "priority": r[4],
            "completed": r[5] if r[5] is not None else 0,
            "category": r[6] if r[6] else "Personal"
        }
        for r in rows
    ])

# ---------- DELETE TASK ----------
@app.route("/delete/<int:id>", methods=["DELETE"])
def delete(id):
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute(
        "DELETE FROM tasks WHERE id=? AND user_id=?",
        (id, session["user_id"])
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True})

# ---------- UPDATE PRIORITY ----------
@app.route("/update_priority/<int:id>", methods=["POST"])
def update_priority(id):
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    new_priority = request.json["priority"]

    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute(
        "UPDATE tasks SET priority=? WHERE id=? AND user_id=?",
        (new_priority, id, session["user_id"])
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True})

# ---------- TOGGLE COMPLETED ----------
@app.route("/toggle_completed/<int:id>", methods=["POST"])
def toggle_completed(id):
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute(
        "SELECT completed FROM tasks WHERE id=? AND user_id=?",
        (id, session["user_id"])
    )
    row = c.fetchone()
    if not row:
        return jsonify({"error": "Task not found"}), 404

    current = row[0] if row[0] is not None else 0
    new_completed = 1 - current
    c.execute(
        "UPDATE tasks SET completed=? WHERE id=? AND user_id=?",
        (new_completed, id, session["user_id"])
    )
    
    # Update streak when marking task as completed
    if new_completed == 1:
        from datetime import datetime, timedelta
        today = datetime.now().date()
        
        # Get user's last_task_date and current streak
        c.execute("SELECT last_task_date, streak FROM users WHERE id=?", (session["user_id"],))
        user = c.fetchone()
        
        if user:
            last_date_str = user[0]
            current_streak = user[1] if user[1] is not None else 0
            
            if last_date_str:
                last_date = datetime.strptime(last_date_str, "%Y-%m-%d").date()
                days_diff = (today - last_date).days
                
                if days_diff == 0:
                    # Same day, no streak change
                    pass
                elif days_diff == 1:
                    # Consecutive day, increment streak
                    current_streak += 1
                    c.execute("UPDATE users SET streak=?, last_task_date=? WHERE id=?", 
                             (current_streak, today.isoformat(), session["user_id"]))
                else:
                    # Streak broken, reset to 1
                    c.execute("UPDATE users SET streak=1, last_task_date=? WHERE id=?", 
                             (today.isoformat(), session["user_id"]))
            else:
                # First completed task ever, start streak
                c.execute("UPDATE users SET streak=1, last_task_date=? WHERE id=?", 
                         (today.isoformat(), session["user_id"]))
    
    conn.commit()
    conn.close()

    return jsonify({"success": True, "completed": new_completed})

# ---------- EDIT TASK ----------
@app.route("/edit/<int:id>", methods=["POST"])
def edit_task(id):
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.json
    task = data.get("task", "")
    date_val = data.get("date", "")
    time_val = data.get("time", "")
    priority = data.get("priority", "Medium")
    category = data.get("category", "Personal")

    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute(
        "UPDATE tasks SET task=?, date=?, time=?, priority=?, category=? WHERE id=? AND user_id=?",
        (task, date_val, time_val, priority, category, id, session["user_id"])
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True})

# ---------- CHANGE PASSWORD ----------
@app.route("/change_password", methods=["POST"])
def change_password():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.json
    old_password = data.get("old_password", "")
    new_password = data.get("new_password", "")

    if not old_password or not new_password:
        return jsonify({"error": "Both passwords required"}), 400

    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute(
        "SELECT password FROM users WHERE id=?",
        (session["user_id"],)
    )
    user = c.fetchone()
    conn.close()

    if not user or not check_password_hash(user[0], old_password):
        return jsonify({"error": "Old password is incorrect"}), 401

    hashed = generate_password_hash(new_password)
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute(
        "UPDATE users SET password=? WHERE id=?",
        (hashed, session["user_id"])
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Password changed successfully"})

# ---------- UPDATE PROFILE ----------
@app.route("/update_profile", methods=["POST"])
def update_profile():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.json
    new_name = data.get("name", "").strip()

    if not new_name:
        return jsonify({"error": "Name cannot be empty"}), 400

    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute(
        "UPDATE users SET name=? WHERE id=?",
        (new_name, session["user_id"])
    )
    conn.commit()
    conn.close()

    session["name"] = new_name
    return jsonify({"success": True, "message": "Profile updated successfully"})

# ---------- UPDATE PROFILE PICTURE ----------
@app.route("/update_profile_picture", methods=["POST"])
def update_profile_picture():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.json
    profile_picture_url = data.get("profile_picture", "").strip()

    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute(
        "UPDATE users SET profile_picture=? WHERE id=?",
        (profile_picture_url, session["user_id"])
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Profile picture updated successfully"})

# ---------- EMAIL REMINDERS ----------
def send_email_reminder(recipient_email, task_name, task_date, task_time):
    """Send email reminder for upcoming task"""
    if not EMAIL_ENABLED:
        return False
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient_email
        msg['Subject'] = f"🔔 Task Reminder: {task_name}"
        
        # Email body
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f4f4f4;">
                <div style="background-color: #16a34a; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="margin: 0;">🔔 Task Reminder</h1>
                </div>
                <div style="background-color: white; padding: 30px; border-radius: 0 0 10px 10px;">
                    <h2 style="color: #16a34a;">Upcoming Task:</h2>
                    <p style="font-size: 18px; font-weight: bold; color: #1e293b;">{task_name}</p>
                    <p style="color: #64748b;">
                        <strong>📅 Date:</strong> {task_date}<br>
                        <strong>⏰ Time:</strong> {task_time}
                    </p>
                    <p style="margin-top: 20px;">This task is due in approximately 1 hour. Don't forget to complete it!</p>
                    <div style="text-align: center; margin-top: 30px;">
                        <a href="http://127.0.0.1:5000" style="background-color: #16a34a; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">View Dashboard</a>
                    </div>
                </div>
                <div style="text-align: center; margin-top: 20px; color: #64748b; font-size: 12px;">
                    <p>This is an automated reminder from your AI Task Manager</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@app.route("/check_email_reminders", methods=["POST"])
def check_email_reminders():
    """Check for tasks due in 1 hour and send email reminders"""
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    if not EMAIL_ENABLED:
        return jsonify({"message": "Email reminders are disabled. Configure SMTP settings in app.py"}), 200
    
    try:
        conn = sqlite3.connect("tasks.db")
        c = conn.cursor()
        
        # Get user email
        c.execute("SELECT email FROM users WHERE id=?", (session["user_id"],))
        user = c.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user_email = user[0]
        
        # Get all pending tasks with date and time
        c.execute("""
            SELECT id, task, date, time 
            FROM tasks 
            WHERE user_id=? AND completed=0 AND date IS NOT NULL AND time IS NOT NULL
        """, (session["user_id"],))
        
        tasks = c.fetchall()
        conn.close()
        
        now = datetime.now()
        reminder_time = now + timedelta(hours=1)
        emails_sent = 0
        
        for task_id, task_name, task_date, task_time in tasks:
            try:
                task_datetime = datetime.strptime(f"{task_date} {task_time}", "%Y-%m-%d %H:%M")
                time_diff = (task_datetime - now).total_seconds() / 60  # minutes
                
                # Send reminder if task is due in 50-70 minutes (1 hour window)
                if 50 <= time_diff <= 70:
                    if send_email_reminder(user_email, task_name, task_date, task_time):
                        emails_sent += 1
            except Exception as e:
                print(f"Error processing task {task_id}: {e}")
                continue
        
        return jsonify({
            "success": True, 
            "message": f"Checked reminders. {emails_sent} email(s) sent.",
            "emails_sent": emails_sent
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
