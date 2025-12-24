from datetime import datetime
from modulos.extensions import db

# =============================
# PRODUTO AVULSO
# =============================
class ProdutoAvulso(db.Model):
    __tablename__ = 'produtos_avulsos'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(12), unique=True, nullable=False)
    descricao = db.Column(db.String(150), nullable=False)
    preco = db.Column(db.Float, nullable=False, default=0.0)
    unidade = db.Column(db.String(20), default='unidade')
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_edicao = db.Column(db.DateTime, onupdate=datetime.utcnow)

    entradas = db.relationship('EntradaAvulsa', backref='produto', lazy=True)
    vendas = db.relationship('VendaAvulsa', backref='produto', lazy=True)

    @property
    def total_vendido(self):
        return sum(v.valor_total for v in self.vendas)

    def __repr__(self):
        return f"<ProdutoAvulso {self.codigo} - {self.descricao}>"

# =============================
# ENTRADA AVULSA
# =============================
class EntradaAvulsa(db.Model):
    __tablename__ = 'entradas_produtos_avulsos'

    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos_avulsos.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False, default=1)
    custo_unitario = db.Column(db.Float, nullable=False, default=0.0)
    custo_total = db.Column(db.Float, nullable=False, default=0.0)
    fornecedor = db.Column(db.String(120), nullable=True)
    data_entrada = db.Column(db.DateTime, default=datetime.utcnow)

    def calcular_custo_total(self):
        return self.quantidade * self.custo_unitario

    def __repr__(self):
        return f"<EntradaAvulsa Produto={self.produto_id} Quantidade={self.quantidade}>"

# =============================
# VENDA AVULSA
# =============================
class VendaAvulsa(db.Model):
    __tablename__ = 'vendas_produtos_avulsos'

    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos_avulsos.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False, default=1)
    preco_unitario = db.Column(db.Float, nullable=False, default=0.0)
    valor_total = db.Column(db.Float, nullable=False, default=0.0)
    valor_unitario = db.Column(db.Float, nullable=False)

    metodo_pagamento = db.Column(db.String(50), nullable=False)
    cliente = db.Column(db.String(120), nullable=True)
    data_venda = db.Column(db.DateTime, default=datetime.utcnow)
    lucro_estimado = db.Column(db.Float, nullable=False, default=0.0)

    def calcular_valor_total(self):
        return self.quantidade * self.preco_unitario

    def __repr__(self):
        return f"<VendaAvulsa Produto={self.produto_id} Valor={self.valor_total}>"
