import logging
import random
import curses
import time


class Game:
    def __init__(self, game_config):
        # set stdscr to None, will be initialized later
        self.stdscr = None

        # init game state
        self.game_config = game_config
        self.nlives = 4

        self.notfound = [word for row in game_config for word in row.words]
        random.shuffle(self.notfound)

        # init screen width (based on game config)
        self.word_width = max(len(t) for t in self.notfound) + 3
        self.width = self.word_width * 4

        self.highlighted = set()

    def init_curses(self, stdscr):
        stdscr.clear()
        stdscr.refresh()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
        self.stdscr = stdscr

    def add_complete_row(self, state):
        row = 4 - len(self.notfound) // 4
        self.stdscr.addstr(row * 2, self.width // 2 - len(state.connection) // 2, state.connection,
                           curses.color_pair(state.level))
        for col, word in enumerate(state.words):
            self.stdscr.addstr(row * 2 + 1, col * self.word_width,
                               word.rjust(self.word_width), curses.color_pair(state.level))

    def add_highlighted_word(self, chosen: str, highlight=False):
        ind = self.notfound.index(chosen)
        row, col = divmod(ind, 4)
        row += (4 - len(self.notfound) // 4)
        if highlight:
            pad_len = self.word_width - len(chosen)
            self.stdscr.addstr(row * 2 + 1, col * self.word_width, ' ' * pad_len)
            self.stdscr.addstr(row * 2 + 1, col * self.word_width + pad_len, chosen, curses.A_REVERSE)
        else:
            self.stdscr.addstr(row * 2 + 1, col * self.word_width, chosen.rjust(self.word_width))

    def add_notfound(self):
        for chosen in self.notfound:
            self.add_highlighted_word(chosen)

    def add_lives(self):
        for i in range(self.nlives):
            self.stdscr.addstr(9, i * 3 + (self.width // 2) - 4, '*')

        for i in range(self.nlives, 4):
            self.stdscr.addstr(9, i * 3 + (self.width // 2) - 4, 'x', curses.A_REVERSE)

    def play_game(self):
        # set initial display
        self.add_notfound()
        self.add_lives()

        # set cursor location
        self.stdscr.addstr(10, 0, '>')

        # main game loop
        current = ''
        addsleep = False
        while True:
            self.stdscr.move(10, 1 + len(current))
            self.stdscr.clrtoeol()
            self.stdscr.refresh()
            if addsleep:
                addsleep = False
                time.sleep(0.3)
                curses.flushinp()

            ch = self.stdscr.getch()

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
                logging.info(str(self.highlighted))
                correct = False
                for row in self.game_config:
                    if self.highlighted == set(row.words):
                        self.add_complete_row(row)
                        for word in self.highlighted:
                            self.notfound.remove(word)
                        correct = True
                        break
                if not correct:
                    self.nlives -= 1
                    self.add_lives()

                # clear and redraw everything without highlights
                self.highlighted.clear()
                self.add_notfound()

            # HANDLE SHUFFLE
            elif ch == '!':
                random.shuffle(self.notfound)
                self.add_notfound()

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
                        self.add_highlighted_word(chosen, highlight=False)
                        self.highlighted.remove(chosen)
                    else:
                        self.add_highlighted_word(chosen, highlight=True)
                        self.highlighted.add(chosen)

            else:
                self.stdscr.addstr(10, 1, current)
