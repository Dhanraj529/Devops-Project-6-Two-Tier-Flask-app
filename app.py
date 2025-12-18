import os
import time
from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

# =========================
# MySQL Configuration
# =========================
# IMPORTANT:
# In Docker, MySQL host MUST be the service name: "mysql"
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'mysql')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'root')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'flaskdb')

mysql = MySQL(app)

# =========================
# Initialize Database
# =========================
def init_db():
    for i in range(10):  # retry 10 times
        try:
            with app.app_context():
                cur = mysql.connection.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        message TEXT
                    );
                """)
                mysql.connection.commit()
                cur.close()

            print("✅ MySQL connected and table initialized")
            return

        except Exception as e:
            print(f"⏳ Waiting for MySQL... ({i+1}/10)")
            time.sleep(5)

    raise Exception("❌ Could not connect to MySQL after retries")

# =========================
# Routes
# =========================
@app.route('/')
def home():
    cur = mysql.connection.cursor()
    cur.execute("SELECT message FROM messages")
    messages = cur.fetchall()
    cur.close()
    return render_template('index.html', messages=messages)

@app.route('/submit', methods=['POST'])
def submit():
    new_message = request.form.get('new_message')
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO messages (message) VALUES (%s)", [new_message])
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': new_message})

# =========================
# App Start
# =========================
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
