class Rectangle:
    shape_type = "Rectangle"
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height
    
    def perimeter(self):
        return 2 * (self.width + self.height)
    
    def is_square(self):
        if self.width == self.height:
            return True
        else:
            return False

rect = Rectangle(10, 5)
square = Rectangle(8, 8)

print(rect.area())
print(rect.perimeter())
print(rect.is_square())
print()

print(square.area())
print(square.perimeter())
print(square.is_square())