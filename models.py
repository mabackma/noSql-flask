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

        # Katsotaan onko sen niminen käyttäjä jo olemassa
        user = db.users.find_one({'username': self.username})
        if user is not None:
            raise ValidationError(message='username must be unique')

        # Jos käyttäjää ei ollut olemassa niin luodaan se
        result = db.users.insert_one({'username': self.username, 'role': self.role, 'password': self.password})
        self._id = str(result.inserted_id)

    def update(self):
        _filter = {'_id': ObjectId(self._id)}
        _update = {
            '$set': {'username': self.username, 'role': self.role}
        }
        print("päivitetään näillä arvoilla:")
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
                 owner=None,  # Oletusarvot owner=None, visibility=2, likes=[], _id=None
                 visibility=2,
                 likes=[],
                 _id=None):
        self.title = title
        self.description = description
        self.url = url
        self.owner = owner
        self.visibility = visibility
        self.likes = likes
        if _id is not None:
            _id = str(_id)
        self._id = _id

    # CRUD:n C (Create)
    def create(self):
        result = db.publications.insert_one({
            'title': self.title,
            'description': self.description,
            'url': self.url,
            'owner': ObjectId(self.owner),
            'visibility': self.visibility
        })
        self._id = str(result.inserted_id)

    # lisätty 9.5
    def update(self):
        _filter = {'_id': ObjectId(self._id)}
        _update = {
            '$set': {'title': self.title, 'description': self.description, 'visibility': self.visibility}
        }
        print("päivitetään näillä arvoilla:")
        print(_update)
        db.publications.update_one(_filter, _update)

    def to_json(self):
        owner = self.owner
        if owner is not None:
            owner = str(owner)
        return {
            '_id': str(self._id),
            'title': self.title,
            'description': self.description,
            'url': self.url,
            'owner': owner,
            'visibility': self.visibility
        }

    # Palauttaa listan jsoneita. Jokainen Publication objekti listassa muutettu json muotoon.
    @staticmethod
    def list_to_json(publication_list):
        publications = []
        for publication in publication_list:
            publications.append(publication.to_json())
        return publications

    @staticmethod
    def _create_list_of_publications(list_of_dictionaries):
        publications = []
        for publication in list_of_dictionaries:
            publication_object = Publication(publication['title'], publication['description'], publication['url'],
                                             # toinen argumentti on oletusarvo jos owneria ei löydy
                                             _id=publication['_id'], owner=publication.get('owner', None),
                                             visibility=publication.get('visibility', 2))
            publications.append(publication_object)
        return publications

    # Palauttaa listan Publication objekteja
    @staticmethod
    def get_all():
        publications_cursor = db.publications.find()
        publications_list = list(publications_cursor)
        publications = Publication._create_list_of_publications(publications_list)
        return publications

    # lisätty 9.5
    @staticmethod
    def get_by_id(_id):
        publication_dictionary = db.publications.find_one({'_id': ObjectId(_id)})
        if publication_dictionary is None:
            raise NotFound(message="publication not found")
        publication = Publication(publication_dictionary['title'], description=publication_dictionary['description'],
                                  url=publication_dictionary['url'], _id=publication_dictionary['_id'],
                                  visibility=publication_dictionary['visibility'])
        return publication

    @staticmethod
    def get_by_visibility(visibility=2):
        publications_cursor = db.publications.find({'visibility': visibility})
        publications_list = list(publications_cursor)
        publications = Publication._create_list_of_publications(publications_list)
        return publications

    @staticmethod
    def get_logged_in_users_and_public_publications(logged_in_user):
        _filter = {
            '$or': [
                {'owner': ObjectId(logged_in_user['sub'])},
                {'visibility': {'$in': [1, 2]}}
            ]
        }
        publications_cursor = db.publications.find(_filter)
        publications_list = list(publications_cursor)
        publications = Publication._create_list_of_publications(publications_list)
        return publications

    # lisätty 9.5
    @staticmethod
    def delete_by_id(_id):
        db.publications.delete_one({'_id': ObjectId(_id)})



