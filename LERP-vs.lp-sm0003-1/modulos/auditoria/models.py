from datetime import datetime
from modulos.extensions import db

class Auditoria(db.Model):
    __tablename__ = "auditoria"

    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(100))
    acao = db.Column(db.String(255), nullable=False)
    modulo = db.Column(db.String(100), nullable=False)
    detalhes = db.Column(db.Text)
    data = db.Column(db.DateTime, default=datetime.utcnow)
