from flask.views import MethodView
from flask import request, jsonify
from models import Publication
from validators.validation_publications import validate_add_publication


class PublicationsRouteHandler(MethodView):

    @validate_add_publication
    def post(self):
        request_body = request.get_json()
        title = request_body['title']
        description = request_body['description']
        url = request_body['url']
        publication = Publication(title, description, url)
        publication.create()

        # palauttaa tässä jsonina juuri lisätyn julkaisun
        return jsonify(publication=publication.to_json())

    def get(self):
        publications = Publication.get_all()
        return jsonify(publications=Publication.list_to_json(publications))


# Alla oleva route handler lisätty 9.5
# TODO: Muuta patch ja putissa url visibilityksi
class PublicationRouteHandler(MethodView):

    def get(self, _id):
        publication = Publication.get_by_id(_id)
        return jsonify(publication=publication.to_json())

    def delete(self, _id):
        Publication.delete_by_id(_id)
        return ""

    def patch(self, _id):
        request_body = request.get_json()

        # haetaan publication tietokannasta id:n perusteella
        publication = Publication.get_by_id(_id)

        # muutetaan publicationin arvoja
        publication.title = request_body.get('title', publication.title)
        publication.description = request_body.get('description', publication.description)
        publication.url = request_body.get('url', publication.url)

        # päivitetään publication tietokantaan
        publication.update()
        return jsonify(publication=publication.to_json())

    # Tekee samat asiat kun patch
    def put(self, _id):
        request_body = request.get_json()
        publication = Publication.get_by_id(_id)
        publication.title = request_body.get('title', publication.title)
        publication.description = request_body.get('description', publication.description)
        publication.url = request_body.get('url', publication.url)
        publication.update()
        return jsonify(publication=publication.to_json())


