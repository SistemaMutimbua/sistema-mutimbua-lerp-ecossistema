from flask import Blueprint

produtos_avulsos_bp = Blueprint(
    "produtos_avulsos",
    __name__,
    template_folder="templates"
)

from . import routes
