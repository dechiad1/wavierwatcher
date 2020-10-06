import requests
import tabula

import playerstats

class Parser:
    def __init__(self, url):
        self.url = url

    def parse(self, game):
        url = self.url.format(game.getGid(), game.getHt())
        b = requests.get(url)
        if b.status_code != 200:
            print("could not get data from", url, " ", b.status_code)
            print("exiting..")
            exit(1)

        with open('test_pdf.pdf', 'wb') as f:
            f.write(b.content)
            f.close()

        df = tabula.read_pdf("test_pdf.pdf", pages='all')

        frame_proper = None
        for frame in df:
            if 'RUSHING' in frame:
                frame_proper = frame

        if frame_proper is None:
            print('could not find any dataframe with RUSHING in the headers. exiting..')
            exit(1)

        stats = frame_proper.T.reset_index().T
        at = stats.iloc[:,:5].dropna(axis=1,thresh=10).fillna(-1)
        at.columns = [1,2,3,4]
        ht = stats.iloc[:,8:13].dropna(axis=1,thresh=10).fillna(-1)
        ht.columns = [1,2,3,4]

        """ sample DF after filter / parsing
                                1           2      3      4                                                
        index           RUSHING.1  Unnamed: 3  ATT.1  YDS.1                                                
        0               M.Sanders          -1     20     95
        1                 B.Scott          -1      4     19
        2                 C.Wentz          -1      2      7
        3                      -1          -1     -1     -1
        4                      -1          -1     -1     -1
        5                      -1          -1     -1     -1
        6                      -1          -1     -1     -1
        7                   Total          -1     26    121
        8                 PASSING     ATT CMP    YDS  SK/YD
        9                 C.Wentz       43 26    242    0/0
        10                  Total       43 26    242    0/0
        11         PASS RECEIVING         TAR    REC    YDS
        12              D.Jackson           9      6     64
        13                 Z.Ertz           7      5     42
        14               J.Reagor           4      4     41
        15              D.Goedert           8      4     30
        16              M.Sanders           7      3     36
        """

        result = []
        result.append(parse_team(ht))
        result.append(parse_team(at))
        # TODO: remove test_pdf
        return result

def parse_team(df):
        rushflag = False
        receiveflag = False
        result = {}
        for index, row in df.iterrows():
            if rushflag:
                if row[1] == -1 or row[1] == "Total":
                    rushflag = False
            
            if receiveflag:
                if row[1] == -1 or row[1] == "Total":
                    receiveflag = False
            
            if rushflag or receiveflag:
                p = playerstats.Player(row[1], 'TODO')
                ps = {}
                
                if rushflag:
                    ps = parse_rusher(row)
                elif receiveflag:
                    ps = parse_receiver(row)
                
                if p in result:
                    x = result[p]
                    x.append(ps)
                    result[p] = x
                else:
                    result[p] = [ps]

            # print(row)
            # print(row[1])
            if row[1] == 'RUSHING' or row[1] == 'RUSHING.1':
                rushflag = True
            if row[1] == 'PASS RECEIVING':
                receiveflag = True
        return result

def parse_receiver(row):
    return playerstats.Receiver(row[2], row[3], row[4])

def parse_rusher(row):
    p = playerstats.Player(row[1], 'rb')
    return playerstats.Rusher(row[3], row[4])

            