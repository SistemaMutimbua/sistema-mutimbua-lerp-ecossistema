from modulos.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(db.Model, UserMixin):
    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)          # Nome ou login
    email = db.Column(db.String(120), unique=True, nullable=False)  # Email obrigatório
    password_hash = db.Column(db.String(128), nullable=False) # Senha criptografada
    is_admin = db.Column(db.Boolean, default=False)           # Admin ou operador

    def set_senha(self, senha):
        self.password_hash = generate_password_hash(senha)

    def checar_senha(self, senha):
        return check_password_hash(self.password_hash, senha)
