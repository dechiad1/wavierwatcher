import json
import requests
import xml.etree.ElementTree as ET

from game import Game

class GameSet:
    
    def __init__(self, year, week, url):
        self.year = year
        self.week = week
        self.url = url
        self.games = []

    def fetch(self):
        url = self.url.format(self.year, self.week)
        data = requests.get(url)
        if data.status_code != 200:
            print("could not get data from", url, " ", data.status_code)
            print("exiting..")
            exit(1)

        xml_data = ET.fromstring(data.text)
        """
        <ss>
          <gms>
            <g> ... we want these </g>
          </gms>
        </ss>
        """
        # TODO: change findall to use .//
        game_elements = xml_data.find("gms").findall("g")
        games = []
        for g in game_elements:
            
            eid = g.get("eid")
            gsis = g.get("gsis")
            ha = g.get("h")
            ht = g.get("hnn")
            at = g.get("vnn")
            hs = g.get("hs")
            vs = g.get("vs")

            game = Game(eid, gsis, ha, ht, at, hs, vs)
            games.append(game)
        self.games = games

    def get_games(self):
        return self.games

    def json_games_string(self):
        l = []
        for g in self.games:
            l.append(g.__dict__)
        return json.dumps(l)
