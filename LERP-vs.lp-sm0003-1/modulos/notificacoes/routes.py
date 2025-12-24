from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from modulos.extensions import db
from modulos.auditoria.utils import registrar_acao
from .models import Notificacao
from .forms import NotificacaoForm

notificacoes_bp = Blueprint("notificacoes", __name__, url_prefix="/notificacoes")


# ========================================
# LISTA NOTIFICAÇÕES
# ========================================
@notificacoes_bp.route("/")
#@login_required
def lista_notificacoes():
    notificacoes = Notificacao.query.order_by(Notificacao.data.desc()).all()

    # Auditoria: registra ação do usuário
    try:
        registrar_acao(
            usuario=getattr(current_user, "username", "Anônimo"),
            acao="Visualizou a lista de notificações",
            modulo="Notificações"
        )
    except Exception:
        pass

    return render_template(
        "notificacoes/lista.html",
        notificacoes=notificacoes,
        titulo_pagina="Notificações"
    )


# ========================================
# CRIAR NOTIFICAÇÃO
# ========================================
@notificacoes_bp.route("/criar", methods=["GET", "POST"])
#@login_required
def criar_notificacao():
    form = NotificacaoForm()

    if form.validate_on_submit():
        nova = Notificacao(
            titulo=form.titulo.data,
            mensagem=form.mensagem.data,
            tipo=form.tipo.data,
        )

        try:
            db.session.add(nova)
            db.session.commit()
            flash("Notificação criada com sucesso!", "success")

            # Auditoria
            try:
                registrar_acao(
                    usuario=getattr(current_user, "username", "Anônimo"),
                    acao=f"Criou uma nova notificação ({nova.titulo})",
                    modulo="Notificações"
                )
            except Exception:
                pass

            return redirect(url_for("notificacoes.lista_notificacoes"))

        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao criar notificação: {e}", "danger")

    return render_template(
        "notificacoes/criar.html",
        form=form,
        titulo_pagina="Criar Notificação"
    )


# ========================================
# APAGAR NOTIFICAÇÃO
# ========================================
@notificacoes_bp.route("/apagar/<int:id>", methods=["POST", "GET"])
#@login_required
def apagar_notificacao(id):
    notif = Notificacao.query.get_or_404(id)

    try:
        db.session.delete(notif)
        db.session.commit()
        flash("Notificação removida com sucesso.", "success")

        # Auditoria
        try:
            registrar_acao(
                usuario=getattr(current_user, "username", "Anônimo"),
                acao=f"Apagou notificação ({notif.titulo})",
                modulo="Notificações"
            )
        except Exception:
            pass

    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao apagar notificação: {e}", "danger")
        try:
            registrar_acao(
                usuario=getattr(current_user, "username", "Anônimo"),
                acao=f"Erro ao apagar notificação ({notif.titulo})",
                modulo="Notificações"
            )
        except Exception:
            pass

    return redirect(url_for("notificacoes.lista_notificacoes"))
