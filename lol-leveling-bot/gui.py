#   @author: Mitchell Levesque                                                          #
#   @desc  : A file containing all code for building the user interfaces.               #

import sys
import tkinter as tk

import globals
import listener
import utilities

window = tk.Tk()
setting_win = None


def build():
    # Create the window
    global window, pause_button
    window.title('League Leveling Bot')
    window.resizable(False, False)
    window.focus_set()
    window.protocol("WM_DELETE_WINDOW", destroy)
    window.geometry("300x105+800+400")

    # Ask the user how many games to play
    globals.number_of_games_to_play = 321

    # If the user hit cancel, quit the program
    if globals.number_of_games_to_play is None:
        destroy()

    # Create status label
    globals.last_status = "Current status: Starting bot..."
    globals.status_label = tk.Label(window, text=globals.last_status)
    globals.status_label.grid(row=0, column=0, columnspan=3)

    # Create games played label
    globals.games_played_label = tk.Label(window,
                                          text="Number of games played so far: %d" % globals.number_of_games_finished)
    globals.games_played_label.grid(row=1, column=0, columnspan=3)

    # Create games left to play label
    if globals.number_of_games_to_play == 1:
        globals.games_left_label = tk.Label(window, text="Bot will stop after this game.")
    else:
        globals.games_left_label = tk.Label(window, text="Bot will stop after %d more games." % int(
            globals.number_of_games_to_play - globals.number_of_games_finished))
    globals.games_left_label.grid(row=2, column=0, columnspan=3)

    # Create quit button
    quit_button = tk.Button(window, text="Quit", width=12, command=destroy)
    quit_button.grid(row=3, column=2)

    # TODO create pause function
    # Create pause button
    globals.pause_button = tk.Button(window, text="Pause (F6)", width=12, command=destroy)
    globals.pause_button.grid(row=3, column=1)

    # TODO create settings button + GUI
    # Create settings button
    settings_button = tk.Button(window, text="Settings", width=12, command=build_settings)
    settings_button.grid(row=3, column=0)

    # Configure rows/columns
    window.grid_columnconfigure(0, weight=1)
    window.grid_columnconfigure(1, weight=1)
    window.grid_columnconfigure(2, weight=1)
    window.grid_rowconfigure(3, weight=1)

    # Start loop
    window.mainloop()


# TODO: For some reason the entry widgets crash when text is spammed
def build_settings():
    global setting_win

    # Create the settings window
    setting_win = tk.Toplevel()
    setting_win.title("Settings")
    setting_win.resizable(False, False)
    setting_win.focus_set()
    setting_win.geometry("300x105+800+400")
    setting_win.grab_set()

    # Create way to change number of games
    num_of_games_to_play_label = tk.Label(setting_win, text="Number of games left to play:")
    num_of_games_to_play_label.grid(row=0, column=0)

    current_num_of_games = tk.StringVar()
    limit_entry(current_num_of_games, 4)
    globals.settings_num_games = tk.Entry(setting_win, textvariable=current_num_of_games)
    current_num_of_games.set("%d" % int(globals.number_of_games_to_play - globals.number_of_games_finished))
    globals.settings_num_games.grid(row=0, column=1)

    # Create way to change the pause hotkey
    num_of_games_to_play_label = tk.Label(setting_win, text="Pause hotkey:")
    num_of_games_to_play_label.grid(row=1, column=0)

    current_pause_hotkey = tk.StringVar()
    limit_entry(current_pause_hotkey, 3)
    globals.settings_pause_key = tk.Entry(setting_win, textvariable=current_pause_hotkey)
    current_pause_hotkey.set("%s" % globals.pause_key)
    globals.settings_pause_key.grid(row=1, column=1)

    # Create save button
    save_button = tk.Button(setting_win, text="Save", width=10, command=save)
    save_button.grid(row=2, column=0)

    # Create cancel button
    save_button = tk.Button(setting_win, text="Cancel", width=10, command=lambda: setting_win.destroy())
    save_button.grid(row=2, column=1)

    # Configure rows/columns
    setting_win.grid_columnconfigure(0, weight=1)
    setting_win.grid_rowconfigure(0, weight=1)
    setting_win.grid_rowconfigure(1, weight=1)
    setting_win.grid_rowconfigure(2, weight=1)


def limit_entry(str_to_limit, length):
    def callback(str_var):
        c = str_var.get()[0:length]
        str_var.set(c)
    str_to_limit.trace("w", lambda name, index, mode, str_var=str_to_limit: callback(str_to_limit))


def save():
    globals.number_of_games_to_play = int(globals.settings_num_games.get())
    globals.pause_key = globals.settings_pause_key.get()
    utilities.reset_labels()
    setting_win.destroy()


def destroy():
    window.destroy()
    listener.stop()
    globals.listener_thread.join()
    sys.exit()
