import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import datetime
import re
import random
from beautifultable import BeautifulTable
from config import credentials, browser_options, game_options, casino_games
import json

url = 'https://www.downtown-mafia.com'
options = webdriver.ChromeOptions()

if browser_options['headless-browser']:
    options.add_argument('headless')
    driver = webdriver.Chrome(chrome_options=options)
else:
    driver = webdriver.Chrome()

driver.get(url)

#######################
#   Helper functions  #
#######################
def config():

    print(json.dumps(game_options, indent=4))
    print(json.dumps(casino_games, indent=4))

    print('Change the configuration and then run the command run() to start the script.')
    print('You will need to be logged in already into the game.')
    print('To change any of the settings:')
    info = 'To change game_options type exacly like:\n'
    info += 'game_options["attempt-bust"] = True or False\n'
    info += 'game_options["bust-game"] = True or False\n'
    info += 'game_options["crimes-amount"] = "all" or "random" or "custom" . Type one. If "custom" configure "checkboxes" with numbers.\n'
    info += 'game_options["checkboxes"] = [1,2,3]\n'
    info += '\n'
    info += 'To change casino_games type exacly like below:\n'
    info += 'casino_games["black-jack" or "video-poker"]["active"] = True or False - choose either "black-jack" or "video-poker" do not type both.\n'
    info += 'casino_games["black-jack" or "video-poker"]["bet-amount"] = 1000 - choose either "black-jack" or "video-poker" do not type both.\n'
    info += 'casino_games["black-jack" or "video-poker"]["max-bet-runs"] = 100 - choose either "black-jack" or "video-poker" do not type both.\n'
    info += 'casino_games["black-jack"]["double-until-win"] = True or False - Only works for "black-jack"\n'
    info += '\n'
    info += 'Once you finish configuring, run run().\n'
    print(info)


# Log data paramenter in a .txt file called data.txt
def log(data, file='data.txt'):
    ''' Log data into a file called data.txt '''

    # todo - improvement: append to begining of file and not end.

    mode = 'a+'
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M")
    text_file = open(file, mode)
    text_file.write(str(timestamp) + ' -->  ' + str(data))
    text_file.write('\n')
    text_file.close()


# Loops through the timers for each crime and returns an object with {'crime name':'cooldown time'} pairs.
def get_timers():
    ''' Loop through timers for each crime and return an object with {'crime name':'cooldown time'} pairs. '''

    timers = driver.find_elements_by_xpath('/html/body/div[1]/main/div[1]/div[2]/ul/li')
    order  = {}

    for i in timers:
        time = i.text.split('\n')
        order[time[0]] = time[1]

    return order


# Converts hh:mm:ss to seconds and returns.
def get_sleep_time(element):
    ''' Takes an 'element' which may be an HTML element (<span>hh:mm:ss</span>) or the text itself (hh:mm:ss).
        and returns the amount of seconds corresponding to the timestamp. '''

    try:
        t = element.text.split(':')
    except Exception as e:
        log(e)
        t = element.split(':')

    hours = int(t[0])
    minutes = int(t[1])
    seconds = int(t[2])
    sleep = int((hours*3600) + (minutes*60) + seconds)

    return sleep


# Returns an array of the checkboxes to select to commit crimes based on config setup.
def get_crimes_checkboxes(checkboxes_array):

    crimes_amounts_config = game_options['crimes-amount']
    custom_checkboxes_selection = list(set(game_options['checkboxes']))

    if crimes_amounts_config == 'random':

        random_crimes_array = []
        rn = random.randint(1, len(checkboxes_array)-1)

        for t in range(rn):
            arn = random.randint(0, len(checkboxes_array)-1)
            random_crimes_array.append(checkboxes_array[arn])

        crimes_checkboxes = list(set(random_crimes_array))

    elif crimes_amounts_config == 'custom':

        crimes_checkboxes = []

        a = len(custom_checkboxes_selection)
        b = len(checkboxes_array)

        if a < b or a == b:

            for e in custom_checkboxes_selection:
                if type(e) is int and int(e) != 0:
                    crimes_checkboxes.append(checkboxes_array[e - 1])

    else:
        crimes_checkboxes = []
        for each in checkboxes_array:
            crimes_checkboxes.append(each)


    return crimes_checkboxes



