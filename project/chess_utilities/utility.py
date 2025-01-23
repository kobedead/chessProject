import math
from abc import ABC
from functools import reduce

import chess

from project.chess_utilities.PieceSquareTable import PieceSquareTable

"""A generic utility class"""
class Utility(ABC):

    def __init__(self) -> None:
        """Setup the Search Agent"""
        self.prev_bestMove = None
        self.prev_bestValue = 0

        self.pawn_value = 100
        self.knight_value = 300
        self.bishop_value = 300
        self.rook_value = 500
        self.queen_value = 900

        #ijn board stupid
        self.bitmap_3x3_corners = 0b1110011111100111111001110000000000000000111001111110011111100111
        self.bitmap_2x2_corners = 0b1100001111000011000000000000000000000000000000001100001111000011
        self.bitmap_center4x4 = 0b0000000000000000001111000011110000111100001111000000000000000000



        #parameters


    def total_pieces(self , board : chess.Board) -> int:
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

    def total_pieces_color(self , board : chess.Board , color) -> int:
        value = 0

        value += len(board.pieces(piece_type=chess.PAWN, color=color))
        value += len(board.pieces(piece_type=chess.BISHOP, color=color))
        value += len(board.pieces(piece_type=chess.KNIGHT, color=color))
        value += len(board.pieces(piece_type=chess.ROOK, color=color))
        value += len(board.pieces(piece_type=chess.QUEEN, color=color))

        return value




    def eval(self ,board : chess.Board) :


        if board.is_checkmate():
            return -math.inf if board.turn else +math.inf


        if board.is_stalemate() or board.is_insufficient_material():
            return 0  # Draw


        #linear transition from global midgame to endgame
        total_material = self.material_value(board, chess.WHITE) + self.material_value(board, chess.BLACK)
        endgame_phase = max(0, min(1, (3200 - total_material) / 1200))
        midgame_phase = (1-endgame_phase)

        #PieceSquareValue
        white_value = self.getPiecesScuareValue(board, chess.WHITE,endgame_phase)
        black_value = self.getPiecesScuareValue(board, chess.BLACK,endgame_phase)

        #material value
        white_value += self.material_value(board, chess.WHITE)
        black_value += self.material_value(board, chess.BLACK)

        #pawnn structure (acttached)
        white_value += self.evaluate_pawn_structure(board, chess.WHITE)
        black_value += self.evaluate_pawn_structure(board, chess.BLACK)

        #king safety
        white_value += self.pawn_shield(board , chess.WHITE) * midgame_phase
        black_value += self.pawn_shield(board , chess.BLACK) * midgame_phase

        #endgame
        white_value += self.endgame(board , chess.WHITE)
        black_value += self.endgame(board, chess.BLACK)


        #mobility
        if board.turn == chess.WHITE :
            white_value += len(list(board.legal_moves))  # White mobility
            board.push(chess.Move.null())
            black_value += len(list(board.legal_moves))  # Black mobility
            board.pop()
        else:
            black_value += len(list(board.legal_moves))  # Black mobility
            board.push(chess.Move.null())
            white_value += len(list(board.legal_moves))  # White mobility
            board.pop()


        flip_value = 1 if board.turn == chess.WHITE else -1
        return (white_value-black_value) *flip_value



    def getPiecesScuareValue(self , board , player , end):


            value = PieceSquareTable.get_value(board , chess.BISHOP , player )
            value += PieceSquareTable.get_value(board , chess.KNIGHT , player )
            value += PieceSquareTable.get_value(board , chess.ROOK , player)
            value += PieceSquareTable.get_value(board , chess.QUEEN , player)


            value += PieceSquareTable.get_value(board,chess.PAWN , player )*(1-end)
            value += PieceSquareTable.get_value(board , chess.PAWN , player , True)*(end)


            value += PieceSquareTable.get_value(board , chess.KING, player ) *(1-end)
            value += PieceSquareTable.get_value(board, chess.KING , player , True)*end

            return value


    def material_value(self ,board , player ):
        value = 0
        value += len(board.pieces(piece_type=chess.PAWN, color=player)) * self.pawn_value
        value += len(board.pieces(piece_type=chess.BISHOP, color=player)) * self.bishop_value
        value += len(board.pieces(piece_type=chess.KNIGHT, color=player)) * self.knight_value
        value += len(board.pieces(piece_type=chess.ROOK, color=player)) * self.rook_value
        value += len(board.pieces(piece_type=chess.QUEEN, color=player)) * self.queen_value

        return value


    def evaluate_pawn_structure(self, board: chess.Board , player) :


        score = 0

        BB_pawns = board.pieces_mask(chess.PAWN, player)
        BB_enemy_pawns = board.pieces_mask(chess.PAWN, not player)

        for square in board.pieces(chess.PAWN, player):


            file_pawn = chess.square_file(square)
            rank_pawn = chess.square_rank(square)

            prev_file_BB = chess.BB_FILES[file_pawn - 1 if file_pawn > 0 else 0]
            next_file_BB = chess.BB_FILES[file_pawn + 1 if file_pawn < 7 else 7]


            #now containes rank and neigboring ranks
            BB_passed_pawn = chess.BB_FILES[file_pawn] | prev_file_BB | next_file_BB

            if player == chess.WHITE :
                # do bitwise or on the list of ranks to get 1 bitmask
                BB_ranks_ahead = reduce(lambda x, y: x | y, chess.BB_RANKS[rank_pawn + 1: 8], 0)

            else :
                # do bitwise or on the list of ranks to get 1 bitmask
                BB_ranks_ahead = reduce(lambda x, y: x | y, chess.BB_RANKS[0 : rank_pawn], 0)


            BB_passed_pawn &= BB_ranks_ahead

            #passed pawn
            if not (BB_passed_pawn & BB_enemy_pawns):
                score += 50


            #Isolated pawn
            if (prev_file_BB & chess.BB_SQUARES[square] == 0 and next_file_BB & chess.BB_SQUARES[square] == 0):
                score-=30


            # Double pawn penalty
            BB_double_pawn = chess.BB_FILES[file_pawn] & BB_pawns
            #convert bistmask to string and count how many 1s
            if bin(BB_double_pawn).count('1') > 1:
                score -= -10  #happens 2 times (for every doulbe pawn)

        return score






    def pawn_shield(self ,board : chess.Board , player):


            king_square = board.king(player)
            BB_shield_squares = 0

            file_king = chess.square_file(king_square)
            rank_king = chess.square_rank(king_square)

            BB_prev_file = chess.BB_FILES[file_king - 1 if file_king > 0 else 0]
            BB_next_file = chess.BB_FILES[file_king + 1 if file_king < 7 else 7]

            if (chess.square_rank(king_square) < 2) or (chess.square_rank(king_square) > 5 ):
                if player == chess.WHITE :
                    BB_shield_squares = chess.BB_RANKS[rank_king+1 if rank_king<7 else 7] & (chess.BB_FILES[file_king] |  BB_prev_file | BB_next_file)
                else:
                    BB_shield_squares = chess.BB_RANKS[rank_king-1 if rank_king>0 else 0] & (chess.BB_FILES[file_king] |  BB_prev_file | BB_next_file)


            BB_pawns_shield = BB_shield_squares & board.pieces_mask(chess.PAWN , player)


            #print("bin" , bin(BB_pawns_shield))
            shielded_pawns = bin(BB_pawns_shield).count('1')



            score = shielded_pawns  * 20

            #penalty for no shield
            if shielded_pawns == 0:
                score -= 50  # Add a penalty for no pawns around the king


            #penalty if opponent in adjencent open file
            BB_enemy_pawn = board.pieces_mask(chess.PAWN , not player)
            if (BB_next_file & BB_enemy_pawn) or (BB_prev_file & BB_enemy_pawn):
                score -= 30

            return score





    def endgame(self , board : chess.Board , player ):

        enemy = not player
        endgame = 0


        end_spec_color = (self.total_pieces_color(board , player) - self.total_pieces_color(board , enemy))/6

        #enemy king in corner :
        if board.pieces_mask(piece_type=chess.KING, color=enemy) & chess.BB_CORNERS:
            endgame += 90
        elif board.pieces_mask(piece_type=chess.KING, color=enemy) & self.bitmap_2x2_corners:
            endgame += 60
        elif board.pieces_mask(piece_type=chess.KING ,  color=enemy) & self.bitmap_3x3_corners :
            endgame += 20


        #distance between kings needs to close
        player_king_square = board.pieces(piece_type=chess.KING, color=enemy).pop()
        enemy_king_square = board.pieces(piece_type=chess.KING, color=player).pop()

        dis = chess.square_manhattan_distance( player_king_square, enemy_king_square)
        dis = 50/dis*3

        return dis*end_spec_color




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


