from flask import render_template, redirect, url_for, flash, request, send_file, session, jsonify
from io import BytesIO
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime, timedelta
from flask_babel import _
from modulos.extensions import db
from . import vendas_bp
from .models import Venda, VendaItem        # ✅ apenas os modelos de vendas
from modulos.produtos.models import Produto  # ✅ import do Produto
from .forms import VendaForm
from sqlalchemy import func, or_
from modulos.cotacoes.models import Cotacao  # import local




# -----------------------------
# Auditoria
# -----------------------------
try:
    from modulos.auditoria.utils import registrar_acao
except Exception:
    def registrar_acao(acao, modulo="vendas", detalhes=""):
        return

# ================================
# Classe Item para carrinho


@vendas_bp.route("/vendas/buscar_produtos")
def buscar_produtos():
    termo = request.args.get("q", "").strip()
    if not termo:
        return jsonify([])

    # Busca por nome ou código
    produtos = Produto.query.filter(
        or_(Produto.nome.ilike(f"%{termo}%"), Produto.codigo.ilike(f"%{termo}%"))
    ).all()

    resultado = []
    for p in produtos:
        resultado.append({
            "id": p.id,
            "nome": p.nome,
            "codigo": p.codigo,
            "preco": float(p.preco)
        })

    return jsonify(resultado)

# ================================
# Criar venda a partir da cotação
# ================================
@vendas_bp.route("/criar_venda_a_partir_cotacao/<int:cotacao_id>")
def criar_venda_a_partir_cotacao(cotacao_id):
    from modulos.cotacoes.models import Cotacao

    cotacao = Cotacao.query.get(cotacao_id)
    if not cotacao:
        flash("Cotação não encontrada.", "danger")
        return redirect(url_for("cotacoes.listar_cotacoes"))

    carrinho_venda = []
    for item in cotacao.itens:
        carrinho_venda.append({
            "produto_id": item["produto_id"],
            "quantidade": item["quantidade"]
        })

    session["carrinho_venda"] = carrinho_venda
    flash("Cotação carregada no carrinho de venda.", "success")
    return redirect(url_for("vendas.nova_venda"))

# ================================
# Nova venda
# ================================

def init_carrinho():
    if "carrinho_venda" not in session:
        session["carrinho_venda"] = []

@vendas_bp.route("/nova", methods=["GET", "POST"])
def nova_venda():
    form = VendaForm()
    init_carrinho()
    carrinho = session["carrinho_venda"]

    # Converter carrinho em objetos Item para o template
    itens_obj = []
    for item_dict in carrinho:
        produto = Produto.query.get(item_dict["produto_id"])
        if produto:
            itens_obj.append(Item(produto, item_dict["quantidade"]))

    # Preparar lista de produtos para autocomplete
    produtos = Produto.query.all()
    produtos_data = []
    for p in produtos:
        produtos_data.append({
            "id": p.id,
            "codigo": p.codigo,
            "nome": p.nome,
            "preco_venda": float(p.preco_venda or 0),
            "categoria": p.categoria or ""
        })

    # Adicionar produto via formulário
    if form.validate_on_submit():
        produto = Produto.query.filter_by(codigo=form.codigo_produto.data).first()
        if not produto:
            flash("Produto não encontrado.", "danger")
            return redirect(url_for("vendas.nova_venda"))

        # Verificar se produto já existe no carrinho
        encontrado = False
        for item in carrinho:
            if item["produto_id"] == produto.id:
                item["quantidade"] += form.quantidade.data
                encontrado = True
                break
        if not encontrado:
            carrinho.append({
                "produto_id": produto.id,
                "quantidade": form.quantidade.data
            })

        session["carrinho_venda"] = carrinho
        flash(f"{produto.nome} adicionado ao carrinho.", "success")
        return redirect(url_for("vendas.nova_venda"))

    return render_template(
        "vendas/nova_venda.html",
        form=form,
        itens=itens_obj,
        produtos=produtos_data
    )


# ================================
# Adicionar item via Ajax
# ================================
@vendas_bp.route("/vendas/adicionar_item", methods=["POST"])
def adicionar_item():
    init_carrinho()
    data = request.get_json()
    codigo = data.get("codigo")
    quantidade = int(data.get("quantidade", 1))

    produto = Produto.query.filter_by(codigo=codigo).first()
    if not produto:
        return jsonify({"error": _("Produto não encontrado")})

    carrinho = session["carrinho_venda"]

    # Se já existe, soma a quantidade
    for item in carrinho:
        if item["produto_id"] == produto.id:
            item["quantidade"] += quantidade
            break
    else:
        carrinho.append({"produto_id": produto.id, "quantidade": quantidade})

    session["carrinho_venda"] = carrinho
    return jsonify({"carrinho": carrinho})

# ================================
# Remover item do carrinho
# ================================
@vendas_bp.route("/vendas/remover_item/<int:produto_id>")
def remover_item(produto_id):
    init_carrinho()
    carrinho = session["carrinho_venda"]
    carrinho = [item for item in carrinho if item["produto_id"] != produto_id]
    session["carrinho_venda"] = carrinho
    flash("Item removido do carrinho.", "success")
    return redirect(url_for("vendas.nova_venda"))

