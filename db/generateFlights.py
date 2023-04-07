import mysql.connector, datetime
from datetime import timedelta

database = mysql.connector.connect(
    host="localhost",
    user="root",
    password="PASSWORD",
    database="Assignment2DB"
)

cursor = database.cursor(buffered=True, dictionary=True)

# Generating data for the next 3 months from today
date = datetime.date.today()
date_final = date + timedelta(weeks=12)

flights_insert_query = "INSERT INTO flights (flight_start_point, flight_expected_departure_date, " \
                       "flight_expected_departure_time, flight_end_point, " \
                       "flight_expected_arrival_date, flight_expected_arrival_time, " \
                       "flight_is_interconnecting, flight_cost, " \
                       "flight_number_of_available_seats) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, " \
                       "(SELECT plane_total_seats FROM planes WHERE plane_code = %s))"

plane_to_flights_insert_query = "INSERT INTO plane_to_flight (flight_id, plane_id) VALUES (%s, " \
                                "(SELECT plane_id FROM planes WHERE plane_code = %s))"

flight_id_query = "SELECT flight_id FROM flights WHERE flight_expected_departure_date = %s AND " \
                  "flight_expected_departure_time = %s"

interconnecting_flights_insert_query = "INSERT INTO interconnecting_flights (flight_id_in, flight_id_out) " \
                                       "VALUES(%s, %s)"

