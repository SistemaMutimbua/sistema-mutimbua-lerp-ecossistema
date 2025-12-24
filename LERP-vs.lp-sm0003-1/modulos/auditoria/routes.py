from flask import Blueprint, render_template
from flask_babel import _
from modulos.auditoria.models import Auditoria

auditoria_bp = Blueprint("auditoria", __name__, url_prefix="/auditoria")

@auditoria_bp.route("/")
def index():
    logs = Auditoria.query.order_by(Auditoria.data.desc()).limit(200).all()
    return render_template(
        "auditoria/index.html",
        titulo_pagina=_("Auditoria do Sistema"),
        logs=logs
    )
