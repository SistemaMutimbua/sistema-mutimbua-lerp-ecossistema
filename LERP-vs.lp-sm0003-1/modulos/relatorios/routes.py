from flask import render_template
from flask_babel import gettext as _
from modulos.produtos.models import Produto
from modulos.vendas.models import Venda
from modulos.compras.models import Compra
from modulos.caixa.models import Caixa
from modulos.pagamentos.models import Pagamento
from modulos.extensions import db
from sqlalchemy import func
from . import relatorios_bp

@relatorios_bp.route("/")
def dashboard():
    """
    Dashboard completo da empresa:
    - Top 5 produtos mais vendidos
    - Top 5 produtos mais comprados
    - Stock remanescente
    - Entradas e saídas do caixa
    - Saldo financeiro
    """

    # --- Produtos mais vendidos ---
    vendas_produtos = (
        db.session.query(Venda.produto, func.sum(Venda.quantidade).label("total_vendido"))
        .group_by(Venda.produto)
        .order_by(func.sum(Venda.quantidade).desc())
        .all()
    )
    top_vendidos = vendas_produtos[:5]

    # --- Produtos mais comprados ---
    compras_produtos = (
        db.session.query(Compra.produto, func.sum(Compra.quantidade).label("total_comprado"))
        .group_by(Compra.produto)
        .order_by(func.sum(Compra.quantidade).desc())
        .all()
    )
    top_comprados = compras_produtos[:5]

    # --- Stock remanescente ---
    produtos = Produto.query.all()

    # --- Entradas e saídas ---
    total_entradas = db.session.query(func.sum(Pagamento.valor)).scalar() or 0.0
    total_saidas = (
        db.session.query(func.sum(Caixa.valor))
        .filter(Caixa.tipo == "saida")
        .scalar()
        or 0.0
    )
    saldo = total_entradas - total_saidas

    return render_template(
        "relatorios/dashboard.html",
        top_vendidos=top_vendidos,
        top_comprados=top_comprados,
        produtos=produtos,
        total_entradas=total_entradas,
        total_saidas=total_saidas,
        saldo=saldo,
        titulo_pagina=_("Relatórios e Estatísticas"),
        titulo_top_vendidos=_("Top 5 Produtos Mais Vendidos"),
        titulo_top_comprados=_("Top 5 Produtos Mais Comprados"),
        titulo_stock=_("Stock Remanescente"),
        titulo_caixa=_("Movimentação do Caixa"),
        titulo_saldo=_("Saldo Financeiro Atual"),
    )
