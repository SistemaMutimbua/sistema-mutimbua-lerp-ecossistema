from flask import Blueprint

caixa_bp = Blueprint("caixa", __name__, template_folder="templates")

from . import routes
