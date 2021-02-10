#   @author: Mitchell Levesque                                                          #
#   @desc  : A program for the game League of legends which will automatically queue    #
#            a player for intermediate bots, attack move on the enemy nexus until game  #
#            ends, and then repeat.                                                     #

import atexit

import robot
import utilities
import listener
import globals


def exit_handler():
    utilities.set_user_files()
    print("Bot has terminated.")


if __name__ == '__main__':

    atexit.register(exit_handler)

    # Ask the user how many games they want to play
    while True:
        try:
            globals.number_of_games_to_play = int(input("How many games do you want to play? "))
            if globals.number_of_games_to_play < 1 or globals.number_of_games_to_play > 100:
                raise ValueError
            break
        except ValueError:
            print("Invalid integer. The number must be in the range of 1-100.")

    # Perform setup
    utilities.setup()

    # Create listener thread
    listener.create_thread()

    # Run bot
    robot.run()

