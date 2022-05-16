from flask import jsonify, request
from flask.views import MethodView
from errors.not_found import NotFound
from models import User
from passlib.hash import pbkdf2_sha256 as sha256
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from errors.validation_error import ValidationError


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

class AccountRouteHandler(MethodView):

    @jwt_required(optional=False)
    def get(self):
        logged_in_user = get_jwt()
        account = User.get_by_id(logged_in_user['sub'])
        return jsonify(account=account.to_json())

    @jwt_required(optional=False)
    def patch(self):
        logged_in_user = get_jwt()
        account = User.get_by_id(logged_in_user['sub'])
        request_body = request.get_json()
        if request_body and 'username' in request_body:
            account.username = request_body['username']
            account.update()
            return jsonify(account=account.to_json())

class AccountPasswordRouteHandler(MethodView):

    @jwt_required(optional=False)
    def patch(self):
        logged_in_user = get_jwt()
        account = User.get_by_id(logged_in_user['sub'])
        request_body = request.get_json()
        if request_body and 'password' in request_body:
            account.password = sha256.hash(request_body['password'])
            account.update_password()
            return ""
        raise ValidationError(message="password is required")

