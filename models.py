import pymongo
from pymongo.server_api import ServerApi

import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('./venv/.env')
load_dotenv(dotenv_path=dotenv_path)

MONGO_URL = os.getenv('MONGO_URL')
client = pymongo.MongoClient(
    MONGO_URL,
    server_api=ServerApi('1'))
db = client.noSql_database

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


    def to_json(self):
        return{
            '_id': str(self._id),
            'title': self.title,
            'description': self.description,
            'url': self.url
        }


    @staticmethod
    def list_to_json(publication_list):
        publications = []
        for publication in publication_list:
            publications.append(publication.to_json())
        return publications


    # CRUD:n C (Create)
    def create(self):
        result = db.publications.insert_one({
            'title': self.title,
            'description': self.description,
            'url': self.url
        })
        print("create() tehty")
        self._id = str(result.inserted_id)


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


    """
        publications_list = list(publications_cursor)

        for publication in publications_list:
            publication["_id"] = str(publication["_id"])
        return publications_list
    """
