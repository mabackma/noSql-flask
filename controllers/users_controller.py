from flask import request, jsonify
from bson import ObjectId
from models import db
from flask.views import MethodView


# Tätä käytetään patch ja put metodeissa kun päivitetään yhtä käyttäjää
def update_user(request_body, _id):
    username = request_body['username']

    _filter = {'_id': ObjectId(_id)}
    _update = {
        '$set': {'username': username}
    }
    print("Updated user " + _id)
    db.users.update_one(_filter, _update)


class UsersRouteHandler(MethodView):
    def get(self):
        users_cursor = db.users.find()
        users_list = list(users_cursor)

        for user in users_list:
            user["_id"] = str(user["_id"])
        return jsonify(users=users_list)

    def post(self):
        request_body = request.get_json()
        username = request_body["username"]

        db.users.insert_one({"username": username})
        return "lisätään käyttäjä: " + username

class UserRouteHandler(MethodView):
    def get(self, _id):
        user = db.users.find_one({'_id': ObjectId(_id)})
        user['_id'] = str(user['_id'])
        print(user)
        return jsonify(user=user)

    def delete(self, _id):
        db.users.delete_one({'_id': ObjectId(_id)})
        return ""

    def patch(self, _id):
        request_body = request.get_json()
        update_user(request_body, _id)
        return ""

    def put(self, _id):
        request_body = request.get_json()
        update_user(request_body, _id)
        return ""


# Alla samat jutut mutta funktioina
"""
def users_route_handler():
    if request.method == "GET":
        users_cursor = db.users.find()
        users_list = list(users_cursor)

        for user in users_list:
            user["_id"] = str(user["_id"])
        return jsonify(users=users_list)

    elif request.method == "POST":
        request_body = request.get_json()
        username = request_body["username"]

        db.users.insert_one({"username": username})
        return "lisätään käyttäjä: " + username


def user_route_handler(_id):
    if request.method == "GET":
        user = db.users.find_one({'_id': ObjectId(_id)})
        user['_id'] = str(user['_id'])
        print(user)
        return jsonify(user=user)

    elif request.method == "DELETE":
        db.users.delete_one({'_id': ObjectId(_id)})
        return ""

    elif request.method == "PATCH" or request.method == "PUT":
        request_body = request.get_json()
        username = request_body['username']
        # username = request_body.get('username', '') myös mahdollista oletusarvolla ''

        _filter = {'_id': ObjectId(_id)}
        _update = {
            '$set': {'username': username}
        }
        print("Updated user " + _id)
        db.users.update_one(_filter, _update)
        return ""
"""

