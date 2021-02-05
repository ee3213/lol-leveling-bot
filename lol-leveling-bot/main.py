#   @author: Mitchell Levesque                                                          #
#   @desc  : A program for the game League of legends which will automatically queue    #
#            a player for intermediate bots, attack move on the enemy nexus until game  #
#            ends, and then repeat.                                                     #

import os

import listener
import utilities
import gui


if __name__ == '__main__':
    utilities.setup()
    # listener.create_thread()
    #utilities.find_league_location()
