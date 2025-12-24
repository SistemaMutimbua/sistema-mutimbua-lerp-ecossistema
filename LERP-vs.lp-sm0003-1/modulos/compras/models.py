# modulos/compras/models.py

from modulos.extensions import db
from datetime import datetime


class Compra(db.Model):
    __tablename__ = "compras"

    id = db.Column(db.Integer, primary_key=True)

    codigo_produto = db.Column(db.String(20), nullable=False)
    produto = db.Column(db.String(100), nullable=False)

    preco_compra = db.Column(db.Float, nullable=False)
    preco_venda = db.Column(db.Float, nullable=False)

    quantidade = db.Column(db.Float, nullable=False)

    # Valores calculados
    valor_total = db.Column(db.Float, nullable=False)
    margem_lucro = db.Column(db.Float, nullable=False)
    lucro_total = db.Column(db.Float, nullable=False)

    fornecedor = db.Column(db.String(100))
    categoria = db.Column(db.String(50), nullable=True)

    data_compra = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    def __repr__(self):
        return (
            f"<Compra {self.produto} | "
            f"Qtd: {self.quantidade} | "
            f"Lucro: {self.lucro_total}>"
        )


# =========================================================
# 📉 HISTÓRICO DE CUSTO DO PRODUTO
# =========================================================
class HistoricoCustoProduto(db.Model):
    __tablename__ = "historico_custo_produto"

    id = db.Column(db.Integer, primary_key=True)

    produto_codigo = db.Column(
        db.String(20),
        nullable=False
    )

    custo = db.Column(
        db.Float,
        nullable=False
    )

    quantidade = db.Column(
        db.Integer,
        nullable=False
    )

    data_registo = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    def __repr__(self):
        return (
            f"<HistoricoCusto "
            f"{self.produto_codigo} | "
            f"Custo: {self.custo} | "
            f"Qtd: {self.quantidade}>"
        )
