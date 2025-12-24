from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class CotacaoForm(FlaskForm):
    cliente = StringField("Cliente", validators=[DataRequired()])
    submit = SubmitField("Salvar Cotação")
