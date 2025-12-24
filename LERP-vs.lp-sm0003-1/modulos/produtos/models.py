from modulos.extensions import db
from datetime import datetime

class Produto(db.Model):
    __tablename__ = "produtos"

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    preco_unitario = db.Column(db.Float, nullable=False)
    preco_venda = db.Column(db.Float)
    stock = db.Column(db.Integer, nullable=False, default=0)
    estado = db.Column(db.String(20), default="Normal")  # Normal ou Alerta
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
   
    def atualizar_estado(self):
        """Atualiza automaticamente o estado do produto conforme o stock"""
        if self.stock < 10:
            self.estado = "Alerta"
        else:
            self.estado = "Normal"



