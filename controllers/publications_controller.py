from bson import ObjectId
from flask.views import MethodView
from flask import request, jsonify
from errors.not_found import NotFound
from models import Publication
from validators.validation_publications import validate_add_publication, validate_patch_publication
from flask_jwt_extended import jwt_required, get_jwt


# Alla olevissa metodeissa @jwt_required(optional=True) tarkoittaa että kuka vaan voi suorittaa metodin.
# @jwt_required(optional=False) vaatii tokenin, eli käyttäjän pitää olla sisäänkirjautunut.
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

        # poistetaan tietokannasta jos kyseessä 'user'.
        if logged_in_user['role'] == 'user':
            Publication.delete_by_id_and_owner(_id, logged_in_user)
            return ""

        # poistetaan tietokannasta jos kyseessä 'admin'.
        # Tarkistus tapahtuu admin_delete funktiolla joka käyttää validate_delete_publication dekoraattoria.
        Publication.admin_delete(_id)

        return ""

    @jwt_required(optional=False)
    def patch(self, _id):
        logged_in_user = get_jwt()
        publication = Publication.get_by_id(_id)

        # käyttäjä on aina 'admin' tai 'user'
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

        # päivitetään publication tietokantaan jos kyseessä 'user'
        if logged_in_user['role'] == 'user':
            publication.update()
            return jsonify(publication=publication.to_json())

        # päivitetään tietokantaan jos kyseessä 'admin'.
        # Tarkistus tapahtuu admin_patch funktiolla joka käyttää validate_patch_publication dekoraattoria
        Publication.admin_patch(publication)

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
        if logged_in_user['role'] == 'user':
            publication.update()
            return jsonify(publication=publication.to_json())
        Publication.admin_patch(publication)
        return jsonify(publication=publication.to_json())


class LikePublicationRouteHandler(MethodView):
    # /api/publications/<_id>/like
    @jwt_required(optional=False)
    def patch(self, _id):
        logged_in_user = get_jwt()
        publication = Publication.get_by_id(_id)
        found_index = -1   # -1 koska listat alkavat 0, -1 tarkoittaa että käyttäjiä ei ole likes-listassa

        for index, user_object_id in enumerate(publication.likes):
            if str(user_object_id) == logged_in_user['sub']:
                found_index = index
                break

        if found_index != -1:
            del publication.likes[found_index]
        else:
            publication.likes.append(ObjectId(logged_in_user['sub']))

        publication.like()
        return jsonify(publication=publication.to_json())
