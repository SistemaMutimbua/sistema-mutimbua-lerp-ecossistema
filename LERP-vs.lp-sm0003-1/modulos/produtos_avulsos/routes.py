from flask import Blueprint, render_template, request, redirect, url_for, flash
from modulos.extensions import db
from datetime import datetime
from .models import ProdutoAvulso, EntradaAvulsa, VendaAvulsa

# ==========================================================
# BLUEPRINT
# ==========================================================
produtos_avulsos_bp = Blueprint(
    "produtos_avulsos",
    __name__,
    url_prefix="/produtos-avulsos"
)

# ==========================================================
# LISTAR PRODUTOS
# ==========================================================
@produtos_avulsos_bp.route("/listar")
def listar_produtos():
    produtos = ProdutoAvulso.query.all()

    return render_template(
        "produtos_avulsos/listar.html",
        produtos=produtos
    )

# ==========================================================
# CADASTRAR PRODUTO
# ==========================================================
@produtos_avulsos_bp.route("/cadastrar", methods=["GET", "POST"])
def cadastrar_produto():
    if request.method == "POST":
        nome = request.form.get("nome").strip()  # Remove espaços extras
        preco_str = request.form.get("preco", "0")
        unidade = request.form.get("unidade", "unidade").strip()

        # Validação do nome
        if not nome:
            flash("O nome do produto é obrigatório!", "danger")
            return redirect(url_for("produtos_avulsos.cadastrar_produto"))

        # Validação do preço
        try:
            preco = float(preco_str)
            if preco < 0:
                raise ValueError
        except ValueError:
            flash("O preço informado é inválido!", "danger")
            return redirect(url_for("produtos_avulsos.cadastrar_produto"))

        # Verifica se já existe
        existente = ProdutoAvulso.query.filter_by(codigo=nome).first()
        if existente:
            flash(f"O produto '{nome}' já está cadastrado!", "warning")
            return redirect(url_for("produtos_avulsos.cadastrar_produto"))

        novo = ProdutoAvulso(
            codigo=nome,
            descricao=nome,
            preco=preco,
            unidade=unidade
        )

        db.session.add(novo)
        db.session.commit()

        flash("Produto cadastrado com sucesso!", "success")
        return redirect(url_for("produtos_avulsos.listar_produtos"))

    return render_template("produtos_avulsos/cadastrar.html")

# ==========================================================
# EDITAR PRODUTO
# ==========================================================
@produtos_avulsos_bp.route("/editar/<int:id>", methods=["GET", "POST"])
def editar_produto(id):
    produto = ProdutoAvulso.query.get_or_404(id)

    if request.method == "POST":
        produto.codigo = request.form.get("codigo")
        produto.descricao = request.form.get("descricao")
        produto.preco = float(request.form.get("preco", 0))
        produto.unidade = request.form.get("unidade")

        db.session.commit()

        flash("Produto atualizado com sucesso!", "success")
        return redirect(url_for("produtos_avulsos.listar_produtos"))

    return render_template("produtos_avulsos/editar.html", produto=produto)

# ==========================================================
# APAGAR PRODUTO
# ==========================================================
@produtos_avulsos_bp.route("/apagar/<int:id>")
def apagar_produto(id):
    produto = ProdutoAvulso.query.get_or_404(id)

    # limpar vínculos antes
    EntradaAvulsa.query.filter_by(produto_id=id).delete()
    VendaAvulsa.query.filter_by(produto_id=id).delete()

    db.session.delete(produto)
    db.session.commit()

    flash("Produto eliminado com sucesso!", "danger")
    return redirect(url_for("produtos_avulsos.listar_produtos"))

# ==========================================================
# REGISTRAR ENTRADA FINANCEIRA
# ==========================================================
@produtos_avulsos_bp.route("/entrada/<int:produto_id>", methods=["GET", "POST"])
def registrar_entrada(produto_id):
    produto = ProdutoAvulso.query.get_or_404(produto_id)

    if request.method == "POST":
        qtd = int(request.form.get("quantidade", 1))
        custo_unitario = float(request.form.get("custo_unitario", produto.preco))
        fornecedor = request.form.get("fornecedor", "Desconhecido")

        entrada = EntradaAvulsa(
            produto_id=produto.id,
            quantidade=qtd,
            custo_unitario=custo_unitario,
            custo_total=qtd * custo_unitario,
            fornecedor=fornecedor
        )

        db.session.add(entrada)
        db.session.commit()

        flash("Entrada registrada com sucesso!", "success")
        return redirect(url_for("produtos_avulsos.listar_produtos"))

    return render_template("produtos_avulsos/entrada.html", produto=produto)

# ==========================================================
# REGISTRAR VENDA
# ==========================================================
@produtos_avulsos_bp.route("/vender/<int:produto_id>", methods=["GET", "POST"])
def vender(produto_id):
    produto = ProdutoAvulso.query.get_or_404(produto_id)

    if request.method == "POST":
        qtd = int(request.form.get("quantidade", 1))
        cliente = request.form.get("cliente", "Consumidor Final")
        metodo = request.form.get("metodo_pagamento", "dinheiro")

        total = qtd * produto.preco

        venda = VendaAvulsa(
            produto_id=produto.id,
            quantidade=qtd,
            valor_unitario=produto.preco,
            valor_total=total,
            cliente=cliente,
            metodo_pagamento=metodo
        )

        db.session.add(venda)
        db.session.commit()

        flash("Venda registrada!", "success")
        return redirect(url_for("produtos_avulsos.listar_produtos"))

    return render_template("produtos_avulsos/vender.html", produto=produto)

# ==========================================================
# DETALHES FINANCEIROS
# ==========================================================
# ==========================================================
# DETALHES FINANCEIROS
# ==========================================================
@produtos_avulsos_bp.route("/detalhes/<int:produto_id>")
def detalhes_financeiros(produto_id):
    produto = ProdutoAvulso.query.get_or_404(produto_id)

    entradas = EntradaAvulsa.query.filter_by(produto_id=produto_id).all()
    vendas = VendaAvulsa.query.filter_by(produto_id=produto_id).all()

    total_entradas = sum(e.custo_total for e in entradas)
    total_vendas = sum(v.valor_total for v in vendas)

    lucro = total_vendas - total_entradas

    return render_template(
        "produtos_avulsos/detalhes.html",
        produto=produto,
        entradas=entradas,
        vendas=vendas,
        total_entradas=total_entradas,
        total_vendas=total_vendas,
        lucro=lucro
    )
