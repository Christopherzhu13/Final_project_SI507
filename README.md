# Final_project_SI507

This project craws the leaderboards of servers of League of Legends in different countries. The data source I used is https://lolprofile.net/leaderboards. On this website, people can choose which server you want to see and the leaderboard infomation. And you can click each player to see the more detailed information of the player. What's more, the usage of plotly refers to https://plot.ly/python/getting-started/.
● This code first crawl the data from the leaderboard page(server's name and player's name) Then it goes deeper into each page of player to crawl the detailed information of each player. After getting the data, change the format into the format of json and store them into two json file All of this is done by two functions called get_server_info() and get_players_for_server() And then, create a database with two table using the data in these json files. Using a function called process_command() to handle different command. There is a class called Player() to store the info for player. The two json files are two lists of dictionaries. Each dictionary is the whole info of a player or a server And then I silced all the data columnwise so that I can use ploty to present it.
● In this code, we can start from the pycharm or the command line, and then, we can enter 'help' to see the help info there are serveral options to get the data and exit to quit the program. We can enter player or server to see the info table by ploty, in player,enter bar can generate a bar chart of the winrate of player(use bar point can show a bar of point). You can also enter 'playerid=' to get the detailed info of this player shown on the command line. You can also use server=|lane=|rank= to specifiy a sever or lane within which to limit the results, and also specifies whether to limit by the server or lane. Use top=|bottom= to specify whether to list the top matches or the bottom matches. In the server option, a table of infomation for servers are shown. Use server best can show who is the beat player in the servers. What's more you c