import responseCodes
import globalvars
mysql = ""


def init(_mysql):
    """function to initialize queries, rather than passing mysql into every function/
    having mysql in the global variables python file.

    :param _mysql: (object) mysql
    :return: (none) no return value
    """
    global mysql
    mysql = _mysql


def create_user(username, password, email=None):
    """A function to add a user row to the users table in the database
    Assignment2DB.

    :param username: (String)
    :param password: (String)
    :param email: (OPTIONAL String)
    :return: (int) response code: 0 (SUCCESS); 1 (User already exists)
    """
    query = f"SELECT COUNT(*) FROM users WHERE user_username = '{username}'"
    connection = mysql.connect()
    cursor = connection.cursor()
    cursor.execute(query)
    count = cursor.fetchone()[0]
    if count != 0:
        cursor.close()
        return responseCodes.DATABASE_ROW_ALREADY_EXISTS
    else:
        query = f"INSERT INTO users (user_username, user_password, user_email) " \
                f"VALUES ('{username}', '{password}', '{email}')"
        cursor.execute(query)
        connection.commit()
        connection.close()
        return responseCodes.SUCCESS


def fetch_user(username, password):
    """Function to fetch a user from the database Assignment2DB.
    If not null, the data has the form [username, password, email (null)]

    :param username: (String)
    :param password: (String)
    :return: (Array/ NULL) data
    """
    query = f"SELECT * FROM users WHERE " \
            f"user_username = '{username}' AND user_password = '{password}'"
    connection = mysql.connect()
    cursor = connection.cursor()
    cursor.execute(query)
    data = cursor.fetchone()
    connection.close()
    return data


def fetch_all_flight_details(search_term="",interconnecting_flights=False ,start_date="", end_date="",
                             sort_by="flight_expected_departure_date", direction="ASC"):
    """Function to fetch all flights from database Assignment2DB
    Data has the form [flight_id, flight_start_point, flight_expected_departure_time,
    flight_expected_departure_day, flight_end_point, flight_expected_arrival_time,
    flight_is_interconnecting, flight_cost, plane_id, plane_code, plane_type_code,
    plane_total_seats, plane_available_seats]

    :param search_term: (String)
    :param interconnecting_flights: (boolean)
    :param start_date: (String)
    :param end_date: (String)
    :param sort_by: (String)
    :param direction: (String)
    :return: (Array) data
    """
    # From my internship, I found that for larger queries its good practice to state what you want to
    # retrieve instead of using '*'. Even for smaller queries it is useful
    # - as it makes it easier to work out what it being retrieved.
    # Database queries are very expensive (mainly in large databases) - so it is good practice
    # to retrieve all the data you need in as few queries as possible.
    query = "SELECT f.flight_id, flight_start_point, date_format(flight_expected_departure_date, '%d/%m/%y')," \
            "time_format(flight_expected_departure_time, '%h:%i %p'), flight_end_point, " \
            "date_format(flight_expected_arrival_date, '%d/%m/%y')," \
            "time_format(flight_expected_arrival_time, '%h:%i %p'), flight_is_interconnecting, " \
            "flight_cost, p.plane_id, plane_code, plane_type_code," \
            "plane_total_seats, flight_number_of_available_seats FROM flights f INNER JOIN plane_to_flight ptf " \
            "ON ptf.flight_id = f.flight_id INNER JOIN planes p ON p.plane_id = ptf.plane_id "
    if search_term != "":
        query += f"WHERE (flight_end_point LIKE '%{search_term}%' OR flight_start_point LIKE '%{search_term}%' OR " \
                 f"plane_type_code LIKE '%{search_term}%' OR plane_code LIKE '%{search_term}%') "
    if start_date != "":
        query += f"AND flight_expected_departure_date >= '{start_date}' "
    if end_date != "":
        query += f"AND flight_expected_departure_date <= '{end_date}' "
    if interconnecting_flights == 'true':
        query += "AND flight_is_interconnecting = 1 "
    query += f"ORDER BY {sort_by} {direction}, flight_expected_departure_time {direction}"
    connection = mysql.connect()
    cursor = connection.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    connection.close()
    return data


