import math
from abc import ABC
from datetime import time

import chess

from project.data.PieceSquareTable import PieceSquareTable

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
        self.bitmap_center4x4 = 0b0000000000000000001111000011110000111100001111000000000000000000



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




    def eval(self ,board : chess.Board) :


        if board.is_checkmate():
            return float('-inf') if board.turn else float('inf')  # Negative for current player if checkmate

        if board.is_stalemate() or board.is_insufficient_material():
            return 0  # Draw

        endgame = False if self.total_pieces(board)>14 else True

        white_squaretable = 0
        black_squaretable =0
        if board.move_stack :
            move = board.pop()
            white_squaretable = PieceSquareTable.get_value(board.piece_at(move.from_square).piece_type , move  , chess.WHITE , endgame )
            black_squaretable = PieceSquareTable.get_value(board.piece_at(move.from_square).piece_type , move  , chess.BLACK , endgame)
            board.push(move)


        white_matscore = self.material_value( board , chess.WHITE)
        black_matscore = self.material_value(board , chess.BLACK)

        eval_pawn = self.evaluate_pawn_structure(board, chess.WHITE)

        eval_mob_wh = self.evaluate_mobility(board)


        flip_value = 1 if board.turn == chess.WHITE else -1
        return (white_squaretable-black_squaretable)*flip_value + (white_matscore-black_matscore)*flip_value +eval_mob_wh*flip_value + eval_pawn



    def material_value(self ,board , active_player ):
        enemy_player = not active_player
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

        return value


    def evaluate_pawn_structure(self, board: chess.Board , active_player) -> float:
        #not nessesary because of quiescence_search , could with pruning?
        enemy_player = not active_player
        score = 0
        for square in board.pieces(chess.PAWN, active_player):
            if board.is_attacked_by(enemy_player, square):
                score -= -5
        for square in board.pieces(chess.PAWN, enemy_player):
            if board.is_attacked_by(active_player, square):
                score += 5
        return score

    def evaluate_mobility(self , board: chess.Board) -> float:
        white_mobility = len(list(board.legal_moves))
        board.turn = not board.turn
        black_mobility = len(list(board.legal_moves))
        board.turn = not board.turn

        #print("white mobility : " , white_mobility , " black mobility : " , black_mobility)
        return (white_mobility - black_mobility)

    def evaluate_king_safety( sef ,board: chess.Board , active_player) -> float:
        king_safety = 0
        if (board.pieces_mask(piece_type=chess.KING, color=active_player) & chess.BB_CORNERS ) :
            king_safety += 1

        #print("king safety : " , king_safety )

        return king_safety





    def quiescence_search(self, board : chess.Board, alpha, beta):

        stand_pat = self.eval(board)
        best_value = stand_pat
        # Alpha-beta pruning
        if stand_pat >= beta:
            return stand_pat
        alpha = max(alpha, stand_pat)

        # Generate all capture moves
        capture_moves = [move for move in board.legal_moves if board.is_capture(move)]
        for move in capture_moves:
            board.push(move)
            score = -self.quiescence_search(board, -beta, -alpha)
            board.pop()
            # Alpha-beta pruning
            if score >= beta:
                return score
            best_value = max(score,best_value)
            alpha = max(alpha, score)

        return best_value




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
