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

import PIL.ImageGrab
import psutil
import pyautogui
import win32api
import win32con
import win32gui

# Global variables
listOfChampions = [pictures.ashe, pictures.annie]
client_path = 'C:\\Riot Games\\League of Legends\\LeagueClient.exe'
picture_path = "C:\\Users\\tplev\\PycharmProjects\\lol-leveling-bot-old\\search_images\\"


def attempt_to_click_on(picture, region, is_game=False, click=True, conf=0.90):
    if not globals.go_flag:
        return False
    picture = picture_path + picture
    try:
        if is_game:
            rect = utilities.get_game_coords()
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
    while globals.number_of_games_to_play == -1:
        time.sleep(0.1)
    if globals.number_of_games_to_play is None:
        return
    print('Current status: Starting bot...')
    utilities.save_user_files()
    utilities.set_bot_files()
    # If league is in game
    if utilities.is_league_in_game():
        if globals.stop_flag:
            return
        focus_game_or_client()
        click_mid()
    # Otherwise
    else:
        if globals.stop_flag:
            return
        restart_client()
        print('Current status: Awaiting login...')
        client_open = False
        await_login()
    globals.time_since_last_click = timer()
    print('Current status: Queueing for a game...')
    while True:
        if globals.stop_flag:
            return
        # If bot is paused, wait 1 second then try again
        if not globals.go_flag:
            time.sleep(1)
            globals.time_since_last_click = timer()
            continue
        # If we are in game, simply execute the ClickMid() function
        if utilities.is_league_in_game():
            click_mid()
            continue
        # Check for daily play rewards
        if attempt_to_click_on(pictures.daily_play, daily_play_color):
            daily_play()
        # Check for level up rewards
        attempt_to_click_on(ok_levelup_coords, ok_levelup_color)

        # Check for buttons
        AttemptToClickOnPix(play_coords, play_party_color)
        AttemptToClickOnPix(party_coords, play_party_color)
        AttemptToClickOnPix(coop_vs_ai_coords, coop_vs_ai_color)
        AttemptToClickOnPix(find_match_coords, find_match_color)
        AttemptToClickOnPix(intermediate_coords, intermediate_color)
        AttemptToClickOnPix(confirm_coords, confirm_color)
        AttemptToClickOnPix(find_match_coords, find_match_color)
        AttemptToClickOnPix(accept_coords, accept_color)
        if (LockInChampion()):
            SetStatus("Current status: In champion select...")
            while (AttemptToClickOnPix(champ_locked_coords, champ_locked_color, click=False)):
                time.sleep(1)
        AttemptToClickOnPix(play_again_coords, play_again_color)
        AttemptToClickOnPix(find_match_coords, find_match_color)

        # If 2 minutes has elapsed without doing anything, restart client
        if (DidTimeout(120)):
            ClientStuck()


def did_timeout(seconds):
    global timeSinceLastClick
    if (timer() - timeSinceLastClick > seconds):
        return True
    else:
        return False


def lock_in_champion():
    global listOfChampions
    if (not AttemptToClickOnPix(champ_select_coords, champ_select_color, click=False)):
        return False
    for champion in listOfChampions:
        if (ScanForChamp(champion)):
            if (AttemptToClickOnPix(lock_in_coords, lock_in_color)):
                return True
            else:
                return False
    return False


def scan_for_champ(champColor):
    try:
        rect = GetClientCoords()
        img = PIL.ImageGrab.grab(bbox=rect)
        for x in range(champ_select_left[0], champ_select_right[0]):
            for y in range(champ_select_left[1], champ_select_right[1]):
                pix = img.getpixel((x, y))
                if (pix == champColor):
                    xCoord = rect[0] + x
                    yCoord = rect[1] + y
                    pyautogui.click(x=xCoord, y=yCoord)
                    time.sleep(0.5)
                    return True
    except Exception:
        return False