##################################
#   In Game Secondary functions  #
##################################

# Print player and game statistics
def player_stats():
    url = 'https://www.downtown-mafia.com/main'
    driver.get(url)
    proper_table_one = []
    proper_table_two = []
    final_table_one = BeautifulTable() # 4 size array
    final_table_two = BeautifulTable() # 2 size array

    try:
        stats_table_one = driver.find_element_by_xpath('/html/body/div[1]/main/div[2]/div[1]/div/div[3]/div[2]/table[1]/tbody').text
        stats_table_two = driver.find_element_by_xpath('/html/body/div[1]/main/div[2]/div[1]/div/div[3]/div[2]/table[2]/tbody').text
        checked_string = stats_table_one.replace('Major Crimes', 'Major-Crimes').replace('Car Theft', 'Car-Theft').replace('Jail Busting','Jail-Busting')
        first_split = checked_string.split('\n')

        for each in first_split:
            proper_table_one.append(each.split(' '))

        for i in range(len(proper_table_one)):
            if len(proper_table_one[i]) == 4:
                final_table_one.append_row(proper_table_one[i])

        checked_string_two = stats_table_two
        second_split = checked_string_two.split('\n')

        for e in range(5):
            proper_table_two.append(second_split[e].split(' '))

        for i in range(len(proper_table_two)):
            if len(proper_table_two[i]) == 2:
                final_table_two.append_row(proper_table_two[i])

        right_list = driver.find_elements_by_xpath('//*[@id="progNav"]/li')

        final_table_two.append_row(['City', right_list[3].text])
        final_table_two.append_row(['Crew', right_list[5].text])

        if 'Not yet ranked' in right_list[6].text:
            final_table_two.append_row(['Rank','Not yet ranked!'])
        else:
            final_table_two.append_row(right_list[6].text.split(' '))

        messages = driver.find_element_by_xpath('//*[@id="comms"]/li[1]').text
        if len(messages.split()) == 2:
            final_table_two.append_row(messages.split())
        else:
            final_table_two.append_row([messages, '(0)'])

        driver.get('https://www.downtown-mafia.com/bank')

        savings = driver.find_element_by_xpath('/html/body/div[1]/main/div[2]/div[1]/form/table[1]/tbody/tr[4]').text.replace('Balance', 'Savings-balance')

        if 'No Money' in savings:
            final_table_two.append_row(['Savings-balance','No Money!'])
        if len(savings.split()) == 2:
            final_table_two.append_row(savings.split())

        log('BEGIN PLAYER STATS')
        log(final_table_one)
        log(final_table_two)
        log('END PLAYER STATS')
        print('Player Stats:')
        print(final_table_one)
        print(final_table_two)

    except Exception as e:
        print(e)
        log(e)
        print('Could not get stats')
        log('[EXCEPTION 1 - player_stats() - Could not get stats ]')


# Return True is user is in jail and False is the user is not in jail.
def get_jail_status():
    match_user = credentials['user']
    term_to_confirm_jail = 'Federal'
    arrested = False
    jail_time = 0
    info = '\n|Checking jail status: '

    try:
        url = 'https://www.downtown-mafia.com/jail'
        driver.get(url)

        jail_table_text = driver.find_element_by_xpath('/html/body/div[1]/main/div[2]/div[1]/table[1]/tbody/tr[1]/td').text

        if term_to_confirm_jail in jail_table_text:

            jail_table_rows = driver.find_elements_by_xpath('/html/body/div[1]/main/div[2]/div[1]/table[1]/tbody/tr')

            for row in jail_table_rows:
                if match_user in row.text:
                    arrested = True

                    row_text_array = row.text.split()

                    for element in row_text_array:
                        if ':' in element:
                            element = '00:' + element
                            jail_time = get_sleep_time(element)
    except Exception as e:
        print(e)
        log(e)
        info += 'Exception'

    if arrested:
        info += 'Arrested! :('
    else:
        info += 'Not arrested! :)'

    print(info)
    log(info)

    return {'arrested': arrested, 'jail-time': jail_time}


