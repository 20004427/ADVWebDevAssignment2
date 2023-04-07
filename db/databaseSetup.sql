DROP DATABASE IF EXISTS Assignment2DB;


/* CREATING THE DATABASE */
CREATE DATABASE Assignment2DB;

USE Assignment2DB;

CREATE TABLE flights (
    flight_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    flight_start_point VARCHAR(255) NOT NULL,
    /* Separating date and time to make it easier to filter/ search */
    flight_expected_departure_date Date NOT NULL,
    flight_expected_departure_time TIME NOT NULL,
    flight_end_point VARCHAR(255) NOT NULL,
    flight_expected_arrival_date Date NOT NULL,
    flight_expected_arrival_time TIME NOT NULL,
    flight_is_interconnecting TINYINT(1) NOT NULL DEFAULT 0,
    flight_cost DOUBLE NOT NULL,
    flight_number_of_available_seats INTEGER NOT NULL
);

CREATE TABLE interconnecting_flights (
    flight_id_in INTEGER NOT NULL,
    flight_id_out INTEGER NOT NULL
);

CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    user_username VARCHAR(255) NOT NULL UNIQUE,
    user_password VARCHAR(255) NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    user_level INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE user_to_flight (
    flight_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    seats_booked INTEGER NOT NULL,
    FOREIGN KEY (flight_id) REFERENCES flights(flight_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE plane_types (
    plane_type_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    plane_type_full_name VARCHAR(255) NOT NULL,
    plane_type_code VARCHAR(255) NOT NULL
);

CREATE TABLE planes (
    plane_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    plane_code VARCHAR(255) NOT NULL,
    plane_type_code VARCHAR(255) NOT NULL,
    plane_total_seats INTEGER NOT NULL
);

CREATE TABLE plane_to_flight (
    flight_id INTEGER NOT NULL,
    plane_id INTEGER NOT NULL,
    FOREIGN KEY (flight_id) REFERENCES flights(flight_id),
    FOREIGN KEY (plane_id) REFERENCES planes(plane_id)
);

/* ADDING VALUES TO THE DATABASE */
USE Assignment2DB;

DELIMITER //
CREATE procedure add_plane_types()
    BEGIN
    INSERT INTO plane_types (plane_type_full_name, plane_type_code)
        VALUES ("SyberJet", "SJ30i");
    INSERT INTO plane_types (plane_type_full_name, plane_type_code)
        VALUES ("CirrusJet", "SF50");
    INSERT INTO plane_types (plane_type_full_name, plane_type_code)
        VALUES ("HondaJet Elite", "HJE5");
    END //
DELIMITER ;
CALL add_plane_types();
DELIMITER //
CREATE procedure add_planes ()
    BEGIN
    INSERT INTO planes (plane_code, plane_type_code, plane_total_seats)
        VALUES ("GBSJ1", "SJ30i", 6);
    INSERT INTO planes (plane_code, plane_type_code, plane_total_seats)
        VALUES("GBSF1", 'SF50', 4);
    INSERT INTO planes (plane_code, plane_type_code, plane_total_seats)
        VALUES("GBSF2", 'SF50', 4);
    INSERT INTO planes (plane_code, plane_type_code, plane_total_seats)
        VALUES("GBHJ1", 'HJE5', 5);
    INSERT INTO planes (plane_code, plane_type_code, plane_total_seats)
        VALUES("GBHJ2", 'HJE5', 5);
    END //
DELIMITER ;
CALL add_planes();
