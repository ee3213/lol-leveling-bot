import shutil
import os
import win32gui
from pywinauto.findwindows import find_window
from timeit import default_timer as timer
import robot

import globals

user_settings_path = os.path.join(os.getcwd(), "user_settings")
bot_settings_path = os.path.join(os.getcwd(), "bot_settings")
lol_settings_path = "C:\\Riot Games\\League of Legends\\Config"


def setup():
    globals.picture_path = os.path.join(os.getcwd(), "search_images")
    find_league_location()
    save_user_files()
    set_bot_files()


def find_league_location():
    global lol_settings_path
    print("Attempting to locate League of Legends...")
    for r, d, f in os.walk("C:\\"):
        for files in f:
            if files == "LeagueClient.exe":
                print("Successfully found %s" % r)
                globals.lol_client_path = os.path.join(r, files)
                lol_settings_path = os.path.join(r, "Config")
                return
    for r, d, f in os.walk("D:\\"):
        for files in f:
            if files == "LeagueClient.exe":
                print("Successfully found %s" % r)
                globals.lol_client_path = os.path.join(r, files)
                lol_settings_path = os.path.join(r, "Config")
                return
    print("Failed to locate League of Legends.")


def save_user_files():
    global user_settings_path
    try:
        print("Attempting to create folder %s..." % user_settings_path)
        os.mkdir(user_settings_path)
        print("Successfully created %s" % user_settings_path)
    except FileExistsError:
        print("Folder %s already exists" % user_settings_path)
    for files in globals.files_to_replace:
        shutil.copy(os.path.join(lol_settings_path, files), os.path.join(user_settings_path, files))
    print("Successfully saved user settings to %s" % user_settings_path)


def set_bot_files():
    for files in globals.files_to_replace:
        shutil.copy(os.path.join(bot_settings_path, files), os.path.join(lol_settings_path, files))
    print("Successfully loaded bot settings to %s" % lol_settings_path)


def set_user_files():
    for files in globals.files_to_replace:
        shutil.copy(os.path.join(user_settings_path, files), os.path.join(lol_settings_path, files))
    print("Successfully loaded user settings to %s" % lol_settings_path)


def get_client_coords():
    hwnd = win32gui.FindWindow(None, 'League of Legends')
    rect = win32gui.GetWindowRect(hwnd)
    return rect


def get_game_coords():
    hwnd = win32gui.FindWindow(None, 'League of Legends (TM) Client')
    rect = win32gui.GetWindowRect(hwnd)
    return rect


def get_riot_client_coords():
    hwnd = win32gui.FindWindow(None, 'Riot Client')
    rect = win32gui.GetWindowRect(hwnd)
    return rect


def is_league_in_game():
    try:
        find_window(title='League of Legends (TM) Client')
        return True
    except Exception:
        return False


def is_client_open():
    try:
        find_window(title='League of Legends')
        return True
    except Exception:
        return False


def is_riot_client_open():
    try:
        find_window(title='Riot Client')
        return True
    except Exception:
        return False


def set_status(status):
    globals.last_status = status
    print(status)


def test_speed(picture, region=None):
    globals.picture_path = os.path.join(os.getcwd(), "search_images")
    start = timer()
    found = robot.attempt_to_click_on(picture, region)
    end = timer()
    if found:
        print("Picture found!")
    else:
        print("Picture not found!")
    print("Total time elapsed = %f" % (end - start))