# Returns an object with the times in seconds for each support bonus.
def check_support_us_bonuses():
    support_us_config = game_options['support-us']
    times = {}

    if support_us_config:

        url = 'https://www.downtown-mafia.com/rewards'
        driver.get(url)

        rank_boost = driver.find_element_by_xpath('/html/body/div[1]/main/div[2]/div[1]/table/tbody/tr[3]/td[3]')
        money_300 = driver.find_element_by_xpath('/html/body/div[1]/main/div[2]/div[1]/table/tbody/tr[3]/td[4]')
        bullets_100 = driver.find_element_by_xpath('/html/body/div[1]/main/div[2]/div[1]/table/tbody/tr[3]/td[5]')

        try:
            t1 = get_sleep_time(rank_boost.text)
            times['Rank-Boost'] = t1
        except Exception as e:
            print(e)
            log(e)
            t1 = 0

        try:
            t2 = get_sleep_time(money_300.text)
            times['Money-300'] = t2
        except Exception as e:
            print(e)
            log(e)
            t2 = 0

        try:
            t3 = get_sleep_time(bullets_100.text)
            times['Bullets-100'] = t3
        except Exception as e:
            print(e)
            log(e)
            t3 = 0

    return times


# Bust ownself out of jail. Returns boolean result.
def bust_out_of_jail():

    url = 'https://www.downtown-mafia.com/jail'

    try:
        print('|Attempting jail bust.')
        driver.get(url)
        bust_buttons = driver.find_elements_by_xpath('//button[@name="bustout"]')

        for bust in bust_buttons:
            if 'Escape' in bust.text:
                bust.click()

        time.sleep(1.5)
        result = driver.find_element_by_xpath('//*[@id="theBox"]').text
        print('|' + result)
        log(result)
    except Exception as e:
        print(e)
        log(e)
        result = ''

    if 'success' in result:
        return True

    else:
        return False


# Busts a random user out of jail. Returns boolean result.
def bust_user_out_of_jail():
    url = 'https://www.downtown-mafia.com/jail'

    try:
        print('|Attempting to bust some user.')
        driver.get(url)
        bust_buttons = driver.find_elements_by_xpath('//button[@name="bustout"]')
        max_num = len(bust_buttons)-1
        random_number = random.randint(0, max_num)
        bust_buttons[random_number].click()
        time.sleep(1.5)
        result = driver.find_element_by_xpath('//*[@id="theBox"]').text
        print('|' + result)
        log(result)
        if 'success' in result:
            return True
        else:
            return False

    except Exception as e:
        print(e)
        log(e)
        print('Exception ar bust_user_out_of_jail()')
        return False




#######################
#   Main functions  #
#######################

