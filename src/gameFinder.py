import json
import os
from types import SimpleNamespace

from src.fileUtils import get_game_filename, GAMES_FOLDER, get_author_folder, get_machine_logfile
from pathlib import Path

from src.gitUtils import pull_master


def get_game_status(logfile: Path):
    if not logfile.exists():
        return 'untouched'
    with open(logfile, 'r') as f:
        # get to last line of file
        for line in f:
            pass
        json_line = json.loads(line)
        if 'skip' in json_line:
            return 'skip'
        if 'complete' in json_line:
            return 'complete'

    return 'incomplete'


def find_unplayed(walk_path, user_config, tried_pull=False):
    first_untouched = None, None, None
    for root, dirs, files in os.walk(walk_path):
        author = Path(root).name
        # don't pick games the user made (they know the answer!)
        if author == user_config.username:
            continue
        for file in sorted(files, key=int):
            logfile = get_machine_logfile(user_config.username, author, int(file))
            status = get_game_status(logfile)
            if status == 'incomplete':
                return author, int(file), file_to_game_config(Path(root) / file)
            if first_untouched[0] is None and status == 'untouched':
                first_untouched = author, int(file), file_to_game_config(Path(root) / file)

    if first_untouched[0] is None and not tried_pull:
        pull_master()
        find_unplayed(walk_path, user_config, tried_pull=True)
    else:
        print('No new games were found, try to convince your friends to make more!')
    return first_untouched


def file_to_game_config(file):
    with open(file, 'r') as f:
        game_config = json.load(f)
        game_config = [SimpleNamespace(**x) for x in game_config]
        return game_config


def find_game(args, user_config):
    if args.author == user_config.username:
        print('You cannot play your own games! You may use -u friend if you are sharing your puzzle with a friend!')
        return None, None, None

    walk_path = GAMES_FOLDER
    if args.author:
        if args.number:
            logfile = get_machine_logfile(user_config.username, args.author, args.number)
            status = get_game_status(logfile)
            if status == 'complete':
                print('You have already played this game!')
                print('If you would like to share this puzzle with a friend, please exit and use the username flag ('
                      '-u)!')
                c = input('enter "c" to continue to game or any other character to exit:')
                if c != 'c':
                    return None, None, None
            return args.author, args.number, file_to_game_config(get_game_filename(args.author, args.number))
        walk_path = get_author_folder(args.author)
    return find_unplayed(walk_path, user_config)
