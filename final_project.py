import sqlite3
import requests
import json
from bs4 import BeautifulSoup
import plotly.graph_objs as go



class Player():
    def __init__(self, GameID=None, Rank=None, Point=None, WinRate=None, Mostplayedhero=None, Mostplayedlane=None, ServerName=None):

        self.name = GameID
        self.Rank = Rank
        self.Point = Point
        self.WinRate = WinRate
        self.Mostplayedhero = Mostplayedhero
        self.Mostplayedlane = Mostplayedlane
        self.ServerName = ServerName

    def __str__(self):
        if (self.Rank==None or self.Point==None or self.WinRate==None or self.Mostplayedlane==None):
            output='The information of this player is currently missing!\n'
        else:
            output = self.name +'('+ self.ServerName+')'+ ': rank ' + self.Rank + ', ' + self.Point + ', ' + self.WinRate + ' ' + self.Mostplayedlane
        return output

CACHE_FNAME = 'cache_project_final.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()


except:
    CACHE_DICTION = {}

def make_request_using_cache(url,header=None,content=None):
    unique_ident = url
    ## first, look in the cache to see if we already have this data
    if unique_ident in CACHE_DICTION:
        return CACHE_DICTION[unique_ident]

    ## if not, fetch the data afresh, add it to the cache,
    ## then write the cache to file
    else:
        resp = requests.get(url, headers=header).text
        if content is None:
            CACHE_DICTION[unique_ident] = resp
            dumped_json_cache = json.dumps(CACHE_DICTION)
            fw = open(CACHE_FNAME,"w")
            fw.write(dumped_json_cache)
            fw.close() # Close the open file
        else:
            page_soup=BeautifulSoup(resp,'html.parser')
            content=page_soup.find(class_=content)
            content=str(content)
            CACHE_DICTION[unique_ident]=content
            dumped_json_cache=json.dumps(CACHE_DICTION)
            fw=open(CACHE_FNAME,"w")
            fw.write(dumped_json_cache)
            fw.close()

        return CACHE_DICTION[unique_ident]

def get_server_info():
    print("Getting data for servers...")
    server_list = []
    player_list = []
    user_agent = {'User-agent': 'Mozilla/5.0'}
    page_url = 'https://lolprofile.net/leaderboards'
    content_div = 'r100'
    servers_info = make_request_using_cache(page_url, user_agent, content_div)
    servers_info = BeautifulSoup(servers_info, 'html.parser')
    table_cells = servers_info.find_all('a')
    for region in table_cells:
        num_mid=0
        num_top=0
        num_jg=0
        num_bot=0
        server_n = {}
        server_url = region['href']
        server_abb = region.text
        if server_abb=='Champion':
            continue
        state_content = 'd-c stats'
        server_name = make_request_using_cache(server_url, user_agent, state_content)
        server_name = BeautifulSoup(server_name, 'html.parser')
        server_name = server_name.find('span').text[2::]
        server_n['Abbreviation'] = server_abb
        server_n['Name'] = server_name

        state_content = 'table table1 s-c-table lb-table'
        server_details = make_request_using_cache(server_url, user_agent, state_content)
        server_details = BeautifulSoup(server_details, 'html.parser')
        players = server_details.find('tbody')
        players = players.find_all('tr')
        for player in players:
            n_player = {}
            rank = player.find('td').text
            rank = rank[1:]
            id = player.find('span').text
            print(id)
            point = player.find(class_='alt ce mhide')
            point = point.text
            point = point.split()[0]
            player_url = player.find('a')['href']

            DETAIL = make_request_using_cache(player_url, user_agent)
            DETAIL = BeautifulSoup(DETAIL, 'html.parser')
            detail_info = DETAIL.find(class_='a2')
            if detail_info == None:
                n_player['id'] = id
                n_player['rank'] = rank
                n_player['point'] = point
                n_player["play's url"] = player_url
                n_player['Name of Server'] = server_abb
                n_player['win rate'] = None
                n_player['Most played hero'] = None
                n_player['Most played lane'] = None
                player_list.append(n_player)
                continue
            detail_info1 = detail_info.find('div')
            win_rate = detail_info1.find('div').text
            lane = detail_info.find_all('div')[5].text
            hero = DETAIL.find(class_="champid")
            if hero == None:
                n_player['id'] = id
                n_player['rank'] = rank
                n_player['point'] = point
                n_player["play's url"] = player_url
                n_player['Name of Server'] = server_abb
                n_player['win rate'] = win_rate
                n_player['Most played hero'] = None
                n_player['Most played lane'] = lane
                player_list.append(n_player)
                continue
            hero = hero.text

            n_player['id'] = id
            n_player['rank'] = rank
            n_player['point'] = point
            n_player["play's url"] = player_url
            n_player['Name of Server'] = server_abb
            n_player['win rate'] = win_rate
            n_player['Most played hero'] = hero
            n_player['Most played lane'] = lane
            player_list.append(n_player)

            if lane=='Mid':
                num_mid+=1
            if lane == 'Top':
                num_top += 1
            if lane=='Jungle':
                num_jg+=1
            if lane=='Bot':
                num_bot+=1
        server_n['Mid'] = num_mid
        server_n['Top'] = num_top
        server_n['Jungle'] = num_jg
        server_n['Bot'] = num_bot
        server_list.append(server_n)
    json_str1 = json.dumps(server_list)
    with open('servers.json', 'w') as json_file:
        json_file.write(json_str1)
    json_str2 = json.dumps(player_list)
    with open('players.json', 'w') as json_file:
        json_file.write(json_str2)




