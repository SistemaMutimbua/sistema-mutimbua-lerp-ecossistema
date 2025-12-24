from modulos.extensions import db
from datetime import datetime

class Pagamento(db.Model):
    __tablename__ = 'pagamentos'
    id = db.Column(db.Integer, primary_key=True)
    codigo_pagamento = db.Column(db.String(20), unique=True, nullable=False)
    valor = db.Column(db.Float, nullable=False)
    preco_unitario = db.Column(db.Float, nullable=False, default=0.0)
    tipo_pagamento = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.String(255), nullable=True)

    
    # Preenche automaticamente a data de registro ao criar o objeto
    data = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Pode ser preenchida pelo usuário ou automaticamente
    data_pagamento = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Se futuramente quiser vincular a uma venda:
    # venda_id = db.Column(db.Integer, db.ForeignKey("vendas.id"), nullable=True)
    # venda = db.relationship("Venda", backref="pagamentos")

    def __repr__(self):
        return f"<Pagamento {self.codigo_pagamento} - {self.valor:.2f}>"

    def to_dict(self):
        return {
            "id": self.id,
            "codigo_pagamento": self.codigo_pagamento,
            "valor": self.valor,
            "preco_unitario": self.preco_unitario,
            "tipo_pagamento": self.tipo_pagamento,
            "data_pagamento": self.data_pagamento.isoformat()
        }


class FolhaCaixa(db.Model):
    __tablename__ = 'folha_caixa'

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    tipo_pagamento = db.Column(db.String(50), nullable=False, default="Todos")
    total_entrada = db.Column(db.Float, nullable=False, default=0.0)
    total_saida = db.Column(db.Float, nullable=False, default=0.0)
    detalhes = db.Column(db.String(200), nullable=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<FolhaCaixa {self.data} - Entrada: {self.total_entrada:.2f}>"
