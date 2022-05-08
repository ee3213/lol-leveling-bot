# Setting variables
pause_key = "F6"

# Numerical variables
number_of_games_to_play = -1  # default to -1 to tell the robot and listener threads to wait
number_of_games_finished = 0
go_flag = 1
stop_flag = 0
time_since_last_click = 0

# String variables
last_status = None

# File variables
lol_client_path = None
picture_path = None
files_to_replace = ['game.cfg', 'input.ini']

# Thread variables
listener_thread = None
listener_thread_id = None
bot_thread = None
