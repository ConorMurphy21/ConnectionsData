import json
import os

from src.fileUtils import get_game_filename


def get_last_number(user_config) -> int:
    pass


def generate_con_file(user_config):
    game_config = []
    diff = ['easy', 'medium', 'hard', 'hardest']
    for i in range(4):
        while True:
            row = {'words': [], 'connection': '', 'level': i + 1}
            for j in range(4):
                row['words'].append(input(f'{diff[i]} - #{j}: ').upper())
            row['connection'] = input(f'{diff[i]} - connection: ').upper()
            print(row)
            confirm = input('Is this correct (y / n): ').lower()
            if confirm in {'y', 'yes', 'ye'}:
                game_config.append(row)
                break

    last_number = get_last_number(user_config)
    filename = get_game_filename(user_config.username, last_number + 1)
    filename.parent.mkdir(exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(game_config, f, ensure_ascii=False, indent=4)
