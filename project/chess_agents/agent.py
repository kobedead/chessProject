import math
import operator
from abc import ABC
from copy import deepcopy
import time

import random
from typing import Tuple, Union

import chess
from project.chess_utilities.utility import Utility

"""A generic agent class"""


class Agent(ABC):

    def __init__(self, utility: Utility, time_limit_move: float) -> None:
        """Setup the Search Agent"""
        self.utility = utility
        self.time_limit_move = time_limit_move

    def calculate_move(self, board: chess.Board):

        self.expanded_nodes = 0
        self.utility.self_color = board.turn
        self.utility.enemy_color = not board.turn

        self.dont_return = False

        self.start_time = time.time()
        self.delta_time = 0.0

        depth = 0

        while (self.delta_time < self.time_limit_move):
            best_score = self.min_max(board, depth, depth, -math.inf, +math.inf, True)

            depth += 1

            self.delta_time = time.time() - self.start_time

        print(self.delta_time)
        print(self.expanded_nodes)
        print(depth)
        print(self.utility.prev_bestValue)
        return self.utility.prev_bestMove

    def min_max(self, board: chess.Board, depth, init_depth, alpha, beta, trueIfMax):

        if (depth == 0) or (time.time() - self.start_time) > self.time_limit_move:
            self.expanded_nodes += + 1
            u = self.utility.quiescence_search(board, alpha, beta)
            return u

        moves_with_values = [(move, self.utility.move_value(board, move)) for move in board.legal_moves]
        mover_ordering = [move for move, _ in sorted(moves_with_values, key=lambda x: x[1], reverse=True)]

        if trueIfMax:  # we need to get the max from children

            for childMoves in mover_ordering:

                self.expanded_nodes = self.expanded_nodes + 1

                board.push(childMoves)
                value = self.min_max(board, depth - 1, init_depth, alpha, beta, False)
                board.pop()

                if (depth == init_depth and value > self.utility.prev_bestValue):
                    self.utility.prev_bestMove = childMoves
                    self.utility.prev_bestValue = value

                alpha = max(alpha, value)
                if (beta <= alpha):
                    break

            return alpha

        elif not trueIfMax:  # we need to get the min from children
            for childMoves in mover_ordering:

                self.expanded_nodes = self.expanded_nodes + 1

                board.push(childMoves)
                value = self.min_max(board, depth - 1, init_depth, alpha, beta, True)
                board.pop()
                beta = min(beta, value)

                if (beta <= alpha):
                    break

            return beta
