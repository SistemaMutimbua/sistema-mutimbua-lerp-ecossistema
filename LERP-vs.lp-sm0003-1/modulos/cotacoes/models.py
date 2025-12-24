from modulos.extensions import db
from datetime import datetime
import json

class Cotacao(db.Model):
    __tablename__ = "cotacoes"

    id = db.Column(db.Integer, primary_key=True)
    cliente = db.Column(db.String(120), nullable=False)

    itens_json = db.Column(db.Text, nullable=False)

    total_valor = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default="rascunho")  
    data_cotacao = db.Column(db.DateTime, default=datetime.now)

    venda_id = db.Column(db.Integer, nullable=True)

    @property
    def itens(self):
        return json.loads(self.itens_json)

    @itens.setter
    def itens(self, value):
        self.itens_json = json.dumps(value)
