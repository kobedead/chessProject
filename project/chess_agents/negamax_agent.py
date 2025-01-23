import math
from abc import ABC
import time
import random
import chess
from project.chess_utilities.utility import Utility


"""A generic agent class"""

class Agent(ABC):

    def __init__(self, utility: Utility, time_limit_move: float) -> None:
        """Setup the Search Agent"""
        self.utility = utility
        self.time_limit_move = time_limit_move
        self.transposition_table = dict()


    def calculate_move(self, board: chess.Board):

        self.utility.prev_bestValue = -math.inf

        self.hasnewMove = False

        self.expanded_nodes = 0
        self.breaks = 0
        self.translookupcount = 0
        self.translookupcount_success = 0


        self.start_time = time.time()
        self.delta_time = 0.0

        depth = 1

        #iterative deepning
        while (self.delta_time < self.time_limit_move):
            self.utility.prev_bestValue = -math.inf

            self.negamax(board, depth, depth, -math.inf, +math.inf)

            depth += 1

            self.delta_time = time.time() - self.start_time



        print("")
        print("time it took : " , self.delta_time)
        print("depth reached  : " , depth)

        print("")
        print("expanded nodes" , self.expanded_nodes)
        print("times pruning break : " ,self.breaks)
        print("time trans lookup : " ,self.translookupcount)
        print("times meaningfull trans " , self.translookupcount_success)
        print("")


        print("best value : ",self.utility.prev_bestValue)
        print("best move  : " ,self.utility.prev_bestMove)



        if(self.hasnewMove):
            return self.utility.prev_bestMove
        else:
            return random.choice(list(board.legal_moves))


    def negamax(self, board: chess.Board, depth, init_depth, alpha, beta):

        zobrist_key = board._transposition_key()    #not the best -> protected

        if zobrist_key in self.transposition_table:
            self.translookupcount += 1
            entry = self.transposition_table[zobrist_key]

            # check depth
            if entry['depth'] >= depth:
                self.translookupcount_success += 1

                # use the value if it matches the alpha-beta bounds
                if entry['flag'] == 'EXACT':
                    return entry['value']
                elif entry['flag'] == 'UPPERBOUND' and entry['value'] <= alpha:
                    return entry['value']
                elif entry['flag'] == 'LOWERBOUND' and entry['value'] >= beta:
                    return entry['value']



        if (depth == 0) or (time.time() - self.start_time) > self.time_limit_move:
            self.expanded_nodes += 1
            u = self.quiescence_search(board, alpha, beta)
            return u

        best_move = None
        best_score = -math.inf
        original_alpha = alpha


        sorted_moves = sorted(board.legal_moves, key=lambda move: self.utility.move_value(board, move), reverse=True)

        for childMoves in sorted_moves:

            self.expanded_nodes += 1

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
                 self.hasnewMove = True


            alpha = max(alpha, best_score)

            if (beta <= alpha):
                self.breaks +=1
                break


        if depth == init_depth :
            self.utility.prev_bestValue = best_score
            self.utility.prev_bestMove = best_move

        # store position in transposition table with flag
        flag = 'EXACT'
        if best_score <= original_alpha:
            flag = 'UPPERBOUND'
        elif best_score >= beta:
            flag = 'LOWERBOUND'

        self.transposition_table[zobrist_key] = {
            'value': best_score,
            'depth': depth,
            'flag': flag
        }

        return best_score






    def quiescence_search(self, board : chess.Board, alpha, beta):

        stand_pat = self.utility.eval(board)
        best_value = stand_pat
        # Alpha-beta pruning
        if stand_pat >= beta:
            self.breaks += 1
            return stand_pat
        alpha = max(alpha, stand_pat)

        # Generate all capture moves
        capture_moves = [move for move in board.legal_moves if board.is_capture(move) or board.gives_check(move) ]
        sorted_moves = sorted(capture_moves, key=lambda move: self.utility.move_value(board, move), reverse=True)
        for move in sorted_moves:

            self.expanded_nodes +=1
            board.push(move)
            score = -self.quiescence_search(board, -beta, -alpha)
            board.pop()
            # Alpha-beta pruning
            if score >= beta:
                self.breaks +=1
                return score
            best_value = max(score,best_value)
            alpha = max(alpha, score)

        return best_value








