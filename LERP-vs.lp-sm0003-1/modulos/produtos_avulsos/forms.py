from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange, Length

# =====================================
# FORMULÁRIO PRODUTO AVULSO
# =====================================
class ProdutoAvulsoForm(FlaskForm):
    codigo = StringField('Código', validators=[DataRequired(), Length(max=12)])
    descricao = StringField('Descrição', validators=[DataRequired(), Length(max=150)])
    preco = FloatField('Preço', validators=[DataRequired(), NumberRange(min=0)])
    unidade = StringField('Unidade', default='unidade')
    submit = SubmitField('Salvar')


# =====================================
# FORMULÁRIO ENTRADA DE PRODUTO AVULSO
# =====================================
class EntradaAvulsoForm(FlaskForm):
    quantidade = IntegerField('Quantidade', validators=[DataRequired(), NumberRange(min=1)])
    custo_unitario = FloatField('Custo Unitário', validators=[DataRequired(), NumberRange(min=0)])
    fornecedor = StringField('Fornecedor', validators=[Length(max=120)])
    submit = SubmitField('Registrar Entrada')


# =====================================
# FORMULÁRIO VENDA DE PRODUTO AVULSO
# =====================================
class VendaAvulsoForm(FlaskForm):
    quantidade = IntegerField('Quantidade', validators=[DataRequired(), NumberRange(min=1)])
    cliente = StringField('Cliente', validators=[Length(max=120)])
    metodo_pagamento = SelectField('Método de Pagamento', choices=[
        ('dinheiro', 'Dinheiro'),
        ('mpesa', 'Mpesa'),
        ('cartao', 'Cartão')
    ], validators=[DataRequired()])
    submit = SubmitField('Registrar Venda')
