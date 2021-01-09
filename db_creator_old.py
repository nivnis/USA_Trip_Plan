from random import uniform
import mysql.connector as MySQL
from mysql.connector import errorcode
from csv import reader, writer

CAMP_ROW_COLUMNS = [5, 15]  # id
CAMP_ROW_LOCATIONS_COLUMNS = [0, 1, 3, 11]  # type, id
PARKS_ROW_COLUMNS = [6, 21]  # id
PARKS_ROW_LOCATIONS_COLUMNS = [23, 24, 25,26]  # type, id
AIRBNB_ROW_COLUMNS = [0, 6, 13, 15,16]  # id
AIRBNB_ROW_LOCATIONS_COLUMNS = [1, 7, 11, 12]  # type, id
CITIES_ROW_COLUMNS = [0, 5]  # id
CITIES_ROW_LOCATIONS_COLUMNS = [0,1,2,3,4]  # type, id


class DbCreator:
    def create_db(self):
        conn = MySQL.connect(
            host="localhost",
            database='plan_trip',
            user="root",
            password="",
        )
        if conn:
            print("Connected to DB")
        else:
            print("Didn't connect to db")
        curr = conn.cursor()


        # NEW
        # curr.execute("TRUNCATE TABLE users")
        curr.execute("CREATE TABLE IF NOT EXISTS users ("
                     "username varchar(20) NOT NULL,"
                     "password varchar(20) NOT NULL,"
                     "email varchar(50) NOT NULL,"
                     "home_country varchar(40) NOT NULL,"
                     "PRIMARY KEY (username)"
                     ")")
        # NEW
        # curr.execute("TRUNCATE TABLE trips")
        curr.execute("CREATE TABLE IF NOT EXISTS trips ("
                     "trip_id int NOT NULL AUTO_INCREMENT,"
                     "username varchar(20) NOT NULL,"
                     "PRIMARY KEY (trip_id),"
                     "CONSTRAINT fk_username_from_users FOREIGN KEY (username) REFERENCES users (username)"
                     ")")

        # NEW create states
        # curr.execute("DROP TABLE IF EXISTS states")
        # curr.execute("TRUNCATE TABLE states")
        curr.execute("CREATE TABLE IF NOT EXISTS states ("
                     "state varchar(30) NOT NULL,"
                     "state_code char(2) NOT NULL,"
                     "PRIMARY KEY (state)"
                     ")")
        # NEW
        # curr.execute("TRUNCATE TABLE locations")
        curr.execute("CREATE TABLE IF NOT EXISTS locations("
                     "location_id varchar(50) NOT NULL,"
                     "latitude double NOT NULL,"
                     "longitude double NOT NULL,"
                     "name varchar(255) NOT NULL,"
                     "state varchar(30) NOT NULL,"
                     "type int NOT NULL,"
                     "PRIMARY KEY (location_id)"
                     "KEY location_id_index (location_id),"
                     "CONSTRAINT fk_state_from_states_idx FOREIGN KEY (state) REFERENCES states (state)"
                     ")")
        # NEW
        # curr.execute("TRUNCATE TABLE waypoints_in_trip")
        curr.execute("CREATE TABLE IF NOT EXISTS waypoints_in_trip ("
                     "trip_id int NOT NULL,"
                     "location_id varchar(50) NOT NULL,"
                     "station_number int NOT NULL,"
                     "PRIMARY KEY (trip_id,location_id),"
                     "CONSTRAINT fk_trip_id_from_trips FOREIGN KEY (trip_id) REFERENCES trips (trip_id),"
                     "CONSTRAINT location_id_from_locations FOREIGN KEY (location_id) REFERENCES locations (location_id)"
                     ")")

        #  NEW crete cities
        # curr.execute("DROP TABLE IF EXISTS cities")
        # curr.execute("TRUNCATE TABLE cities")
        curr.execute("CREATE TABLE IF NOT EXISTS cities ("
                     "city_id varchar(50) NOT NULL,"
                     "county varchar(50) NOT NULL,"
                     "PRIMARY KEY (city_id),"
                     "KEY fk_state_from_states_idx (state),"
                     "CONSTRAINT fk_city_id_from_locations_location_id_idx FOREIGN KEY (city_id) "
                     "REFERENCES locations (location_id)"
                     ")")

        # NEW create airbnb
        # Listing_url, name, city, state, latitude, longitude, root_type,price,review_score] + airbbn_id
        # Airbnb [0,1,6,7,11,12,13,15,16] +17
        # curr.execute("DROP TABLE IF EXISTS Airbnb")
        # curr.execute("TRUNCATE TABLE Airbnb")
        curr.execute("CREATE TABLE IF NOT EXISTS Airbnb("
                     "airbnb_id varchar(50) NOT NULL,"
                     "listing_url varchar(255) DEFAULT NULL,"
                     "city varchar(50) NOT NULL,"
                     "property_type varchar(20) DEFAULT NULL,"
                     "price double NOT NULL,"
                     "rank_score double NOT NULL,"
                     "PRIMARY KEY (airbnb_id),"
                     "CONSTRAINT fk_airbnb_id_from_locations_id FOREIGN KEY (airbnb_id) "
                     "REFERENCES locations (location_id),"
                     "CONSTRAINT fk_city_from_cities_idx FOREIGN KEY (city) REFERENCES cities (city_id)"
                     ")")
        # NEW
        # Campsites
        # curr.execute("DROP TABLE IF EXISTS Campsites")
        # curr.execute("TRUNCATE TABLE Campsites")
        curr.execute("CREATE TABLE IF NOT EXISTS campsites("
                     "campsite_id varchar(50) NOT NULL,"
                     "phone varchar(50) DEFAULT NULL,"
                     "city varchar(50) NOT NULL,"
                     "PRIMARY KEY (campsite_id),"
                     "CONSTRAINT fk_camp_id_from_locations_id FOREIGN KEY (campsite_id) "
                     "REFERENCES locations (location_id)," 
                     "CONSTRAINT fk_city_campsites_from_cities_idx FOREIGN KEY (city) REFERENCES cities (city_id)"
                     ")")
        # parks [6, 21, 23, 24]
        # curr.execute("DROP TABLE IF EXISTS Parks")
        # curr.execute("TRUNCATE TABLE Parks")
        # NEW create parks
        curr.execute("CREATE TABLE IF NOT EXISTS Parks ("
                     "park_id varchar(50) NOT NULL,"
                     "website varchar(255) DEFAULT NULL,"
                     "national_or_state varchar(10) DEFAULT NULL,"
                     "PRIMARY KEY (park_id),"
                     "CONSTRAINT fk_park_id_from_locations_id FOREIGN KEY (park_id) REFERENCES locations (location_id)"
                     ")")

        # Insert states.
        infilecomp = open("states.csv")
        csv_reader = reader(infilecomp)
        next(csv_reader)
        flag = False
        for row in csv_reader:
            try:
                if not flag:
                    flag = True
                    continue
                locations_row, res_row = create_row(row, "states.csv")
                if not res_row:
                    continue
                my_insert_data = (res_row[0], res_row[1])
                my_query = """INSERT INTO states VALUES (%s,%s)"""
                curr.execute(my_query, my_insert_data)
                conn.commit()
            except MySQL.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print("already exists.")
                else:
                    print(err.msg)
            else:
                print("OK")

        infilecomp = open("cities_extended.csv")
        csv_reader = reader(infilecomp)
        next(csv_reader)
        flag = False
        for row in csv_reader:
            try:
                if not flag:
                    flag = True
                    continue
                locations_row, res_row = create_row(row, "cities_extended.csv")
                if not res_row:
                    continue
                my_insert_data = (
                                locations_row[0], locations_row[1], locations_row[2], locations_row[3], locations_row[4],
                                locations_row[5])
                my_query = """INSERT INTO locations VALUES (%s,%s,%s,%s,%s,%s)"""
                curr.execute(my_query, my_insert_data)
                conn.commit()
                my_insert_data = (res_row[0], res_row[1])
                my_query = """INSERT INTO cities VALUES (%s,%s)"""
                curr.execute(my_query, my_insert_data)
                conn.commit()
            except MySQL.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print("already exists.")
                else:
                    print(err.msg)
            else:
                print("OK")

        # Insert campsites.
        infilecomp = open("us_campsites.csv")
        csv_reader = reader(infilecomp)
        next(csv_reader)
        flag = False
        for row in csv_reader:
            try:
                if not flag:
                    flag = True
                    continue
                locations_row, res_row = create_row(row, "us_campsites.csv")
                if not res_row:
                    continue
                my_insert_data = (
                    locations_row[0], locations_row[1], locations_row[2], locations_row[3], locations_row[4],
                    locations_row[5])
                my_query = """INSERT INTO locations VALUES (%s,%s,%s,%s,%s,%s)"""
                curr.execute(my_query, my_insert_data)
                my_insert_data = (res_row[0], res_row[1], res_row[2])
                my_query = """INSERT INTO Campsites VALUES (%s,%s,%s)"""
                curr.execute(my_query, my_insert_data)
                conn.commit()
            except MySQL.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print("already exists.")
                else:
                    print(err.msg)
            else:
                print("OK")

        infilecomp = open("airbnb_all.csv", encoding="utf8")
        csv_reader = reader(infilecomp)
        next(csv_reader)
        for row in csv_reader:
            try:
                locations_row, res_row = create_row(row, "airbnb_all.csv")
                if not res_row:
                    continue
                my_insert_data = (
                    locations_row[0], locations_row[1], locations_row[2], locations_row[3], locations_row[4],
                    locations_row[5])
                my_query = """INSERT INTO locations VALUES (%s,%s,%s,%s,%s,%s)"""
                curr.execute(my_query, my_insert_data)
                my_insert_data = (res_row[0], res_row[1], res_row[2], res_row[3], res_row[4], res_row[5])
                my_query = """INSERT INTO Airbnb VALUES (%s,%s,%s,%s,%s,%s)"""
                curr.execute(my_query, my_insert_data)
                conn.commit()
            except MySQL.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print("already exists.")
                else:
                    print(err.msg)
            else:
                print("OK")

        # Insert parks.
        infilecomp = open("National-Park-Database-DFE.csv")
        csv_reader = reader(infilecomp)
        next(csv_reader)
        flag = False
        for row in csv_reader:
            try:
                if not flag:
                    flag = True
                    continue
                locations_row, res_row = create_row(row, "National-Park-Database-DFE.csv")
                if not res_row:
                    continue
                my_insert_data = (
                    locations_row[0], locations_row[1], locations_row[2], locations_row[3], locations_row[4],
                    locations_row[5])
                my_query = """INSERT INTO locations VALUES (%s,%s,%s,%s,%s,%s)"""
                curr.execute(my_query, my_insert_data)
                my_insert_data = (res_row[0], res_row[1], res_row[2])
                my_query = """INSERT INTO Parks VALUES (%s,%s,%s)"""
                curr.execute(my_query, my_insert_data)
                conn.commit()
            except MySQL.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print("already exists.")
                else:
                    print(err.msg)
            else:
                print("OK")
        curr.close()


