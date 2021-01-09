from random import uniform
import self as self
import simplejson as json
# from flask_restful.representations import json
from mysql.connector import errorcode
from csv import reader, writer
from flask import Flask, request, jsonify, redirect, render_template, url_for, make_response
from flask_restful import Api, Resource, abort
from flask_mysqldb import MySQL

# from db_creator_old import DbCreator
from db_model import DbModel

app = Flask(__name__)
api = Api(app)
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = "plan_trip"
mysql = MySQL(app)

# A Class that takes care of everything that relates to the User table.
class UserController(Resource):
    # Add new user.
    def post(self, username):
        try:
            db_model = DbModel()
            if username == 'login':
                # This is login in for user.
                data = request.form
                # Use model to get user info from db.
                res, username = db_model.get_user(data)
                if not len(res) == 0:
                    state = res[0]['home_country']
                    # Use redirect to redirect the user to its dashboard page.
                    return redirect(url_for("dashboard"))
                else:
                    abort(404, message="Could not find that user.")
            else:
                # This is sign in user.
                data = request.form
                # Use model to sign user in to db.
                db_model.sign_in_user(data)
                username = data['username']
                state = data['home_country']
                return redirect(url_for("dashboard"))
        except Exception as e:
            msg = e.data['message']
            return redirect(url_for("error_index", msg=msg))

    # def get(self, username):
    #     try:
    #         # db_model = DbModel
    #         # db_model.get_user()
    #         if not username == 'login':
    #             extra_condition = ""
    #             user = abort_if_username_doesnt_exist('*', "users", 'username', username, extra_condition, 'get')
    #     except Exception as e:
    #         if not e.data['message'] == 'Lost connection with DB':
    #             abort(409, message=e.data['message'])
    #         else:
    #             abort(409, message="Lost connection with DB")


# A Class that takes care of everything that relates to the Airbnb table.
class AirbnbController(Resource):
    def get(self, airbnb_id):
        try:
            db_model = DbModel()
            # Use model to get the airbnb information from db.
            res = db_model.get_airbnb(airbnb_id)
            return res
        except Exception as e:
            msg = e.data['message']
            return redirect(url_for("error_index", msg=msg))


# A Class that takes care of everything that relates to the Parks table.
class ParksController(Resource):
    def get(self, park_id):
        try:
            db_model = DbModel()
            # Use model to get the park information from db.
            res = db_model.get_park(park_id)
            return res
        except Exception as e:
            msg = e.data['message']
            return redirect(url_for("error_index", msg=msg))


# A Class that takes care of everything that relates to the Campsites table.
class CampsitesController(Resource):
    def get(self, campsite_id):
        try:
            db_model = DbModel()
            # Use model to get the campsite information from db.
            res = db_model.get_campsite(campsite_id)
            return res
        except Exception as e:
            if not e.data['message'] == 'Lost connection with DB':
                abort(409, message=e.data['message'])
            else:
                abort(409, message="Lost connection with DB")


# A Class that takes care of everything that relates to the Cities table.
class CitiesController(Resource):

    def post(self, city_id):
        try:
            data = request.json
            db_model = DbModel()
            # Use model to get the start cities from db.
            res = db_model.get_start_cities(data)
            return res
        except Exception as e:
            msg = e.data['message']
            return redirect(url_for("error_index", msg=msg))


# A Class that takes care of everything that relates to the Locations table.
class LocationsController(Resource):

    def post(self):
        try:
            tables_names_list = request.json['filterList']
            db_model = DbModel()
            # Use model to get all locations on map according to the user's filters.
            res = db_model.get_locations(tables_names_list)
            return res
        except Exception as e:
            msg = e.data['message']
            return redirect(url_for("error_index", msg=msg))


