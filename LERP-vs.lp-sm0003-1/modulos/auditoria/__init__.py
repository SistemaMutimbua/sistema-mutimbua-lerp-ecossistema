from flask import Blueprint

auditoria_bp = Blueprint("auditoria", __name__)

from . import routes
