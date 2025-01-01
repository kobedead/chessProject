import math
from abc import ABC
from datetime import time

import chess

from project.data.PieceSquareTable import PieceSquareTable

"""A generic utility class"""
class Utility(ABC):

    def __init__(self) -> None:
        """Setup the Search Agent"""
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



        #parameters







    def total_pieces(self , board : chess.Board):
        value = 0

        value += len(board.pieces(piece_type=chess.PAWN, color=chess.WHITE))
        value += len(board.pieces(piece_type=chess.BISHOP, color=chess.WHITE))
        value += len(board.pieces(piece_type=chess.KNIGHT, color=chess.WHITE))
        value += len(board.pieces(piece_type=chess.ROOK, color=chess.WHITE))
        value += len(board.pieces(piece_type=chess.QUEEN, color=chess.WHITE))

        value += len(board.pieces(piece_type=chess.PAWN, color=chess.BLACK))
        value += len(board.pieces(piece_type=chess.BISHOP, color=chess.BLACK))
        value += len(board.pieces(piece_type=chess.KNIGHT, color=chess.BLACK))
        value += len(board.pieces(piece_type=chess.ROOK, color=chess.BLACK))
        value += len(board.pieces(piece_type=chess.QUEEN, color=chess.BLACK))

        return value




    def eval(self ,board : chess.Board) :


        if board.is_checkmate():
            return -math.inf if board.turn else +math.inf


        if board.is_stalemate() or board.is_insufficient_material():
            return 0  # Draw



        #PieceSquareValue
        white_value = self.getPiecesScuareValue(board , chess.WHITE)/2
        black_value = self.getPiecesScuareValue(board , chess.BLACK)/2

        #material value
        white_value += self.material_value( board , chess.WHITE)*2
        black_value += self.material_value(board , chess.BLACK)*2

        #pawnn structure (acttached)
        white_value += self.evaluate_pawn_structure(board, chess.WHITE)
        black_value += self.evaluate_pawn_structure(board , chess.BLACK)

        #mobility
        white_value += len(list(board.legal_moves))  # White mobility
        board.push(chess.Move.null())
        black_value += len(list(board.legal_moves))  # Black mobility
        board.pop()


        flip_value = 1 if board.turn == chess.WHITE else -1
        return (white_value-black_value) *flip_value






    def getPiecesScuareValue(self , board , player):


            value = PieceSquareTable.get_value(board , chess.BISHOP , player )
            value += PieceSquareTable.get_value(board , chess.KNIGHT , player )
            value += PieceSquareTable.get_value(board , chess.ROOK , player)
            value += PieceSquareTable.get_value(board , chess.QUEEN , player)

            end = 2/self.total_pieces(board)

            value += PieceSquareTable.get_value(board,chess.PAWN , player )*(1-end)
            value += PieceSquareTable.get_value(board , chess.PAWN , player , True)*(end)


            value += PieceSquareTable.get_value(board , chess.KING, player ) *(1-end)
            value += PieceSquareTable.get_value(board, chess.KING , player , True)*end

            return   value






    def material_value(self ,board , player ):
        value = 0
        value += len(board.pieces(piece_type=chess.PAWN, color=player)) * self.pawn_value
        value += len(board.pieces(piece_type=chess.BISHOP, color=player)) * self.bishop_value
        value += len(board.pieces(piece_type=chess.KNIGHT, color=player)) * self.knight_value
        value += len(board.pieces(piece_type=chess.ROOK, color=player)) * self.rook_value
        value += len(board.pieces(piece_type=chess.QUEEN, color=player)) * self.queen_value

        return value


    def evaluate_pawn_structure(self, board: chess.Board , player) -> float:


        #not nessesary because of quiescence_search , could with pruning!!
        score = 0
        for square in board.pieces(chess.PAWN, player):
            #check if passed pawn
            if player == chess.WHITE :
                if chess.BB_SQUARES[square] & chess.BB_RANK_7 :
                    score += 10
                elif chess.BB_SQUARES[square] & chess.BB_RANK_8 :
                    score += 20
            else :
                if chess.BB_SQUARES[square] & chess.BB_RANK_2 :
                    score += 10
                elif chess.BB_SQUARES[square] & chess.BB_RANK_1 :
                    score += 20

            # Doubled pawns penalty
            if board.pawns & chess.BB_FILES[chess.square_file(square)] > 1:
                score -= 5



        return score


    def evaluate_king_safety( sef ,board: chess.Board , active_player) -> float:
        king_safety = 0
        if (board.pieces_mask(piece_type=chess.KING, color=active_player) & chess.BB_CORNERS ) :
            king_safety += 1

        #print("king safety : " , king_safety )

        return king_safety









    def move_value(self, board : chess.Board , move : chess.Move):

        value = 0

        #check if its a favorable capture
        if(board.is_capture(move)) :
            victim = board.piece_at(move.to_square)
            attacker = board.piece_at(move.from_square)
            if victim :
                value += (victim.piece_type * 10) - attacker.piece_type
        #check if its a promotion
        elif(move.promotion) :
            value += 20

        #if it was previous found move -> add value
        if(move == self.prev_bestMove) :
            value += self.prev_bestValue

        #check if it gives check
        if board.gives_check(move):
            value += 30

        #if move to center
        if chess.BB_SQUARES[move.to_square] & chess.BB_CENTER :
            value += 5

        return value
