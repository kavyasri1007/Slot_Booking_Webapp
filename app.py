from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'


db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Kavya@1213", 
    database="blueapple"
)
cursor = db.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS slots (
    id INT AUTO_INCREMENT PRIMARY KEY,
    slot_time VARCHAR(50) NOT NULL,
    booked_by VARCHAR(255) DEFAULT NULL
)
""")


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        account = cursor.fetchone()
        if account:
            return "User already exists! Please <a href='/login'>login</a>."
        cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, password))
        db.commit()
        return "Registration Successful! <a href='/login'>Login Now</a>"
    return render_template('register.html')


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        account = cursor.fetchone()
        if account:
            session['email'] = email
            return redirect('/dashboard')
        else:
            return "Login Failed! <a href='/login'>Try again</a>"
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        return redirect('/login')
    cursor.execute("SELECT id, email FROM users")
    users = cursor.fetchall()
    total_users = len(users)
    return render_template('dashboard.html', users=users, total_users=total_users, email=session['email'])

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/')


@app.route('/slots')
def slots():
    if 'email' not in session:
        return redirect('/login')
    cursor.execute("SELECT id, slot_time, booked_by FROM slots")
    slot_list = cursor.fetchall()
    return render_template('slots.html', slots=slot_list, email=session['email'])


@app.route('/book/<int:slot_id>')
def book_slot(slot_id):
    if 'email' not in session:
        return redirect('/login')
    
    cursor.execute("SELECT booked_by FROM slots WHERE id=%s", (slot_id,))
    slot = cursor.fetchone()
    if slot and slot[0] is None:
        cursor.execute("UPDATE slots SET booked_by=%s WHERE id=%s", (session['email'], slot_id))
        db.commit()
        return redirect('/slots')
    else:
        return "Slot already booked! <a href='/slots'>Back to Slots</a>"
@app.route('/users')
def users():
    cursor = db.cursor()
    cursor.execute("SELECT id, email FROM users")
    user_list = cursor.fetchall()
    return render_template("users.html", users=user_list)

if __name__ == '__main__':
    app.run(debug=True)