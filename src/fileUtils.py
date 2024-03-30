from pathlib import Path

GAMES_FOLDER = Path('./games')

RESULTS_FOLDER = Path('./results')


def get_game_filename(author: str, number: int) -> Path:
    return GAMES_FOLDER / author / str(number)


def get_author_folder(author: str) -> Path:
    return GAMES_FOLDER / author


def get_logfile_dir(user: str, author: str, number: int) -> Path:
    return RESULTS_FOLDER / author / str(number) / user
