from flask_login import current_user
from modulos.extensions import db
from .models import Auditoria
from datetime import datetime

def registrar_acao(acao, modulo, detalhes=""):
    try:
        usuario = current_user.username if hasattr(current_user, "username") else "Sistema/Desconhecido"

        reg = Auditoria(
            usuario=usuario,
            acao=acao,
            modulo=modulo,
            detalhes=detalhes,
            data=datetime.utcnow()
        )
        db.session.add(reg)
        db.session.commit()
    except Exception as e:
        print("Erro ao registrar auditoria:", str(e))
