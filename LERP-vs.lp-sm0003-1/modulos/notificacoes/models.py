from datetime import datetime
from modulos.extensions import db

class Notificacao(db.Model):
    __tablename__ = "notificacoes"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(50), nullable=False, default="info")  # info, alerta, sucesso, etc
    data = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Notificacao {self.titulo}>"
