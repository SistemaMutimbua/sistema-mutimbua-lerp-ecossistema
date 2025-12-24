from modulos.extensions import db
from datetime import datetime

class Caixa(db.Model):
    __tablename__ = "caixa"

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(10), nullable=False)  # entrada ou saida
    valor = db.Column(db.Float, nullable=False)
    justificativa = db.Column(db.String(200), nullable=True)  # obrigatório se saida
    data = db.Column(db.DateTime, default=datetime.utcnow)