# A Class that takes care of everything that relates to the Trips table.
class TripsController(Resource):
    def post(self, trip_id):
        db_model = DbModel()
        try:
            data = request.form
            flag_json = False
            if len(data) == 0:
                flag_json = True
                data = request.json
            username = data['username']
            if trip_id == 'login':
                # Its login check so we need to make sure the user is already in DB before saving its trip.
                try:
                    user, username = db_model.get_user(data)
                    # Need to check if user in db if not then error
                    if len(user) == 0:
                        abort(409, message="User is not registered.")
                except Exception as e:
                    msg = e.data['message']
                    return redirect(url_for("error_index", msg=msg))
            elif trip_id == 'signup':
                # Its sign in so we need to make sure the username is not already in DB before saving its trip.
                try:
                    db_model.sign_in_user(data)
                except Exception as e:
                    msg = e.data['message']
                    return redirect(url_for("error_index", msg=msg))
            try:
                # Its regular saving trip.
                res = db_model.save_trip(data, flag_json)
                if trip_id == 'login' or trip_id == 'signup':
                    # If its login or sign up + saving trip, than we want to redirect the user to its dashboard.
                    try:
                        print("want to move to dashboard\n")
                        return redirect(url_for("dashboard"))
                        # return render_template("http://127.0.0.1:5500/wwwroot/Pages/Dashboard.html")
                        # return username, 204
                    except Exception as e:
                        msg = e.data['message']
                        return redirect(url_for("error_index", msg=msg))
                response = make_response(
                    jsonify(
                        {"message": "test"}
                    ),
                    200,
                )
                # return response
                return redirect(url_for("dashboard"))
            except:
                abort(409, message="Lost connection with DB")
        except Exception as e:
            msg = e.data['message']
            return redirect(url_for("error_index", msg=msg))

    def get(self, trip_id):
        try:
            try:
                db_model = DbModel()
                # Use the model to get the trip using its id.
                my_trip = db_model.get_trip(trip_id)
                return my_trip
            except Exception as e:
                msg = e.data['message']
                return redirect(url_for("error_index", msg=msg))
        except Exception as e:
            msg = e.data['message']
            return redirect(url_for("error_index", msg=msg))

    def delete(self, trip_id):
        try:
            # Use model to delete trip using its trip_id.
            db_model = DbModel()
            db_model.delete_trip(trip_id)
            response = make_response(
                jsonify(
                    {"message": "test"}
                ),
                200,
            )
            return 200
        except Exception as e:
            msg = e.data['message']
            return redirect(url_for("error_index", msg=msg))


# A Class that takes care of everything that relates to the Radius calculation.
# class Radius(Resource):
#     def get(self):
#         try:
#             data = request.get_json()
#             latitude = data['latitude']
#             longitude = data['longitude']
#             distance = data['distance']
#             params = [latitude, longitude, latitude, distance]
#             my_query = """SELECT
#                       location_id, name, state, latitude, longitude, (
#                         3959 * acos (
#                           cos ( radians(%s) )
#                           * cos( radians( latitude ) )
#                           * cos( radians( longitude ) - radians(%s) )
#                           + sin ( radians(%s) )
#                           * sin( radians( latitude ) )
#                         )
#                       ) AS distance
#                     FROM locations
#                     HAVING distance < %s
#                     ORDER BY distance
#                     LIMIT 0 , 100;"""
#             cur = mysql.connection.cursor()
#             cur.executemany(my_query, (params,))
#             data = cur.fetchall()
#             data = make_res_as_json_with_col_names(data, cur)
#             json.dumps(data, use_decimal=True)
#             return data
#         except:
#             abort(409, message="Lost connection with DB")


# Route that in charge of the search for cities when the user search for start and end destination.
@app.route("/livesearch", methods=["POST","GET"])
def livesearch():
    try:
        searchbox = request.form.get("text")
        db_model = DbModel()
        res = db_model.get_live_search(searchbox)
        return res
    except Exception as e:
        msg = "Something happened. Please try again."
        return redirect(url_for("error_index", msg=msg))


# Route that in charge of redirect the user to its dashboard page.
@app.route("/Dashboard")
def dashboard():
    print("In Dashboard")
    # return "http://127.0.0.1:5000/Dashboard/"+user_name+"/"+state
    return render_template("Dashboard.html")
    # return render_template("Dashboard.html")


# Route that in charge of redirect the user to its dashboard page.
@app.route("/ErrorIndex/<msg>")
def error_index(msg):
    # return "http://127.0.0.1:5000/Dashboard/"+user_name+"/"+state
    return render_template("ErrorIndex.html", msg=msg)
    # return render_template("Dashboard.html")


@app.route("/MemberIndex")
def memberIndex():
    #http://127.0.0.1:5500
    return render_template("MemberIndex.html")

# Route that in charge of redirect the user to its home page.
@app.route("/")
def home():
    return render_template("index.html")

# /state_from_username?username=a
# Route that in charge of the getting state of user using it username.
@app.route("/state_from_username")
def state_from_username():
    try:
        username = request.args.get("username")
        db_model = DbModel()
        res = db_model.get_state_by_username(username)
        return res
    except Exception as e:
        msg = "Something happened. Please try again."
        return redirect(url_for("error_index", msg=msg))



api.add_resource(UserController, "/users/<string:username>")
api.add_resource(AirbnbController, "/airbnb/<string:airbnb_id>")
api.add_resource(ParksController, "/parks/<string:park_id>")
api.add_resource(CampsitesController, "/campsites/<string:campsite_id>")
api.add_resource(CitiesController, "/cities/<string:city_id>")
api.add_resource(LocationsController, "/locations")
api.add_resource(TripsController, "/trips/<string:trip_id>")
# api.add_resource(Radius, "/radius")
if __name__ == "__main__":
    # main()
    # db_creator = DbCreator
    # db_creator.create_db(self)
    global local_user_name
    app.run(debug=True)

