from flask import Blueprint

pagamentos_bp = Blueprint("pagamentos", __name__, template_folder="templates")

from . import routes
