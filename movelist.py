
class Move:
     def __init__(self, name, damage, accuracy, critrate, penetration, charged, ranged):
        self.name = name
        self.damage = damage 
        self.accuracy = accuracy #percent as integer
        self.critrate = critrate #crit hit rate as integer
        self.penetration = penetration #percent as decimal
        self.charged = charged #charges left
        self.ranged = ranged #kinda redundant, but its just for shoot/ranged attacks

fullmovelist = dict([
    ("slash", Move("slash",20,95,10,0.60,99,0)),
    ("blast", Move("blast",15,85,10,0.20,1,1)),
    ("pierce", Move("pierce",20,95,10,1.00,1,0)),
])

