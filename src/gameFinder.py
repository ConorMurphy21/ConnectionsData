import json
import os
from types import SimpleNamespace

from src.fileUtils import get_game_filename, GAMES_FOLDER, get_author_folder, get_log_filename
from pathlib import Path


def find_unplayed(walk_path, user_config):
    for root, dirs, files in os.walk(walk_path):
        author = Path(root).name
        # don't pick games the user made (they know the answer!)
        if author == user_config.username:
            continue
        for file in sorted(files, key=int):
            log_file = get_log_filename(user_config.username, author, int(file))
            if not log_file.exists():
                return author, int(file), file_to_game_config(Path(root) / file)


def file_to_game_config(file):
    with open(file, 'r') as f:
        game_config = json.load(f)
        game_config = [SimpleNamespace(**x) for x in game_config]
        return game_config


def find_game(args, user_config):
    walk_path = GAMES_FOLDER
    if args.author:
        if args.number:
            return args.author, args.number, file_to_game_config(get_game_filename(args.author, args.number))
        walk_path = get_author_folder(args.author)
    return find_unplayed(walk_path, user_config)
