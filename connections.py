import argparse
import sys
from curses import wrapper
from typing import Optional

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
    parser.add_argument('-u', '--username', type=str, help="use this username instead of configured username \
							    (will not overwrite config file)")
    parser.add_argument('-d', '--no-git', action='store_true', help="only use for development")
    return parser.parse_args()


GAME: Optional[Game] = None


def start_game(stdscr):
    GAME.init_curses(stdscr)
    GAME.play_game()


def main():
    args = get_args()
    config = get_user_config()

    if args.username:
        config.username = args.username

    if args.generate:
        new_file = generate_con_file(config)
        save_to_git(args, config, new_file)
    else:
        author, number, game_config = find_game(args, config)
        setup_logger(config, author, number)
        global GAME
        GAME = Game(game_config)
        wrapper(start_game)


if __name__ == '__main__':
    main()
