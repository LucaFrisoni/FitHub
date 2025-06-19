from flask import Blueprint
from flasgger import Swagger

docs_bp = Blueprint("docs", __name__)


def init_docs(app):
    Swagger(app, template_file="docs/swagger.yaml")
