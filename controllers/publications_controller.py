from flask.views import MethodView
from flask import request, jsonify
from models import Publication

class PublicationsRouteHandler(MethodView):
    def post(self):
        request_body = request.get_json()
        title = request_body['title']
        description = request_body['description']
        url = request_body['url']

        publication = Publication(title, description, url)
        publication.create()
        # palauta tässä jsonina juuri lisätty julkaisu
        return "Created " + title


    def get(self):
        publications = Publication.get_all()
        return jsonify(publications=Publication.list_to_json(publications))



