"""CSC148 Assignment 2: Autocomplete engines

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module description ===
This file contains starter code for the three different autocomplete engines
you are writing for this assignment.

As usual, be sure not to change any parts of the given *public interface* in the
starter code---and this includes the instance attributes, which we will be
testing directly! You may, however, add new private attributes, methods, and
top-level functions to this file.
"""
from __future__ import annotations
import csv
from typing import Any, Dict, List, Optional, Tuple

from melody import Melody
from prefix_tree import SimplePrefixTree, CompressedPrefixTree


################################################################################
# Text-based Autocomplete Engines (Task 4)
################################################################################
class LetterAutocompleteEngine():
    """An autocomplete engine that suggests strings based on a few letters.

    The *prefix sequence* for a string is the list of characters in the string.
    This can include space characters.

    This autocomplete engine only stores and suggests strings with lowercase
    letters, numbers, and space characters; see the section on
    "Text sanitization" on the assignment handout.

    === Attributes ===
    autocompleter: An Autocompleter used by this engine.
    """
    autocompleter: Autocompleter

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize this engine with the given configuration.

        <config> is a dictionary consisting of the following keys:
            - 'file': the path to a text file
            - 'autocompleter': either the string 'simple' or 'compressed',
              specifying which subclass of Autocompleter to use.
            - 'weight_type': either 'sum' or 'average', which specifies the
              weight type for the prefix tree.

        Each line of the specified file counts as one input string.
        Note that the line may or may not contain spaces.
        Each string must be sanitized, and if the resulting string contains
        at least one alphanumeric character, it is inserted into the
        Autocompleter.

        *Skip lines that do not contain at least one alphanumeric character!*

        When each string is inserted, it is given a weight of one.
        Note that it is possible for the same string to appear on more than
        one line of the input file; this would result in that string getting
        a larger weight (because of how Autocompleter.insert works).
        """
        # We've opened the file for you here. You should iterate over the
        # lines of the file and process them according to the description in
        # this method's docstring.
        if config['autocompleter'] == "simple":
            self.autocompleter = SimplePrefixTree(config["weight_type"])
        # else:
        #     self.autocompleter = CompressedPrefixTree(config["weight_type"])
        with open(config['file'], encoding='utf8') as f:
            for line in f:
                n = line.rstrip('\n')
                new_string = ""
                for char in n:
                    if char.isalpha() or char == " " or char.isdigit():
                        new_string += char.lower()
                if len(new_string) > 0:
                    self.autocompleter.insert(new_string, 1.0, list(new_string))
        # self.autocompleter.insert('cat', 2.0, ['c', 'a', 't'])
        # self.autocompleter.insert('car', 3.0, ['c', 'a', 'r'])
        # self.autocompleter.insert('dog', 7.0, ['d', 'o', 'g'])
        # print(self.autocompleter)

    def autocomplete(self, prefix: str,
                     limit: Optional[int] = None) -> List[Tuple[str, float]]:
        """Return up to <limit> matches for the given prefix string.

        The return value is a list of tuples (string, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Note that the given prefix string must be transformed into a list
        of letters before being passed to the Autocompleter.

        Preconditions:
            limit is None or limit > 0
            <prefix> contains only lowercase alphanumeric characters and spaces
        """
        return self.autocompleter.autocomplete(list(prefix), limit)

    def remove(self, prefix: str) -> None:
        """Remove all strings that match the given prefix string.

        Note that the given prefix string must be transformed into a list
        of letters before being passed to the Autocompleter.

        Precondition: <prefix> contains only lowercase alphanumeric characters
                      and spaces.
        """
        return self.autocompleter.remove(list(prefix))


class SentenceAutocompleteEngine:
    """An autocomplete engine that suggests strings based on a few words.

    A *word* is a string containing only alphanumeric characters.
    The *prefix sequence* for a string is the list of words in the string
    (separated by whitespace). The words themselves do not contain spaces.

    This autocomplete engine only stores and suggests strings with lowercase
    letters, numbers, and space characters; see the section on
    "Text sanitization" on the assignment handout.

    === Attributes ===
    autocompleter: An Autocompleter used by this engine.
    """
    autocompleter: Autocompleter

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize this engine with the given configuration.

        <config> is a dictionary consisting of the following keys:
            - 'file': the path to a CSV file
            - 'autocompleter': either the string 'simple' or 'compressed',
              specifying which subclass of Autocompleter to use.
            - 'weight_type': either 'sum' or 'average', which specifies the
              weight type for the prefix tree.

        Precondition:
        The given file is a *CSV file* where each line has two entries:
            - the first entry is a string
            - the second entry is the a number representing the weight of that
              string

        Note that the line may or may not contain spaces.
        Each string must be sanitized, and if the resulting string contains
        at least one word, it is inserted into the Autocompleter.

        *Skip lines that do not contain at least one alphanumeric character!*

        When each string is inserted, it is given THE WEIGHT SPECIFIED ON THE
        LINE FROM THE CSV FILE. (Updated Nov 19)
        Note that it is possible for the same string to appear on more than
        one line of the input file; this would result in that string getting
        a larger weight.
        """
        # We haven't given you any starter code here! You should review how
        # you processed CSV files on Assignment 1.

        if config['autocompleter'] == "simple":
            self.autocompleter = SimplePrefixTree(config["weight_type"])

        with open(config['file']) as csv_file:
            reader = csv.reader(csv_file)
            for line in reader:
                n = line[0]
                new_token = [""]
                marker = 0
                value = ""
                weight = float(line[1])
                for char in n:
                    if char.isalpha() or char.isdigit():
                            new_token[marker] += char.lower()
                            value += char.lower()
                    elif char == " ":
                        marker += 1
                        new_token.append("")
                        value += " "
                if len(new_token) > 0:
                    self.autocompleter.insert(value, weight, new_token)


    def autocomplete(self, prefix: str,
                     limit: Optional[int] = None) -> List[Tuple[str, float]]:
        """Return up to <limit> matches for the given prefix string.

        The return value is a list of tuples (string, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Note that the given prefix string must be transformed into a list
        of words before being passed to the Autocompleter.

        Preconditions:
            limit is None or limit > 0
            <prefix> contains only lowercase alphanumeric characters and spaces
        """
        if prefix == '':
            return self.autocompleter.autocomplete([], limit)
        sanitized = prefix.split(" ")
        return self.autocompleter.autocomplete(sanitized, limit)

    def remove(self, prefix: str) -> None:
        """Remove all strings that match the given prefix.

        Note that the given prefix string must be transformed into a list
        of words before being passed to the Autocompleter.

        Precondition: <prefix> contains only lowercase alphanumeric characters
                      and spaces.
        """
        if prefix == '':
            self.autocompleter.remove([])
        sanitized = prefix.split(" ")
        self.autocompleter.remove(sanitized)


################################################################################
# Melody-based Autocomplete Engines (Task 5)
################################################################################
class MelodyAutocompleteEngine:
    """An autocomplete engine that suggests melodies based on a few intervals.

    The values stored are Melody objects, and the corresponding
    prefix sequence for a Melody is its interval sequence.

    Because the prefix is based only on interval sequence and not the
    starting pitch or duration of the notes, it is possible for different
    melodies to have the same prefix.

    # === Private Attributes ===
    autocompleter: An Autocompleter used by this engine.
    """
    autocompleter: Autocompleter

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize this engine with the given configuration.

        <config> is a dictionary consisting of the following keys:
            - 'file': the path to a CSV file
            - 'autocompleter': either the string 'simple' or 'compressed',
              specifying which subclass of Autocompleter to use.
            - 'weight_type': either 'sum' or 'average', which specifies the
              weight type for the prefix tree.

        Precondition:
        The given file is a *CSV file* where each line has the following format:
            - The first entry is the name of a melody (a string).
            - The remaining entries are grouped into pairs (as in Assignment 1)
              where the first number in each pair is a note pitch,
              and the second number is the corresponding duration.

            HOWEVER, there may be blank entries (stored as an empty string '');
            as soon as you encounter a blank entry, stop processing this line
            and move onto the next line the CSV file.

        Each melody is be inserted into the Autocompleter with a weight of 1.
        """
        # We haven't given you any starter code here! You should review how
        # you processed CSV files on Assignment 1.
        if config['autocompleter'] == "simple":
            self.autocompleter = SimplePrefixTree(config["weight_type"])

        with open(config['file']) as csv_file:
            reader = csv.reader(csv_file)

            for line in reader:

                name = line[0]
                tuple_list = []
                for i in range(1, len(line), 2):
                    if line[i] == "" or line[i+1] == "":
                        break
                    tuple_list.append((int(line[i]), int(line[i+1])))

                m = Melody(name, tuple_list)
                interval_sequence = []
                for i in range(len(tuple_list)-1):
                    interval_sequence.append((tuple_list[i+1][0] - tuple_list[i][0]))
                self.autocompleter.insert(m, 1, interval_sequence)


    def autocomplete(self, prefix: List[int],
                     limit: Optional[int] = None) -> List[Tuple[Melody, float]]:
        """Return up to <limit> matches for the given interval sequence.

        The return value is a list of tuples (melody, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given interval sequence.

        Precondition:
            limit is None or limit > 0
        """
        return self.autocompleter.autocomplete(prefix, limit)


    def remove(self, prefix: List[int]) -> None:
        """Remove all melodies that match the given interval sequence.
        """
        self.autocompleter.remove(prefix)

###############################################################################
# Sample runs
###############################################################################
def sample_letter_autocomplete() -> List[Tuple[str, float]]:
    """A sample run of the letter autocomplete engine."""
    engine = LetterAutocompleteEngine({
        # NOTE: you should also try 'data/google_no_swears.txt' for the file.
        # 'file': 'data/google_no_swears.txt',
        'file': 'test.txt',
        'autocompleter': 'simple',
        'weight_type': 'sum'
    })
    engine.remove("how")
    return engine.autocomplete('', 20)


def sample_sentence_autocomplete() -> List[Tuple[str, float]]:
    """A sample run of the sentence autocomplete engine."""
    engine = SentenceAutocompleteEngine({
        # 'file': 'data/random_melodies_c_scale.csv',
        'file': 'data/songbook.csv',
        'autocompleter': 'simple',
        'weight_type': 'sum'
    })
    # engine.remove('what')
    return engine.autocomplete("how to", 20)


def sample_melody_autocomplete() -> None:
    """A sample run of the melody autocomplete engine."""
    engine = MelodyAutocompleteEngine({
        # 'file': 'data/random_melodies_c_scale.csv',
        'file': 'data/songbook.csv',
        'autocompleter': 'simple',
        'weight_type': 'sum'
    })
    engine.remove([])
    melodies = engine.autocomplete([])
    for melody, _ in melodies:
        melody.play()


if __name__ == '__main__':
    # import python_ta
    # python_ta.check_all(config={
    #     'allowed-io': ['__init__'],
    #     'extra-imports': ['csv', 'prefix_tree', 'melody']
    # })

    # This is used to increase the recursion limit so that your sample runs
    # work even for fairly tall simple prefix trees.
    import sys
    import os

    sys.setrecursionlimit(5000)

    # print(sample_letter_autocomplete())
    # print(sample_sentence_autocomplete())
    sample_melody_autocomplete()