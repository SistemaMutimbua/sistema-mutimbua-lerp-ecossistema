from flask_wtf import FlaskForm
from wtforms import FloatField, StringField, SubmitField
from wtforms.validators import DataRequired, Length

class SaidaForm(FlaskForm):
    valor = FloatField("Valor", validators=[DataRequired()])
    justificativa = StringField("Justificativa", validators=[DataRequired(), Length(min=5)])
    submit = SubmitField("Registrar Saída")
