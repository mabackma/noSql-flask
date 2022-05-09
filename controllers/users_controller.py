from flask import request, jsonify
from models import User
from flask.views import MethodView


# vastaa osoitteessa /api/users
class UsersRouteHandler(MethodView):
    def get(self):
        users_list = User.get_all()
        return jsonify(users=User.list_to_json(users_list))

    def post(self):
        request_body = request.get_json()
        user = User(request_body['username'], role=request_body.get('role', 'user'))
        user.create()
        return jsonify(user=user.to_json())


class UserRouteHandler(MethodView):

    def get(self, _id):
        user = User.get_by_id(_id)
        return jsonify(user=user.to_json())

    def delete(self, _id):
        User.delete_by_id(_id)
        return ""

    def patch(self, _id):
        request_body = request.get_json()

        # haetaan user tietokannasta id:n perusteella
        user = User.get_by_id(_id)

        # muutetaan userin arvoja
        user.username = request_body.get('username', user.username)
        user.role = request_body.get('role', user.role)

        # päivitetään user tietokantaan
        user.update()
        return jsonify(user=user.to_json())

    # Tekee samat asiat kun patch
    def put(self, _id):
        request_body = request.get_json()
        user = User.get_by_id(_id)
        user.username = request_body.get('username', user.username)
        user.role = request_body.get('role', user.role)
        user.update()
        return jsonify(user=user.to_json())

"""
class PictureRouteHandler(MethodView):
    
    def get(self):
        
        
"""

