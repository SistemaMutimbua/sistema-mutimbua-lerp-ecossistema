from modulos.extensions import db
from .models import Usuario

def criar_superadmin():
    """Cria um superadmin padrão se não existir."""
    if not Usuario.query.filter_by(username="admin").first():
        admin = Usuario(username="admin", is_superadmin=True)
        admin.set_password("admin123")  # senha padrão
        db.session.add(admin)
        db.session.commit()
        print("Superadmin criado: usuário=admin senha=admin123")
