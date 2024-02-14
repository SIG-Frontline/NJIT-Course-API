from flask import Blueprint

docs = Blueprint('docs', __name__, url_prefix='/docs')

@docs.route('/help')
def help():
    return "This is the docs help page."