#using JSON to create the data base
DBNAME = 'LOL.db'
serverJSON= 'servers.json'
playerJSON = 'players.json'
try:
    file_server = open(serverJSON, 'r', encoding='utf-8')
    server_data = file_server.read()
    server_data = json.loads(server_data)
    file_server.close()
    file_player = open(playerJSON, 'r', encoding='utf-8')
    player_data = file_player.read()
    player_data = json.loads(player_data)
    file_player.close()
except:
    get_server_info()
    file_server = open(serverJSON, 'r', encoding='utf-8')
    server_data = file_server.read()
    server_data = json.loads(server_data)
    file_server.close()
    file_player = open(playerJSON, 'r', encoding='utf-8')
    player_data = file_player.read()
    player_data = json.loads(player_data)
    file_player.close()



conn = sqlite3.connect(DBNAME)
cur = conn.cursor()
Check_exist = 'DROP TABLE IF EXISTS "Servers";'
cur.execute(Check_exist)
Check_exist = 'DROP TABLE IF EXISTS "Players";'
cur.execute(Check_exist)
conn.commit()


statement = '''
            CREATE TABLE 'Servers' (
                'ID' INTEGER PRIMARY KEY AUTOINCREMENT,
                'Abbreviation' TEXT,
                'ServerName' TEXT,
                'Top' INTEGER,
                'Mid' INTEGER,
                'Jungle' INTEGER,
                'Bot' INTEGER
            );
        '''
try:
    cur.execute(statement)
except:
   print("Fail creating Servers")
conn.commit()


count = 1

for server in server_data:
    insertion = (None, server['Abbreviation'], server['Name'],server['Top'], server['Mid'], server['Jungle'], server['Bot'])
    statement = 'INSERT INTO "Servers" VALUES (?, ?, ?, ?, ?, ?, ?)'
    cur.execute(statement, insertion)

conn.commit()


statement = '''
            CREATE TABLE 'Players' (
                'ID' INTEGER PRIMARY KEY AUTOINCREMENT,
                'GameID' TEXT,
                'Rank' INTEGER,
                'Point' INTEGER,
                "Playerurl" TEXT,
                'NameofServer' TEXT,
                'WinRate' REAL,
                'Mostplayedhero' TEXT,
                'Mostplayedlane' TEXT
            );
        '''
try:
    cur.execute(statement)
except:
    print("Fail creating Players")
