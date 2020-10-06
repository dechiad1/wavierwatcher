import json

class Game:
    def __init__(self, eid, gsis, homeabbreviation, hometeam, awayteam, homescore, awayscore):
        self.eid = eid
        self.gsis = gsis
        self.homeabbreviation = homeabbreviation
        self.hometeam = hometeam
        self.awayteam = awayteam
        self.homescore = homescore
        self.awayscore = awayscore
        self.winner = hometeam if homescore > awayscore else awayteam
    
    def getGid(self):
        return self.gsis

    def getHt(self):
        return self.homeabbreviation

    def to_string(self):
        return json.dumps(self.__dict__)