def create_row(row, csv_name):
    res_row = []
    locations_row = []
    row_id = ""
    hash_id = ""
    if csv_name == "us_campsites.csv":
        # CAMP_ROW_LOCATIONS_COLUMNS = [0, 1, 3, 11] + ID
        # CAMP_ROW_COLUMNS = [5, 15]
        for i in CAMP_ROW_LOCATIONS_COLUMNS:
            element = row[i]
            if element == "":
                return True, False
            if i == 0 or i == 1:
                temp = str(element)
                hash_id += temp
            locations_row.append(element)
        locations_row.append(0)
        row_id += "campsite_" + str(hash(hash_id))
        locations_row.insert(0, row_id)
        for i in CAMP_ROW_COLUMNS:
            element = row[i]
            if element == "":
                return True, False
            res_row.append(element)
        res_row.insert(0, row_id)
    elif csv_name == "National-Park-Database-DFE.csv":
        # PARKS_ROW_COLUMNS = [6, 21]  # id
        # PARKS_ROW_LOCATIONS_COLUMNS = [23, 24]  # type, id
        for i in PARKS_ROW_LOCATIONS_COLUMNS:
            element = row[i]
            if element == "":
                return True, False
            locations_row.append(element)
        locations_row.append(1)
        hash_id = str(row[23]) + str(row[24])
        row_id += "park_" + str(hash(hash_id))
        locations_row.insert(0, row_id)
        for i in PARKS_ROW_COLUMNS:
            element = row[i]
            if element == "":
                return True, False
            res_row.append(element)
        res_row.insert(0, row_id)
    elif csv_name == "airbnb_all.csv":
        # AIRBNB_ROW_COLUMNS = [0, 6, 13, 15, 16]  # id
        # AIRBNB_ROW_LOCATIONS_COLUMNS = [1, 7, 11, 12]  # type, id
        for i in AIRBNB_ROW_LOCATIONS_COLUMNS:
            element = row[i]
            if element == "":
                return True, False
            if i == 11 or i == 12:
                temp = str(element)
                hash_id += temp
                locations_row.insert(0, element)
            else:
                locations_row.append(element)
        locations_row.append(2)
        row_id += "airbnb_" + str(hash(hash_id))
        locations_row.insert(0, row_id)
        for i in AIRBNB_ROW_COLUMNS:
            element = row[i]
            if element == "":
                return True, False
            res_row.append(element)
        res_row.insert(0, row_id)
    elif csv_name == "cities_extended.csv":
        for i in CITIES_ROW_LOCATIONS_COLUMNS:
            locations_row.append(row[i])
        locations_row.append(3)
        for i in CITIES_ROW_COLUMNS:
            res_row.append(row[i])
    elif csv_name == "states.csv":
        for i in row:
            res_row.append(i)
    else:
        return
    return locations_row, res_row