players_info=[]
for player in player_data:
    player_n_info = Player(player['id'],  player['rank'], player['point'], player['win rate'], player['Most played hero'], player['Most played lane'], player['Name of Server'])
    players_info.append(player_n_info)
    if player['win rate']==None:
        insertion = (
        None, player['id'], player['rank'], player['point'], player["play's url"], player['Name of Server'],
        player['win rate'], player['Most played hero'], player['Most played lane'])
    else:
        insertion = (None, player['id'], player['rank'], player['point'], player["play's url"], player['Name of Server'], float(player['win rate'].strip('%')), player['Most played hero'], player['Most played lane'])
    statement = 'INSERT INTO "Players" VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'
    cur.execute(statement, insertion)

conn.commit()
conn.close()



def process_command(command):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    result = []

    command_word = command.split()
    #search for players
    if command_word[0] == 'player':
        statement = '''SELECT m.GameID, m.rank, m.Point, m.WinRate,m.Mostplayedhero,m.Mostplayedlane, s.ServerName
                    FROM Players as m JOIN Servers as s ON m.NameofServer=s.Abbreviation Where m.GameID is not NULL '''
        order='ORDER BY m.rank '
        limit='LIMIT 10'
        header1=['GameID', 'Rank', 'Point', 'Win Rate','Most played hero','Most played lane', 'Server Name']
        for command_para in command_word:
            if 'server=' in command_para:
                print('limit by the server:')
                servername = command_para.split('=')[1]
                servername = str.upper(servername)
                statement = statement + 'AND m.NameofServer="' + servername + '" '
                continue
            elif 'lane=' in command_para:
                print('limit by the lane:')
                lane = command_para.split('=')[1]
                lane=str.capitalize(lane)
                statement = statement + "AND m.mostplayedlane='" + lane + "'"
                continue
            elif 'rank=' in command_para:
                print('limit by rank:')
                rank = command_para.split('=')[1]
                statement = statement + 'AND m.rank="' + rank + '" '
                continue
            elif 'winrate' in command_para:
                order= 'ORDER BY m.winrate DESC '
                continue
            elif 'bottom=' in command_para:
                num = command_para.split('=')[1]
                limit= 'DESC LIMIT ' + num
                continue
            elif 'top=' in command_para:
                num = command_para.split('=')[1]
                limit= 'LIMIT ' + num
                continue

        statement += order
        statement += limit
        cur.execute(statement)
        for cur_row in cur:
            result_row = []
            for r in cur_row:
                if not r:
                    r = 'Unknown'
                result_row.append(r)
            result.append(result_row)
            result[-1][3] = str(int(result[-1][3])) + '%'

        size_result=len(result)
        table=[]
        for j in range(7):
            table_col = []
            for i in range(size_result):
                table_col.append(result[i][j])
            table.append(table_col)
        #print(table)
        if ('bar' in command_word):
            if ('point' in command_word):

                fig = go.Figure(data=[go.Bar(
                    x=table[0], y=table[2],
                    text=table[2],
                    textposition='auto',
                )])
                fig.update_layout(title_text='Rank Point of Players')
            else:
                fig = go.Figure(data=[go.Bar(
                    x=table[0], y=table[3],
                    text=table[3],
                    textposition='auto',
                )])
                fig.update_layout(title_text='Win Rate of Players')


        else:
            fig = go.Figure(data=[go.Table(header=dict(values=header1),
                                       cells=dict(values=table))
                                ])
        fig.show()

        return result



