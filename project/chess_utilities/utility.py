import math
from abc import ABC
from datetime import time

import chess

"""A generic utility class"""
class Utility(ABC):

    def __init__(self) -> None:
        """Setup the Search Agent"""
        self.self_color = None
        self.enemy_color = None
        self.prev_pawns_middle = 0
        self.prev_knight_middel = 0

        self.prev_bestMove = None
        self.prev_bestValue = 0

        self.pawn_value = 1
        self.knight_value = 3
        self.bishop_value = 3
        self.rook_value = 5
        self.queen_value = 9

        #ijn board stupid
        self.bitmap_3x3_corners = 0b1110011111100111111001110000000000000000111001111110011111100111
        self.bitmap_2x2_corners = 0b1100001111000011000000000000000000000000000000001100001111000011
        self.bitmap_corners     = 0b1000000100000000000000000000000000000000000000000000000010000001
        self.bitmap_center = 0b0000000000000000001111000011110000111100001111000000000000000000


    def begin(self , board : chess.Board):
        begin_value = 0
        if (self.total_pieces(board) > 20) :
            pawns_center = board.pieces_mask(piece_type=chess.PAWN, color=self.self_color)& self.bitmap_center
            knights_center = board.pieces_mask(piece_type=chess.KNIGHT, color=self.self_color) & self.bitmap_center


            if pawns_center > self.pawns_middle :
                begin_value += 1
                self.pawns_middle = pawns_center
            if knights_center > self.knight_middel :
                begin_value += 1
                self.knight_middel = knights_center


        return begin_value



    def total_pieces(self , board : chess.Board):
        value = 0

        value += len(board.pieces(piece_type=chess.PAWN, color=self.self_color))
        value += len(board.pieces(piece_type=chess.BISHOP, color=self.self_color))
        value += len(board.pieces(piece_type=chess.KNIGHT, color=self.self_color))
        value += len(board.pieces(piece_type=chess.ROOK, color=self.self_color))
        value += len(board.pieces(piece_type=chess.QUEEN, color=self.self_color))

        value += len(board.pieces(piece_type=chess.PAWN, color=self.enemy_color))
        value += len(board.pieces(piece_type=chess.BISHOP, color=self.enemy_color))
        value += len(board.pieces(piece_type=chess.KNIGHT, color=self.enemy_color))
        value += len(board.pieces(piece_type=chess.ROOK, color=self.enemy_color))
        value += len(board.pieces(piece_type=chess.QUEEN, color=self.enemy_color))

        return value







    def board_value(self, board: chess.Board):




        #higher is better
        value = 0

        value += len(board.pieces(piece_type=chess.PAWN, color=self.self_color)) * self.pawn_value
        value += len(board.pieces(piece_type=chess.BISHOP, color=self.self_color)) * self.bishop_value
        value += len(board.pieces(piece_type=chess.KNIGHT, color=self.self_color)) * self.knight_value
        value += len(board.pieces(piece_type=chess.ROOK, color=self.self_color)) * self.rook_value
        value += len(board.pieces(piece_type=chess.QUEEN, color=self.self_color)) * self.queen_value

        value -= len(board.pieces(piece_type=chess.PAWN, color=self.enemy_color)) * self.pawn_value
        value -= len(board.pieces(piece_type=chess.BISHOP, color=self.enemy_color)) * self.bishop_value
        value -= len(board.pieces(piece_type=chess.KNIGHT, color=self.enemy_color)) * self.knight_value
        value -= len(board.pieces(piece_type=chess.ROOK, color=self.enemy_color)) * self.rook_value
        value -= len(board.pieces(piece_type=chess.QUEEN, color=self.enemy_color)) * self.queen_value

        #max 16

        return value


        #for endgame we want to drive the king of other player into a corner, so these board posiitons are favored
        #if black king is more in corner -> higher value

        # gets higher if engame is more 'in sight'
        endgame_process = 2/self.total_pieces(board)

        #bitmaps for corners


        corner_king_value = 0
        if (board.pieces_mask(piece_type=chess.KING, color=self.enemy_color)) & self.bitmap_corners :
            corner_king_value +=20
        elif (board.pieces_mask(piece_type=chess.KING, color=self.enemy_color)) & self.bitmap_2x2_corners :
            corner_king_value += 12
        elif (board.pieces_mask(piece_type=chess.KING, color=self.enemy_color)) & self.bitmap_3x3_corners  :
            corner_king_value += 5


        begin_value = 0
        if (self.total_pieces(board) > 20) :
            pawns_center = board.pieces_mask(piece_type=chess.PAWN, color=self.self_color)& self.bitmap_center
            knights_center = board.pieces_mask(piece_type=chess.KNIGHT, color=self.self_color) & self.bitmap_center


            if pawns_center > self.pawns_middle :
                begin_value += 1
                self.pawns_middle = pawns_center
            if knights_center > self.knight_middel :
                begin_value += 1
                self.knight_middel = knights_center






        return value + corner_king_value * endgame_process + begin_value

    def board_value_negamax(self, board: chess.Board):

        """Evaluates the board from the perspective of the current player (the one to move)."""
        #cause of negamax



        active_player = board.turn
        enemy_player = not board.turn

        if board.is_checkmate():
            return float('-inf') if board.turn else float('inf')  # Negative for current player if checkmate

        if board.is_stalemate() or board.is_insufficient_material():
            return 0  # Draw

        value = 0
        value += len(board.pieces(piece_type=chess.PAWN, color=active_player)) * chess.PAWN
        value += len(board.pieces(piece_type=chess.BISHOP, color=active_player)) * chess.BISHOP
        value += len(board.pieces(piece_type=chess.KNIGHT, color=active_player)) * chess.KNIGHT
        value += len(board.pieces(piece_type=chess.ROOK, color=active_player)) * chess.ROOK
        value += len(board.pieces(piece_type=chess.QUEEN, color=active_player)) * chess.QUEEN

        value -= len(board.pieces(piece_type=chess.PAWN, color=enemy_player)) * chess.PAWN
        value -= len(board.pieces(piece_type=chess.BISHOP, color=enemy_player)) * chess.BISHOP
        value -= len(board.pieces(piece_type=chess.KNIGHT, color=enemy_player)) * chess.KNIGHT
        value -= len(board.pieces(piece_type=chess.ROOK, color=enemy_player)) * chess.ROOK
        value -= len(board.pieces(piece_type=chess.QUEEN, color=enemy_player)) * chess.QUEEN


        endgame_process = 2/self.total_pieces(board) #less pieces -> more endgame

        # Positional factors
        pawn_structure = self.evaluate_pawn_structure(board , active_player)
        mobility = self.evaluate_mobility(board , active_player)
        king_safety = self.evaluate_king_safety(board , active_player)

        begin = self.begingame_eval(board , active_player)
        end = self.endgame_eval(board , active_player)



        # Combine factors
        evaluation = value + pawn_structure + mobility + king_safety + begin +end
        return evaluation



    def begingame_eval(self , board : chess.Board , active_player ):
        #in the begin of the game we want to move advance some pieces
        #also if no good move is found i should want to advance

        enemy_player = not active_player

        begin_process = self.total_pieces(board)/10
        begin_value= 0

        #pawns_center = board.pieces_mask(piece_type=chess.PAWN, color=self.self_color) & self.bitmap_center
        #knights_center = board.pieces_mask(piece_type=chess.KNIGHT, color=self.self_color) & self.bitmap_center

        for square in board.pieces(chess.PAWN, active_player):
            if chess.BB_SQUARES[square] & self.bitmap_center :
                begin_value += 1

        for square in board.pieces(chess.ROOK, active_player):
            if chess.BB_SQUARES[square] & self.bitmap_center :
                begin_value += 1

        return begin_value * begin_process












    def endgame_eval(self ,board :chess.Board , active_player):
        #we want to draw the enemy king into a corner

        enemy_player = not active_player

        endgame_process = 2 / self.total_pieces(board)

        corner_king_value = 0
        if (board.pieces_mask(piece_type=chess.KING, color=enemy_player)) & chess.BB_CORNERS:
            corner_king_value += 8
        elif (board.pieces_mask(piece_type=chess.KING, color=enemy_player)) & self.bitmap_2x2_corners:
            corner_king_value += 5
        elif (board.pieces_mask(piece_type=chess.KING, color=enemy_player)) & self.bitmap_3x3_corners:
            corner_king_value += 3


        return corner_king_value * endgame_process









    def evaluate_pawn_structure(self, board: chess.Board , active_player) -> float:
        #not nessesary because of quiescence_search , could with pruning?
        enemy_player = not active_player
        score = 0
        for square in board.pieces(chess.PAWN, active_player):
            if board.is_attacked_by(enemy_player, square):
                score -= 1
        for square in board.pieces(chess.PAWN, enemy_player):
            if board.is_attacked_by(active_player, square):
                score += 1
        return score

    def evaluate_mobility(self , board: chess.Board, active_player) -> float:
        white_mobility = len(list(board.legal_moves))
        board.turn = not board.turn
        black_mobility = len(list(board.legal_moves))
        board.turn = not board.turn


        return (white_mobility - black_mobility) * 0.1

    def evaluate_king_safety( sef ,board: chess.Board , active_player) -> float:
        king_safety = 0
        if (board.pieces_mask(piece_type=chess.KING, color=active_player) & chess.BB_CORNERS ) :
            king_safety += 1
        return king_safety





    def quiescence_search(self, board : chess.Board, alpha, beta):

        stand_pat = self.board_value_negamax(board)
        # Alpha-beta pruning
        if stand_pat >= beta:
            return beta
        alpha = max(alpha, stand_pat)

        # Generate all capture moves
        capture_moves = [move for move in board.legal_moves if board.is_capture(move)]
        for move in capture_moves:
            board.push(move)
            score = -self.quiescence_search(board, -beta, -alpha)
            board.pop()
            # Alpha-beta pruning
            if score >= beta:
                return beta
            alpha = max(alpha, score)

        return alpha




    def move_value(self, board : chess.Board , move : chess.Move):

        value = 0

        if(board.is_capture(move)) :
            value += 10
        elif(move.promotion) :
            value += 20
        elif(move == self.prev_bestMove) :
            value = self.prev_bestValue


        board.push(move)
        if (board.is_checkmate()):
            value += 30
        board.pop()

        return value
