from flask import render_template, redirect, url_for, flash, request
from datetime import datetime, timedelta
from flask_babel import gettext as _
from flask_login import current_user

from modulos.extensions import db
from . import caixa_bp
from .models import Caixa
from .forms import SaidaForm
from modulos.pagamentos.models import Pagamento
from modulos.auditoria.utils import registrar_acao


# -------------------------------------------------------------------
# --- REGISTRAR SAÍDA ---
# -------------------------------------------------------------------
@caixa_bp.route("/caixa/saida", methods=["GET", "POST"])
def nova_saida():
    form = SaidaForm()

    if form.validate_on_submit():

        saida = Caixa(
            tipo="saida",
            valor=form.valor.data,
            justificativa=form.justificativa.data
        )

        db.session.add(saida)
        db.session.commit()

        # 🔹 Registrar auditoria
        registrar_acao(
            acao="Registrar saída",
            modulo="caixa",
            detalhes=f"Valor: {saida.valor} MT | Justificativa: {saida.justificativa}"
        )

        flash(
            _("Saída de %(valor).2f MT registrada com sucesso.", valor=saida.valor),
            "success"
        )

        return redirect(url_for("caixa.lista_caixa"))

    # 🔹 Registrar auditoria ao acessar formulário
    registrar_acao(
        acao="Acessou formulário de nova saída",
        modulo="caixa"
    )

    return render_template(
        "caixa/nova_saida.html",
        form=form,
        titulo=_("Registrar Saída")
    )


# -------------------------------------------------------------------
# --- LISTAR CAIXA ---
# -------------------------------------------------------------------
@caixa_bp.route("/caixa")
def lista_caixa():

    # Entradas: caixa + pagamentos
    entradas_caixa = db.session.query(Caixa.valor).filter(Caixa.tipo == "entrada").all()
    entradas_pagamentos = db.session.query(Pagamento.valor).all()

    total_entradas = sum(v[0] for v in entradas_caixa) + sum(v[0] for v in entradas_pagamentos)

    # Saídas
    saidas = Caixa.query.filter_by(tipo="saida").all()
    total_saidas = sum(s.valor for s in saidas)

    # Saldo total geral
    saldo = total_entradas - total_saidas

    # ---------------- FILTRAR POR PERÍODO ----------------
    periodo = request.args.get("periodo", "hoje")
    agora = datetime.utcnow()

    if periodo == "hoje":
        data_inicio = datetime(agora.year, agora.month, agora.day)
        nome_periodo = _("Hoje")

    elif periodo == "semana":
        data_inicio = agora - timedelta(days=agora.weekday())
        data_inicio = datetime(data_inicio.year, data_inicio.month, data_inicio.day)
        nome_periodo = _("Esta Semana")

    elif periodo == "mes":
        data_inicio = datetime(agora.year, agora.month, 1)
        nome_periodo = _("Este Mês")

    elif periodo == "ano":
        data_inicio = datetime(agora.year, 1, 1)
        nome_periodo = _("Este Ano")

    else:
        data_inicio = None
        nome_periodo = _("Todos os Registos")

    # ---------------- CALCULAR SALDOS POR PERÍODO ----------------
    if data_inicio:
        entradas_pagamentos_periodo = db.session.query(Pagamento.valor).filter(
            Pagamento.data_pagamento >= data_inicio
        ).all()

        saidas_periodo = Caixa.query.filter(
            Caixa.tipo == "saida",
            Caixa.data >= data_inicio
        ).all()

        total_entradas_periodo = sum(v[0] for v in entradas_pagamentos_periodo)
        total_saidas_periodo = sum(s.valor for s in saidas_periodo)
        saldo_periodo = total_entradas_periodo - total_saidas_periodo

    else:
        total_entradas_periodo = total_entradas
        total_saidas_periodo = total_saidas
        saldo_periodo = saldo

    # 🔹 Registrar auditoria – acesso ao relatório
    registrar_acao(
        acao="Visualizou relatório do caixa",
        modulo="caixa",
        detalhes=f"Período selecionado: {periodo}"
    )

    return render_template(
        "caixa/lista_caixa.html",
        entradas=total_entradas_periodo,
        saidas=total_saidas_periodo,
        saldo=saldo_periodo,
        periodo=periodo,
        nome_periodo=nome_periodo,
        lista_saidas=saidas,
        titulo=_("Movimentações do Caixa")
    )
