import argparse
import sys
from curses import wrapper
from typing import Optional

from src.fileUtils import get_logfile_dir, get_machine_logfile
from src.game import Game
from src.gameFinder import find_game
from src.generator import generate_con_file
from src.gitUtils import save_to_git
from src.logger import setup_logger
from src.userConfig import get_user_config


def get_args():
    parser = argparse.ArgumentParser(
        prog='Connections',
        description='Plays and shares homemade connections')
    parser.add_argument('-g', '--generate', action='store_true', help="generate a connections game")
    parser.add_argument('-a', '--author', type=str, help="specify who's game you'd like to play")
    parser.add_argument('-n', '--number', type=str, help="pick a specific game to play (author required)")
    parser.add_argument('-u', '--username', type=str, help="use this username instead of configured username "
                                                           "(will not overwrite config file)")
    parser.add_argument('-d', '--no-git', action='store_true', help="only use for development")
    parser.add_argument('-t', '--tutorial', action='store_true', help="show a tutorial on how to play")
    return parser.parse_args()


GAME: Optional[Game] = None


def print_tutorial():
    print('''
*************** OVERVIEW ***************
This is a much improved Command Line Interface for the New York Times connections game!!!  
There are 4 groups of 4 words, and the objective is to find each of the 4 groups!

*********** IN GAME CONTROLS ***********
[a-z]: Select or Unselect word  
?: Guess currently selected words  
-: Clear currently selected words  
!: Shuffle all the words around  
[1-9]: Show previous guess #n  
:q: Exit game  
>: Exit with Skip log

***************** LIVES ****************
If your guess was one away it will display o where your life used to be,
if you are more than one away it will display x where your life used to be.
''')


def start_game(stdscr):
    success = GAME.init_curses(stdscr)
    if success:
        GAME.play_game()


def main():
    args = get_args()
    config = get_user_config()

    if args.username:
        config.username = args.username
    if args.tutorial:
        print_tutorial()
    elif args.generate:
        new_file = generate_con_file(config)
        save_to_git(args, config, new_file)
    else:
        author, number, game_config = find_game(args, config)
        if game_config is None:
            return
        setup_logger(config, author, number)
        global GAME
        GAME = Game(author, number, config, game_config)
        wrapper(start_game)
        save_to_git(args, config, get_logfile_dir(config.username, author, number) / '*')


if __name__ == '__main__':
    main()
