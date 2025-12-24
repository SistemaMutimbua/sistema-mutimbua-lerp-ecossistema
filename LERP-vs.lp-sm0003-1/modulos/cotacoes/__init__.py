from flask import Blueprint

cotacoes_bp = Blueprint(
    "cotacoes",
    __name__,
    url_prefix="/cotacoes"
)

from . import routes
