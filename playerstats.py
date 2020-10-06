class Player:
    def __init__(self, name, position):
        self.name = name
        self.position = position

    def __repr__(self):
        return str(vars(self))

    def __str__(self):
        return str(vars(self))

    # use the name as the key in a dict
    # name CANNOT be modified
    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def set_rusher(self, rusher):
        self.rusher = rusher

    def set_receiver(self, receiver):
        self.receiver = receiver

    def pickup_worthy(self):
        result = False
        if hasattr(self, 'rusher'):
            result = self.rusher.pickup_worthy()
        if hasattr(self, 'receiver'):
            result = result or self.receiver.pickup_worthy()
        return result

class Rusher:
    def __init__(self, att, yds):
        self.att = att
        self.yds = yds

    def pickup_worthy(self):
        yardage_points = int(self.yds) / 10
        avg = int(self.yds) / int(self.att)
        
        if yardage_points > 7 and self.att > 5:
            return True
        
        if avg > 5 and self.att > 5:
            return True

        return False

    def get_statline(self):
        return f'{self.yds} yards on {self.att} attempts'

class Receiver:
    def __init__(self, tar, rec, yds):
        self.tar = tar
        self.rec = rec
        self.yds = yds

    def pickup_worthy(self):
        yardage_points = int(self.yds) / 10
        
        if yardage_points > 5 and self.tar > 5:
            return True
        
        return False
    
    def get_statline(self):
        return f'{self.yds} yards on {self.rec}/{self.tar} targets'
        