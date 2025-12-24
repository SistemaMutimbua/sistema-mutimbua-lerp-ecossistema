from flask import (
    render_template, redirect, url_for, flash,
    request, send_file
)
from io import BytesIO
import pandas as pd
from datetime import datetime
from flask_babel import _
from sqlalchemy.exc import SQLAlchemyError

from . import pagamentos_bp
from .models import Pagamento, FolhaCaixa
from .forms import PagamentoForm
from modulos.extensions import db
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4




# Auditoria (fallback)
try:
    from modulos.auditoria.utils import registrar_acao
except ImportError:
    def registrar_acao(acao="", modulo="", detalhes=""):
        pass

# -------------------------------
# 🔹 Função para gerar código único
# -------------------------------
def gerar_codigo_pagamento():
    ultimo = Pagamento.query.order_by(Pagamento.id.desc()).first()
    if ultimo:
        try:
            num = int(str(ultimo.codigo_pagamento).replace("pgag", ""))
        except Exception:
            num = ultimo.id or 0
        return f"pgag{num + 1:04d}"
    return "pgag0001"

# -------------------------------
# 🔹 Novo Pagamento
# -------------------------------

@pagamentos_bp.route("/pagamentos/novo", methods=["GET", "POST"])
def novo_pagamento():
    form = PagamentoForm()
    
    # Receber valor e código via query string (da venda)
    valor = request.args.get("total")
    codigo = request.args.get("codigo")

    if request.method == "GET":
        # Preencher automaticamente campos do pagamento
        form.preco_unitario.data = float(valor) if valor else 0.0
        form.codigo_pagamento.data = codigo or gerar_codigo_pagamento()

    if form.validate_on_submit():
        pagamento = Pagamento(
            codigo_pagamento=form.codigo_pagamento.data,
            valor=form.preco_unitario.data,
            tipo_pagamento=form.tipo_pagamento.data,
            descricao=form.descricao.data or ""
        )
        try:
            db.session.add(pagamento)
            db.session.commit()
            flash(_("Pagamento registrado com sucesso!"), "success")
            return redirect(url_for("pagamentos.lista_pagamentos"))
        except Exception as e:
            db.session.rollback()
            flash(_("Erro ao registrar pagamento: ") + str(e), "danger")

    return render_template("pagamentos/novo_pagamento.html", form=form)

# -------------------------------
# 🔹 Lista de Pagamentos

@pagamentos_bp.route("/pagamentos")
def lista_pagamentos():
    # Filtros
    filtro = request.args.get("filtro", "")
    tipo = request.args.get("tipo", "")

    query = Pagamento.query

    if filtro:
        query = query.filter(Pagamento.codigo_pagamento.contains(filtro))
    if tipo:
        query = query.filter(Pagamento.tipo_pagamento == tipo)

    pagamentos = query.order_by(Pagamento.data_pagamento.desc()).all()

    # Total pago
    total_pago = sum(float(p.preco_unitario or 0) for p in pagamentos)

    return render_template(
        "pagamentos/lista_pagamentos.html",
        pagamentos=pagamentos,
        total_pago=total_pago
    )


# -------------------------------
# 🔹 Exportar Excel
# -------------------------------
@pagamentos_bp.route("/pagamentos/exportar_excel")
def exportar_excel():
    pagamentos = Pagamento.query.order_by(Pagamento.data_pagamento.desc()).all()
    data = [{
        _("Código"): p.codigo_pagamento,
        _("Valor"): p.valor,
        _("Preço Unitário"): p.preco_unitario,
        _("Tipo de Pagamento"): p.tipo_pagamento,
        _("Data"): p.data_pagamento.strftime("%d/%m/%Y %H:%M") if p.data_pagamento else ""
    } for p in pagamentos]

    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name=str(_("Pagamentos")))
    output.seek(0)

    registrar_acao("exportar_excel_pagamentos", "pagamentos", "")
    return send_file(output, as_attachment=True, download_name="pagamentos.xlsx")

