'''
+------------------------------------------------------------------+
|  CONFIGURATION HELP                                              |
|                                                                  |
|  See help.text to learn how to configure these properties.       |
+------------------------------------------------------------------+
'''

'''
See help.txt section:
+--------------+
|  credentials |
+--------------+
'''

credentials = {

    'user':'XXXX',
    'secret':'YYYY'

}


'''
See help.txt section:
+------------------+
| headless-browser |
+------------------+
'''
browser_options = {

    'headless-browser': False

}


'''
See help.txt sections:
+----------------+
|  attempt-bust  |
|  crimes-amount |
|  checkboxes    |
|  bust-game     |
+----------------+
'''
'''
    Precedence
    1) Bust-game
    2) Video-poker
    3) Black-jack
    4) All crimes
'''

game_options = {

    'attempt-bust': True,
    'crimes-amount': 'all',
    'checkboxes': [],
    'bust-game': False

}


'''
See help.txt section:
+------------------+
|   casino-games   |
+------------------+
'''
casino_games = {

    'video-poker':{

        'active': False,
        'max-bet-runs': 100,
        'bet-amount': 100

    },
    'black-jack':{

        'active': False,
        'max-bet-runs': 10,
        'bet-amount': 100,
        'double-until-win': False

    }

}