def click_mid():
    global goFlag, stopFlag, numberOfGamesFinished, gameFlag, lbl1, lbl2, lbl3, timeSinceLastClick
    SetStatus('Current status: Waiting for game to start...')
    # Wait until recall is visible, then we know we're in game
    while (not AttemptToClickOnPix(game_recall_coords, game_recall_color, isGame=True, click=False)):
        if (stopFlag):
            return
        if (not goFlag):
            time.sleep(1)
            continue
        time.sleep(1)
    # Lock the screen once we're in game
    LockScreen()
    # Test to see if the game just started, or if the bot started mid game (check trinket)
    if (AttemptToClickOnPix(game_trinket_coords, game_trinket_color, isGame=True, click=False)):
        SetStatus('Current status: Waiting for minions to spawn...')
        rect = GetGameCoords()
        x = rect[0] + 1170
        y = rect[1] + 666
        win32api.SetCursorPos((x, y))
        time.sleep(15)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, x, y, 0, 0)
        for i in range(70):
            if (stopFlag):
                return
            time.sleep(1)
    # Click mid
    SetStatus('Current status: Running it down mid...')
    gameFlag = 1
    while (gameFlag):
        if (stopFlag):
            return
        if (not goFlag):
            time.sleep(1)
            continue
        # If we're out of game
        if (not IsLeagueInGame()):
            gameFlag = 0
            continue
        try:
            rect = GetGameCoords()
        except Exception as e:
            time.sleep(3)
            continue
        x = rect[0] + 1260
        y = rect[1] + 592
        # Right click down mid
        for i in range(5):
            if (not goFlag):
                continue
            # if(AttemptToClickOnPix(game_health_coords, game_health_color, isGame=True, click=False)):
            # FallBack()
            try:
                win32api.SetCursorPos((x, y))
                win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEDOWN, x, y, 0, 0)
                win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEUP, x, y, 0, 0)
                time.sleep(1)
            except Exception:
                time.sleep(3)
                continue
    if (not stopFlag):
        IncrementGames()
        if (numberOfGamesFinished == numberOfGamesToPlay):
            SetStatus(
                "The bot successfully finished %d out of %d games!" % (numberOfGamesFinished, numberOfGamesToPlay))
            lbl3.config(text="")
            lbl2.config(text="")
            stopFlag = 1
            win32api.PostThreadMessage(th2_id, win32con.WM_QUIT, 0, 0)
            return
        SetStatus("Currently queueing for a game...")
        timeSinceLastClick = timer()
        while (not AttemptToClickOnPix(skip_honor_coords, skip_honor_color)):
            if (stopFlag):
                return
            if (DidTimeout(30)):
                ClientStuck()
                return
            time.sleep(1)


def client_stuck():
    global timeSinceLastClick, goFlag, stopFlag
    SetStatus('Current status: Program stuck.  Rebooting...')
    RestartClient()
    SetStatus('Current status: Awaiting login...')
    AwaitLogin()
    timeSinceLastClick = timer()
    SetStatus('Current status: Queueing for a game...')


def await_login():
    while (True):
        if (stopFlag):
            return
        elif (not goFlag):
            time.sleep(1)
            continue
        elif (AttemptToClickOnPix(play_coords, play_party_color)):
            return
        elif (AttemptToClickOnPix(party_coords, play_party_color)):
            return
        elif (AttemptToClickOnPix(daily_play_coords, daily_play_color)):
            DailyPlay()
            return
        elif (AttemptToClickOnPix(riot_client_play_coords, riot_client_play_color, isRiotClient=True)):
            pass


def lock_screen():
    try:
        rect = GetGameCoords()
        x, y = game_lockscreen_coords
        x = rect[0] + x
        y = rect[1] + y
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
    except:
        pass


def open_client():
    global clientPath
    try:
        subprocess.Popen(clientPath)
    except Exception as e:
        print(e)
        sys.exit()


def restart_client():
    if (IsClientOpen()):
        SetStatus('Current status: Restarting client...')
        try:
            for proc in psutil.process_iter():
                if proc.name() == "LeagueClient.exe":
                    proc.kill()
                    break
        except Exception as e:
            print(e)
        while (IsClientOpen()):
            if (stopFlag):
                return
            time.sleep(1)
    else:
        SetStatus('Current status: Starting client...')
    OpenClient()
    for i in range(5):
        if (stopFlag):
            return
        time.sleep(1)


def daily_play():
    done = False
    start = timer()
    while not done:
        if stopFlag:
            return
        if not goFlag:
            timeSinceLastClick = timer()
            time.sleep(1)
            continue
        # If we don't find anything within 30 seconds, the client is probably stuck
        if DidTimeout(30):
            ClientStuck()
        AttemptToClickOn('dailyplay_caitlyn.png', None)
        AttemptToClickOn('dailyplay_illaoi.png', None)
        AttemptToClickOn('dailyplay_ziggs.png', None)
        if (AttemptToClickOnPix(daily_play_thresh_coords, daily_play_thresh_color)):
            AttemptToClickOnPix(daily_play_middle_select_coords, daily_play_middle_select_color)
        AttemptToClickOn('dailyplay_ekko.png', None)
        AttemptToClickOn('select_daily.png', LOWER_HALF_RECT)
        done = AttemptToClickOnPix(daily_play_ok_coords, daily_play_ok_color)
    return


def move_windows():
    try:
        if IsClientOpen():
            hwnd = win32gui.FindWindow(None, 'League of Legends')
            win32gui.MoveWindow(hwnd, 350, 180, 1280, 720, True)
        if IsLeagueInGame():
            hwnd = win32gui.FindWindow(None, 'League of Legends (TM) Client')
            win32gui.MoveWindow(hwnd, 600, 180, 1280, 720, True)
    except Exception as e:
        return


def focus_game_or_client():
    pass
    # if(IsLeagueInGame()):
    #     SetForegroundWindow(find_window(title='League of Legends (TM) Client'))
    # elif(IsClientOpen()):
    #     SetForegroundWindow(find_window(title='League of Legends'))
