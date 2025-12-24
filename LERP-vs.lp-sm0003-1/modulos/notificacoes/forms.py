from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

class NotificacaoForm(FlaskForm):
    titulo = StringField("Título", validators=[DataRequired(), Length(max=100)])
    mensagem = TextAreaField("Mensagem", validators=[DataRequired()])
    tipo = SelectField(
        "Tipo",
        choices=[("info", "Info"), ("alerta", "Alerta"), ("sucesso", "Sucesso")],
        validators=[DataRequired()]
    )
    submit = SubmitField("Salvar")
