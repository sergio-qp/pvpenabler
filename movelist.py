
class Move:
     def __init__(self, damage, accuracy, critrate, penetration, charged, ranged):
        self.damage = damage 
        self.accuracy = accuracy #percent as integer
        self.critrate = critrate #crit hit rate as integer
        self.penetration = penetration #percent as decimal
        self.charged = charged #charges left
        self.ranged = ranged #kinda redundant, but its just for shoot/ranged attacks

fullmovelist = dict([
    ("strike", Move(20,95,10,0.60,99,0)),
    ("shoot", Move(15,85,10,0.20,1,1)),
    ("pierce", Move(40,95,10,1.00,1,0)),
    ("hyperdodge", Move(30,95,10,0.60,1,0)),
])

