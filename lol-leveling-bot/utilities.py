import shutil
import os
import win32gui
# from pywinauto.findwindows import find_window

import globals


def save_user_files():
    src = 'C:\\Riot Games\\League of Legends\\Config'
    dst = '.\\user-settings'
    for files in globals.files_to_replace:
        shutil.copy(os.path.join(src, files), os.path.join(dst, files))


def set_bot_files():
    src = '.\\bot-settings'
    dst = 'C:\\Riot Games\\League of Legends\\Config'
    for files in globals.files_to_replace:
        shutil.copy(os.path.join(src, files), os.path.join(dst, files))


def set_user_files():
    src = '.\\user-settings'
    dst = 'C:\\Riot Games\\League of Legends\\Config'
    for files in globals.files_to_replace:
        shutil.copy(os.path.join(src, files), os.path.join(dst, files))


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


def increment_games():
    globals.number_of_games_finished = globals.number_of_games_finished + 1
    games_left = globals.number_of_games_to_play - globals.number_of_games_finished
