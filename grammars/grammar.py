from fuzzingbook import bookutils
from typing import List, Dict, Union, Any, Tuple, Optional
from fuzzingbook import Fuzzer
from fuzzingbook.Grammars import Grammar
import re
import random
import time

random.seed(time.time())


class ExpansionError(Exception):
    pass


Option = Dict[str, Any]
Expansion = Union[str, Tuple[str, Option]]
Grammar = Dict[str, List[Expansion]]

RE_NONTERMINAL = re.compile(r'(<[^<> ]*>)')


def nonterminals(expansion):
    # In later chapters, we allow expansions to be tuples,
    # with the expansion being the first element
    if isinstance(expansion, tuple):
        expansion = expansion[0]

    return RE_NONTERMINAL.findall(expansion)


def is_nonterminal(s):
    return RE_NONTERMINAL.match(s)


START_SYMBOL = "<start>"


def simple_grammar_fuzzer(grammar: Grammar,
                          start_symbol: str = START_SYMBOL,
                          max_nonterminals: int = 10,
                          max_expansion_trials: int = 100,
                          log: bool = False) -> str:
    """Produce a string from `grammar`.
       `start_symbol`: use a start symbol other than `<start>` (default).
       `max_nonterminals`: the maximum number of nonterminals
         still left for expansion
       `max_expansion_trials`: maximum # of attempts to produce a string
       `log`: print expansion progress if True"""

    term = start_symbol
    expansion_trials = 0

    while len(nonterminals(term)) > 0:
        symbol_to_expand = random.choice(nonterminals(term))
        expansions = grammar[symbol_to_expand]
        expansion = random.choice(expansions)
        # In later chapters, we allow expansions to be tuples,
        # with the expansion being the first element
        if isinstance(expansion, tuple):
            expansion = expansion[0]

        new_term = term.replace(symbol_to_expand, expansion, 1)

        if len(nonterminals(new_term)) < max_nonterminals:
            term = new_term
            if log:
                print("%-40s" % (symbol_to_expand + " -> " + expansion), term)
            expansion_trials = 0
        else:
            expansion_trials += 1
            if expansion_trials >= max_expansion_trials:
                raise ExpansionError("Cannot expand " + repr(term))

    return term


EXPR_GRAMMAR: Grammar = {
    "<start>":
        ["<expr>"],

    "<expr>":
        ["<term> + <expr>", "<term> - <expr>", "<term>"],

    "<term>":
        ["<factor> * <term>", "<factor> / <term>", "<factor>"],

    "<factor>":
        ["+<factor>",
         "-<factor>",
         "(<expr>)",
         "<integer>.<integer>",
         "<integer>"],

    "<integer>":
        ["<digit><integer>", "<digit>"],

    "<digit>":
        ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
}

CMD_GRAMMAR: Grammar = {
    "<start>":
        ["<cmdlist>"],

    "<cmdlist>":
        ["<cmd>", "<cmd> <cmdlist>"],

    "<cmd>":
        [
            "TCM(<integer>)",
            "SBO(<integer>,<integer>)",
            "BAT(<integer>)",
            "DSN(<integer>,<integer>,<integer>)"
        ],

    "<integer>":
        ["<digit><integer>", "<digit>"],

    "<digit>":
        ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
}

if __name__ == '__main__':
    print('\nCommand lists (inputs to system under test):\n')
    for x in range(100):
        cmd_list = simple_grammar_fuzzer(
            grammar=CMD_GRAMMAR,
            max_nonterminals=100,
            log=False)
        print(f'{x:3d}: {cmd_list}')

