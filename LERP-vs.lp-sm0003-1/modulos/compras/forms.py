from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    IntegerField,
    DecimalField,
    SubmitField
)
from wtforms.validators import DataRequired, NumberRange, ValidationError
from modulos.produtos.models import Produto


class CompraForm(FlaskForm):

    codigo_produto = StringField(
        "Código do Produto",
        validators=[DataRequired()]
    )

    produto = StringField(
        "Produto",
        validators=[DataRequired()]
    )

    quantidade = IntegerField(
        "Quantidade",
        validators=[DataRequired(), NumberRange(min=1)]
    )

    preco_compra = DecimalField(
        "Preço de Compra",
        validators=[DataRequired()]
    )

    preco_venda = DecimalField(
        "Preço de Venda",
        validators=[DataRequired()]
    )

    categoria = StringField("Categoria")

    valor_total = DecimalField(
        "Valor Total",
        validators=[DataRequired()]
    )

    submit = SubmitField("Registrar Compra")

    # 🔐 Validação crítica
    def validate_codigo_produto(self, field):
        produto = Produto.query.filter_by(codigo=field.data).first()
        if not produto:
            raise ValidationError("Produto inválido ou inexistente.")
