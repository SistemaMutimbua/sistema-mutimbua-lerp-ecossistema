from flask import render_template, request, redirect, url_for, flash, send_file
from flask_babel import gettext as _
from flask_login import login_required, current_user

from io import BytesIO
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import func

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from . import compras_bp
from .forms import CompraForm
from .models import Compra, HistoricoCustoProduto
from modulos.extensions import db
from modulos.produtos.models import Produto
from modulos.auditoria.utils import registrar_acao

# =========================================================
# 🧾 LISTA DE COMPRAS
# =========================================================
@compras_bp.route("/compras")
# @login_required
def lista_compras():
    filtro = request.args.get("filtro", "").strip()
    campo = request.args.get("campo", "produto")

    query = Compra.query

    registrar_acao(
        acao="Acessou lista de compras",
        modulo="compras",
        detalhes=f"Campo: {campo} | Filtro: {filtro}"
    )

    if filtro:
        if campo == "codigo":
            query = query.filter(Compra.codigo_produto.ilike(f"%{filtro}%"))
        elif campo == "categoria":
            query = query.filter(Compra.categoria.ilike(f"%{filtro}%"))
        else:
            query = query.filter(Compra.produto.ilike(f"%{filtro}%"))

        registrar_acao(
            acao="Pesquisa na lista de compras",
            modulo="compras",
            detalhes=f"{campo}: {filtro}"
        )

    compras = query.order_by(Compra.data_compra.desc()).all()

    total_geral = db.session.query(func.sum(Compra.valor_total)).scalar() or 0
    total_lucro = db.session.query(func.sum(Compra.lucro_total)).scalar() or 0

    produtos_stock = {p.nome: p.stock for p in Produto.query.all()}

    return render_template(
        "compras/lista_compras.html",
        compras=compras,
        total_geral=total_geral,
        total_lucro=total_lucro,
        produtos=produtos_stock,
        titulo=_("Lista de Compras")
    )

# =========================================================
# ➕ NOVA COMPRA
# =========================================================
@compras_bp.route("/compras/nova", methods=["GET", "POST"])
# @login_required
def nova_compra():
    form = CompraForm()
    produtos = Produto.query.all()

    produtos_data = [{
        "codigo": p.codigo,
        "nome": p.nome,
        "preco_compra": p.preco_unitario,
        "preco_venda": p.preco_venda,
        "categoria": p.categoria
    } for p in produtos]

    if request.method == "POST":
        try:
            codigo_produto = request.form.get("codigo_produto")
            quantidade = float(request.form.get("quantidade"))
            preco_compra = float(request.form.get("preco_compra"))
            preco_venda = float(request.form.get("preco_venda"))
            categoria = request.form.get("categoria")
        except (ValueError, TypeError):
            flash(_("Valores inválidos."), "danger")
            return redirect(url_for("compras.nova_compra"))

        produto = Produto.query.filter_by(codigo=codigo_produto).first()
        if not produto:
            flash(_("Produto não encontrado."), "danger")
            return redirect(url_for("compras.nova_compra"))

        if preco_venda < preco_compra:
            flash(_("O preço de venda não pode ser inferior ao preço de compra."), "danger")
            return redirect(url_for("compras.nova_compra"))

        # ===============================
        # CÁLCULOS AUTOMÁTICOS
        # ===============================
        valor_total = round(preco_compra * quantidade, 2)
        margem_lucro = round(preco_venda - preco_compra, 2)
        lucro_total = round(margem_lucro * quantidade, 2)

        compra = Compra(
            codigo_produto=produto.codigo,
            produto=produto.nome,
            preco_compra=preco_compra,
            preco_venda=preco_venda,
            quantidade=quantidade,
            valor_total=valor_total,
            margem_lucro=margem_lucro,
            lucro_total=lucro_total,
            categoria=categoria
        )

        # ===============================
        # ATUALIZAR STOCK (MÉDIA PONDERADA)
        # ===============================
        stock_antigo = produto.stock
        custo_antigo = produto.preco_unitario

        produto.stock += quantidade
        produto.preco_unitario = round(
            ((custo_antigo * stock_antigo) + (preco_compra * quantidade)) / (stock_antigo + quantidade),
            2
        )

        produto.atualizar_estado()

        # ===============================
        # HISTÓRICO DE CUSTO
        # ===============================
        historico = HistoricoCustoProduto(
            produto_codigo=produto.codigo,
            custo=preco_compra,
            quantidade=quantidade
        )

        db.session.add_all([compra, historico])
        db.session.commit()

        registrar_acao(
            acao="Nova compra registrada",
            modulo="compras",
            detalhes=f"{produto.nome} | Qtd: {quantidade} | Total: {valor_total} | Lucro: {lucro_total}"
        )

        flash(_("Compra registrada com sucesso!"), "success")
        return redirect(url_for("compras.lista_compras"))

    return render_template(
        "compras/nova_compra.html",
        form=form,
        produtos=produtos_data
    )

