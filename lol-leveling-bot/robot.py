#   @author: Mitchell Levesque                                                          #
#   @desc  : A script for the game League of legends which will automatically queue     #
#            a player for intermediate bots, attack move on the enemy nexus until game  #
#            ends, and then repeat.                                                     #

import subprocess
import sys
import time
from timeit import default_timer as timer

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

# Global variables
listOfChampions = [pictures.ashe, pictures.annie]


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


def attempt_to_click_on(picture, region, is_game=False, is_riot_client=False, click=True, conf=0.90):
    if not globals.go_flag:
        return False
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
            time.sleep(0.5)
            globals.time_since_last_click = timer()
            return True
    except Exception:
        return False


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
    while True:
        pause_if_needed()

        # If we are in game, simply execute the click_mid() function
        if utilities.is_league_in_game():
            complete_game()
            continue

        # Check for daily play rewards
        if attempt_to_click_on(pictures.daily_play, None):
            daily_play()

        # Check for level up rewards
        attempt_to_click_on(pictures.ok, None)

        # Check for buttons
        attempt_to_click_on(pictures.play_button, None)
        attempt_to_click_on(pictures.party, None)
        attempt_to_click_on(pictures.coop_vs_ai, None)
        attempt_to_click_on(pictures.find_match, None)
        attempt_to_click_on(pictures.intermediate_bots, None)
        attempt_to_click_on(pictures.confirm, None)
        attempt_to_click_on(pictures.find_match, None)
        attempt_to_click_on(pictures.accept, None)
        if lock_in_champion():
            utilities.set_status("Current status: In champion select...")
            while attempt_to_click_on(pictures.intermediate_bots, None, click=False):
                time.sleep(1)
        attempt_to_click_on(pictures.play_again, None)
        attempt_to_click_on(pictures.find_match, None)

        # If 2 minutes has elapsed without doing anything, restart client
        if did_timeout(120):
            client_stuck()


def did_timeout(seconds):
    if timer() - globals.time_since_last_click > seconds:
        return True
    else:
        return False


def lock_in_champion():
    for champion in listOfChampions:
        if attempt_to_click_on(champion, None):
            time.sleep(2)
            if attempt_to_click_on(pictures.lockin, None):
                return True
            else:
                return False
    return False


def complete_game():
    utilities.set_status('Waiting for game to start...')

    # Wait until recall is visible, then we know we're in game
    while not attempt_to_click_on(pictures.recall, None, is_game=True, click=False):
        pause_if_needed()

    # Lock the screen once we're in game
    lock_screen()

    # Test to see if the game just started, or if the bot started mid game (check trinket)
    if attempt_to_click_on(pictures.trinket, None, is_game=True, click=False):
        utilities.set_status('Waiting for minions to spawn...')
        rect = utilities.get_game_coords()
        x = rect[0] + 1170
        y = rect[1] + 666
        win32api.SetCursorPos((x, y))
        time.sleep(15)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, x, y, 0, 0)
        for i in range(70):
            time.sleep(1)

    # Click mid
    utilities.set_status('Running it down mid...')
    globals.game_flag = 1
    while globals.game_flag:
        pause_if_needed()

        # If we're out of game
        if not utilities.is_league_in_game():
            globals.game_flag = 0
            continue
        try:
            rect = utilities.get_game_coords()
        except Exception:
            time.sleep(3)
            continue
        x = rect[0] + 1260
        y = rect[1] + 592
        # Right click down mid
        for i in range(5):
            pause_if_needed()
            try:
                win32api.SetCursorPos((x, y))
                win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEDOWN, x, y, 0, 0)
                win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEUP, x, y, 0, 0)
                time.sleep(1)
            except Exception:
                time.sleep(3)
                continue
    # Once the game is finished
    increment_games()
    if globals.number_of_games_finished == globals.number_of_games_to_play:
        utilities.set_status("The bot successfully finished %d out of %d games!" %
                             (globals.number_of_games_finished, globals.number_of_games_to_play))
        quit_bot()
        return
    utilities.set_status("Currently queueing for a game...")
    globals.time_since_last_click = timer()
    while not attempt_to_click_on(pictures.skip_honor, None):
        if did_timeout(30):
            client_stuck()
            return
        time.sleep(1)


def client_stuck():
    utilities.set_status('Program stuck.  Rebooting...')
    restart_client()
    utilities.set_status('Awaiting login...')
    await_login()
    globals.time_since_last_click = timer()
    utilities.set_status('Queueing for a game...')


def await_login():
    while True:
        if globals.stop_flag:
            return
        elif not globals.go_flag:
            time.sleep(1)
            continue
        elif attempt_to_click_on(pictures.play_button, None):
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
    # games_left = globals.number_of_games_to_play - globals.number_of_games_finished


def focus_game_or_client():
    pass
    # if(IsLeagueInGame()):
    #     SetForegroundWindow(find_window(title='League of Legends (TM) Client'))
    # elif(IsClientOpen()):
    #     SetForegroundWindow(find_window(title='League of Legends'))


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
