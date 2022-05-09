import subprocess
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


def run():
    utilities.set_status('Starting bot...')

    # If league is already in game, finish the game
    if utilities.is_league_in_game():
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

        # Check for clash notification
        attempt_to_click_on(pictures.clash, None)

        # Check if champ select bugged
        attempt_to_click_on(pictures.ok_champ_select_bug, None)

        # Check if we're in champ select
        if attempt_to_click_on(pictures.choose_champ, regions.choose_champ, click=False):
            champ_select()

        # Check for level 30
        if attempt_to_click_on(pictures.level_30, None, click=False):
            utilities.set_status("The account has reached level 30!")
            stop_bot()

        # Check for key fragment popups
        attempt_to_click_on(pictures.key_fragment, None)

        # Check for other buttons
        attempt_to_click_on(pictures.play_button, regions.play_button)
        attempt_to_click_on(pictures.party, regions.party_button)
        attempt_to_click_on(pictures.coop_vs_ai, regions.coop_vs_ai)
        attempt_to_click_on(pictures.intermediate_bots, regions.intermediate_bots)
        attempt_to_click_on(pictures.confirm, regions.confirm)
        attempt_to_click_on(pictures.find_match, regions.find_match)
        attempt_to_click_on(pictures.accept, regions.accept)
        attempt_to_click_on(pictures.play_again, None)

        # If 2 minutes has elapsed without doing anything, restart client
        if did_timeout(120):
            client_stuck()


def complete_game():
    utilities.set_status('Waiting for game to start...')

    # Wait until lock screen button is visible, then we know we're in game
    while not attempt_to_click_on(pictures.lock_camera, None, is_game=True, click=False):
        pause_if_needed()

    # Click mid
    utilities.set_status('Running it down mid...')
    while True:
        pause_if_needed()

        # If we're out of game
        if not utilities.is_league_in_game():
            break

        # If the camera isn't locked, lock it
        if attempt_to_click_on(pictures.lock_camera, None, is_game=True, click=False):
            lock_screen()

        # Get the location of league window
        try:
            rect = utilities.get_game_coords()
        except Exception:
            continue
        x = rect[0] + 1260
        y = rect[1] + 592

        # Right click down mid every 3 seconds
        try:
            win32api.SetCursorPos((x, y))
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, x, y, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, x, y, 0, 0)
            time.sleep(3)
        except Exception:
            continue

    # Once the game is finished
    increment_games()

    # Skip honor
    globals.time_since_last_click = timer()
    while not attempt_to_click_on(pictures.skip_honor, None):
        if did_timeout(30):
            client_stuck()
            return
        time.sleep(1)

    # Requeue for another game
    utilities.set_status("Queueing for a game...")


def attempt_to_click_on(picture, region, is_game=False, is_riot_client=False, click=True, conf=0.95, delay=True):
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
            width = region[2] - region[0]
            height = region[3] - region[1]
            rect = (start_x, start_y, width, height)
        coordinates = pyautogui.locateCenterOnScreen(picture, region=rect, confidence=conf)
        if coordinates is not None:
            if click:
                pyautogui.click(coordinates[0], coordinates[1])
            globals.time_since_last_click = timer()
            if delay:
                time.sleep(1)
            return True
    except Exception:
        return False


def did_timeout(seconds):
    if timer() - globals.time_since_last_click > seconds:
        return True
    else:
        return False


def champ_select():
    for champion in list_of_champs:
        if attempt_to_click_on(champion, regions.champ_select):
            time.sleep(2)
            if attempt_to_click_on(pictures.lockin, regions.lockin):
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
        if attempt_to_click_on(pictures.play_button, regions.play_button):
            return
        elif attempt_to_click_on(pictures.party, regions.party_button):
            return
        elif attempt_to_click_on(pictures.daily_play, None):
            daily_play()
            return
        elif utilities.is_league_in_game():
            complete_game()
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
        time.sleep(0.5)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
    except Exception:
        pass


def open_client():
    try:
        subprocess.Popen(globals.lol_client_path)
    except Exception:
        print("Couldn't open league client")
        stop_bot()


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
            time.sleep(1)
    else:
        utilities.set_status('Starting client...')
    open_client()


def daily_play():
    print("Claiming daily play rewards...")
    done = False
    while not done:
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
    utilities.set_status("The bot has finished %d games." % globals.number_of_games_finished)


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


def stop_bot():
    listener.stop()
    print("Bot has terminated.")
    while True:
        time.sleep(3)
