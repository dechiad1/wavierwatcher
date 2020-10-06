import base64
import json
import os
import xml.etree.ElementTree as ET

import requests
import playerstats

class YahooSports:
    oauth_url = 'https://api.login.yahoo.com/oauth2/get_token'
    fa_url_base = 'https://fantasysports.yahooapis.com/fantasy/v2/league/'
    player_stats_url_base = 'https://fantasysports.yahooapis.com/fantasy/v2/player/'
    stat_id_url = 'https://fantasysports.yahooapis.com/fantasy/v2/game/nfl/stat_categories'

    xmlns = { 'fantasy' : 'http://fantasysports.yahooapis.com/fantasy/v2/base.rng' }

    def __init__(self, file):
        if not os.path.isfile(file):
            print(f'could not find credentials in file {file}')
            exit(1)

        self.file = file
        with open(file, 'r') as f:
            data = json.load(f)
            self.consumer_key = data['CONSUMER_KEY']
            self.consumer_secret = data['CONSUMER_SECRET']
            self.yahoo_refresh_token = data['REFRESH_TOKEN']
            self.league_id = data['LEAGUE_ID']
            auth_string = f'{self.consumer_key}:{self.consumer_secret}'
            self.auth_header = base64.b64encode(bytes(auth_string, 'utf-8'))

        self.login()
        self.fetch_stats_ids()

    def login(self):
        # requires saving the refresh token! 
        # Yahoo requires user visiting the browser, which we do out of band by visiting the following
        # https://api.login.yahoo.com/oauth2/request_auth?client_id=ENTER_CLIENT_ID&redirect_uri=oob&response_type=code&language=en-us
        # & hitting accept - this gives the one time code we use to get the first access token
        # a single request is made with the 'code' param instead of 'refresh_token' & a grant_type of 'authorization_code'
        param = {
            'client_id': self.consumer_key,
            'client_secret': self.consumer_secret,
            'grant_type': 'refresh_token',
            'redirect_uri': 'oob',
            'refresh_token': self.yahoo_refresh_token
        }

        token_response = requests.post(YahooSports.oauth_url, data=param)
        token = json.loads(token_response.text)
        # DEBUG: print(token)

        new_refresh_token = token['refresh_token']
        with open(self.file, 'r+') as f:
            data = json.load(f)
            data['REFRESH_TOKEN'] = new_refresh_token
            f.seek(0)
            f.write(json.dumps(data))
            f.truncate()
        
        access_token = token['access_token']
        auth_headers = {
            'Authorization': f'Bearer {access_token}'
        }
        self.auth_headers = auth_headers

    def get_available(self, week):
        if self.auth_headers is None:
            print('can not call yahoo api without building auth headers')
            return
        
        query = YahooSports.fa_url_base + self.league_id + f'/players;status=A;sort=PTS;sort_type=week;sort_week={week};count=20'
        d = requests.get(query, headers = self.auth_headers)
        if d.status_code != 200:
            print(f'could not execute {query}')
            print(d.status_code)
            print(d.text)
        
        xml_data = ET.fromstring(d.text)
        """
        <fantasy_content>
          <league>
            <players>
              <player>
        """

        # note the .// states that ET should look for matching child elements in all the sub elements
        players = xml_data.findall('.//fantasy:player', YahooSports.xmlns)
        ids = []
        for p in players:
            id = p.find('fantasy:player_key', YahooSports.xmlns)
            ids.append(id.text)
        return ids

    def fetch_player_stats(self, week, key):
        if self.auth_headers is None:
            print('can not call yahoo api without building auth headers')
            return
        
        query = YahooSports.player_stats_url_base + f'{key}/stats;type=week;week={week}'
        d = requests.get(query, headers = self.auth_headers)
        if d.status_code != 200:
            print(f'could not execute {query}')
            print(d.status_code)
            print(d.text)

        return d.text

    def parse_player_stats(self, d):
        # input is expected to be xml text
        xml_data = ET.fromstring(d)
        xml_name = xml_data.find('.//fantasy:full', YahooSports.xmlns)
        name = xml_name.text
        xml_position = xml_data.findall('.//fantasy:position', YahooSports.xmlns)
        positions = []
        for p in xml_position:
            positions.append(p.text)

        xml_stats = xml_data.findall('.//fantasy:stat', YahooSports.xmlns)
        #78 - targets
        #11 - receptions
        #12 - receiving yards
        #8 - rushing attempts
        #9 - rushing yards
        targets = 0
        rushing_attempts = 0
        for stat in xml_stats:
            stat_id = stat.find('fantasy:stat_id', YahooSports.xmlns)
            if int(stat_id.text) == 78:
                targets = stat.find('fantasy:value', YahooSports.xmlns).text
            if int(stat_id.text) == 11:
                receptions = stat.find('fantasy:value', YahooSports.xmlns).text
            if int(stat_id.text) == 12:
                receiving_yards = stat.find('fantasy:value', YahooSports.xmlns).text
            if int(stat_id.text) == 8:
                rushing_attempts = stat.find('fantasy:value', YahooSports.xmlns).text
            if int(stat_id.text) == 9:
                rushing_yards = stat.find('fantasy:value', YahooSports.xmlns).text

        p = playerstats.Player(name, positions[0])
        if int(targets) > 0:
            re = playerstats.Receiver(int(targets), int(receptions), int(receiving_yards))
            p.set_receiver(re)

        if int(rushing_attempts) > 0:
            ru = playerstats.Rusher(int(rushing_attempts), int(rushing_yards))
            p.set_rusher(ru)
        
        return p


    def fetch_stats_ids(self):
        if self.auth_headers is None:
            print('can not call yahoo api without building auth headers')
            return

        d = requests.get(YahooSports.stat_id_url, headers = self.auth_headers)
        if d.status_code != 200:
            print(f'could not execute {YahooSports.stat_id_url}')
            print(d.status_code)
            print(d.text)
        
        xml_data = ET.fromstring(d.text)
        """
        <fantasy_content>
          <game>
            <stat_categories>
              <stats>
                <stat>
        """
        categories = {}
        stats = xml_data.findall('.//fantasy:stat', YahooSports.xmlns)
        for stat in stats:
            id = stat.find('fantasy:stat_id', YahooSports.xmlns)
            name = stat.find('fantasy:name', YahooSports.xmlns)
            categories[name.text] = id.text

        self.stat_categories = categories

        