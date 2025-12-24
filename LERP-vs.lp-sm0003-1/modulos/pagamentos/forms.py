from flask import render_template, redirect, url_for, request, flash
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Optional
from . import pagamentos_bp
from .models import Pagamento  # Assumindo que você tem um modelo Pagamento
from modulos.extensions import db  # Para a conexão com o banco de dados

class PagamentoForm(FlaskForm):
    codigo_pagamento = StringField("Código Pagamento", validators=[DataRequired()])
    preco_unitario = FloatField("Valor (MT)", validators=[DataRequired()])
    tipo_pagamento = SelectField(
        "Tipo de Pagamento",
        choices=[
            ("mpesa", "Mpesa"),
            ("emola", "Emola"),
            ("cash", "Cash"),
            ("pos", "POS"),
            ("banco", "Banco")
        ],
        validators=[DataRequired()]
    )
    descricao = TextAreaField("Descrição", validators=[Optional()])

