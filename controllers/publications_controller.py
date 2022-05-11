from flask.views import MethodView
from flask import request, jsonify
from errors.not_found import NotFound
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
        publications = []
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


class PublicationRouteHandler(MethodView):

    @jwt_required(optional=True)
    def get(self, _id):
        publication = None
        logged_in_user = get_jwt()
        if logged_in_user:
            if logged_in_user['role'] == 'admin':
                publication = Publication.get_by_id(_id)
            elif logged_in_user['role'] == 'user':
                publication = Publication.get_logged_in_users_and_public_publication(_id, logged_in_user)
        else: # kun käyttäjä ei ole kirjautunut sisään
            publication = Publication.get_one_by_id_and_visibility(_id)
        return jsonify(publication=publication.to_json())

    @jwt_required(optional=False) # @jwt_required(), False on oletusarvo
    def delete(self, _id):
        logged_in_user = get_jwt()
        if logged_in_user['role'] == 'admin':
            Publication.delete_by_id(_id)
        elif logged_in_user['role'] == 'user':
            Publication.delete_by_id_and_owner(_id, logged_in_user)
        return ""

    @jwt_required(optional=False)
    def patch(self, _id):
        logged_in_user = get_jwt()
        publication = Publication.get_by_id(_id)

        # käyttäjä on aina 'admin' tai 'user', ja vain 'user' voi saada NotFound errorin.
        # 'admin' voi aina muokata publicationia.
        if logged_in_user['role'] == 'user':
            if publication.owner is None or str(publication.owner) != logged_in_user['sub']:
                raise NotFound(message="publication not found")
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
    @jwt_required(optional=False)
    def put(self, _id):
        logged_in_user = get_jwt()
        publication = Publication.get_by_id(_id)
        if logged_in_user['role'] == 'user':
            if publication.owner is None or str(publication.owner) != logged_in_user['sub']:
                raise NotFound(message="publication not found")
        request_body = request.get_json()
        publication = Publication.get_by_id(_id)
        publication.title = request_body.get('title', publication.title)
        publication.description = request_body.get('description', publication.description)
        publication.visibility = request_body.get('visibility', publication.visibility)
        publication.update()
        return jsonify(publication=publication.to_json())