# Main function
def run():

    '''
    Precedence
    1) Bust-game
    2) Video-poker
    3) Black-jack
    4) All crimes
    '''

    bust_game_config = game_options['bust-game']
    casino_games_poker_config = casino_games['video-poker']
    casino_games_blackjack_config = casino_games['black-jack']

    if bust_game_config:

        jail_status = get_jail_status()
        arrested = jail_status['arrested']

        if arrested:
            # bust myself out
            escaped_jail = bust_out_of_jail()

            if escaped_jail:
                # run() will go to 'else' as use is NOT arrested
                run()
            else:
                print('|Sleeping 30 sec as someone might help me escape.')
                time.sleep(30)
                run()
        else:
            # bust other people
            busted_some_user = bust_user_out_of_jail()
            time.sleep(1)
            # If the user suceeds, repeating will exit in this 'else',
            # Otherwise it will go to the 'if' statement.
            run()
    else:

        if casino_games_poker_config['active']:
            # Poker is active

            loop = 0
            max_bet_runs_config = casino_games['video-poker']['max-bet-runs']
            url = 'https://www.downtown-mafia.com/videopoker'
            driver.get(url)

            while loop < max_bet_runs_config:
                videopoker = video_poker()

                if videopoker == 'NO FUNDS':
                    print('Sorry, you don\'t have enough funds to play video-poker.\nWithdraw some from the bank and re-run the script.')
                    break
                else:
                    loop += 1

        elif casino_games_blackjack_config['active']:
            # Blackjack is active
            game_config = casino_games['black-jack']
            log_file = 'blackjack.txt'
            msg = 'Started blackjack. Your configurations are: ' + str(game_config)
            log(msg, log_file)

            url = 'https://www.downtown-mafia.com/blackjack'
            driver.get(url)

            loop = 0
            max_bet_runs_config = casino_games_blackjack_config['max-bet-runs']

            while loop < max_bet_runs_config:
                blackjack = black_jack()

                if blackjack == 'NO FUNDS':
                    print('Sorry, you don\'t have enough funds to play Blackjack.\nWithdraw some from the bank and re-run the script.')
                    break
                else:
                    loop += 1

        else:
            # All crimes only
            match_user = credentials['user']
            attempt_bust = game_options['attempt-bust']
            timers_object = get_timers()

            waiting_times = []

            jail_status_object = get_jail_status()
            arrested = jail_status_object['arrested']
            jail_time = jail_status_object['jail-time']

            if not arrested:
                for crime in timers_object:

                    sleep_time = get_sleep_time(timers_object[crime])

                    if sleep_time == 0:
                        print('|Doing:', crime)

                        if crime == 'Crimes':
                            new_time = crimes()
                            time.sleep(1)
                        elif crime == 'Heists':
                            new_time = heist()
                            time.sleep(1)
                        elif crime == 'Car Theft':
                            new_time = gta()
                            time.sleep(1)
                        elif crime == 'Drug Lab':
                            print('Function does not exist.')
                            break
                        elif crime == 'Major Crimes':
                            print('Function does not exist.')
                            break
                        else:
                            print('This is not a crime.')
                            break

                        waiting_times.append(new_time)
                    else:
                        waiting_times.append(sleep_time)

                lowest_wait_time = sorted(waiting_times)

                try:
                    minimun_wait = lowest_wait_time[0]
                except Exception as e:
                    log(e)
                    minimun_wait = 0

                print('|Going to sleep now for', str(minimun_wait), 'seconds.')
                print('---------------------------------------------------------')
                time.sleep(minimun_wait)
                run()

            # Arrested
            else:
                print('|You need to serve', str(jail_time), 'seconds for your sentence.')

                if attempt_bust:
                    escaped_jail = bust_out_of_jail()

                    if not escaped_jail:
                        time.sleep(jail_time)

                    run()
                else:
                    time.sleep(jail_time)
                    run()



################################
#   In Game Primary functions  #
################################

# Logs into the game. Takes credentials in plain text.
def login():

    user = credentials['user']
    secret = credentials['secret']

    try:
        username = driver.find_element_by_xpath('//*[@id="login"]/div/form/input[1]')
        password = driver.find_element_by_xpath('//*[@id="login"]/div/form/input[2]')
        login = driver.find_element_by_xpath('//*[@id="login"]/div/form/div[3]/button')
        username.send_keys(user)
        password.send_keys(secret)
        login.click()
        log('Logged in')
        print('Logged in!')
        print('Getting stats...')
    except Exception as e:
        print(e)
        log(e)
        error = '[Exception 1 @ login()] - Could not run login'
        print(error)
        log(error)

    try:
        player_stats()
    except Exception as e:
        print(e)
        log(e)
        error = '[Exception 2 @ login()] - Could not run stats from login()'
        print(error)
        log(error)


