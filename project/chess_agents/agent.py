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

        self.utility.prev_bestValue = -math.inf

        self.expanded_nodes = 0
        self.start_time = time.time()
        self.delta_time = 0.0

        depth = 0

        #iterative deepning
        while (self.delta_time < self.time_limit_move):
            self.utility.prev_bestValue = -math.inf

            self.negamax(board, depth, depth, -math.inf, +math.inf)

            depth += 1

            self.delta_time = time.time() - self.start_time

        print(self.delta_time)
        print(self.expanded_nodes)
        print(depth)
        print(self.utility.prev_bestValue)
        return self.utility.prev_bestMove

    def negamax(self, board: chess.Board, depth, init_depth, alpha, beta):

        if (depth == 0) or (time.time() - self.start_time) > self.time_limit_move:
            self.expanded_nodes += + 1
            u = self.utility.quiescence_search(board, alpha, beta)
            print(u)
            return u

        best_move = None
        best_score = -math.inf


        sorted_moves = sorted(board.legal_moves, key=lambda move: self.utility.move_value(board, move), reverse=True)

        for childMoves in sorted_moves:
            self.expanded_nodes = self.expanded_nodes + 1



            board.push(childMoves)

            # if threefold repetition we do not analyze this position
            if board.can_claim_threefold_repetition():
                board.pop()
                continue

            value = -self.negamax(board, depth - 1, init_depth, -alpha, -beta)
            board.pop()


            if value >= best_score :
                 best_score = value
                 best_move = childMoves


            alpha = max(alpha, best_score)

            if (beta <= alpha):
                break


        if(depth == init_depth) :
            self.utility.prev_bestValue = best_score
            self.utility.prev_bestMove = best_move


        return best_score















    def min_max(self, board: chess.Board, depth, init_depth, alpha, beta, trueIfMax):



        if (depth == 0) or (time.time() - self.start_time) > self.time_limit_move:
            self.expanded_nodes += + 1
            u = self.utility.quiescence_search(board, alpha, beta)
            return u

        sorted_moves = sorted(board.legal_moves, key=lambda move: self.utility.move_value(board, move), reverse=True)

        if trueIfMax:  # we need to get the max from children

            for childMoves in sorted_moves:

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
            for childMoves in sorted_moves:

                self.expanded_nodes = self.expanded_nodes + 1

                board.push(childMoves)
                value = self.min_max(board, depth - 1, init_depth, alpha, beta, True)
                board.pop()
                beta = min(beta, value)

                if (beta <= alpha):
                    break

            return beta
