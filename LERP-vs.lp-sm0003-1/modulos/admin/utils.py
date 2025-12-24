from .models import Usuario
from modulos.extensions import db

def criar_superadmin():
    admin_existente = Usuario.query.filter_by(email="admin@lerp.com").first()
    if not admin_existente:
        superadmin = Usuario(
            nome="Mutimbua",
            email="admin@lerp.com",
            tipo="superadmin"
        )
        superadmin.set_senha("admin123")
        db.session.add(superadmin)
        db.session.commit()
        print("✅ SuperAdmin criado automaticamente: admin@lerp.com / admin123")
