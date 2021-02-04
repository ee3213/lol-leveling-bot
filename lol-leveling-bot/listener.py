#   @author: Mitchell Levesque                                                          #
#   @desc  : A file that listens for global key presses to handle pausing hotkeys       #

import threading

import pyWinhook
import pythoncom
import win32api
import win32con
import time

import globals

listener_thread_id = None  # used for terminating the thread properly


# TODO make Pause() function for bot class
def on_keyboard_event(event):
    if event.Key == globals.pause_key:
        if globals.go_flag == 0:
            globals.status_label.config(text=globals.last_status)
            globals.pause_button.config(text="Pause (F6)")
            globals.go_flag = 1
        else:
            globals.last_status = globals.status_label.cget("text")
            globals.status_label.config(text="Bot paused!")
            globals.pause_button.config(text="Unpause (F6)")
            globals.go_flag = 0
    # return True to pass the event to other handlers
    return True


def hook_keyboard():
    global listener_thread_id

    # wait until the gui thread gets an input
    while globals.number_of_games_to_play == -1:
        time.sleep(0.1)
    # if the user canceled input, then return
    if globals.number_of_games_to_play is None:
        return

    # save the id of the thread
    listener_thread_id = threading.get_ident()

    # create a hook manager
    hm = pyWinhook.HookManager()
    # watch for all mouse events
    hm.KeyDown = on_keyboard_event
    # set the hook
    hm.HookKeyboard()
    # wait forever
    pythoncom.PumpMessages()


def create_thread():
    globals.listener_thread = threading.Thread(target=hook_keyboard)
    globals.listener_thread.start()


def stop():
    if listener_thread_id is not None:
        win32api.PostThreadMessage(listener_thread_id, win32con.WM_QUIT, 0, 0)