#search for servers
    elif command_word[0] == 'server':


        country_info=''
        server_list=['BR', 'EUNE', 'EUW', 'JP', 'KR', 'LAN', 'LAS', 'NA', 'OCE', 'TR', 'RU']
        group=' Group by ServerName'
        statement = '''SELECT s.ServerName, s.Abbreviation,s.Top,s.Mid,s.Jungle, s.Bot
                    FROM Servers as s Join Players as m on s.Abbreviation=m.NameofServer'''
        for command_para in command_word:

            if 'best' in command_para:
                country_info =' Where m.rank=1'
                statement = '''SELECT s.ServerName, s.Abbreviation,s.Top,s.Mid,s.Jungle, s.Bot, m.GameID
                                    FROM Servers as s Join Players as m on s.Abbreviation=m.NameofServer'''



        statement =statement+country_info+group
        cur.execute(statement)
        for cur_row in cur:
            result_row = []
            #print(cur_row)
            for r in cur_row:
                result_row.append(r)
            result.append(result_row)
        size_result=len(result)
        table=[]
        len_row=len(result_row)
        if 'best' in command_word:
            header2=['ServerName', 'Abbreviation', 'Top', 'Mid', 'Jungle', 'Bot', 'Best player']
        else:
            header2 = ['ServerName', 'Abbreviation', 'Top', 'Mid', 'Jungle', 'Bot']
        for j in range(len_row):
            table_col = []
            for i in range(size_result):
                table_col.append(result[i][j])
            table.append(table_col)

        if ('pie' in command_word):
            servername=input('Which server do you want to search?\n')
            servername=str.upper(servername)
            if servername in server_list:
                for i in range(size_result):
                    if result[i][1]==servername:
                        values=[result[i][2], result[i][3], result[i][4], result[i][5]]
                        break
                labels = ['Top', 'Mid', 'Jungle', 'Bot']
                fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
                fig.update_layout(title_text='Lane percentage info of '+servername)
                fig.show()
            else:
                print('Sorry, there is no such server.')
        elif('horizontal' in command_word):




            top_labels = ['Top', 'Mid', 'Jungle', 'Bot']

            colors = ['rgba(38, 24, 74, 0.8)', 'rgba(71, 58, 131, 0.8)',
                      'rgba(122, 120, 168, 0.8)', 'rgba(190, 192, 213, 1)']

            x_data = [result[0][2:6],
                      result[1][2:6],
                      result[2][2:6],
                      result[3][2:6],
                      result[4][2:6],
                      result[5][2:6],
                      result[6][2:6],
                      result[7][2:6],
                      result[8][2:6],
                      result[9][2:6],
                      result[10][2:6]]

            y_data = ['BR', 'EUNE', 'EUW', 'JP', 'KR', 'LAN', 'LAS', 'NA', 'OCE', 'TR', 'RU']

            fig = go.Figure()

            for i in range(0, len(x_data[0])):
                for xd, yd in zip(x_data, y_data):
                    fig.add_trace(go.Bar(
                        x=[xd[i]], y=[yd],
                        orientation='h',
                        marker=dict(
                            color=colors[i],
                            line=dict(color='rgb(248, 248, 249)', width=1)
                        )
                    ))

            fig.update_layout(
                xaxis=dict(
                    showgrid=False,
                    showline=False,
                    showticklabels=False,
                    zeroline=False,
                    domain=[0.15, 1]
                ),
                yaxis=dict(
                    showgrid=False,
                    showline=False,
                    showticklabels=False,
                    zeroline=False,
                ),
                barmode='stack',
                paper_bgcolor='rgb(248, 248, 255)',
                plot_bgcolor='rgb(248, 248, 255)',
                margin=dict(l=120, r=10, t=140, b=80),
                showlegend=False,
            )

            annotations = []

            for yd, xd in zip(y_data, x_data):
                # labeling the y-axis
                annotations.append(dict(xref='paper', yref='y',
                                        x=0.14, y=yd,
                                        xanchor='right',
                                        text=str(yd),
                                        font=dict(family='Arial', size=14,
                                                  color='rgb(67, 67, 67)'),
                                        showarrow=False, align='right'))
                # labeling the first percentage of each bar (x_axis)
                annotations.append(dict(xref='x', yref='y',
                                        x=xd[0] / 2, y=yd,
                                        text=str(xd[0]),
                                        font=dict(family='Arial', size=14,
                                                  color='rgb(248, 248, 255)'),
                                        showarrow=False))
                # labeling the first Likert scale (on the top)
                if yd == y_data[-1]:
                    annotations.append(dict(xref='x', yref='paper',
                                            x=xd[0] / 2, y=1.1,
                                            text=top_labels[0],
                                            font=dict(family='Arial', size=14,
                                                      color='rgb(67, 67, 67)'),
                                            showarrow=False))
                space = xd[0]
                for i in range(1, len(xd)):
                    # labeling the rest of percentages for each bar (x_axis)
                    annotations.append(dict(xref='x', yref='y',
                                            x=space + (xd[i] / 2), y=yd,
                                            text=str(xd[i]),
                                            font=dict(family='Arial', size=14,
                                                      color='rgb(248, 248, 255)'),
                                            showarrow=False))
                    # labeling the Likert scale
                    if yd == y_data[-1]:
                        annotations.append(dict(xref='x', yref='paper',
                                                x=space + (xd[i] / 2), y=1.1,
                                                text=top_labels[i],
                                                font=dict(family='Arial', size=14,
                                                          color='rgb(67, 67, 67)'),
                                                showarrow=False))
                    space += xd[i]
            fig.update_layout(title_text='Lane choice in different servers')
            fig.update_layout(annotations=annotations)

            fig.show()
        else:
            fig = go.Figure(data=[go.Table(header=dict(values=header2),
                                           cells=dict(values=table))
                                  ])
            fig.show()



        return result


    elif command_word[0].split('=')[0] == 'playerid':
        id=command_word[0].split('=')[1]

        idvalid=False

        for i in range(len(players_info)):

            if players_info[i].name==id:
                print(players_info[i])
                idvalid=True
                break
        if idvalid==False:
            print("No player found!")




