import pymongo
from flask import jsonify
from pymongo.server_api import ServerApi
from config import Config
from bson.objectid import ObjectId
from errors.not_found import NotFound
from errors.validation_error import ValidationError
from validators.validation_publications import validate_patch_publication, validate_delete_publication

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

    def get_id(self):
        return self._id


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
            '$set': {'username': self.username}
        }
        # hae käyttäjä jonka käyttäjänimi on self.usernamen arvo ja _id eri suuri kuin self._id:n arvo
        user = db.users.find_one({'username': self.username, '_id': {'$ne': ObjectId(self._id)}})
        if user is not None:
            raise ValidationError(message="username must be unique")
        db.users.update_one(_filter, _update)

    def update_password(self):
        _filter = {'_id': ObjectId(self._id)}
        _update = {
            '$set': {'password': self.password}
        }
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
                 owner=None,  # Oletusarvot owner=None, visibility=2, likes=[], _id=None, share_link=None, shares
                 visibility=2,
                 likes=None,   # likes lista sisältää käyttäjien _id arvoja ObjectId
                 share_link=None,
                 shares=0,
                 _id=None):
        if likes is None:
            likes = []
        self.likes = likes
        self.title = title
        self.description = description
        self.url = url
        self.owner = owner
        self.visibility = visibility
        self.likes = likes
        self.share_link = share_link
        self.shares = shares
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

    def update(self):
        _filter = {'_id': ObjectId(self._id)}
        _update = {
            '$set': {'title': self.title, 'description': self.description, 'visibility': self.visibility}
        }
        print("päivitetään näillä arvoilla:")
        print(_update)
        db.publications.update_one(_filter, _update)

    def like(self):
        _filter = {'_id': ObjectId(self._id)}
        _update = {
            '$set': {'likes': self.likes}
        }
        db.publications.update_one(_filter, _update)

    def share(self):
        _filter = {'_id': ObjectId(self._id)}
        _update = {
            '$set': {'shares': self.shares, 'share_link': self.share_link}
        }
        db.publications.update_one(_filter, _update)

    # Palauttaa Jsonin objektista
    def to_json(self):
        likes = []
        for user_id in self.likes:
            likes.append(str(user_id))

        owner = self.owner
        if owner is not None:
            owner = str(owner)
        return {
            '_id': str(self._id),
            'title': self.title,
            'description': self.description,
            'url': self.url,
            'owner': owner,
            'visibility': self.visibility,
            'likes': likes,   # 'likes': [str(user_id) for user_id in self.likes]
            'shares': self.shares,
            'share_link': self.share_link
        }

    # Palauttaa listan Jsoneita. Jokainen Publication objekti listassa muutettu json muotoon.
    @staticmethod
    def list_to_json(publication_list):
        publications = []
        for publication in publication_list:
            publications.append(publication.to_json())
        return publications

    # Palauttaa Publication objektin
    @staticmethod
    def _from_json(publication):
        publication_object = Publication(publication['title'], publication['description'], publication['url'],
                                         # toinen argumentti on oletusarvo ensimmäiselle argumentille,
                                         # jos ensimmäistä argumenttia ei löydy
                                         _id=publication['_id'], owner=publication.get('owner', None),
                                         visibility=publication.get('visibility', 2),
                                         likes=publication.get('likes', []),
                                         share_link=publication.get('share_link', None),
                                         shares=publication.get('shares', 0))
        return publication_object

    # Palauttaa listan Publication objekteja
    @staticmethod
    def _list_from_json(list_of_dictionaries):
        publications = []
        for publication in list_of_dictionaries:
            publication_object = Publication._from_json(publication)
            publications.append(publication_object)
        return publications

    @staticmethod
    def get_all():
        publications_cursor = db.publications.find()
        publications_list = list(publications_cursor)
        publications = Publication._list_from_json(publications_list)
        return publications

    @staticmethod
    def get_by_id(_id):
        publication_dictionary = db.publications.find_one({'_id': ObjectId(_id)})
        if publication_dictionary is None:
            raise NotFound(message="publication not found")
        publication = Publication._from_json(publication_dictionary)
        return publication

    # palauttaa vain kaikille julkiset publicationit
    @staticmethod
    def get_by_visibility(visibility=2):
        publications_cursor = db.publications.find({'visibility': visibility})
        publications_list = list(publications_cursor)
        publications = Publication._list_from_json(publications_list)
        return publications

    @staticmethod
    def get_one_by_id_and_visibility(_id, visibility=2):
        publication = db.publications.find({'_id': ObjectId(_id), 'visibility': visibility})
        publication_doc = publication.next()
        if publication is None:
            raise NotFound(message="publication not found")
        return Publication._from_json(publication_doc)

    @staticmethod
    def get_logged_in_users_and_public_publications(logged_in_user):
        _filter = {
            '$or': [
                # etsitään käyttäjän omat julkaisut
                {'owner': ObjectId(logged_in_user['sub'])},
                # etsitään julkaisut joilla visibility 1 tai 2
                {'visibility': {'$in': [1, 2]}}
            ]
        }
        publications_cursor = db.publications.find(_filter)
        publications_list = list(publications_cursor)
        publications = Publication._list_from_json(publications_list)
        return publications

    @staticmethod
    def get_logged_in_users_and_public_publication(_id, logged_in_user):
        """ SELECT * FROM publications WHERE id = ? AND (owner = ? OR visibility IN (1, 2)) LIMIT 1; """
        _filter = {
            # hae ensimmäinen, jossa _id = _id ja (owner = sisäänkirjautunut käyttäjä tai visibility 1 tai visibility 2)
            '_id': ObjectId(_id),
            '$or': [
                {'owner': ObjectId(logged_in_user['sub'])},
                {'visibility': {'$in': [1, 2]}}
            ]
        }
        publication = db.publications.find_one(_filter)
        if publication is None:
            raise NotFound(message="publication not found")
        publication_object = Publication._from_json(publication)
        return publication_object

    @staticmethod
    def delete_by_id(_id):
        result = db.publications.delete_one({'_id': ObjectId(_id)})
        if result.deleted_count == 0:
            raise NotFound(message="publication not found")

    @staticmethod
    def delete_by_id_and_owner(_id, owner):
        result = db.publications.delete_one({'_id': ObjectId(_id), 'owner': ObjectId(owner['sub'])})
        if result.deleted_count == 0:
            raise NotFound(message="publication not found")

    # admin saa muokata kenen tahansa julkaisua.
    @staticmethod
    @validate_patch_publication
    def admin_patch(publication):
        publication.update()
        return jsonify(publication=publication.to_json())

    # admin saa poistaa kenen tahansa julkaisua.
    @staticmethod
    @validate_delete_publication
    def admin_delete(_id):
        db.publications.delete_one({'_id': ObjectId(_id)})
        return ""