def fetch_details_for_booking(flight_id):
    """Essentially the same as fetch_all_flight_details,
    however this function just fetches the details for one flight.
    NOTE: it is assumed that the flight exists (which it should if this function is called)
    The data returned is in the format [flight_id, flight_start_point, flight_expected_departure_date,
    flight_expected_departure_time, flight_end_point, flight_expected_arrival_date,
    flight_expected_arrival_time, flight_is_interconnecting, flight_cost, plane_id, plane_code, plane_type_code,
    total_seats, plane_available_seats]. This is for both the details and interconnecting flight details

    :param flight_id: (int)
    :return: (array) details, (array| NULL) interconnecting flight details
    """
    query = "SELECT f.flight_id, flight_start_point, flight_expected_departure_date," \
            "flight_expected_departure_time, flight_end_point, flight_expected_arrival_date," \
            "flight_expected_arrival_time, flight_is_interconnecting, " \
            "flight_cost, p.plane_id, plane_code, plane_type_code," \
            "plane_total_seats, flight_number_of_available_seats FROM flights f INNER JOIN plane_to_flight ptf " \
            "ON ptf.flight_id = f.flight_id INNER JOIN planes p ON " \
            f"p.plane_id = ptf.plane_id WHERE f.flight_id = {flight_id}"
    connection = mysql.connect()
    cursor = connection.cursor()
    cursor.execute(query)
    data = cursor.fetchone()
    interconnecting_flight_data = None
    if data[7] == 1:
        interconnecting_flight_data = get_interconnecting_flight(flight_id)
    connection.close()
    return data, interconnecting_flight_data


def make_a_booking(flight_id, user_id, no_seats_to_book):
    """Function to make a link between a user and a flight,
    That is, make a booking. Returns 0 on success. Returns 1 on booking
    already exists.

    :param flight_id: (int)
    :param user_id: (int)
    :param no_seats_to_book: (int)
    :return: (int) responseCode. 0 or 1
    """
    # Double checking that there are still seats available
    seats = get_available_seats(flight_id)
    if seats[1] - no_seats_to_book < 0 or seats[1] <= 0:
        return responseCodes.INVALID_INPUT
    user_has_previously_booked = check_user_has_booked_flight(flight_id, user_id)
    connection = mysql.connect()
    cursor = connection.cursor()
    if not user_has_previously_booked:
        query = "INSERT INTO user_to_flight (flight_id, user_id, seats_booked) VALUES (" \
                f"'{flight_id}', '{user_id}', '{no_seats_to_book}')"
    else:
        user_cur_booked_seats = int(get_number_of_seats_user_booked(flight_id, user_id))
        user_cur_booked_seats += no_seats_to_book
        query = f"UPDATE user_to_flight SET seats_booked = '{user_cur_booked_seats}' WHERE " \
                f"user_id = '{user_id}' AND flight_id = '{flight_id}'"
    cursor.execute(query)
    connection.commit()
    connection.close()
    # updating the number of available seats
    update_flight_available_seats(flight_id, seats[1] - no_seats_to_book)
    return responseCodes.SUCCESS


def cancel_a_booking(flight_id, user_id, seats_to_cancel, max_seats):
    """Removes a users booking. Will delete the row entirely from the user_to_flights table
    if the user no longer has seats booked.

    :param flight_id: (int)
    :param user_id: (int)
    :param seats_to_cancel: (int)
    :param max_seats: (int) the number of seats the user has booked in total.
    :return: (None | int) int => return code
    """
    connection = mysql.connect()
    cursor = connection.cursor()
    new_seats_value = max_seats - seats_to_cancel
    if new_seats_value > 0:
        query = f"UPDATE user_to_flight SET seats_booked = {new_seats_value} WHERE " \
                f"flight_id = {flight_id} AND user_id = {user_id}"
    else:
        query = f"DELETE FROM user_to_flight WHERE user_id = {user_id} AND flight_id = {flight_id}"
    cursor.execute(query)
    connection.commit()
    query = f"SELECT flight_number_of_available_seats FROM flights WHERE flight_id = {flight_id}"
    cursor.execute(query)
    old_seats_value = cursor.fetchone()[0]
    new_seats_value = old_seats_value + seats_to_cancel
    query = f"UPDATE flights SET flight_number_of_available_seats = {new_seats_value} WHERE " \
            f"flight_id = {flight_id}"
    cursor.execute(query)
    connection.commit()
    connection.close()
    return responseCodes.SUCCESS


