import dataclasses
import json
import logging
import random
import curses
import time
from typing import Set
from src.fileUtils import get_machine_logfile

logger = logging.getLogger(__name__)

ONE_AWAY_HIGHLIGHT = 0
FAIL_HIGHLIGHT = 0

TITLE_OFFSET = 0
BOARD_OFFSET = TITLE_OFFSET + 1
BOARD_HEIGHT = 8
LIVES_OFFSET = BOARD_OFFSET + BOARD_HEIGHT + 1
CURSOR_OFFSET = LIVES_OFFSET + 1


@dataclasses.dataclass
class Fail:
    one_away: bool
    guessed: Set[str]


def _log_skipped():
    logger.debug('skipped', extra={'skip': True})


class Game:
    def __init__(self, author: str, number: int, user_config, game_config):
        # set stdscr to None, will be initialized later
        self.stdscr = None

        # init game state
        self.game_config = game_config

        self.fails = []
        self.notfound = [word for row in game_config for word in row.words]
        random.shuffle(self.notfound)

        # init screen width (based on game config)
        self.word_width = max(len(t) for t in self.notfound) + 3
        self.width = self.word_width * 4

        self.highlighted = set()

        self.author = author
        self.number = number
        self.logfile = get_machine_logfile(user_config.username, author, number)

    def nlives(self):
        return 4 - len(self.fails)

    def init_curses(self, stdscr):
        stdscr.clear()
        stdscr.refresh()
        height, width = stdscr.getmaxyx()
        if height <= CURSOR_OFFSET or width <= self.width:
            stdscr.addstr(0, 0, 'Window size too small, please resize window to try again!')
            stdscr.addstr(1, 0, 'Hit any key to exit.')
            stdscr.getch()
            return False
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_MAGENTA)
        global FAIL_HIGHLIGHT, ONE_AWAY_HIGHLIGHT
        FAIL_HIGHLIGHT = curses.color_pair(5)
        ONE_AWAY_HIGHLIGHT = curses.color_pair(6)
        self.stdscr = stdscr
        return True

    def init_from_logfile(self):
        if not self.logfile.exists():
            return
        with open(self.logfile, 'r') as f:
            lines = f.readlines()
            for line in lines:
                json_line = json.loads(line)
                if 'level' in json_line:
                    row = self.game_config[json_line['level'] - 1]
                    for word in row.words:
                        self.notfound.remove(word)
                    self.add_complete_row(row)
                elif 'one_away' in json_line:
                    self.fails.append(Fail(json_line['one_away'], set(json.loads(json_line['guessed']))))

    def add_title(self):
        self.stdscr.addstr(TITLE_OFFSET, 0, f'{self.author} #{self.number}'.rjust(self.width))

    def add_complete_row(self, state):
        row = (3 - len(self.notfound) // 4) * 2 + BOARD_OFFSET
        self.stdscr.addstr(row, max(0, self.width // 2 - len(state.connection) // 2), state.connection,
                           curses.color_pair(state.level))
        for col, word in enumerate(state.words):
            self.stdscr.addstr(row + 1, col * self.word_width,
                               word.rjust(self.word_width), curses.color_pair(state.level))

    def add_highlighted_word(self, chosen: str, color_pair=curses.A_NORMAL):
        ind = self.notfound.index(chosen)
        row, col = divmod(ind, 4)
        row += (4 - len(self.notfound) // 4)
        row *= 2
        row += BOARD_OFFSET + 1
        pad_len = self.word_width - len(chosen)
        self.stdscr.addstr(row, col * self.word_width, ' ' * pad_len)
        self.stdscr.addstr(row, col * self.word_width + pad_len, chosen, color_pair)

    def add_notfound(self):
        for chosen in self.notfound:
            self.add_highlighted_word(chosen)

    def add_highlight_set(self, words: Set[str], color_pair=curses.A_NORMAL):
        for word in words:
            if word in self.notfound:
                self.add_highlighted_word(word, color_pair)

    def add_single_life(self, fail_index: int, curses_color=curses.A_NORMAL):
        fail_mark = 'o' if self.fails[fail_index].one_away else 'x'
        position = ((3 - fail_index) * 3 + (self.width // 2) - 4 + self.width) % self.width
        self.stdscr.addstr(LIVES_OFFSET, position, fail_mark, curses_color)

    def add_lives(self):
        nlives = self.nlives()
        for i in range(nlives):
            self.stdscr.addstr(LIVES_OFFSET, i * 3 + (self.width // 2) - 4, '*')

        for i in range(nlives, 4):
            fail_mark = 'o' if self.fails[nlives - i - 1].one_away else 'x'
            col = ((i * 3 + (self.width // 2) - 4) + self.width) % self.width
            if col < 0:
                continue
            self.stdscr.addstr(LIVES_OFFSET, col, fail_mark)

    def check_guess(self):
        for row in self.game_config:
            diff = set(row.words) - self.highlighted
            if len(diff) == 0:
                for word in self.highlighted:
                    self.notfound.remove(word)
                return row
            elif len(diff) == 1:
                self.fails.append(Fail(True, self.highlighted.copy()))
                return
        self.fails.append(Fail(False, self.highlighted.copy()))

    def play_game(self):
        self.init_from_logfile()
        # set initial display
        self.add_title()
        self.add_notfound()
        self.add_lives()

        # set cursor location
        self.stdscr.addstr(CURSOR_OFFSET, 0, '>')

        # main game loop
        current = ''
        addsleep = False
        highlighted_fail_index = 0
        highlighted_fail = False

        while True:

            # INIT CODE THAT NEEDS TO BE DONE BEFORE EVERY LOOP
            # AND BEFORE FIRST LISTEN
            self.stdscr.move(CURSOR_OFFSET, 1 + len(current))
            self.stdscr.clrtoeol()
            self.stdscr.refresh()
            if addsleep:
                addsleep = False
                time.sleep(0.3)
                curses.flushinp()

            # START OF THE NEXT INPUT WAIT LOOP
            ch = self.stdscr.getch()

            # REMOVE ANY FAIL HIGHLIGHTING
            if highlighted_fail:
                highlighted_fail = False
                self.add_single_life(highlighted_fail_index)
                self.add_highlight_set(self.fails[highlighted_fail_index].guessed)

            # HANDLE BACKSPACE
            if ch in [curses.KEY_BACKSPACE, 8]:
                current = current[0:-1]
                continue
            ch = chr(ch).upper()

            # HANDLE GUESS
            if ch == '?':
                # only check if there are 4 highlighted
                if len(self.highlighted) != 4:
                    continue

                # be generous and don't count guesses that have already been guessed
                if any(fail.guessed == self.highlighted for fail in self.fails):
                    self.highlighted.clear()
                    self.add_notfound()
                    continue

                correct_row = self.check_guess()
                if correct_row is not None:
                    self.add_complete_row(correct_row)
                else:
                    self.add_lives()

                self._log_guess(correct_row)
                # clear and redraw everything without highlights
                self.highlighted.clear()
                self.add_notfound()

            # HANDLE SHUFFLE
            elif ch == '!':
                random.shuffle(self.notfound)
                self.add_notfound()

            # HANDLE CLEAR
            elif ch == '\\':
                self.highlighted.clear()
                self.add_notfound()

            elif ch == ':':
                return

            elif ch == '>':
                _log_skipped()
                return

            elif '0' <= ch <= '9' or ch == '-' or ch == '=' or ch == '+':
                # this works for < 10 guesses
                # therefore the game is undefined behaviour after 11 guesses ig
                if ch == '-':
                    fail_index = (highlighted_fail_index + 1) % len(self.fails)
                elif ch == '=' or ch == '+':
                    fail_index = (highlighted_fail_index - 1 + len(self.fails)) % len(self.fails)
                else:
                    fail_index = (int(ch) + 9) % 10

                if fail_index >= len(self.fails):
                    continue
                fail = self.fails[fail_index]
                color_pair = ONE_AWAY_HIGHLIGHT if fail.one_away else FAIL_HIGHLIGHT
                self.add_highlight_set(fail.guessed, color_pair)
                self.add_single_life(fail_index, color_pair)
                highlighted_fail = True
                highlighted_fail_index = fail_index

            else:
                # HANDLE SELECT / DESELECT
                current += ch
                filtered = [word for word in self.notfound if word.startswith(current)]
                # query is no ambiguous (either 1 valid word or no valid words)
                if len(filtered) <= 1:
                    addsleep = True
                    # clear current regardless of if entry is valid
                    current = ''
                    if len(filtered) == 1:
                        chosen = filtered[0]
                        if chosen in self.highlighted:
                            self.add_highlighted_word(chosen)
                            self.highlighted.remove(chosen)
                        else:
                            self.add_highlighted_word(chosen, curses.A_REVERSE)
                            self.highlighted.add(chosen)

                else:
                    self.stdscr.addstr(CURSOR_OFFSET, 1, current)

    def _log_guess(self, row):
        if row is None:
            fail = self.fails[-1]
            extra = {'guessed': json.dumps(list(fail.guessed)), 'one_away': fail.one_away}
            logger.info(f'Incorrectly Guessed {fail.guessed}', extra=extra)
        else:
            extra = {'level': row.level}
            logger.info(f'Found {row.connection}: {row.words}', extra=extra)

        # add log message for game won
        if len(self.notfound) == 0:
            logger.info(f'All Connections Found in {len(self.fails) + 4} guesses!', extra={'complete': True})
