from flask import jsonify, request
from flask.views import MethodView
from errors.not_found import NotFound
from models import User
from passlib.hash import pbkdf2_sha256 as sha256
from flask_jwt_extended import create_access_token

class RegisterRouteHandler(MethodView):

    def post(self):
        request_body = request.get_json()
        username = request_body['username']
        password = request_body['password']

        hashed_password = sha256.hash(password)
        user = User(username, password=hashed_password)
        user.create()
        return jsonify(user=user.to_json())

class LoginRouteHandler(MethodView):

    def post(self):
        request_body = request.get_json()

        # 1 haetaan käyttäjä käyttäjänimellä
        user = User.get_by_username(request_body['username'])

        # 2 tarkistetaan onko salasana oikein
        if sha256.verify(request_body['password'], user.password):
            access_token = create_access_token(user._id,
                           additional_claims={'username': user.username, 'role': user.role})
            return jsonify(access_token=access_token)
        raise NotFound(message="user not found")