class Comment:

    def __init__(self, body, owner, publication, _id=None):
        self.body = body
        self.owner = str(owner)
        self.publication = str(publication)
        if _id is not None:
            _id = str(_id)
        self._id = _id

    def to_json(self):
        return {
            '_id': str(self._id),
            'body': self.body,
            'owner': str(self.owner),
            'publication': str(self.publication)
        }

    @staticmethod
    def list_to_json(comments):
        comments_in_json = []
        for comment in comments:
            comments_in_json.append(comment.to_json())
        return comments_in_json

    def create(self):
        result = db.comments.insert_one({'body': self.body, 'owner': ObjectId(self.owner),
                                         'publication': ObjectId(self.publication)})
        self._id = str(result.inserted_id)

    @staticmethod
    def get_all_by_publication(_publication_id):
        comments = []
        comments_cursor = db.comments.find({'publication': ObjectId(_publication_id)})
        for comment in comments_cursor:
            comments.append(Comment(comment['body'], comment['owner'], comment['publication'], _id=comment['_id']))
        return comments

    @staticmethod
    def update_by_id(_comment_id, body):
        _filter = {'_id': ObjectId(_comment_id)}
        _update = {'$set': {'body': body}}
        db.comments.update_one(_filter, _update)
        comment = db.comments.find_one({'_id': ObjectId(_comment_id)})
        return Comment(body, comment['owner'], comment['publication'], _id=comment['_id'])

    @staticmethod
    def delete_by_id(_comment_id):
        db.comments.delete_one({'_id': ObjectId(_comment_id)})




