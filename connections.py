import curses
import json
import os
import random
import sys
import time
from curses import wrapper
from typing import List


def add_complete_row(stdscr, state, row, width):
    word_width = width // 4
    stdscr.addstr(row * 2, width // 2 - len(state['connection']) // 2, state['connection'],
                  curses.color_pair(state['level']))
    for col, word in enumerate(state['words']):
        stdscr.addstr(row * 2 + 1, col * word_width, word.rjust(word_width), curses.color_pair(state['level']))


def add_highlighted_word(stdscr, notfound: List[str], word_width: int, chosen: str, highlight=False):
    ind = notfound.index(chosen)
    row, col = divmod(ind, 4)
    row += (4 - len(notfound) // 4)
    if highlight:
        pad_len = word_width - len(chosen)
        stdscr.addstr(row * 2 + 1, col * word_width, ' ' * pad_len)
        stdscr.addstr(row * 2 + 1, col * word_width + pad_len, chosen, curses.A_REVERSE)
    else:
        stdscr.addstr(row * 2 + 1, col * word_width, chosen.rjust(word_width))


def add_notfound(stdscr, notfound: List[str], word_width: int):
    for chosen in notfound:
        add_highlighted_word(stdscr, notfound, word_width, chosen)


def add_lives(stdscr, nlives: int, width: int):
    for i in range(nlives):
        stdscr.addstr(9, i * 3 + (width // 2) - 4, '*')

    for i in range(nlives, 4):
        stdscr.addstr(9, i * 3 + (width // 2) - 4, 'x', curses.A_REVERSE)


def play_game(stdscr):
    stdscr.clear()
    stdscr.refresh()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_MAGENTA)

    nlives = 4

    with open(sys.argv[2], 'r', encoding='utf-8') as f:
        game_config = json.load(f)

    notfound = [word for row in game_config for word in row['words']]
    random.shuffle(notfound)

    WORD_WIDTH = max(len(t) for t in notfound) + 3
    WIDTH = WORD_WIDTH * 4

    highlighted = set()

    # set initial display
    add_notfound(stdscr, notfound, WORD_WIDTH)
    add_lives(stdscr, nlives, WIDTH)

    # set cursor location
    stdscr.addstr(10, 0, '>')

    # main game loop
    current = ''
    addsleep = False
    while True:
        stdscr.move(10, 1 + len(current))
        stdscr.clrtoeol()
        stdscr.refresh()
        if addsleep:
            addsleep = False
            time.sleep(0.3)
            curses.flushinp()
        ch = stdscr.getch()

        # HANDLE BACKSPACE
        if ch in [curses.KEY_BACKSPACE, 8]:
            current = current[0:-1]
            continue
        ch = chr(ch).upper()

        # HANDLE GUESS
        if ch == '?':
            # only check if there are 4 highlighted
            if len(highlighted) != 4:
                continue
            correct = False
            for row in game_config:
                if highlighted == set(row['words']):
                    add_complete_row(stdscr, row, 4 - len(notfound) // 4, WIDTH)
                    for word in highlighted:
                        notfound.remove(word)
                    correct = True
                    break
            if not correct:
                nlives -= 1
                add_lives(stdscr, nlives, WIDTH)

            # clear and redraw everything without highlights
            highlighted.clear()
            add_notfound(stdscr, notfound, WORD_WIDTH)

        # HANDLE SHUFFLE
        elif ch == '!':
            random.shuffle(notfound)
            add_notfound(stdscr, notfound, WORD_WIDTH)

        # HANDLE SELECT / DESELECT
        current += ch
        filtered = [word for word in notfound if word.startswith(current)]
        # query is no ambiguous (either 1 valid word or no valid words)
        if len(filtered) <= 1:
            addsleep = True
            # clear current regardless of if entry is valid
            current = ''
            if len(filtered) == 1:
                chosen = filtered[0]
                if chosen in highlighted:
                    add_highlighted_word(stdscr, notfound, WORD_WIDTH, chosen, highlight=False)
                    highlighted.remove(chosen)
                else:
                    add_highlighted_word(stdscr, notfound, WORD_WIDTH, chosen, highlight=True)
                    highlighted.add(chosen)

        else:
            stdscr.addstr(10, 1, current)


def generate_con_file(user_config, fout: str):
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

    if not fout.endswith('.con'):
        fout += '.con'
    filename = os.path.join('games', os.path.join(user_config['username'], fout))
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(game_config, f, ensure_ascii=False, indent=4)


def get_user_config():
    if os.path.exists('.config'):
        with open('.config', 'r') as f:
            return json.load(f)

    config = {'username': input('please enter username:')}
    with open('.config', 'w') as f:
        json.dump(config, f)


def main():
    config = get_user_config()
    if sys.argv[1] == '-o':
        generate_con_file(config, sys.argv[2])
    else:
        wrapper(play_game)


if __name__ == '__main__':
    main()