while date <= date_final:
    date += timedelta(days=1)
    if date.weekday() == 0:
        # Inserting the monday flight from Dairy flat to Claris
        cursor.execute(flights_insert_query, ("NZNE", date.strftime("%Y-%m-%d"), "06:30", "NZGB",
                                              date.strftime("%Y-%m-%d"), "07:30", 0, 100, "GBSF2"))
        database.commit()
        cursor.execute(flight_id_query, (date.strftime("%Y-%m-%d"), "06:30"))
        flight_id = cursor.fetchone()['flight_id']
        cursor.execute(plane_to_flights_insert_query, (flight_id, 'GBSF2'))
        database.commit()

        # Inserting the flight from dairy flat to Tekapo
        cursor.execute(flights_insert_query, ("NZNE", date.strftime("%Y-%m-%d"), "12:00", "NZTL",
                                              date.strftime("%Y-%m-%d"), "14:20", 0, 250, "GBHJ2"))
        database.commit()
        cursor.execute(flight_id_query, (date.strftime("%Y-%m-%d"), "12:00"))
        flight_id = cursor.fetchone()['flight_id']
        cursor.execute(plane_to_flights_insert_query, (flight_id, "GBHJ2"))
        database.commit()
    if date.weekday() == 1:
        # Inserting the tuesday flight from Claris to Dairy flat
        cursor.execute(flights_insert_query, ("NZGB", date.strftime("%Y-%m-%d"), "06:30", "NZNE",
                                              date.strftime("%Y-%m-%d"), "07:30", 0, 100, "GBSF2"))
        database.commit()
        cursor.execute(flight_id_query, (date.strftime("%Y-%m-%d"), "06:30"))
        flight_id = cursor.fetchone()['flight_id']
        cursor.execute(plane_to_flights_insert_query, (flight_id, "GBSF2"))
        database.commit()

        # Inserting the Dairy Flat to Tuuta flight
        cursor.execute(flights_insert_query, ("NZNE", date.strftime("%Y-%m-%d"), "10:00", "NZCI",
                                              date.strftime("%Y-%m-%d"), "12:30", 0, 269, "GBHJ1"))
        database.commit()
        cursor.execute(flight_id_query, (date.strftime("%Y-%m-%d"), "10:00"))
        flight_id = cursor.fetchone()['flight_id']
        cursor.execute(plane_to_flights_insert_query, (flight_id, "GBHJ1"))
        database.commit()

    if date.weekday() == 2:
        # Inserting the wednesday flight for the Dairy flat to Claris
        cursor.execute(flights_insert_query, ("NZNE", date.strftime("%Y-%m-%d"), "06:30", "NZGB",
                                              date.strftime("%Y-%m-%d"), "07:30", 0, 100, "GBSF2"))
        database.commit()
        cursor.execute(flight_id_query, (date.strftime("%Y-%m-%d"), "06:30"))
        flight_id = cursor.fetchone()['flight_id']
        cursor.execute(plane_to_flights_insert_query, (flight_id, 'GBSF2'))
        database.commit()

        # Inserting the wednesday return flight from Tuuta to Dairy flat
        cursor.execute(flights_insert_query, ("NZCI", date.strftime("%Y-%m-%d"), "09:00", "NZNE",
                                              date.strftime("%Y-%m-%d"), "11:30", 0, 269, "GBHJ1"))
        database.commit()
        cursor.execute(flight_id_query, (date.strftime("%Y-%m-%d"), "09:00"))
        flight_id = cursor.fetchone()['flight_id']
        cursor.execute(plane_to_flights_insert_query, (flight_id, "GBHJ1"))
        database.commit()
    if date.weekday() == 4:
        # Inserting prestige flight
        # North shore to Rotorua leg
        cursor.execute(flights_insert_query, ("NZNE", date.strftime("%Y-%m-%d"), "05:00", "NZRO",
                                              date.strftime("%Y-%m-%d"), "06:00", 1, 150, "GBSJ1"))
        database.commit()
        cursor.execute(flight_id_query, (date.strftime("%Y-%m-%d"), "05:00"))
        flight_id = cursor.fetchone()['flight_id']
        flight_id_in = flight_id
        cursor.execute(plane_to_flights_insert_query, (flight_id, 'GBSJ1'))
        database.commit()
        # Rotorua to Sydney leg
        cursor.execute(flights_insert_query, ("NZRO", date.strftime("%Y-%m-%d"), "7:30", "YSSY",
                                              date.strftime("%Y-%m-%d"), "15:00", 0, 1500, "GBSJ1"))
        database.commit()
        cursor.execute(flight_id_query, (date.strftime("%Y-%m-%d"), "7:30"))
        flight_id = cursor.fetchone()['flight_id']
        flight_id_out = flight_id
        cursor.execute(plane_to_flights_insert_query, (flight_id, 'GBSJ1'))
        database.commit()
        # Inserting into the interconnecting_flights (connecting the Nothshore -> Rotorua and the Rotorua -> Sydney)
        cursor.execute(interconnecting_flights_insert_query, (flight_id_in, flight_id_out))
        database.commit()

        # Inserting the Friday flight for the Dairy flat to Claris
        cursor.execute(flights_insert_query, ("NZNE", date.strftime("%Y-%m-%d"), "06:30", "NZGB",
                                              date.strftime("%Y-%m-%d"), "07:30", 0, 100, "GBSF2"))
        database.commit()
        cursor.execute(flight_id_query, (date.strftime("%Y-%m-%d"), "06:30"))
        flight_id = cursor.fetchone()['flight_id']
        cursor.execute(plane_to_flights_insert_query, (flight_id, 'GBSF2'))
        database.commit()

        # Inserting the Friday flight from Claris to Dairy flat
        cursor.execute(flights_insert_query, ("NZGB", date.strftime("%Y-%m-%d"), "09:30", "NZNE",
                                              date.strftime("%Y-%m-%d"), "10:30", 0, 100, "GBSF2"))
        database.commit()
        cursor.execute(flight_id_query, (date.strftime("%Y-%m-%d"), "09:30"))
        flight_id = cursor.fetchone()['flight_id']
        cursor.execute(plane_to_flights_insert_query, (flight_id, "GBSF2"))
        database.commit()

        # Inserting the Friday flight from Dairy flat to Tuuta
        cursor.execute(flights_insert_query, ("NZNE", date.strftime("%Y-%m-%d"), "10:00", "NZCI",
                                              date.strftime("%Y-%m-%d"), "12:30", 0, 269, "GBHJ1"))
        database.commit()
        cursor.execute(flight_id_query, (date.strftime("%Y-%m-%d"), "10:00"))
        flight_id = cursor.fetchone()['flight_id']
        cursor.execute(plane_to_flights_insert_query, (flight_id, "GBHJ1"))
        database.commit()

        # Inserting the friday return flight from Tekapo to dairy flat
        cursor.execute(flights_insert_query, ("NZTL", date.strftime("%Y-%m-%d"), "12:00", "NZNE",
                                              date.strftime("%Y-%m-%d"), "14:20", 0, 250, "GBHJ2"))
        database.commit()
        cursor.execute(flight_id_query, (date.strftime("%Y-%m-%d"), "12:00"))
        flight_id = cursor.fetchone()['flight_id']
        cursor.execute(plane_to_flights_insert_query, (flight_id, "GBHJ2"))
        database.commit()
    if date.weekday() <= 4:
        # Inserting the twice daily shuttle service to Rotorua from dairy flat
        cursor.execute(flights_insert_query,
                       ("NZNE", date.strftime("%Y-%m-%d"), "05:30", "NZRO", date.strftime("%Y-%m-%d"),
                        "06:30", 0, 150, 'GBSF1'))
        database.commit()
        cursor.execute(flight_id_query, (date.strftime("%Y-%m-%d"), "05:30"))
        flight_id = cursor.fetchone()['flight_id']
        cursor.execute(plane_to_flights_insert_query, (flight_id, "GBSF1"))
        database.commit()

        cursor.execute(flights_insert_query,
                       ("NZRO", date.strftime("%Y-%m-%d"), "12:00", "NZNE", date.strftime("%Y-%m-%d"),
                        "13:00", 0, 150, 'GBSF1'))
        database.commit()
        cursor.execute(flight_id_query, (date.strftime("%Y-%m-%d"), "12:00"))
        flight_id = cursor.fetchone()['flight_id']
        cursor.execute(plane_to_flights_insert_query, (flight_id, "GBSF1"))
        database.commit()

        cursor.execute(flights_insert_query,
                       ("NZNE", date.strftime("%Y-%m-%d"), "15:30", "NZRO", date.strftime("%Y-%m-%d"),
                        "16:30", 0, 150, 'GBSF1'))
        database.commit()
        cursor.execute(flight_id_query, (date.strftime("%Y-%m-%d"), "15:30"))
        flight_id = cursor.fetchone()['flight_id']
        cursor.execute(plane_to_flights_insert_query, (flight_id, "GBSF1"))
        database.commit()

        cursor.execute(flights_insert_query,
                       ("NZRO", date.strftime("%Y-%m-%d"), "21:00", "NZNE", date.strftime("%Y-%m-%d"),
                        "22:00", 0, 150, 'GBSF1'))
        database.commit()
        cursor.execute(flight_id_query, (date.strftime("%Y-%m-%d"), "21:00"))
        flight_id = cursor.fetchone()['flight_id']
        cursor.execute(plane_to_flights_insert_query, (flight_id, "GBSF1"))
        database.commit()
    if date.weekday() == 5:
        # Inserting the Saturday flight from Claris to Dairy flat
        cursor.execute(flights_insert_query,
                       ("NZGB", date.strftime("%Y-%m-%d"), "06:30", "NZNE", date.strftime("%Y-%m-%d"),
                        "7:30", 0, 100, "GBSF2"))
        database.commit()
        cursor.execute(flight_id_query, (date.strftime("%Y-%m-%d"), "06:30"))
        flight_id = cursor.fetchone()['flight_id']
        cursor.execute(plane_to_flights_insert_query, (flight_id, "GBSF2"))
        database.commit()

        # Inserting the Saturday return flight from Tuuta to Dairy flat
        cursor.execute(flights_insert_query, ("NZCI", date.strftime("%Y-%m-%d"), "09:00", "NZNE",
                                              date.strftime("%Y-%m-%d"), "11:30", 0, 269, "GBHJ1"))
        database.commit()
        cursor.execute(flight_id_query, (date.strftime("%Y-%m-%d"), "09:00"))
        flight_id = cursor.fetchone()['flight_id']
        cursor.execute(plane_to_flights_insert_query, (flight_id, "GBHJ1"))
        database.commit()
    if date.weekday() == 6:
        # Inserting the Prestige flight from Sydney to Dairy flat
        # NOTE: All the times here are in NZ time, They are converted to the relative time zone at runtime
        arrival_date = date + timedelta(days=1)
        cursor.execute(flights_insert_query, ("YSSY", date.strftime("%Y-%m-%d"), "17:00", "NZNE",
                                              arrival_date.strftime("%Y-%m-%d"), "00:40", 0, 1500, "GBSJ1"))
        database.commit()
        cursor.execute(flight_id_query, (date.strftime("%Y-%m-%d"), "17:00"))
        flight_id = cursor.fetchone()['flight_id']
        cursor.execute(plane_to_flights_insert_query, (flight_id, "GBSJ1"))
        database.commit()

cursor.close()
database.close()
