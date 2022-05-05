from flask import Flask, jsonify
from controllers.home_controller import home_route_handler
from controllers.publications_controller import PublicationsRouteHandler
from controllers.users_controller import UsersRouteHandler, UserRouteHandler
from errors.validation_error import ValidationError
from errors.not_found import NotFound

app = Flask(__name__)

@app.errorhandler(ValidationError)
def handle_validation_error(err):
    return jsonify(err=err.args), 400

@app.errorhandler(NotFound)
def handle_not_found_error(err):
    return jsonify(err=err.args), 404

app.add_url_rule("/", view_func=home_route_handler)

app.add_url_rule("/api/users", view_func=UsersRouteHandler.as_view('users_route_handler'), methods=['GET', 'POST'])
app.add_url_rule("/api/users/<_id>", view_func=UserRouteHandler.as_view('user_route_handler'),
                 methods=["GET", "DELETE", "PATCH", "PUT"])

app.add_url_rule("/api/publications", view_func=PublicationsRouteHandler.as_view('publications_route_handler'),
                 methods=['GET', 'POST'])

# @app.route()
app.run(debug=True)
