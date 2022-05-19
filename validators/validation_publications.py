from flask import request
from errors.validation_error import ValidationError
from flask_jwt_extended import jwt_required, get_jwt

def validate_add_publication(publications_route_handler):
    def validate_add_publication_wrapper(*args, **kwargs):
        request_body = request.get_json()
        if "title" in request_body and "description" in request_body and "url" in request_body:
            return publications_route_handler(*args, **kwargs)
        raise ValidationError(message="title, description and url are required")
    return validate_add_publication_wrapper



def validate_patch_publication(publications_route_handler):
    def validate_patch_publication_wrapper(*args, **kwargs):
        logged_in_user = get_jwt()
        print("Admin voi päivittää! " + logged_in_user['role'])
        if logged_in_user['role'] == 'admin':
            return publications_route_handler(*args, **kwargs)
        raise ValidationError(message="Must be admin to update post")
    return validate_patch_publication_wrapper

def validate_delete_publication(publications_route_handler):
    def validate_delete_publication_wrapper(*args, **kwargs):
        logged_in_user = get_jwt()
        print("Admin voi poistaa! " + logged_in_user['role'])
        if logged_in_user['role'] == 'admin':
            return publications_route_handler(*args, **kwargs)
        raise ValidationError(message="Must be admin to update post")
    return validate_delete_publication_wrapper
