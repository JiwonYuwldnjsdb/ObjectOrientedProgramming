class Product:
    tax_rate = 0.1
    
    def __init__(self, name, price, stock):
        self.name = name
        self.price = price
        self.stock = stock
    
    def get_price_with_tax(self):
        return (1 + Product.tax_rate) * self.price
    
    def sell(self, qunatity):
        if self.stock >= qunatity:
            self.stock -= qunatity
            return True
        else:
            return False

keyboard = Product("단청 키보드 (화이트)", 110000, 0)
mouse = Product("Razer basilisk v3 x hyperspeed", 200000, 120)

print(keyboard.get_price_with_tax())
print(keyboard.sell(1))

print(mouse.get_price_with_tax())
print(mouse.sell(57))