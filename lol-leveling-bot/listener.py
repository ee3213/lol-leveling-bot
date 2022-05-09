#   @author: Mitchell Levesque                                                          #
#   @desc  : A file that listens for global key presses to handle pausing hotkeys       #

import threading

import pyWinhook
import pythoncom
import win32api
import win32con
import time

import globals
import robot
import utilities


def on_keyboard_event(event):
    if event.Key == globals.pause_key:
        robot.set_to_pause()
    elif event.Key == globals.move_windows_key:
        utilities.move_windows()
    # return True to pass the event to other handlers
    return True


def hook_keyboard():
    # save the id of the thread
    globals.listener_thread_id = threading.get_ident()

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
    if globals.listener_thread_id is not None:
        win32api.PostThreadMessage(globals.listener_thread_id, win32con.WM_QUIT, 0, 0)
