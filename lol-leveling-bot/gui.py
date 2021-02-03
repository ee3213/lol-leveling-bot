import sys
import tkinter as tk
import tkinter.simpledialog

import globals
import listener

window = tk.Tk()


def build():
    # Create the window
    global window
    window.title('League Leveling Bot')
    window.resizable(False, False)
    window.focus_set()
    window.protocol("WM_DELETE_WINDOW", destroy)
    window.geometry("300x105+800+400")

    # Ask the user how many games to play
    globals.number_of_games_to_play = tkinter.simpledialog.askinteger(title="League Leveling Bot",
                                                                      prompt="How many games do you want to play?",
                                                                      minvalue=1, maxvalue=9999, parent=window)
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
    globals.quit_button = tk.Button(window, text="Quit", width=10, command=destroy)
    globals.quit_button.grid(row=3, column=2)

    # TODO create pause function
    # Create pause button
    globals.pause_button = tk.Button(window, text="Pause (F6)", width=10, command=destroy)
    globals.pause_button.grid(row=3, column=1)

    # TODO create settings button + GUI
    # Create settings button
    globals.settings_button = tk.Button(window, text="Settings", width=10, command=destroy)
    globals.settings_button.grid(row=3, column=0)

    # Configure rows/columns
    window.grid_columnconfigure(0, weight=1)
    window.grid_columnconfigure(1, weight=1)
    window.grid_columnconfigure(2, weight=1)
    window.grid_rowconfigure(3, weight=1)

    # Start loop
    window.mainloop()


def destroy():
    window.destroy()
    listener.stop()
    globals.listener_thread.join()
    sys.exit()
