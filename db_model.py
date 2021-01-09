from random import uniform

import self as self
import simplejson as json
# from flask_restful.representations import json
from mysql.connector import errorcode
from csv import reader, writer
from flask import Flask, request, jsonify, redirect, render_template, url_for
from flask_restful import Api, Resource, abort
from flask_mysqldb import MySQL

app = Flask(__name__)
api = Api(app)

app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = "plan_trip"
mysql = MySQL(app)


class DbModel:

    # A function that creates a dynamic query
    def create_exists_query(self, select_what, table_name, value_name, extra_condition):
        select_part = "SELECT " + str(select_what)
        from_part = " FROM " + str(table_name)
        condition_part = " WHERE " + str(value_name) + " = %s " + extra_condition
        my_query = select_part + from_part + condition_part
        return my_query

    # A function that create a json back with the columns from the DB of the values that we want to return.
    def make_res_as_json_with_col_names(self, data, cur):
        row_headers = [x[0] for x in cur.description]  # this will extract row headers
        json_data = []
        for result in data:
            json_data.append(dict(zip(row_headers, result)))
        return json_data

    # Check if the value that we are looking for is already in DB. If yes - let the user know!
    def abort_if_username_exist(self, table_name, value_name, value_id):
        # create connection to db to check if username in db.
        try:
            cur = mysql.connection.cursor()
            # my_query = "SELECT * FROM " + str(my_class) + " WHERE username = %s"
            my_query = self.create_exists_query('*', table_name, value_name, "")
            cur.execute(my_query, (value_id,))
            data = cur.fetchall()
            cur.close()
            if len(data) != 0:
                abort(409, message="Username already exists... Pick different a user name.")
        except Exception as e:
            if not e.data['message'] == 'Lost connection with DB':
                abort(409, message=e.data['message'])
            else:
                abort(409, message="Lost connection with DB")

    # Check if the value that we are looking for does not  in DB. If not - let the user know. Else - return it.
    def abort_if_username_doesnt_exist(self, select_what, table_name, value_name, value_id, extra_condition, method):
        try:
            # create connection to db to check if username in db.
            cur = mysql.connection.cursor()
            my_query = self.create_exists_query(select_what, table_name, value_name, extra_condition)
            cur.execute(my_query, (value_id,))
            data = cur.fetchall()
            # Nothing returned so we didn't get anything from DB - does not exists.
            if len(data) == 0:
                cur.close()
                if table_name == "cities":
                    abort(404, message="One of the cities does not exists.")
                abort(404, message="Could not find that user.")
            elif method == 'delete':
                cur.close()
                return
            else:
                # Get headers of the values from the db.
                json_data = self.make_res_as_json_with_col_names(data, cur)
                cur.close()
                json.dumps(json_data, use_decimal=True)
                return json_data
        except Exception as e:
            if not e.data['message'] == 'Lost connection with DB':
                abort(409, message=e.data['message'])
            else:
                abort(409, message="Lost connection with DB")

    # function to get the user information from db.
    def get_user(self, data):
        username = data['username']
        password = data['psw']
        try:
            cur = mysql.connection.cursor()
            my_query = """SELECT * FROM users where username = %s and password = %s"""
            cur.execute(my_query, (username, password,))
            user = cur.fetchall()
            user = self.make_res_as_json_with_col_names(user,cur)
            return user, username
        except:
            abort(409, message="Lost connection with DB")

    # function to get the airbnb information from db.
    def get_airbnb(self, airbnb_id):
        select_what = "L.*, locations.name as city, airbnb.listing_url, airbnb.property_type, " \
                      "airbnb.price, airbnb.rank_score "
        table_name = "locations as L join airbnb on L.location_id = airbnb.airbnb_id join " \
                     "locations on airbnb.city = locations.location_id "
        extra_condition = ""
        # Make sure the airbnb exists in the DB - else return alert.
        airbnb = self.abort_if_username_doesnt_exist(select_what, table_name, 'airbnb_id', airbnb_id, extra_condition, 'get')
        return airbnb

    # function to get the park information from db.
    def get_park(self, park_id):
        select_what = "locations.*, parks.website, parks.national_or_state"
        table_name = "locations join parks on locations.location_id = parks.park_id"
        extra_condition = ""
        # Make sure the park exists in the DB - else return alert.
        park = self.abort_if_username_doesnt_exist(select_what, table_name, 'park_id', park_id, extra_condition, 'get')
        return park

    # function to get the campsite information from db.
    def get_campsite(self, campsite_id):
        select_what = "L.*, locations.name as city, campsites.phone"
        table_name = "locations as L join campsites on L.location_id = campsites.campsite_id " \
                     "join locations on campsites.city = locations.location_id"
        extra_condition = ""
        # Make sure the park exists in the DB - else return alert.
        campsite = self.abort_if_username_doesnt_exist(select_what, table_name, 'campsite_id', campsite_id,
                                                       extra_condition, 'get')
        return campsite

    # function to get the start and destination cities information from db.
    def get_start_cities(self, data):
        # data = request.get_json()
        cities_list = []
        for city in data['cities']:
            extra_condition = ""
            # make sure to mix with locations
            city = self.abort_if_username_doesnt_exist('*', 'locations', 'name', city, extra_condition, 'get')
            cities_list.append(city)
        json.dumps(cities_list, use_decimal=True)
        return cities_list

    def get_locations(self, tables_names_list):
        try:
            cur = mysql.connection.cursor()
            # Make dictionary to know which type is which number when we get it from client.
            type_to_table = {'campsites': 0, 'parks': 1, 'airbnb': 2}
            # Create the query and adding the types to it according to what the user chose.
            total_json_data = []
            for i in tables_names_list:
                select_part = "SELECT *"
                from_part = " FROM locations"
                condition = " Where "
                my_query = select_part + from_part
                type = type_to_table[i]
                condition += "type=" + str(type)
                my_query += condition + " order by RAND() limit 0,30"
                cur.execute(my_query)
                data = cur.fetchall()
                json_data = self.make_res_as_json_with_col_names(data, cur)
                json.dumps(json_data, use_decimal=True)
                total_json_data += json_data
            return total_json_data
        except:
            abort(409, message="Lost connection with DB")

    # Function that inserting the user information to db after he signs in.
    def sign_in_user(self, data):
        try:
            username = data['username']
            param = [data['username'], data['psw'], data['email'], data['home_country']]
            # Need to make sure the username is not exists before saving this user.
            self.abort_if_username_exist('users', 'username', username)
            cur = mysql.connection.cursor()
            my_query = 'INSERT INTO users VALUES(%s,%s,%s,%s)'
            cur.execute(my_query, param)
            mysql.connection.commit()
            # mysql.connection.close()
        except Exception as e:
            abort(409, message=e.data['message'])

    # Function that inserting the saving a trip in db.
    # First saving a new trip and then saving it's way points in waypoint_in_trip table.
    def save_trip(self, data, flag_json):
        try:
            get_waypoint_list = data['locations']
            username = data['username']
            if not flag_json:
                get_waypoint_list = json.loads(get_waypoint_list)
            waypoint_list = get_waypoint_list['location']
            cur = mysql.connection.cursor()
            # First we need to create a trip and than save its way points.
            my_query = """INSERT INTO trips VALUES(DEFAULT,%s)"""
            # insert the trip - dont forget to only commit after all waypoints are in!
            cur.execute(my_query, (username,))
            id = cur.lastrowid
            # waypoint now... loop and insert each waypoint and commit at the end.
            j = 0
            for i in waypoint_list:
                waypoints_param = []
                waypoints_param.insert(0, id)
                waypoints_param.append(i)
                waypoints_param.append(j)
                my_query = """INSERT INTO waypoints_in_trip VALUES(%s,%s,%s)"""
                # cur.executemany(my_query, (waypoints_param,))
                cur.executemany(my_query, (waypoints_param,))
                j += 1
            # insert the trip - don't forget to only commit after all waypoints are in!
            mysql.connection.commit()
            # mysql.connection.close()
        except Exception as e:
            print(e)
            abort(409, message="Lost connection with DB")

    # A function that gets trip information from db using its trip_id
    def get_trip(self, trip_id):
        try:
            # Get specific trips using username or home_country
            select_what = "select trips.trip_id, locations.name, locations.state, station_number "
            from_table = "from trips join waypoints_in_trip on trips.trip_id = waypoints_in_trip.trip_id " \
                         "join locations on waypoints_in_trip.location_id = locations.location_id "
            where = ""
            limit = ""
            if trip_id == 'username':
                # Get the trips for the username.
                username = request.args.get('username')
                where = "where trips.username = '" + str(username) + "' "
            if trip_id == 'home_country':
                # Get the trips for all the users from that home_country.
                home_country = request.args.get('home_country')
                where = "join users on users.username = trips.username " \
                        "where users.home_country = '" + str(home_country) + "' "
            condition = "order by trips.trip_id, waypoints_in_trip.station_number"
            cur = mysql.connection.cursor()
            my_query = select_what + from_table + where + condition
            cur.execute(my_query)
            data = cur.fetchall()
            data = self.make_res_as_json_with_col_names(data, cur)
            json.dumps(data, use_decimal=True)
            return data
        except Exception as e:
            if not e.data['message'] == 'Lost connection with DB':
                abort(409, message=e.data['message'])
            else:
                abort(409, message="Lost connection with DB")

    # A function that deletes trip using its trip_id
    def delete_trip(self, trip_id):
        try:
            # select_what = "trips.trip_id, location_id, station_number"
            select_what = "*"
            table_name = "trips"
            condition = ""
            trip = self.abort_if_username_doesnt_exist(select_what, table_name, 'trips.trip_id', trip_id, condition, 'delete')
            cur = mysql.connection.cursor()
            my_query = "DELETE FROM waypoints_in_trip WHERE trip_id = %s"
            cur.execute(my_query, (trip_id,))
            my_query = "DELETE FROM trips WHERE trip_id = %s"
            cur.execute(my_query, (trip_id,))
            mysql.connection.commit()
            mysql.connection.close()
            # delete the user.
            return 200
        except Exception as e:
            if not e.data['message'] == 'Lost connection with DB':
                abort(409, message=e.data['message'])
            else:
                abort(409, message="Lost connection with DB")

    # A function that search for all the cities for the user's search.
    def get_live_search(self, searchbox):
        try:
            cursor = mysql.connection.cursor()
            query = "select name, locations.state from locations join cities on " \
                    "locations.location_id = cities.city_id where name LIKE " \
                    "'{}%' order by name limit 0,5".format(searchbox)
            cursor.execute(query)
            result = cursor.fetchall()
            result = self.make_res_as_json_with_col_names(result, cursor)
            return jsonify(result)
        except Exception as e:
            if not e.data['message'] == 'Lost connection with DB':
                abort(409, message=e.data['message'])
            else:
                abort(409, message="Lost connection with DB")

    def get_state_by_username(self,username):
        try:
            cursor = mysql.connection.cursor()
            query = "select home_country from users where username=%s"
            cursor.execute(query,(username,))
            result = cursor.fetchall()
            result = self.make_res_as_json_with_col_names(result, cursor)
            return jsonify(result)
        except Exception as e:
            if not e.data['message'] == 'Lost connection with DB':
                abort(409, message=e.data['message'])
            else:
                abort(409, message="Lost connection with DB")