# =========================================================
# 📊 EXPORTAR EXCEL
# =========================================================
@compras_bp.route("/compras/exportar/excel")
# @login_required
def exportar_excel():
    compras = Compra.query.order_by(Compra.data_compra.desc()).all()

    registrar_acao(acao="Exportou compras para Excel", modulo="compras")

    data = [{
        _("Código"): c.codigo_produto,
        _("Produto"): c.produto,
        _("Categoria"): c.categoria,
        _("Preço Compra"): c.preco_compra,
        _("Preço Venda"): c.preco_venda,
        _("Quantidade"): c.quantidade,
        _("Valor Total"): c.valor_total,
        _("Margem"): c.margem_lucro,
        _("Lucro Total"): c.lucro_total,
        _("Data"): c.data_compra.strftime("%d/%m/%Y %H:%M"),
    } for c in compras]

    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name=_("Compras"))
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="compras.xlsx")

# =========================================================
# 📄 EXPORTAR PDF
# =========================================================
@compras_bp.route("/compras/exportar/pdf")
# @login_required
def exportar_pdf():
    compras = Compra.query.order_by(Compra.data_compra.desc()).all()

    registrar_acao(acao="Exportou compras para PDF", modulo="compras")

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4

    y = altura - 50
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(largura / 2, y, _("Relatório de Compras - LERP Management"))
    y -= 30

    pdf.setFont("Helvetica", 9)
    pdf.drawString(40, y, _("Gerado em: ") + datetime.now().strftime("%d/%m/%Y %H:%M"))
    y -= 25

    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(40, y, _("Produto"))
    pdf.drawString(200, y, _("Total"))
    pdf.drawString(270, y, _("Lucro"))
    pdf.drawString(340, y, _("Categoria"))
    pdf.drawString(440, y, _("Data"))
    y -= 15

    pdf.setFont("Helvetica", 9)
    total_geral = 0
    total_lucro = 0

    for c in compras:
        pdf.drawString(40, y, c.produto[:30])
        pdf.drawString(200, y, f"{c.valor_total:.2f} MT")
        pdf.drawString(270, y, f"{c.lucro_total:.2f} MT")
        pdf.drawString(340, y, c.categoria or "-")
        pdf.drawString(440, y, c.data_compra.strftime("%d/%m/%Y"))

        total_geral += c.valor_total
        total_lucro += c.lucro_total
        y -= 14

        if y < 60:
            pdf.showPage()
            pdf.setFont("Helvetica", 9)
            y = altura - 50

    y -= 10
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(40, y, _("Total Compras: ") + f"{total_geral:.2f} MT")
    y -= 15
    pdf.drawString(40, y, _("Total Lucro: ") + f"{total_lucro:.2f} MT")

    pdf.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="compras.pdf", mimetype="application/pdf")

# =========================================================
# 📊 DASHBOARD FINANCEIRO
# =========================================================
@compras_bp.route("/compras/dashboard")
# @login_required
def dashboard_compras():
    hoje = datetime.today().date()

    # Totais gerais
    total_compras = db.session.query(func.sum(Compra.valor_total)).scalar() or 0
    total_lucro = db.session.query(func.sum(Compra.lucro_total)).scalar() or 0

    # Compras de hoje
    compras_hoje = db.session.query(func.sum(Compra.valor_total)).filter(func.date(Compra.data_compra) == hoje).scalar() or 0
    lucro_hoje = db.session.query(func.sum(Compra.lucro_total)).filter(func.date(Compra.data_compra) == hoje).scalar() or 0

    # Últimas compras
    ultimas_compras = Compra.query.order_by(Compra.data_compra.desc()).limit(5).all()

    # ======= Gráfico últimos 30 dias =======
    dias = [hoje - timedelta(days=i) for i in reversed(range(30))]
    chart_labels = [d.strftime("%d/%m") for d in dias]

    chart_compras = []
    chart_lucro = []

    for d in dias:
        soma_compra = db.session.query(func.sum(Compra.valor_total)).filter(func.date(Compra.data_compra) == d).scalar() or 0
        soma_lucro = db.session.query(func.sum(Compra.lucro_total)).filter(func.date(Compra.data_compra) == d).scalar() or 0
        chart_compras.append(round(soma_compra, 2))
        chart_lucro.append(round(soma_lucro, 2))

    registrar_acao(acao="Acessou dashboard financeiro", modulo="compras")

    return render_template(
        "compras/dashboard.html",
        total_compras=total_compras,
        total_lucro=total_lucro,
        compras_hoje=compras_hoje,
        lucro_hoje=lucro_hoje,
        ultimas_compras=ultimas_compras,
        chart_labels=chart_labels,
        chart_compras=chart_compras,
        chart_lucro=chart_lucro
    )
