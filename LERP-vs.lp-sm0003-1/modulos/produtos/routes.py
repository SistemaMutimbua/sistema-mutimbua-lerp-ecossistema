from flask import render_template, request, redirect, url_for, flash, send_file
from io import BytesIO
import os
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from datetime import datetime
from flask_babel import _

from . import produtos_bp
from .models import Produto
from modulos.extensions import db

# Para gerar código de barras
import barcode
from barcode.writer import ImageWriter
from reportlab.lib.utils import ImageReader


# ===========================================================
# 🔹 GERADOR AUTOMÁTICO DE CÓDIGO
# ===========================================================
def gerar_codigo(nome, categoria):
    prefixos = {
        "ferragem": "gf",
        "loja": "gl",
        "botle store": "gbs",
        "mercearia": "gm",
        "supermercado": "gs",
        "farmacia": "gfm",
        "restaurantes": "grs",
        "bar": "gbr",
        "acessorios": "gac",
        "servicos": "gsv"
    }

    categoria_limpa = (categoria or "").strip().lower()
    prefixo = prefixos.get(categoria_limpa, "gen")

    # Conta produtos da mesma categoria para gerar código sequencial
    ultimo_num = Produto.query.filter(
        Produto.categoria.ilike(categoria)
    ).count() + 1

    return f"{prefixo}{str(ultimo_num).zfill(3)}"


# ===========================================================
# 🔹 LISTA DE PRODUTOS
# ===========================================================
@produtos_bp.route("/produtos")
def lista_produtos():
    filtro = request.args.get("filtro", "")
    campo = request.args.get("campo", "nome")

    query = Produto.query

    if filtro:
        filtro_like = f"%{filtro}%"
        if campo == "codigo":
            query = query.filter(Produto.codigo.ilike(filtro_like))
        elif campo == "categoria":
            query = query.filter(Produto.categoria.ilike(filtro_like))
        else:
            query = query.filter(Produto.nome.ilike(filtro_like))

    produtos = query.order_by(Produto.id.desc()).all()

    # Atualizar estado automaticamente
    for p in produtos:
        p.atualizar_estado()

    db.session.commit()

    return render_template("produtos/lista_produtos.html", produtos=produtos)



# ===========================================================
# 🔹 CADASTRAR NOVO PRODUTO
# ===========================================================
@produtos_bp.route("/produtos/novo", methods=["GET", "POST"])
def novo_produto():
    if request.method == "POST":
        nome = request.form["nome"]
        categoria = request.form["categoria"]
        preco = float(request.form["preco_unitario"])
        stock = int(request.form["stock"])

        codigo = gerar_codigo(nome, categoria)

        novo_produto = Produto(
            codigo=codigo,
            nome=nome,
            categoria=categoria,
            preco_unitario=preco,
            stock=stock
        )

        novo_produto.atualizar_estado()
        db.session.add(novo_produto)
        db.session.commit()

        flash(_("Produto cadastrado com sucesso!"), "success")
        return redirect(url_for("produtos.lista_produtos"))

    return render_template("produtos/novo_produto.html")



# ===========================================================
# 🔹 EXPORTAR PARA EXCEL
# ===========================================================
@produtos_bp.route("/produtos/exportar/excel")
def exportar_excel():
    produtos = Produto.query.all()

    data = [{
        _("Código"): p.codigo,
        _("Produto"): p.nome,
        _("Categoria"): p.categoria,
        _("Preço Unitário"): p.preco_unitario,
        _("Stock"): p.stock,
        _("Estado"): p.estado
    } for p in produtos]

    df = pd.DataFrame(data)
    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name=str(_("Produtos")))

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="produtos.xlsx")



# ===========================================================
# 🔹 EXPORTAR PARA PDF (TABELA COMPLETA)
# ===========================================================
@produtos_bp.route("/produtos/exportar/pdf")
def exportar_pdf():
    produtos = Produto.query.all()
    buffer = BytesIO()

    pdf = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=40,
        bottomMargin=40,
        leftMargin=40,
        rightMargin=40,
    )

    elementos = []
    estilos = getSampleStyleSheet()

    # Cabeçalho / Título
    elementos.append(Paragraph("<b>LERP MANAGEMENT SYSTEM</b>", estilos["Title"]))
    elementos.append(Spacer(1, 12))

    data_emissao = datetime.now().strftime("%d/%m/%Y %H:%M")
    elementos.append(Paragraph(f"<b>{_('Emitido em')}:</b> {data_emissao}", estilos["Normal"]))
    elementos.append(Spacer(1, 12))

    elementos.append(Paragraph(f"<b>{_('Lista de Produtos')}</b>", estilos["Heading2"]))
    elementos.append(Spacer(1, 15))

    tabela_dados = [[
        _("Código"),
        _("Nome"),
        _("Categoria"),
        _("Preço Unitário (MT)"),
        _("Stock"),
        _("Estado")
    ]]

    for p in produtos:
        tabela_dados.append([
            p.codigo,
            p.nome,
            p.categoria,
            f"{p.preco_unitario:,.2f}",
            str(p.stock),
            p.estado
        ])

    tabela = Table(tabela_dados, colWidths=[60, 120, 90, 110, 50, 70])

    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0050A0")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
    ]))

    elementos.append(tabela)
    pdf.build(elementos)

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="produtos.pdf", mimetype="application/pdf")



# ===========================================================
# 🔹 DELETAR PRODUTO
# ===========================================================
@produtos_bp.route("/produtos/delete/<int:id>", methods=["POST", "GET"])
def deletar_produto(id):
    produto = Produto.query.get_or_404(id)

    try:
        nome = produto.nome
        db.session.delete(produto)
        db.session.commit()
        flash(_("Produto '%(nome)s' removido com sucesso!", nome=nome), "success")

    except Exception as e:
        db.session.rollback()
        flash(_("Erro ao apagar o produto: %(erro)s", erro=str(e)), "danger")

    return redirect(url_for("produtos.lista_produtos"))



# ===========================================================
# 🔹 GERAR BARCODE DO PRODUTO (PDF)
# ===========================================================
@produtos_bp.route("/produtos/barcode/<int:id>")
def gerar_barcode(id):
    produto = Produto.query.get_or_404(id)

    codigo = produto.codigo

    # Gerar imagem do código de barras
    buffer_img = BytesIO()
    barcode_class = barcode.get_barcode_class("code128")
    barcode_obj = barcode_class(codigo, writer=ImageWriter())
    barcode_obj.write(buffer_img)
    buffer_img.seek(0)

    # Criar PDF
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(80, 800, f"{produto.nome} - {produto.codigo}")

    barcode_image = ImageReader(buffer_img)
    c.drawImage(barcode_image, 80, 680, width=300, height=100)

    c.setFont("Helvetica", 11)
    link_url = url_for("produtos.lista_produtos", _external=True) + f"?codigo={produto.codigo}"
    c.drawString(80, 660, _("Scaneie para abrir o produto: ") + link_url)

    c.showPage()
    c.save()

    pdf_buffer.seek(0)
    return send_file(pdf_buffer,
        as_attachment=True,
        download_name=f"barcode_{produto.codigo}.pdf",
        mimetype="application/pdf"
    )
