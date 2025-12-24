from flask import (
    render_template, redirect, url_for, flash, request, send_file, session
)
from flask_babel import gettext as _
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import json
import pandas as pd

from . import cotacoes_bp
from modulos.extensions import db
from modulos.produtos.models import Produto
from modulos.vendas.models import Venda
from .models import Cotacao
from .forms import CotacaoForm


# ================================
# ➕ NOVA COTAÇÃO
# ================================
@cotacoes_bp.route("/nova", methods=["GET", "POST"])
def nova_cotacao():
    form = CotacaoForm()
    if request.method == "POST":
        cliente = request.form.get("cliente")
        itens_json = request.form.get("itens")

        if not cliente:
            flash(_("Informe o cliente da cotação."), "danger")
            return redirect(url_for("cotacoes.nova_cotacao"))

        if not itens_json:
            flash(_("Adicione pelo menos um item à cotação."), "danger")
            return redirect(url_for("cotacoes.nova_cotacao"))

        try:
            itens = json.loads(itens_json)
        except json.JSONDecodeError:
            flash(_("Erro ao processar os itens da cotação."), "danger")
            return redirect(url_for("cotacoes.nova_cotacao"))

        total_valor = sum(item["preco_unitario"] * item["quantidade"] for item in itens)

        cotacao = Cotacao(cliente=cliente, total_valor=total_valor, status="rascunho")
        cotacao.itens = itens

        db.session.add(cotacao)
        db.session.commit()

        flash(_("Cotação salva com sucesso."), "success")
        return redirect(url_for("cotacoes.listar_cotacoes"))

    return render_template("cotacoes/nova.html", form=form)


# ================================
# 📋 LISTAR COTAÇÕES
# ================================
@cotacoes_bp.route("/")
def listar_cotacoes():
    cotacoes = Cotacao.query.order_by(Cotacao.data_cotacao.desc()).all()
    return render_template("cotacoes/listar.html", cotacoes=cotacoes)


# ================================
# ✏️ EDITAR COTAÇÃO
# ================================
@cotacoes_bp.route("/editar/<int:cotacao_id>", methods=["GET", "POST"])
def editar_cotacao(cotacao_id):
    cotacao = Cotacao.query.get_or_404(cotacao_id)

    if cotacao.status != "rascunho":
        flash(_("Cotação já convertida em venda."), "warning")
        return redirect(url_for("cotacoes.listar_cotacoes"))

    form = CotacaoForm(obj=cotacao)
    produtos = Produto.query.order_by(Produto.nome).all()

    if form.validate_on_submit():
        itens_json = request.form.get("itens")
        if not itens_json:
            flash(_("A cotação precisa ter itens."), "danger")
            return redirect(url_for("cotacoes.editar_cotacao", cotacao_id=cotacao.id))

        itens = json.loads(itens_json)
        total_valor = sum(item["subtotal"] for item in itens)

        cotacao.cliente = form.cliente.data
        cotacao.itens = itens
        cotacao.total_valor = total_valor

        db.session.commit()
        flash(_("Cotação atualizada."), "success")
        return redirect(url_for("cotacoes.listar_cotacoes"))

    return render_template("cotacoes/editar.html", cotacao=cotacao, form=form, produtos=produtos)


# ================================
# 🗑️ EXCLUIR COTAÇÃO
# ================================
@cotacoes_bp.route("/excluir/<int:cotacao_id>", methods=["POST"])
def excluir_cotacao(cotacao_id):
    cotacao = Cotacao.query.get_or_404(cotacao_id)

    if cotacao.status != "rascunho":
        flash(_("Não é possível excluir cotação convertida."), "danger")
        return redirect(url_for("cotacoes.listar_cotacoes"))

    db.session.delete(cotacao)
    db.session.commit()
    flash(_("Cotação excluída."), "success")
    return redirect(url_for("cotacoes.listar_cotacoes"))


# ================================
# 🔗 ABRIR NA VENDA
# ================================
@cotacoes_bp.route("/abrir-venda/<int:cotacao_id>")
def abrir_na_venda(cotacao_id):
    cotacao = Cotacao.query.get_or_404(cotacao_id)

    if cotacao.status != "rascunho":
        flash(_("Esta cotação já foi utilizada."), "warning")
        return redirect(url_for("cotacoes.listar_cotacoes"))

    session["carrinho_venda"] = cotacao.itens
    cotacao.status = "convertida"
    db.session.commit()

    flash(_("Cotação carregada na venda."), "info")
    return redirect(url_for("vendas.nova_venda"))


# ================================
# 🧾 GERAR PDF DA COTAÇÃO
# ================================
@cotacoes_bp.route("/pdf/<int:cotacao_id>")
def gerar_pdf(cotacao_id):
    cotacao = Cotacao.query.get_or_404(cotacao_id)

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    y = 800

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "COTAÇÃO")
    y -= 30

    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, y, f"Cliente: {cotacao.cliente}")
    y -= 20
    pdf.drawString(50, y, f"Data: {cotacao.data_cotacao.strftime('%d/%m/%Y %H:%M')}")
    y -= 30

    for i, item in enumerate(cotacao.itens, 1):
        pdf.drawString(
            50,
            y,
            f"{i}. {item['nome']} | Qtd: {item['quantidade']} | "
            f"Preço: {item['preco_unitario']:.2f} | "
            f"Subtotal: {item['subtotal']:.2f}"
        )
        y -= 15

    y -= 20
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, f"TOTAL: {cotacao.total_valor:.2f}")

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name=f"Cotacao_{cotacao.id}.pdf", mimetype="application/pdf")


# ================================
# 📊 EXPORTAR EXCEL DA COTAÇÃO
# ================================
@cotacoes_bp.route("/excel/<int:cotacao_id>")
def gerar_excel(cotacao_id):
    cotacao = Cotacao.query.get_or_404(cotacao_id)

    data = []
    for item in cotacao.itens:
        data.append({
            "Produto": item["nome"],
            "Quantidade": item["quantidade"],
            "Preço Unitário": item["preco_unitario"],
            "Subtotal": item["subtotal"]
        })

    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Cotacao")
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name=f"Cotacao_{cotacao.id}.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
