from flask.views import MethodView
from flask import request, jsonify
from models import Publication
from validators.validation_publications import validate_add_publication
from flask_jwt_extended import jwt_required, get_jwt


class PublicationsRouteHandler(MethodView):

    @validate_add_publication
    @jwt_required(optional=True)
    def post(self):
        logged_in_user = get_jwt()
        owner = None
        visibility = 2
        request_body = request.get_json()
        if logged_in_user:
            owner = logged_in_user['sub']
            visibility = request_body.get('visibility', 2)

        title = request_body['title']
        description = request_body['description']
        url = request_body['url']
        publication = Publication(title, description, url, owner=owner, visibility=visibility)
        publication.create()

        # palauttaa tässä jsonina juuri lisätyn julkaisun
        return jsonify(publication=publication.to_json())

    # tämä vastaa get request methodiin osoitteessa /api/publications
    @jwt_required(optional=True)
    def get(self):
        logged_in_user = get_jwt()
        print("######################### logged in user: ", logged_in_user)
        if not logged_in_user:
            # käyttäjä ei ole kirjautunut sitään
            # tässä haetaan vain ne publicationit joiden visibility on 2
            publications = Publication.get_by_visibility()
        else:
            if logged_in_user['role'] == 'admin':
                publications = Publication.get_all()
            elif logged_in_user['role'] == 'user':
                # tässä haetaan käyttäjän omat julkaisut ja ne joissa visibility on 1 tai 2
                publications = Publication.get_logged_in_users_and_public_publications(logged_in_user)

        return jsonify(publications=Publication.list_to_json(publications))


# Alla oleva route handler lisätty 9.5
# TODO lisää gettiin logged_in_user ja samat ehdot kun PublicationsRouteHandlerin getissä
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
        publication.visibility = request_body.get('visibility', publication.visibility)

        # päivitetään publication tietokantaan
        publication.update()
        return jsonify(publication=publication.to_json())

    # Tekee samat asiat kun patch
    def put(self, _id):
        request_body = request.get_json()
        publication = Publication.get_by_id(_id)
        publication.title = request_body.get('title', publication.title)
        publication.description = request_body.get('description', publication.description)
        publication.visibility = request_body.get('visibility', publication.visibility)
        publication.update()
        return jsonify(publication=publication.to_json())


