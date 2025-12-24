class Item:
    def __init__(self, produto, quantidade):
        self.produto = produto
        self.preco = produto.preco
        self.quantidade = quantidade
        self.subtotal = self.preco * self.quantidade