def get_available_seats(flight_id):
    """Function to get the number of seats available.
    Returns [maximum number of seats, current number of available seats]

    :param flight_id: (int)
    :return: (Array)
    """
    connection = mysql.connect()
    cursor = connection.cursor()
    query = "SELECT p.plane_total_seats, f.flight_number_of_available_seats FROM flights f INNER JOIN " \
            "plane_to_flight ptf ON f.flight_id = ptf.flight_id INNER JOIN planes p ON ptf.plane_id = " \
            f"p.plane_id WHERE f.flight_id = '{flight_id}'"
    cursor.execute(query)
    results = cursor.fetchone()
    connection.close()
    return results


def check_user_has_booked_flight(flight_id, user_id):
    """Function to check if a user has previously booked the flight.

    :param flight_id: (int)
    :param user_id: (int)
    :return: (boolean)
    """
    connection = mysql.connect()
    cursor = connection.cursor()
    query = f"SELECT COUNT(*) FROM user_to_flight WHERE flight_id = '{flight_id}' " \
            f"AND user_id = '{user_id}'"
    cursor.execute(query)
    results = cursor.fetchone()
    connection.close()
    if results[0] > 0:
        return True
    return False


def get_number_of_seats_user_booked(flight_id, user_id):
    """Function to get the number of seats a user has booked for a flight

    :param flight_id: (int)
    :param user_id: (int)
    :return: (int) number of seats booked
    """
    connection = mysql.connect()
    cursor = connection.cursor()
    query = f"SELECT seats_booked FROM user_to_flight WHERE flight_id = '{flight_id}' " \
            f"AND user_id = '{user_id}'"
    cursor.execute(query)
    results = cursor.fetchone()[0]
    connection.close()
    return results


def get_user_flights_booked(user_id):
    """Function to get all the flights a user has booked.
    Details are of the form: [flight_id, flight_start_point, flight_expected_departure_date,
    flight_expected_departure_time, flight_end_point, flight_expected_arrival_date,
    flight_expected_arrival_time, flight_is_interconnecting,
    flight_cost, plane_id, plane_code, plane_type_code, seats_booked, plane_total_seats

    :param user_id: (int)
    :return: (Array[Array]) details
    """
    connection = mysql.connect()
    cursor = connection.cursor()
    query = "SELECT f.flight_id, flight_start_point, flight_expected_departure_date," \
            "flight_expected_departure_time, flight_end_point, flight_expected_arrival_date," \
            "flight_expected_arrival_time, flight_is_interconnecting, " \
            "flight_cost, p.plane_id, plane_code, plane_type_code," \
            "utf.seats_booked, plane_total_seats FROM flights f " \
            "INNER JOIN user_to_flight utf ON utf.flight_id = f.flight_id INNER JOIN " \
            "plane_to_flight ptf ON ptf.flight_id = f.flight_id INNER JOIN planes p ON " \
            f"p.plane_id = ptf.plane_id WHERE utf.user_id = '{user_id}'"
    cursor.execute(query)
    results = cursor.fetchall()
    connection.close()
    return results


def update_flight_available_seats(flight_id, no_seats):
    """updates the available seats for a given flight

    :param flight_id: (int)
    :param no_seats: (int)
    :return: (int) return code
    """
    connection = mysql.connect()
    cursor = connection.cursor()
    query = f"UPDATE flights SET flight_number_of_available_seats = '{no_seats}' " \
            f"WHERE flight_id = '{flight_id}'"
    cursor.execute(query)
    connection.commit()
    connection.close()
    responseCodes.SUCCESS


def get_interconnecting_flight(flight_id):
    """Gets the interconnecting flight that the given flight_id
    connects to. Makes a call to fetch_details_for_booking.
    see fetch_details_for_booking for returns

    :param flight_id: (int)
    :return: (array) details
    """
    connection = mysql.connect()
    cursor = connection.cursor()
    query = f"SELECT flight_id_out FROM interconnecting_flights WHERE flight_id_in = {flight_id}"
    cursor.execute(query)
    connection.close()
    flight_id_out = cursor.fetchone()[0]
    interconnecting_flight_data = fetch_details_for_booking(flight_id_out)
    return interconnecting_flight_data[0]
