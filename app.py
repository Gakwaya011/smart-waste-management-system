from flask import Flask, render_template, request, redirect, session
from flask_restful import Resource, Api, reqparse
import pymysql

app = Flask(__name__)
api = Api(app)

# Configure secret key for session encryption
app.secret_key = 'insideJoke'  # Replace with a strong secret key

# Database connection setup
conn = pymysql.connect(host='sql12.freesqldatabase.com', user='sql12717723', password='2wRFUq3YKZ', db='sql12717723', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

# Parsers for request arguments
login_parser = reqparse.RequestParser()
login_parser.add_argument('username', type=str, required=True, help="Username cannot be blank!")
login_parser.add_argument('password', type=str, required=True, help="Password cannot be blank!")
login_parser.add_argument('option', type=str, required=True, help="Option cannot be blank!")

register_parser = reqparse.RequestParser()
register_parser.add_argument('username', type=str, required=True, help="Username cannot be blank!")
register_parser.add_argument('email', type=str, required=True, help="Email cannot be blank!")
register_parser.add_argument('password', type=str, required=True, help="Password cannot be blank!")
register_parser.add_argument('option', type=str, required=True, help="Option cannot be blank!")

# API Resources
class LoginAPI(Resource):
    def post(self):
        args = login_parser.parse_args()
        username = args['username']
        password = args['password']
        opt = args['option']
        
        # Change the options to their correspondence
        if opt == 'Admin':
            opt = 'admin'
        elif opt == 'Household User':
            opt = 'User'
        elif opt == 'Waste Collection Services':
            opt = 'Provider'
        else:
            return {"message": "Invalid option. Please try again."}, 400

        try:
            sql = "SELECT * FROM users WHERE username = %s AND password = %s AND `option` = %s"
            cursor = conn.cursor()
            cursor.execute(sql, (username, password, opt))
            user = cursor.fetchone()
            cursor.close()
            if user:
                session['username'] = username
                session['role'] = opt
                return {"message": "Login successful", "role": opt}, 200
            else:
                return {"message": "Invalid username or password. Please try again."}, 401
        except pymysql.MySQLError as e:
            print(f"Error: {e}")
            return {"message": "An error occurred while logging in. Please try again later."}, 500

class RegisterAPI(Resource):
    def post(self):
        args = register_parser.parse_args()
        username = args['username']
        email = args['email']
        password = args['password']
        option = args['option']
        
        # Basic validation
        if not username or not email or not password or not option:
            return {"message": "All fields are required."}, 400
        
        try:
            sql = "INSERT INTO users (username, email, password, `option`) VALUES (%s, %s, %s, %s)"
            cursor = conn.cursor()
            cursor.execute(sql, (username, email, password, option))
            conn.commit()
            cursor.close()
            return {"message": "Registration successful"}, 201
        except pymysql.MySQLError as e:
            print(f"Error: {e}")
            return {"message": "An error occurred while registering. Please try again later."}, 500



# Add API resources to API
api.add_resource(LoginAPI, '/api/login')
api.add_resource(RegisterAPI, '/api/register')

# Web routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        opt = request.form.get('option')

        # Change the options to their correspondence
        if opt == 'Admin':
            opt = 'admin'
        elif opt == 'Household User':
            opt = 'User'
        elif opt == 'Waste Collection Services':
            opt = 'Provider'
        else:
            return "Invalid option. Please try again.", 500
    
        try:
            sql = "SELECT * FROM users WHERE username = %s AND password = %s AND `option` = %s"
            cursor = conn.cursor()
            cursor.execute(sql, (username, password, opt))
            user = cursor.fetchone()
            cursor.close()
            if user:
                session['username'] = username
                session['role'] = opt
                if opt == 'admin':
                    return redirect('/admin')
                elif opt == 'User':
                    return redirect('/user')
                elif opt == 'Provider':
                    return redirect('/provider')
            else:
                error = "Invalid username or password. Please try again."
                return render_template('login.html', error=error)
        except pymysql.MySQLError as e:
            print(f"Error: {e}")
            error = "An error occurred while logging in. Please try again later."
            return render_template('login.html', error=error)                                       
    else:
        return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        option = request.form.get('option')
        
        # Basic validation
        if not username or not email or not password or not option:
            return "All fields are required.", 400
        
        try:
            sql = "INSERT INTO users (username, email, password, `option`) VALUES (%s, %s, %s, %s)"
            cursor = conn.cursor()
            cursor.execute(sql, (username, email, password, option))
            conn.commit()
            cursor.close()
            return render_template('login.html')
        except pymysql.MySQLError as e:
            print(f"Error: {e}")
            return "An error occurred while registering. Please try again later.", 500
    else:
        return render_template('signup.html')

# dashboards routes
@app.route('/admin')
def admin():
    if 'username' not in session or session['role'] != 'admin':
        return redirect('/login')
    username = session['username']

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(username) AS total_providers FROM users WHERE `option` = 'Provider'")
        result = cursor.fetchone()
        cursor.close()
        total_providers = result['total_providers']

        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(username) AS booknum FROM bookings")
        result = cursor.fetchone()
        cursor.close()
        booknum = result['booknum']

        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(username) AS total_users FROM users WHERE `option` = 'User'")
        result = cursor.fetchone()
        cursor.close()
        total_users = result['total_users']

        cursor = conn.cursor()
        cursor.execute("SELECT SUM(revenue) AS total_sum FROM bookings WHERE revenue IS NOT NULL")
        result = cursor.fetchone()
        cursor.close()
        total_sum = result['total_sum']

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bookings WHERE revenue IS NOT NULL ORDER BY date DESC")
        recent = cursor.fetchall()
        cursor.close()

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bookings WHERE revenue IS NOT NULL LIMIT 5")
        bookings = cursor.fetchall()
        cursor.close()
        return render_template('admin-dashboard/index.html', recent=recent, total_sum=total_sum, total_users=total_users, booknum=booknum, total_providers=total_providers, bookings=bookings, username=username, role=session.get('role'))
    
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        error = "An error occurred while retrieving bookings. Please try again later."
        return render_template('admin-dashboard/index.html', error=error)
    

@app.route('/user')
def user():
    if 'username' not in session or session['role'] != 'User':
        return redirect('/login')
    username = session['username']

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(DISTINCT username) AS total_providers FROM users WHERE `option` = 'Provider'")
        result = cursor.fetchone()
        cursor.close()

        if result is None:
            total_providers = 0
        else:
            total_providers = result['total_providers']

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bookings WHERE revenue IS NOT NULL")
        bookings = cursor.fetchall()
        cursor.close()
        return render_template('user-dashboard/index.html', total_providers=total_providers, bookings=bookings, username=username, role=session.get('role'))
    
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        error = "An error occurred while retrieving bookings. Please try again later."
        return render_template('user-dashboard/index.html', error=error)

@app.route('/provider')
def provider():
    if 'username' not in session or session['role'] != 'Provider':
        return redirect('/login')
    username = session['username']

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(username) AS booknum FROM bookings")
        result = cursor.fetchone()
        cursor.close()
        booknum = result['booknum']

        cursor = conn.cursor()
        cursor.execute("SELECT SUM(revenue) AS total_sum FROM bookings WHERE revenue IS NOT NULL")
        result = cursor.fetchone()
        cursor.close()
        total_sum = result['total_sum']

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bookings WHERE revenue IS NOT NULL ORDER BY date DESC")
        bookings = cursor.fetchall()
        cursor.close()
        return render_template('provider-dashboard/index.html', total_sum=total_sum, booknum=booknum, bookings=bookings, username=username, role=session.get('role'))
    
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        error = "An error occurred while retrieving bookings. Please try again later."
        return render_template('provider-dashboard/index.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# Common pages
@app.route('/faq')
def faq():
    return render_template('common/pages-faq.html', role=session.get('role'))

@app.route('/contact')
def contact():
    return render_template('common/pages-contact.html', role=session.get('role'))

@app.route('/profile', methods=['POST', 'GET'])
def profile():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')

        try:
            sql = "UPDATE users SET username = %s, email = %s WHERE username = %s"
            cursor = conn.cursor()
            cursor.execute(sql, (username, email, session['username']))
            conn.commit()
            cursor.close()
            # Update session username if it changes
            session['username'] = username
            return redirect('/profile')
        except pymysql.MySQLError as e:
            print(f"Error: {e}")
            error = "An error occurred while updating user data. Please try again later."
            return render_template('common/users-profile.html', error=error)

    else:
        if 'username' not in session:
            return redirect('/login')
        username = session['username']

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            cursor.close()
            if user:
                return render_template('common/users-profile.html', email=user['email'], username=username, role=session.get('role'))
            else:
                error = "User not found."
                return render_template('common/users-profile.html', error=error)
        except pymysql.MySQLError as e:
            print(f"Error: {e}")
            error = "An error occurred while retrieving user data. Please try again later."
            return render_template('common/users-profile.html', error=error)

    # Default return for unexpected paths
    return render_template('common/users-profile.html')
@app.route('/book', methods=['POST', 'GET'])
def book():
    if 'username' not in session:
        return redirect('/login')
    username = session['username']

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        address = request.form.get('address')
        date = request.form.get('date')
        company = request.form.get('company')

        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO bookings (username, adress, date, email, company) VALUES (%s, %s, %s, %s, %s)", (username, address, date, email, company))
            conn.commit()
            cursor.close()
            return render_template('user-dashboard/forms-layouts.html')
        except pymysql.MySQLError as e:
            print(f"Error: {e}")
            error = "An error occurred while booking. Please try again later."
            return render_template('user-dashboard/forms-layouts.html', error=error)
    else:
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users where `option` = 'Provider'")
            users = cursor.fetchall()
            cursor.close()
            return render_template('user-dashboard/forms-layouts.html', users=users, username=username)

        except pymysql.MySQLError as e:
            print(f"Error: {e}")
            error = "Trouble getting the companies. Please try again later."
            return render_template('user-dashboard/forms-layouts.html', error=error)


@app.route('/table')
def table():
    if 'username' not in session:
        return redirect('/login')
    username = session['username']

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bookings")
        bookings = cursor.fetchall()
        cursor.close()
        return render_template('user-dashboard/tables-data.html', bookings=bookings, username=username, role=session.get('role'))

    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        error = "An error occurred while retrieving bookings. Please try again later."
        return render_template('user-dashboard/tables-data.html', error=error)

@app.route('/appointments')
def appointments():
    if 'username' not in session:
        return redirect('/login')
    username = session['username']

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bookings WHERE company = %s", (username))
        bookings = cursor.fetchall()
        cursor.close()
        return render_template('provider-dashboard/tables-data.html', bookings=bookings, username=username, role=session.get('role'))

    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        error = "An error occurred while retrieving bookings. Please try again later."
        return render_template('provider-dashboard/tables-data.html', error=error)
    
@app.route('/management', methods=['POST', 'GET'])
def management():
    if 'username' not in session:
        return redirect('/login')
    username = session['username']

    if request.method == 'POST':
        revenue = request.form.get('revenue')
        status = request.form.get('status')
        username = request.form.get('username')

        if status != "Done" and status != "Cancelled":
            return status, 5000

        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE bookings SET revenue = %s, status = %s WHERE username = %s", (revenue, status, username))
            conn.commit()
            cursor.close()
            return redirect('/appointments')
        except pymysql.MySQLError as e:
            print(f"Error: {e}")
            error = "An error occurred while booking. Please try again later."
            return render_template('provider-dashboard/forms-layouts.html', error=error)
        
    else:
        booking_id = request.args.get('booking_id')

        if booking_id:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM bookings WHERE id = %s", (booking_id))
            booking = cursor.fetchone()
            cursor.close()

        return render_template('provider-dashboard/forms-layouts.html', booking=booking)


@app.route('/users-list')
def users_list():
    if 'username' not in session:
        return redirect('/login')
    username = session['username']

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE `option` = 'User'")
        bookings = cursor.fetchall()
        cursor.close()
        return render_template('admin-dashboard/users.html', bookings=bookings, username=username, role=session.get('role'))

    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        error = "An error occurred while retrieving users. Please try again later."
        return render_template('admin-dashboard/tables-data.html', error=error)

@app.route('/providers-list')
def providers_list():
    if 'username' not in session:
        return redirect('/login')
    username = session['username']

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE `option` = 'Provider'")
        bookings = cursor.fetchall()
        cursor.close()
        return render_template('admin-dashboard/providers.html', bookings=bookings, username=username, role=session.get('role'))

    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        error = "An error occurred while retrieving providers. Please try again later."
        return render_template('admin-dashboard/bookings.html', error=error)


@app.route('/bookings-list')
def bookings_list():
    if 'username' not in session:
        return redirect('/login')
    username = session['username']

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bookings")
        bookings = cursor.fetchall()
        cursor.close()
        return render_template('admin-dashboard/bookings.html', bookings=bookings, username=username, role=session.get('role'))

    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        error = "An error occurred while retrieving bookings. Please try again later."
        return render_template('admin-dashboard/bookings.html', error=error)


if __name__ == '__main__':
    app.run(debug=True)
