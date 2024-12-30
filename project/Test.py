import chess

from project.chess_agents.agent import Agent
from project.chess_agents.example_agent import ExampleAgent
from project.chess_utilities.example_utility import ExampleUtility
from project.chess_utilities.utility import Utility

import chess.pgn
import random

if __name__ == "__main__":
    # Create your utility
    utility = Utility()
    # Create your agent
    agent = Agent(utility, 1.0)
    board = chess.Board()

    png = open("bruh.pgn")
    game = chess.pgn.read_game(png)  # Read the first game

    # Traverse through the moves and randomly select a position
    moves = list(game.mainline_moves())

    # Play up to a random move in the game
    for move in moves[:1]:
        board.push(move)

    print(board.turn)

    print(board)


    print("Best move : " , agent.calculate_move(board))