# -------------------------------
# 🔹 Gerar Recibo
# -------------------------------
@pagamentos_bp.route("/pagamentos/recibo/<int:pagamento_id>")
def gerar_recibo(pagamento_id):
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm

    pagamento = Pagamento.query.get_or_404(pagamento_id)
    buffer = BytesIO()
    largura, altura = 80*mm, 200*mm
    pdf = canvas.Canvas(buffer, pagesize=(largura, altura))

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawCentredString(largura/2, altura-10*mm, _("INSTITUIÇÃO EXEMPLO LDA"))
    pdf.setFont("Helvetica", 9)
    pdf.drawCentredString(largura/2, altura-15*mm, _("NUIT: 123456789"))
    pdf.drawCentredString(largura/2, altura-20*mm, _("Rua Exemplo"))
    pdf.drawCentredString(largura/2, altura-25*mm, _("+258 84 123 4567"))
    pdf.line(5*mm, altura-28*mm, largura-5*mm, altura-28*mm)

    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawCentredString(largura/2, altura-35*mm, _("RECIBO DE PAGAMENTO"))

    y = altura - 50*mm
    pdf.setFont("Helvetica", 9)
    pdf.drawString(5*mm, y, f"{_('Código')}: {pagamento.codigo_pagamento}")
    y -= 6*mm
    pdf.drawString(5*mm, y, f"{_('Valor Pago')}: {(pagamento.valor or 0):.2f} MT")
    y -= 6*mm
    pdf.drawString(5*mm, y, f"{_('Preço Unitário')}: {(pagamento.preco_unitario or 0):.2f} MT")
    y -= 6*mm
    pdf.drawString(5*mm, y, f"{_('Método')}: {pagamento.tipo_pagamento or ''}")
    y -= 6*mm
    pdf.drawString(5*mm, y, f"{_('Data')}: {pagamento.data_pagamento.strftime('%d/%m/%Y %H:%M') if pagamento.data_pagamento else ''}")

    pdf.line(5*mm, 25*mm, largura-5*mm, 25*mm)
    pdf.setFont("Helvetica-Oblique", 8)
    pdf.drawCentredString(largura/2, 18*mm, _("Processado por computador"))
    pdf.drawCentredString(largura/2, 12*mm, _("Obrigado pela preferência!"))
    pdf.drawCentredString(largura/2, 6*mm, _("LERP - The Power of Technology"))

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    registrar_acao("gerar_recibo_pagamento", "pagamentos", f"codigo={pagamento.codigo_pagamento}")
    return send_file(buffer, as_attachment=True, download_name=f"recibo_{pagamento.codigo_pagamento}.pdf", mimetype="application/pdf")


@pagamentos_bp.route("/caixa/exportar_pdf", endpoint="exportar_pdf_caixa")
def exportar_pdf_caixa():
    tipo_pag = request.args.get("tipo_pagamento")
    data_inicio = request.args.get("data_inicio")
    data_fim = request.args.get("data_fim")

    # Filtrar pagamentos
    query = Pagamento.query
    if tipo_pag:
        query = query.filter(Pagamento.tipo_pagamento == tipo_pag)

    if data_inicio:
        try:
            dt_ini = datetime.strptime(data_inicio, "%Y-%m-%d")
            query = query.filter(Pagamento.data_pagamento >= dt_ini)
        except:
            pass

    if data_fim:
        try:
            dt_fim = datetime.strptime(data_fim, "%Y-%m-%d")
            dt_fim = dt_fim.replace(hour=23, minute=59, second=59)
            query = query.filter(Pagamento.data_pagamento <= dt_fim)
        except:
            pass

    pagamentos = query.order_by(Pagamento.data_pagamento.desc()).all()

    total_geral = sum(float(p.valor or 0) for p in pagamentos)

    # Criar PDF (igual ao que você já implementou)
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=20, leftMargin=20,
                            topMargin=30, bottomMargin=20)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("Relatório de Folha de Caixa", styles['Title']))
    elements.append(Spacer(1, 12))
    filtros = f"Filtros: Tipo={tipo_pag or 'Todos'}, Início={data_inicio or '---'}, Fim={data_fim or '---'}"
    elements.append(Paragraph(filtros, styles['Normal']))
    elements.append(Spacer(1, 12))

    cabecalho = ["Código", "Valor (MT)", "Preço Unitário (MT)", "Tipo de Pagamento", "Data Pagamento"]
    data = [cabecalho]
    for p in pagamentos:
        data.append([
            p.codigo_pagamento,
            f"{float(p.valor or 0):.2f}",
            f"{float(p.preco_unitario or 0):.2f}",
            p.tipo_pagamento or "",
            p.data_pagamento.strftime("%d/%m/%Y %H:%M") if p.data_pagamento else ""
        ])
    data.append(["", f"TOTAL: {total_geral:.2f} MT", "", "", ""])

    tabela = Table(data, repeatRows=1, hAlign='CENTER')
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0b4f8a")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.7, colors.grey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BACKGROUND', (0,-1), (-1,-1), colors.lightgrey),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold')
    ]))

    elements.append(tabela)
    doc.build(elements)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="folha_caixa.pdf",
        mimetype="application/pdf"
    )
