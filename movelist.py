
class Move:
     def __init__(self, damage, accuracy, penetration, charged=True):
        self.damage = damage 
        self.accuracy = accuracy #percent as integer
        self.penetration = penetration #percent as decimal
        self.charged = charged

fullmovelist = dict([
    ("strike", Move(20,95,0.60)),
    ("shoot", Move(15,85,0.20)),
    ("pierce", Move(40,95,1.00)),
    ("hyperdodge", Move(30,95,0.60)),
])

