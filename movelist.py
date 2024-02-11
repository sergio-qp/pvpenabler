
class Move:
     def __init__(self, damage, accuracy, penetration, charged=True):
        self.damage = damage
        self.accuracy = accuracy
        self.penetration = penetration
        self.charged = charged

fullmovelist = dict([
    ("strike", Move(20,0.95,3)),
    ("shoot", Move(15,0.85,1)),
    ("pierce", Move(40,0.95,5)),
    ("hyperdodge", Move(30,0.95,3)),
])