# Comites crimes. Selects a random number of crimes to commit.
def crimes():
    url = 'https://www.downtown-mafia.com/crimes'
    driver.get(url)

    new_time = 0

    try:
        crimes_array = driver.find_elements_by_xpath('//*[@type="checkbox"]')
        crimes_checkboxes = get_crimes_checkboxes(crimes_array)

        for each in crimes_checkboxes:
            each.click()

        commit = driver.find_element_by_xpath('//*[@id="crime_submit"]')
        commit.click()

        # Display and log in game message (can be success or failure)
        result = driver.find_element_by_xpath('//*[@id="theBox"]').text
        escaped_result = result.replace('\n', ' ').replace('.', '')
        print('|' + escaped_result)
        m = 'Attempting Crimes: ' + escaped_result
        log(m)

        for word in escaped_result.split():
            if ':' in word:
                try:
                    new_time = get_sleep_time(word)
                except Exception as e:
                    log(e)
                    new_time = -1
    except Exception as e:
        print(e)
        log(e)
        # Some error occured. Log it, print it and break our of while loop.
        error = '[Exception 1 @ crimes()] - Could not commit crimes'
        print(error)
        log(error)

    return new_time


# Commits heists. Selects a random city, a random type and commits.
def heist():
    url = 'https://www.downtown-mafia.com/heists'
    driver.get(url)

    new_time = 0

    try:
        cityId = random.randint(1,3)
        path = '//*[@id="city' + str(cityId) + '"]'
        city = driver.find_element_by_xpath(path)
        city.click()

        criId = random.randint(1,3)

        try:
            cri = '/html/body/div[1]/main/div[2]/div[1]/div[2]/form/table/tbody/tr[2]/td/table/tbody/tr/td[' + str(criId) + ']/button'
            cribtn = driver.find_element_by_xpath(cri)
        except Exception as e:
            log(e)
            cri = '/html/body/div[1]/main/div[2]/div[1]/form/table/tbody/tr[2]/td/table/tbody/tr/td[' + str(criId) + ']/button'
            cribtn = driver.find_element_by_xpath(cri)

        cribtn.click()

        start_heist = driver.find_element_by_xpath('//*[@id="burglary_submit"]')
        start_heist.click()

        result = driver.find_element_by_xpath('//*[@id="theBox"]').text
        escaped_result = result.replace('\n', ' ').replace('.', '')
        print('|' + escaped_result)
        m = 'Attempting heist: ' + escaped_result
        log(m)

        for word in escaped_result.split():
            if ':' in word:
                try:
                    new_time = get_sleep_time(word)
                except Exception as e:
                    log(e)
                    new_time = -1

    except Exception as e:
        print(e)
        log(e)
        # Some error occured. Log it, print it and break our of while loop.
        error = '[Exception 2 @ heist()] - Could not commit heist'
        print(error)
        log(error)

    return new_time


# Commits a car theft. Selects a random city and commits.
def gta():
    url = 'https://www.downtown-mafia.com/cartheft'
    driver.get(url)

    new_time = 0

    try:
        cityId = random.randint(1,3)
        path = '//*[@id="city' + str(cityId) + '"]'
        city = driver.find_element_by_xpath(path)
        city.click()

        steal = driver.find_element_by_xpath('//*[@id="gta_submit"]')
        steal.click()
        time.sleep(1)

        result = driver.find_element_by_xpath('//*[@id="theBox"]').text
        escaped_result = result.replace('\n', ' ').replace('.', '')
        print('|' + escaped_result)
        m = 'Attempting Car Theft: ' + escaped_result
        log(m)

        for word in escaped_result.split():
            if ':' in word:
                try:
                    new_time = get_sleep_time(word)
                except Exception as e:
                    log(e)
                    new_time = -1

    except Exception as e:
        print(e)
        log(e)
        # Some error occured. Log it, print it and break our of while loop.
        error = '[Exception 1 @ gta()] - Could not commit gta'
        print(error)
        log(error)

    return new_time



################################
#   In Game Casino functions   #
################################

