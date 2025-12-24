from modulos.extensions import db
from datetime import datetime

# ================================
# 🧾 Venda
# ================================
class Venda(db.Model):
    __tablename__ = "vendas"

    id = db.Column(db.Integer, primary_key=True)
    codigo_venda = db.Column(db.String(50), unique=True, nullable=False)
    data_venda = db.Column(db.DateTime, default=datetime.now)
    total_valor = db.Column(db.Float, default=0.0)
    total_lucro = db.Column(db.Float, default=0.0)
    produto = db.Column(db.String(200), nullable=False)
    quantidade = db.Column(db.Float, nullable=False)
   
    # Relacionamento com itens da venda
    itens = db.relationship("VendaItem", backref="venda", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Venda {self.codigo_venda} - Total: {self.total_valor:.2f}>"


# ================================
# 🛒 Item da Venda
# ================================
class VendaItem(db.Model):
    __tablename__ = "venda_itens"

    id = db.Column(db.Integer, primary_key=True)
    venda_id = db.Column(db.Integer, db.ForeignKey("vendas.id"), nullable=False)
    produto_id = db.Column(db.Integer, nullable=False)
    codigo_produto = db.Column(db.String(50), nullable=False)
    produto = db.Column(db.String(200), nullable=False)
    quantidade = db.Column(db.Integer, default=1)
    preco_unitario = db.Column(db.Float, default=0.0)
    valor_total = db.Column(db.Float, default=0.0)
    lucro_total = db.Column(db.Float, default=0.0)

    def __repr__(self):
        return f"<VendaItem {self.produto} x {self.quantidade} - Total: {self.valor_total:.2f}>"
