
from enum import Enum

class RefinementStrategy:
    SMT = 1
    PYTHON = 2

class Options:
    GRAPH_PARSE_TREE: bool = False
    REFINEMENT_STRATEGY: RefinementStrategy = RefinementStrategy.PYTHON