# Returns an object with 'type' and 'value' pairs for 'card' input.
def get_card_details(card):
    '''
    Types: Spades, Diamonds, Hearts, Clubs
    Values: A, 2, 3, 4, 5, 6, 7, 8, 9, 10, J, Q, K
    '''

    regex = '[/][SDHCsdhc][/][0-9aAjJqQkK]+[.]'
    card_info = card.get_attribute('style')
    raw_details = re.findall(regex, card_info) #['/s/2.']
    escaped_details = raw_details[0].replace('/','').replace('.','') # s2

    return escaped_details # s2


# Poker brain function. Returns an array of positions.
def poker_brain(cards_object):
    '''
    Types: Spades, Diamonds, Hearts, Clubs
    Values: A, 2, 3, 4, 5, 6, 7, 8, 9, 10, J, Q, K
    '''

    '''
    Example:

    cards_object = {
    '0':'S2',
    '1':'SA',
    '2':'S4',
    '3':'H5',
    '4':'S9'
    }

    precedence
    STRAIGHT FLUSH
    FLUSH
    FOUR OF KIND
    THREE OF KIND
    2 PAIRS
    1 PAIR
    RANDOM
    '''
    log_file = 'poker.txt'
    probable_flush = False
    pairs_found = False
    straight_found = False

    positions = []
    cards_string = '' # 'S2 SA S4 H5 S9 '

    for card in cards_object:
        cards_string += cards_object[card] + ' '

    # Flush checks
    types = 'SDHC'
    flush_object = {}

    for t in types:
        occurence = cards_string.count(t)
        flush_object[t] = occurence

    biggest_occurence = 0
    biggest_type = ''
    for ty in flush_object:
        if flush_object[ty] > biggest_occurence:
            biggest_occurence = flush_object[ty]
            biggest_type = ty

    log('Card string: ' + cards_string + '. Checking for flush. Flush object: ' + str(flush_object), log_file)
    log('Biggest occurence: ' + str(biggest_occurence) + '. Biggest type: ' + biggest_type, log_file)

    if biggest_occurence > 3:
        log('Probable Flush!')

        probable_flush = True
        for position in cards_object:
            if cards_object[position].startswith(biggest_type):
                positions.append(position)

    else:
        # reset variables
        biggest_occurence = 0
        biggest_type = ''
        positions = []

    # Pairs checks only if there is not flush
    if not probable_flush:
        card_values = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
        pairs_object = {}

        for cv in card_values:
            occurence = cards_string.count(cv)
            pairs_object[cv] = occurence

        log('Checking for pairs. Pairs object: ' + str(pairs_object), log_file)

        pairs_found_array = []
        for pair in pairs_object:
            if pairs_object[pair] > 1:
                pairs_found_array.append(pair)

        if len(pairs_found_array) > 0:
            log('Pairs found: ' + str(pairs_found_array), log_file)
            pairs_found = True

            for pair in pairs_found_array:
                for position in cards_object:
                    if cards_object[position].endswith(pair):
                        positions.append(position)

    if not pairs_found and not probable_flush:
        # check for straight
        straight_found = False

    if not pairs_found and not probable_flush and not straight_found:
        log('Odds against us - no flush, no pairs and no straight. Trying random cards.', log_file)
        rn = random.randint(1,5)

        for i in range(rn):
            j = random.randint(0, 4)
            positions.append(j)

    log('Positons returned: ' + str(positions), log_file)
    positions = list(set(positions))

    return positions


