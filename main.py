import gameset
import gameparser
import yahoosport

import json

baseurl = "https://nflcdns.nfl.com/ajax/scorestrip?season={}&seasonType=REG&week={}"
pdfurl = "https://nflcdns.nfl.com/liveupdate/gamecenter/{}/{}_Gamebook.pdf"

if __name__ == '__main__':

    y = yahoosport.YahooSports('credentials.json')
    ids = y.get_available(3)
    players = []
    for id in ids:
        d = y.fetch_player_stats(3, id)
        p = y.parse_player_stats(d)
        players.append(p)

    for p in players:
        if p.pickup_worthy():
            print(p.name)
    
    exit(1)
    # TODO: schedule to generate year / week number

    gameset = gameset.GameSet(2020, 1, baseurl)
    gameset.fetch()
    games = gameset.get_games() # return list of games

    # week_stats = []
    # for game in games:
    parser = gameparser.Parser(pdfurl)
    stats = parser.parse(games[0])

    # stats is [{}]
    for s in stats:
        for (k,vals) in s.items():
            print(k)
            for v in vals:
                statline = v.get_statline()
                print('\t', statline)

    


    


