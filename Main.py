from datetime import timedelta, datetime
from flask import Flask, render_template, send_file, request, Blueprint, flash, url_for, session, redirect, json
from flaskext.mysql import MySQL
import queries
import secrets
import responseCodes
import datetime

global app, mysql, login_manager

app = Flask(__name__)
mysql = MySQL()
# ______________ DATABASE INITIALIZATION ______________
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'PASSWORD'
app.config['MYSQL_DATABASE_DB'] = 'Assignment2DB'
# ______________ !UNCOMMENT THIS IF USING DOCKER! ______________
# app.config['MYSQL_DATABASE_HOST'] = 'db'

app.secret_key = secrets.token_urlsafe(24)
app.permanent_session_lifetime = timedelta(minutes=60)
mysql.init_app(app)

queries.init(mysql)

# ______________ PATH BLUEPRINTS ______________
app_routes_blueprint = Blueprint('main', __name__)
app.register_blueprint(app_routes_blueprint)


# ______________ FILTERS FOR TEMPLATING ______________
# Also, from what I could tell. you can only pass one parameter to these.
# In jinja2, they are called like '<variable> | function', rather than
# 'function(<variable>)'
@app.template_filter('str_to_date')
def str_to_date(date):
    if type(date) == datetime.date:
        return date
    return datetime.datetime.strptime(date, "%d/%m/%y").date()


@app.template_filter('str_to_time')
def str_to_time(time):
    if type(time) == str:
        time = datetime.datetime.strptime(time, "%I:%M %p")
    elif type(time) == datetime.timedelta:
        time = datetime.datetime.strptime(str(time), "%H:%M:%S")
    return time.time()


@app.route('/')
def index():
    return render_template('index.html', loggedin=('loggedin' in session))


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        if "loggedin" in session:
            flash("You're already logged in", "Success")
            return redirect(url_for('index'))
        return render_template('login.html')
    else:
        username = request.form["username"]
        password = request.form["password"]
        if username == "":
            flash("Please enter your username", 'Error')
            return url_for('login')
        elif password == "":
            flash("Please enter your password", "Error")
            return url_for('login')
        user = queries.fetch_user(username, password)
        if user is None:
            flash("Invalid username or password", "Error")
            return url_for('login')
        session['loggedin'] = True
        session['user_id'] = user[0]
        session['username'] = username
        session['password'] = password
        session['email'] = user[3]
        flash("You've been successfully logged in.", "Success")
        return url_for('profile')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "GET":
        return render_template('register.html')
    else:
        username = request.form["username"]
        password = request.form["password"]
        email = request.form.get("email")
        if username == "":
            flash("Username cannot be empty", 'Error')
            # NOTE: ajax does not work directly with redirect,
            # instead you have to return the url to redirect to.
            return url_for('register')
        elif password == "":
            flash("Password cannot be empty", 'Error')
            return url_for('register')
        code = queries.create_user(username, password, email)
        if code == responseCodes.DATABASE_ROW_ALREADY_EXISTS:
            flash("A user already exists with that username", 'Error')
            return url_for("register")
        else:
            flash("Successfully registered with that username", 'Success')
            return url_for("login")


@app.route('/logout', methods=['POST'])
def logout():
    if 'loggedin' not in session:
        flash("You are already logged out", 'Success')
    else:
        session.pop('loggedin', None)
        session.pop('user_id', None)
        session.pop('username', None)
        session.pop('password', None)
        session.pop('email', None)
    return redirect(url_for('index'))


@app.route('/profile', methods=['GET'])
def profile():
    if 'loggedin' not in session:
        flash("You are not logged in", 'Error')
        return redirect(url_for('index'))
    booked_flights = queries.get_user_flights_booked(session.get("user_id"))
    total_cost = 0
    date_now = datetime.date.today()
    time_now = datetime.datetime.now().time()
    for flight in booked_flights:
        total_cost += flight[8] * flight[12]
    return render_template('profile.html', loggedin=('loggedin' in session), user_info=session,
                           flights=booked_flights, total_cost=total_cost, date_now=date_now,
                           time_now=time_now)


@app.route('/checkout', methods=['GET'])
def checkout():
    if 'loggedin' not in session:
        flash("You are not logged in", 'Error')
        return redirect(url_for('index'))
    return render_template('checkout.html', loggedin=('loggedin' in session))


@app.route('/flights', methods=['GET'])
def flights():
    all_flights = queries.fetch_all_flight_details()
    date_now = datetime.date.today()
    time_now = datetime.datetime.now().time()
    return render_template('flights.html', loggedin=('loggedin' in session), flights=all_flights, date_now=date_now,
                           time_now=time_now)


@app.route('/booking', methods=['GET'])
def booking():
    flight_id = request.args.get('flight_id', type=int)
    details = queries.fetch_details_for_booking(flight_id)
    date_now = datetime.date.today()
    time_now = datetime.datetime.now().time()
    return render_template('booking.html', loggedin=('loggedin' in session), details=details[0],
                           interconnecting_flight=details[1], date_now=date_now, time_now=time_now)


@app.route("/book", methods=['POST'])
def book():
    if 'loggedin' not in session:
        flash("Please login to make a booking", "Error")
        return url_for('login')
    flight_id = request.form.get('flight_id', type=int)
    user_id = session.get("user_id")
    no_seats_to_book = request.form.get('no_seats_to_book', type=int)
    code = queries.make_a_booking(flight_id, user_id, no_seats_to_book)
    if code == responseCodes.INVALID_INPUT:
        flash("Sorry, but this flight is fully booked", "Error")
        return url_for('flights')
    flash("Booking successful!", "Success")
    return url_for("profile")


@app.route("/cancel_booking", methods=['POST'])
def cancel_booking():
    if 'loggedin' not in session:
        flash("Please login to cancel a booking", "Error")
        return url_for('login')
    flight_id = request.form.get("flight_id", type=int)
    seats_to_cancel = request.form.get("seats_to_cancel", type=int)
    max_seats_to_cancel = request.form.get("max_seats_to_cancel", type=int)
    user_id = session.get("user_id")
    if seats_to_cancel is None:
        return "INVALID_INPUT", responseCodes.INVALID_INPUT
    if seats_to_cancel < 0 or seats_to_cancel > max_seats_to_cancel:
        return "INVALID_INPUT", responseCodes.INVALID_INPUT
    queries.cancel_a_booking(flight_id, user_id, seats_to_cancel, max_seats_to_cancel)
    flash("Successfully canceled your booking", "Success")
    return url_for('profile')


@app.route("/search_all_flights", methods=["GET"])
def search_all_flights():
    search_term = request.args.get("search_term")
    interconnecting_flights = request.args.get("interconnecting_flights")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    sort_column = request.args.get("sort_column")
    sort_direction = request.args.get("sort_direction")
    if sort_column and sort_direction:
        data = queries.fetch_all_flight_details(search_term, interconnecting_flights, start_date, end_date,
                                                sort_column, sort_direction)
    else:
        data = queries.fetch_all_flight_details(search_term, interconnecting_flights, start_date, end_date)
    return json.jsonify(data)


@app.route('/favicon.ico')
def favicon():
    return send_file("static/images/favicon.jpg", mimetype="image/jpeg")


if __name__ == '__main__':
    Flask.run(app, host='0.0.0.0', port=8000)
