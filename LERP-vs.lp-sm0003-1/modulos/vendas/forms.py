# modulos/vendas/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange

class VendaForm(FlaskForm):
    # Código do produto
    codigo_produto = StringField(
        "Código do Produto",
        validators=[DataRequired()]
    )

    # Nome do produto
    produto = StringField(
        "Produto",
        validators=[DataRequired()]
    )

    # Quantidade
    quantidade = IntegerField(
        "Quantidade",
        validators=[DataRequired(), NumberRange(min=1)]
    )

    # Preço unitário
    preco_unitario = DecimalField(
        "Preço Unitário",
        validators=[DataRequired()]
    )

    # Método de pagamento (opcional no formulário principal, usado no modal)
    metodo_pagamento = SelectField(
        "Método de Pagamento",
        choices=[("dinheiro", "Dinheiro"), ("cartao", "Cartão"), ("transferencia", "Transferência")]
    )

    # Botão de adicionar produto
    submit = SubmitField("Adicionar Produto")