# Main video poker function
def video_poker():
    log_file = 'poker.txt'

    # global variables
    game_config = casino_games['video-poker']

    if game_config['active']:
        msg = 'Started video-poker. Your configurations are: ' + str(game_config)
        log(msg, log_file)

        # configuration variables
        bet_amount_config = game_config['bet-amount']

        try:
            # site variable
            bet_amount_field = driver.find_element_by_xpath('//*[@id="startbet"]')
        except Exception as e:
            log(e)
            # run the game
            hold_selection_button = driver.find_element_by_xpath('//*[@id="stand"]')
            hold_selection_button.click()
            time.sleep(2)

            # site variable
            bet_amount_field = driver.find_element_by_xpath('//*[@id="startbet"]')

        # clear bet amount field
        bet_amount_field.clear()

        # add bet as per configuration
        bet_amount_field.send_keys(bet_amount_config)

        # start game
        start_game_button = driver.find_element_by_xpath('//*[@id="start"]')
        start_game_button.click()

        time.sleep(1.5)

        try:
            results = driver.find_element_by_xpath('//*[@id="theBox"]').text
        except Exception as e:
            log(e)
            results = ''

        if 'do not have enough money' in results:
            return 'NO FUNDS'

        # get the first cards array
        cards_fields_array = driver.find_elements_by_xpath('//*[@id="bstable"]/tbody/tr[3]/td/table/tbody/tr/td')
        cards_object = {}

        position = 0
        for card in cards_fields_array:
            info = get_card_details(card)
            cards_object[str(position)] = info
            position += 1

        # do the poker brain mumbo jumbo
        get_selection_cards_positions = poker_brain(cards_object) # returns an array of integers (position) (0 to 4).

        # select the cards
        for position in get_selection_cards_positions:
            card = cards_fields_array[int(position)]
            card.click()

        try:
            # run the game
            hold_selection_button = driver.find_element_by_xpath('//*[@id="stand"]')
            hold_selection_button.click()
        except Exception as e:
            log(e)
            # probably not enough funds!
            return 'NO FUNDS'

        # check results
        time.sleep(2)
        results = driver.find_element_by_xpath('//*[@id="theBox"]')
        print(results.text)
        log('Results: ' + str(results.text), log_file)
        log('\n')

    else:
        # not active in configurations panel
        # no permissons
        print('Sorry, you don\'t have enough permissons.')


# Main black jack function
def black_jack(new_bet_amount=None):
    log_file = 'blackjack.txt'
    game_config = casino_games['black-jack']

    if new_bet_amount:
        bet_amount_config = new_bet_amount
    else:
        bet_amount_config = game_config['bet-amount']

    try:
        amount_field = driver.find_element_by_xpath('//*[@id="startbet"]')
        amount_field.clear()
        amount_field.send_keys(bet_amount_config)

        start_game_button = driver.find_element_by_xpath('//*[@id="start"]')
        start_game_button.click()
    except Exception as e:
        log(e)
        stand_button = driver.find_element_by_xpath('//*[@id="stand"]')
        stand_button.click()

    first_message = driver.find_element_by_xpath('//*[@id="theBox"]').text
    print(first_message)
    log(first_message, log_file)

    if 'won' in first_message:
        return
    elif 'do not have enough money' in first_message:
        log('No funds exception.')
        return 'NO FUNDS'
    else:

        time.sleep(1.5)
        hand_value = int(driver.find_element_by_xpath('//*[@id="playerValue"]').text)

        try:
            while hand_value < 15:
                hit_button = driver.find_element_by_xpath('//*[@id="hit"]')
                hit_button.click()
                time.sleep(2)
                hand_value = int(driver.find_element_by_xpath('//*[@id="playerValue"]').text)
                second_message = driver.find_element_by_xpath('//*[@id="theBox"]').text
                print(second_message)
                log(second_message, log_file)
        except Exception as e:
            log(e)
            return

        hand_value = int(driver.find_element_by_xpath('//*[@id="playerValue"]').text)
        print('Hand check after loop: ',str(hand_value))

        if hand_value > 21:

            print('Too much! Repeating bet.' )
            return

        else:

            try:
                print('Standing with', str(hand_value))
                stand_button = driver.find_element_by_xpath('//*[@id="stand"]')
                stand_button.click()
                time.sleep(2)
                last_message = driver.find_element_by_xpath('//*[@id="theBox"]').text
                print(last_message)
                log(last_message, log_file)

                if 'lost' in last_message:
                    # double amount of money
                    if game_config['double-until-win']:

                        new_bet_amount = bet_amount_config * 2
                        print('Doubling up the amount to $', str(new_bet_amount))
                        black_jack(new_bet_amount)

            except Exception as e:
                log(e)
                # dealer has blackjack option
                return

