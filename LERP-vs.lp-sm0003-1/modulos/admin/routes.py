from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_babel import gettext as _
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps
from modulos.admin.models import Usuario
from modulos.produtos.models import Produto
from modulos.compras.models import Compra
from modulos.vendas.models import Venda
from modulos.caixa.models import Caixa
from modulos.notificacoes.models import Notificacao
from datetime import datetime
from modulos.extensions import db, login_manager

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ===================== LOGIN MANAGER =====================
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


# ===================== DECORATOR DE ADMIN =====================
def admin_required(f):
    @wraps(f)
    #@login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash(_("Acesso negado: você não tem permissão para esta área."), "danger")
            return redirect(url_for("admin.login_admin"))
        return f(*args, **kwargs)
    return decorated_function


# ===================== LOGIN =====================
@admin_bp.route("/login", methods=["GET", "POST"])
def login_admin():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and usuario.checar_senha(senha):
            login_user(usuario, remember=True)
            flash(_("Bem-vindo, %(nome)s!", nome=usuario.nome), "success")
            return redirect(url_for("admin.dashboard"))
        else:
            flash(_("E-mail ou senha incorretos."), "danger")

    return render_template(
        "admin/login.html",
        titulo_pagina=_("Login Superadmin")
    )


# ===================== LOGOUT =====================
@admin_bp.route("/logout")
#@login_required
def logout_admin():
    logout_user()
    flash(_("Sessão encerrada com sucesso."), "info")
    return redirect(url_for("admin.login_admin"))


# ===================== DASHBOARD =====================

@admin_bp.route("/dashboard")
def dashboard():
    total_produtos = Produto.query.count()
    total_compras = Compra.query.count()
    total_vendas = Venda.query.count()
    total_caixa = Caixa.query.count()
    notificacoes = Notificacao.query.order_by(Notificacao.data.desc()).limit(5).all()

    # --- Gráfico de Vendas por mês ---
    ano_atual = datetime.now().year
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    vendas_mes = []
    for m in range(1, 13):
        total_mes = db.session.query(db.func.sum(Venda.total_valor))\
            .filter(db.extract('month', Venda.data_venda) == m)\
            .filter(db.extract('year', Venda.data_venda) == ano_atual).scalar() or 0
        vendas_mes.append(float(total_mes))

    # --- Produtos com menor estoque (top 5) ---
    produtos = Produto.query.order_by(Produto.stock.asc()).limit(5).all()
    produtos_labels = [p.nome for p in produtos]
    produtos_estoque = [p.stock for p in produtos]

    return render_template(
        "admin/dashboard.html",
        titulo_pagina=_("Painel Superadmin"),
        total_produtos=total_produtos,
        total_compras=total_compras,
        total_vendas=total_vendas,
        total_caixa=total_caixa,
        notificacoes=notificacoes,
        meses=meses,
        vendas_mes=vendas_mes,
        produtos_labels=produtos_labels,
        produtos_estoque=produtos_estoque
    )

# ===================== LISTA DE USUÁRIOS (exemplo adicional) =====================
@admin_bp.route("/usuarios")
#@admin_required
def lista_usuarios():
    usuarios = Usuario.query.order_by(Usuario.nome).all()
    return render_template(
        "admin/usuarios.html",
        titulo_pagina=_("Lista de Usuários"),
        usuarios=usuarios
    )