# ================================
# Finalizar venda
# ================================
@vendas_bp.route("/finalizar_venda", methods=["POST"])
def finalizar_venda():
    init_carrinho()
    carrinho = session.get("carrinho_venda", [])
    if not carrinho:
        flash("O carrinho está vazio. Adicione pelo menos um produto.", "danger")
        return redirect(url_for("vendas.nova_venda"))

    nova_venda = Venda(
        codigo_venda=f"V{int(datetime.now().timestamp())}",
        data_venda=datetime.now(),
        total_valor=0.0
    )
    db.session.add(nova_venda)
    db.session.flush()

    total = 0.0
    for item in carrinho:
        produto = Produto.query.get(item['produto_id'])
        quantidade = item['quantidade']
        if not produto:
            continue
        subtotal = produto.preco * quantidade
        total += subtotal

        item_venda = ItemVenda(
            venda_id=nova_venda.id,
            produto_id=produto.id,
            quantidade=quantidade,
            preco_unitario=produto.preco,
            subtotal=subtotal
        )
        db.session.add(item_venda)

    nova_venda.total_valor = total
    db.session.commit()
    session.pop("carrinho_venda", None)
    flash(f"Venda {nova_venda.codigo_venda} finalizada com sucesso! Total: {total:.2f} MZN", "success")
    return redirect(url_for("vendas.lista_vendas"))

# ================================
# Lista de vendas
# ================================
@vendas_bp.route("/vendas")
def lista_vendas():
    filtro = request.args.get("filtro", "").strip()
    query = Venda.query
    if filtro:
        query = query.filter(Venda.codigo_venda.ilike(f"%{filtro}%"))

    vendas = query.order_by(Venda.data_venda.desc()).all()
    total_vendas = sum(v.total_valor for v in vendas)
    total_lucro = sum(getattr(v, 'total_lucro', 0) for v in vendas)

    registrar_acao("Acessou lista de vendas", "vendas", detalhes=f"Filtro: {filtro}")

    return render_template("vendas/lista_vendas.html",
                           vendas=vendas,
                           total_vendas=total_vendas,
                           total_lucro=total_lucro)







@vendas_bp.route("/dashboard")
def dashboard_vendas():
    hoje = datetime.today().date()

    # Totais gerais
    total_vendas = db.session.query(func.sum(Venda.total_valor)).scalar() or 0
    total_lucro = db.session.query(func.sum(Venda.total_lucro)).scalar() or 0

    # Vendas do dia
    vendas_hoje = db.session.query(func.sum(Venda.total_valor))\
        .filter(func.date(Venda.data_venda) == hoje).scalar() or 0
    lucro_hoje = db.session.query(func.sum(Venda.total_lucro))\
        .filter(func.date(Venda.data_venda) == hoje).scalar() or 0

    # Últimas 5 vendas
    ultimas_vendas = Venda.query.order_by(Venda.data_venda.desc()).limit(5).all()

    # ======= Gráfico últimos 30 dias =======
    dias = [hoje - timedelta(days=i) for i in reversed(range(30))]
    chart_labels = [d.strftime("%d/%m") for d in dias]
    chart_vendas = []
    chart_lucro = []

    for d in dias:
        soma_vendas = db.session.query(func.sum(Venda.total_valor))\
            .filter(func.date(Venda.data_venda) == d).scalar() or 0
        soma_lucro = db.session.query(func.sum(Venda.total_lucro))\
            .filter(func.date(Venda.data_venda) == d).scalar() or 0
        chart_vendas.append(round(soma_vendas, 2))
        chart_lucro.append(round(soma_lucro, 2))

    registrar_acao("Acessou dashboard de vendas", "vendas")

    return render_template(
        "vendas/dashboard_vendas.html",
        total_vendas=round(total_vendas, 2),
        total_lucro=round(total_lucro, 2),
        vendas_hoje=round(vendas_hoje, 2),
        lucro_hoje=round(lucro_hoje, 2),
        ultimas_vendas=ultimas_vendas,
        chart_labels=chart_labels,
        chart_vendas=chart_vendas,
        chart_lucro=chart_lucro
    )











@vendas_bp.route("/vendas/exportar/pdf")
def exportar_pdf():
    vendas = Venda.query.order_by(Venda.data_venda.desc()).all()

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4

    y = altura - 50
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(largura / 2, y, _("Relatório de Vendas - LERP Management"))
    y -= 30

    pdf.setFont("Helvetica", 9)
    pdf.drawString(40, y, _("Gerado em: ") + datetime.now().strftime("%d/%m/%Y %H:%M"))
    y -= 25

    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(40, y, _("Código"))
    pdf.drawString(120, y, _("Data"))
    pdf.drawString(220, y, _("Total (MT)"))
    pdf.drawString(300, y, _("Lucro (MT)"))
    y -= 15

    pdf.setFont("Helvetica", 9)
    total_geral = 0
    total_lucro = 0

    for v in vendas:
        pdf.drawString(40, y, v.codigo_venda)
        pdf.drawString(120, y, v.data_venda.strftime("%d/%m/%Y"))
        pdf.drawString(220, y, f"{v.total_valor:.2f}")
        pdf.drawString(300, y, f"{getattr(v, 'lucro_total', 0):.2f}")  # caso não tenha lucro
        total_geral += v.total_valor
        total_lucro += getattr(v, 'lucro_total', 0)
        y -= 14
        if y < 60:
            pdf.showPage()
            pdf.setFont("Helvetica", 9)
            y = altura - 50

    y -= 10
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(40, y, _("Total Vendas: ") + f"{total_geral:.2f} MT")
    y -= 15
    pdf.drawString(40, y, _("Total Lucro: ") + f"{total_lucro:.2f} MT")

    pdf.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="vendas.pdf", mimetype="application/pdf")



@vendas_bp.route("/vendas/exportar/excel")
def exportar_excel():
    vendas = Venda.query.order_by(Venda.data_venda.desc()).all()

    data = []
    for v in vendas:
        data.append({
            "Código": v.codigo_venda,
            "Data": v.data_venda.strftime("%d/%m/%Y %H:%M"),
            "Total": v.total_valor,
            "Lucro": getattr(v, 'total_lucro', 0)  # caso não tenha lucro
        })

    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Vendas")
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="vendas.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )




