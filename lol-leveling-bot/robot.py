#   @author: Mitchell Levesque                                                          #
#   @desc  : A script for the game League of legends which will automatically queue     #
#            a player for intermediate bots, attack move on the enemy nexus until game  #
#            ends, and then repeat.                                                     #

import subprocess
import sys
import time
from timeit import default_timer as timer

from pywinauto.findwindows import find_window

import globals
import utilities
import pictures
import regions
import listener

import psutil
import pyautogui
import win32api
import win32con
import win32gui
import os

# Champion variables
list_of_champs = [pictures.ashe, pictures.annie]


def start():
    # Ask the user how many games they want to play
    while True:
        try:
            globals.number_of_games_to_play = int(input("How many games do you want to play? "))
            if globals.number_of_games_to_play < 1 or globals.number_of_games_to_play > 100:
                raise ValueError
            break
        except ValueError:
            print("Invalid integer. The number must be in the range of 1-100.")

    # Perform setup
    utilities.setup()

    # Create listener thread
    listener.create_thread()

    # Run bot
    run()


def run():
    utilities.set_status('Starting bot...')

    # If league is in game, finish the game
    if utilities.is_league_in_game():
        focus_game_or_client()
        complete_game()

    # Otherwise, restart client and wait for login
    else:
        restart_client()
        utilities.set_status('Awaiting login...')
        await_login()

    # Start queueing up
    globals.time_since_last_click = timer()
    utilities.set_status('Queueing for a game...')

    # Start loop
    while True:
        pause_if_needed()

        # If game has started, complete the game
        if utilities.is_league_in_game():
            complete_game()
            continue

        # Check for daily play rewards
        if attempt_to_click_on(pictures.daily_play, None, click=False):
            daily_play()

        # Check for level up rewards
        attempt_to_click_on(pictures.ok, None)

        # Check if we're in champ select
        if attempt_to_click_on(pictures.choose_champ, None, click=False):
            champ_select()

        # Check for other buttons
        attempt_to_click_on(pictures.play_button, None)
        attempt_to_click_on(pictures.party, None)
        attempt_to_click_on(pictures.coop_vs_ai, None)
        attempt_to_click_on(pictures.intermediate_bots, None)
        attempt_to_click_on(pictures.confirm, None)
        attempt_to_click_on(pictures.find_match, None)
        attempt_to_click_on(pictures.accept, None)
        attempt_to_click_on(pictures.play_again, None)
        attempt_to_click_on(pictures.find_match, None)

        # If 2 minutes has elapsed without doing anything, restart client
        if did_timeout(120):
            client_stuck()


def complete_game():
    utilities.set_status('Waiting for game to start...')

    # Wait until recall is visible, then we know we're in game
    while not attempt_to_click_on(pictures.recall, None, is_game=True, click=False):
        pause_if_needed()

    # Lock the screen once we're in game
    lock_screen()

    # Click mid
    utilities.set_status('Running it down mid...')
    game_flag = 1
    while game_flag:
        pause_if_needed()

        # If we're out of game
        if not utilities.is_league_in_game():
            game_flag = 0
            continue

        # Get the location of league window
        try:
            rect = utilities.get_game_coords()
        except Exception:
            continue
        x = rect[0] + 1260
        y = rect[1] + 592

        # Right click down mid every 1 second
        try:
            win32api.SetCursorPos((x, y))
            win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEDOWN, x, y, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEUP, x, y, 0, 0)
            time.sleep(1)
        except Exception:
            continue

    # Once the game is finished
    increment_games()

    # Check to see if the bot is finished all games
    if globals.number_of_games_finished == globals.number_of_games_to_play:
        quit_bot()
        return

    # Skip honor
    globals.time_since_last_click = timer()
    while not attempt_to_click_on(pictures.skip_honor, None):
        if did_timeout(30):
            client_stuck()
            return
        time.sleep(1)

    # Requeue for another game
    utilities.set_status("Currently queueing for a game...")


def attempt_to_click_on(picture, region, is_game=False, is_riot_client=False, click=True, conf=0.95):
    if not globals.go_flag:
        return False
    focus_game_or_client()
    picture = os.path.join(globals.picture_path, picture)
    try:
        if is_game:
            rect = utilities.get_game_coords()
        elif is_riot_client:
            rect = utilities.get_riot_client_coords()
        else:
            rect = utilities.get_client_coords()
        if region is not None:
            start_x = rect[0] + region[0]
            start_y = rect[1] + region[1]
            width = region[2]
            height = region[3]
            rect = (start_x, start_y, width, height)
        coordinates = pyautogui.locateCenterOnScreen(picture, region=rect, confidence=conf)
        if coordinates is not None:
            if click:
                pyautogui.click(coordinates[0], coordinates[1])
            globals.time_since_last_click = timer()
            time.sleep(1)
            return True
    except Exception:
        time.sleep(1)
        return False


