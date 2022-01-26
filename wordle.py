#!/usr/bin/env python3

import string
import os
import sys
import csv
import cmd
import logging
import ipdb

from unidecode import unidecode

# Constraints / hints:
# Can be of type either:
#   Green: (index, letter)
#   Yellow: (index, letter)
#   Grey: (letter)

class BasePositionalConstraint(object):
    def __init__(self, index, letter):
        if index not in range(0, 5):
            raise ValueError(f"index {index} out of bounds")
        if letter not in string.ascii_letters:
            raise ValueError(f"letter \"{letter}\" is not a valid letter")

        self.index = index
        self.letter = letter.lower()

    def __str__(self):
        return f"{type(self).__name__}({self.index}, {self.letter})"

class GreenConstraint(BasePositionalConstraint):
    def filter_function(self):
        index, letter = (self.index, self.letter)
        return lambda word: word[index] == letter

class YellowConstraint(BasePositionalConstraint):
    def filter_function(self):
        index, letter = (self.index, self.letter)
        return lambda word: (letter in word) and (word[index] != letter)

class GreyConstraint(object):
    def __init__(self, letter):
        if letter not in string.ascii_letters:
            raise ValueError(f"letter \"{letter}\" is not a valid letter")
        self.letter = letter.lower()

    def __str__(self):
        return f"{type(self).__name__}({self.letter})"

    def filter_function(self):
        letter = self.letter
        return lambda word: letter not in word


class WordleShell(cmd.Cmd):
    intro = """Wordle solver.
    Type in guesses in the form: word <guessed_word> <results>

    Eg: word steam __g_y
    
    Type help or ? for help.
"""
    prompt = '(wordle) '

    def __init__(self, words):
        self.words = words
        self.constraints = []
        super().__init__()
    
    def do_status(self, arg):
        "Print number of remaining possible words."
        print(f"Number of possible words remaining: {len(self.words)}")

    def do_possible(self, arg):
        "Print all remaining possible words."
        print("\n".join(self.words))

    def do_word(self, arg):
        """Add a word and its green/yellow/gray results: word prion g_yy_

(g == green, y == yellow, _ == grey)"""
        word, hints = arg.split()
        if len(word) != 5:
            raise ValueError("word should be 5 chars long")
        if len(hints) != 5:
            raise ValueError("hints should be 5 chars long")

        for i in range(0, 5):
            letter = word[i]
            constraint_type = hints[i]
            if constraint_type == "g":
                constraint = GreenConstraint(i, letter)
            elif constraint_type == "y":
                constraint = YellowConstraint(i, letter)
            elif constraint_type == "_":
                constraint = GreyConstraint(letter)
            else:
                raise ValueError(f"invalid hint type \"{constraint_type}\" at position {i}")
            self.apply_new_constraint(constraint)

        print(f"Number of possible words remaining: {len(self.words)}")

    def do_exit(self, arg):
        "Close this program."
        sys.exit(0)

    def do_EOF(self, arg):
        sys.exit(0)

    def apply_new_constraint(self, constraint):
        print(f"[DEBUG] Applying new constraint {constraint}")
        self.constraints.append(constraint)
        self.words = list(filter(constraint.filter_function(), self.words))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "en_words.txt"

    with open(filename) as f:
        all_words = f.read().split()
    all_words = list(filter(lambda word: len(word) == 5, all_words))

    # massage out accents
    all_words = [unidecode(w) for w in all_words]

    WordleShell(all_words).cmdloop()
