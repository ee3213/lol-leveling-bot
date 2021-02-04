import globals


def reset_labels():
    if globals.go_flag == 1:
        globals.pause_button.config(text="Pause (%s)" % globals.pause_key)
        globals.status_label.config(text=globals.last_status)
    else:
        globals.pause_button.config(text="Unpause (%s)" % globals.pause_key)
        globals.last_status = globals.status_label.cget("text")
        globals.status_label.config(text="Bot paused!")
    globals.games_played_label.config(text="Number of games played so far: %d" % globals.number_of_games_finished)
    if globals.number_of_games_to_play == 1:
        globals.games_left_label.config(text="Bot will stop after this game.")
    else:
        globals.games_left_label.config(text="Bot will stop after %d more games." % int(
            globals.number_of_games_to_play - globals.number_of_games_finished))