def did_timeout(seconds):
    if timer() - globals.time_since_last_click > seconds:
        return True
    else:
        return False


def champ_select():
    utilities.set_status("In champion select...")
    for champion in list_of_champs:
        if attempt_to_click_on(champion, None):
            time.sleep(2)
            if attempt_to_click_on(pictures.lockin, None):
                return True
            else:
                return False
    return False


def client_stuck():
    utilities.set_status('Bot stuck.  Rebooting...')
    restart_client()
    utilities.set_status('Awaiting login...')
    await_login()
    globals.time_since_last_click = timer()
    utilities.set_status('Queueing for a game...')


def await_login():
    while True:
        pause_if_needed()
        if attempt_to_click_on(pictures.play_button, None):
            return
        elif attempt_to_click_on(pictures.party, None):
            return
        elif attempt_to_click_on(pictures.daily_play, None):
            daily_play()
            return
        elif attempt_to_click_on(pictures.riot_client_play, None, is_riot_client=True):
            pass


def lock_screen():
    try:
        rect = utilities.get_game_coords()
        x, y = regions.game_lockscreen_coords
        x = rect[0] + x
        y = rect[1] + y
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
    except Exception:
        pass


def open_client():
    try:
        subprocess.Popen(globals.lol_client_path)
    except Exception as e:
        print("Couldn't open league client")
        sys.exit()


def restart_client():
    if utilities.is_client_open():
        utilities.set_status('Restarting client...')
        try:
            for proc in psutil.process_iter():
                if proc.name() == "LeagueClient.exe":
                    proc.kill()
                    break
        except Exception as e:
            print(e)
        while utilities.is_client_open():
            if globals.stop_flag:
                return
            time.sleep(1)
    else:
        utilities.set_status('Starting client...')
    open_client()
    for i in range(5):
        if globals.stop_flag:
            return
        time.sleep(1)


def daily_play():
    print("Claiming daily play rewards...")
    done = False
    while not done:
        if globals.stop_flag:
            return
        if not globals.go_flag:
            globals.time_since_last_click = timer()
            time.sleep(1)
            continue
        # If we don't find anything within 30 seconds, the client is probably stuck
        if did_timeout(30):
            client_stuck()
        attempt_to_click_on(pictures.daily_play_caitlyn, None)
        attempt_to_click_on(pictures.daily_play_illaoi, None)
        attempt_to_click_on(pictures.daily_play_ziggs, None)
        attempt_to_click_on(pictures.daily_play_thresh, None)
        attempt_to_click_on(pictures.daily_play_ekko, None)
        attempt_to_click_on(pictures.select_daily, None)
        done = attempt_to_click_on(pictures.ok_daily, None)
    return


def move_windows():
    try:
        if utilities.is_client_open():
            hwnd = win32gui.FindWindow(None, 'League of Legends')
            win32gui.MoveWindow(hwnd, 350, 180, 1280, 720, True)
        if utilities.is_league_in_game():
            hwnd = win32gui.FindWindow(None, 'League of Legends (TM) Client')
            win32gui.MoveWindow(hwnd, 600, 180, 1280, 720, True)
    except Exception:
        return


def increment_games():
    globals.number_of_games_finished = globals.number_of_games_finished + 1
    if globals.number_of_games_finished == globals.number_of_games_to_play:
        utilities.set_status("The bot successfully finished %d out of %d games!" %
                             (globals.number_of_games_finished, globals.number_of_games_to_play))
    else:
        utilities.set_status("The bot finished %d out of %d games." %
                             (globals.number_of_games_finished, globals.number_of_games_to_play))


def focus_game_or_client():
    if utilities.is_league_in_game():
        win32gui.SetForegroundWindow(find_window(title='League of Legends (TM) Client'))
    elif utilities.is_client_open():
        win32gui.SetForegroundWindow(find_window(title='League of Legends'))


def set_to_pause():
    if globals.go_flag == 0:
        globals.go_flag = 1
        utilities.set_status(globals.last_status)
    else:
        globals.go_flag = 0
        print("Bot paused.")


def pause_if_needed():
    while not globals.go_flag:
        time.sleep(1)
    globals.time_since_last_click = timer()


def quit_bot():
    listener.stop()
    globals.stop_flag = 1
    utilities.set_user_files()
    print("Bot has finished all games.")
    print("Bot will now quit.")
    while True:
        time.sleep(3)