def interactive_prompt():
    help_info = '''Commands available:

Players
	Description: Lists players, according the specified parameters.

	Options:
		* server=<name>|lane=<name>|rank=<name>|bar
			server=<name>|lane=<name>|rank=<name> [default: none]
		Description: Specifies a sever or lane within which to 
		limit the results, and also specifies whether to limit 
		by the server or lane or rank

		* rank|win rate|point [default: rank]
		Description: Specifies whether to sort by rank|win rate|point

		* top=<limit>|bottom=<limit> [default: top=10]
		Description: Specifies whether to list the top <limit> matches or the
		bottom <limit> matches.
		
		*bar (point)[default:win rate]
		Description:generate a bar graph based on win rate or point

Servers
	Description: Lists Servers according to the specified parameters.

	Options:
		* best
		Description: ad a column show which is the best player in this server


		* horizontal
		Description: Generate a horizontal bar graph shows that the lane choices in each server
		
		*pie
		Description: Generate a pie graph shows that the lane choices in the server you choose

Playerid
    Description: Print the information of certain player by entering the player's id.

	Options:
		* playerid=<name> [default: none]


'''
    command_list = ['player', 'server', 'lane', 'rank', 'point', 'winrate', 'top', 'bottom', 'playerid', 'bar', 'pie','best','horizontal']
    while True:
        response = input('Enter a command: ')
        if response == 'exit':
            break
        if response == 'help':
            print(help_info)
            continue
        commands = response.split()
        Error=False
        invalid_command = ['lane', 'rank', 'point', 'winrate', 'top', 'bottom', 'playerid', 'bar']
        if commands[0]=='server':
            for option in commands:
                if (option in invalid_command or option.split('=')[0] in invalid_command):
                    print('Server do not have this option.')
                    Error=True
                    break
        for word in commands:
            if word not in command_list and word.split('=')[0] not in command_list:
                print('Command not recognized:', response, '\n')
                Error=True
                break
            if word.split('=')[0] in ['top', 'bottom'] and word.split('=')[1].isdigit() is False:
                print('Command not recognized: Input integer as limit\n')
                Error=True
                break
        if Error==True:
            continue
        process_command(response)
    response = 'Exiting!'
    print(response)
    return


if __name__=="__main__":
    interactive_prompt()