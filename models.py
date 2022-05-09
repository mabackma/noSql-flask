import pymongo
from pymongo.server_api import ServerApi
from config import Config
from bson.objectid import ObjectId
from errors.not_found import NotFound
from errors.validation_error import ValidationError

client = pymongo.MongoClient(
    Config.CONNECTION_STRING,
    server_api=ServerApi('1'))
db = client.noSql_database

class User:

    def __init__(self, username, password=None, role='user', _id=None):
        self.username = username
        self.password = password
        self.role = role
        if _id is not None:
            _id = str(_id)
        self._id = _id

    def create(self):
        user = db.users.find_one({'username': self.username})
        if user is not None:
            raise ValidationError(message='username must be unique')
        result = db.users.insert_one({'username': self.username, 'role': self.role, 'password': self.password})
        self._id = str(result.inserted_id)

    def update(self):
        _filter = {'_id': ObjectId(self._id)}
        _update = {
            '$set': {'username': self.username, 'role': self.role}
        }
        print(_filter)
        print(_update)
        db.users.update_one(_filter, _update)

    def to_json(self):
        return {
            '_id': str(self._id),
            'username': self.username,
            'role': self.role
        }

    # Palauttaa listan jsoneita. Jokainen User objekti listassa muutettu json muotoon.
    @staticmethod
    def list_to_json(users_list):
        users = []
        for user in users_list:
            users.append(user.to_json())
        return users

    @staticmethod
    def get_all():
        users_cursor = db.users.find()
        users_list = list(users_cursor)
        users = []
        for user_dictionary in users_list:
            users.append(User(user_dictionary['username'], role=user_dictionary['role'], _id=user_dictionary['_id']))
        return users

    @staticmethod
    def get_by_id(_id):
        user_dictionary = db.users.find_one({'_id': ObjectId(_id)})
        if user_dictionary is None:
            raise NotFound(message="user not found")
        user = User(user_dictionary['username'], role=user_dictionary['role'], _id=user_dictionary['_id'])
        return user

    @staticmethod
    def get_by_username(username):
        user_dictionary = db.users.find_one({'username': username})
        if user_dictionary is None:
            raise NotFound(message="user not found")
        user = User(user_dictionary['username'], role=user_dictionary['role'], _id=user_dictionary['_id'],
                    password= user_dictionary['password'])
        return user

    @staticmethod
    def delete_by_id(_id):
        db.users.delete_one({'_id': ObjectId(_id)})


class Publication:

    def __init__(self,
                 title,
                 description,
                 url,
                 owner=None,  # Oletusarvot owner=None, likes=[], _id=None
                 likes=[],
                 _id=None):
        self.title = title
        self.description = description
        self.url = url
        self.owner = owner
        self.likes = likes
        if _id is not None:
            _id = str(_id)
        self._id = _id

    # CRUD:n C (Create)
    def create(self):
        result = db.publications.insert_one({
            'title': self.title,
            'description': self.description,
            'url': self.url
        })
        self._id = str(result.inserted_id)

    # lisätty 9.5
    # TODO: Muuta url visibilityksi
    def update(self):
        _filter = {'_id': ObjectId(self._id)}
        _update = {
            '$set': {'title': self.title, 'description': self.description, 'url': self.url}
        }
        print("päivitetään näillä arvoilla:")
        print(_update)
        db.publications.update_one(_filter, _update)

    def to_json(self):
        return {
            '_id': str(self._id),
            'title': self.title,
            'description': self.description,
            'url': self.url
        }

    # Palauttaa listan jsoneita. Jokainen Publication objekti listassa muutettu json muotoon.
    @staticmethod
    def list_to_json(publication_list):
        publications = []
        for publication in publication_list:
            publications.append(publication.to_json())
        return publications

    # Palauttaa listan Publication objekteja
    @staticmethod
    def get_all():
        publications_cursor = db.publications.find()
        publications_list = list(publications_cursor)
        publications = []
        for publication in publications_list:
            publication_object = Publication(publication['title'], publication['description'], publication['url'],
                                             _id=publication['_id'])
            publications.append(publication_object)
        return publications

    # lisätty 9.5
    @staticmethod
    def get_by_id(_id):
        publication_dictionary = db.publications.find_one({'_id': ObjectId(_id)})
        if publication_dictionary is None:
            raise NotFound(message="publication not found")
        publication = Publication(publication_dictionary['title'], description=publication_dictionary['description'],
                                  url=publication_dictionary['url'], _id=publication_dictionary['_id'])
        return publication

    # lisätty 9.5
    @staticmethod
    def delete_by_id(_id):
        db.publications.delete_one({'_id': ObjectId(_id)})



