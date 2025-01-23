#!/usr/bin/python3
from project.chess_agents.negamax_agent import Agent
from project.chess_engines.uci_engine import UciEngine

from project.chess_utilities.utility import Utility

if __name__ == "__main__":
    # Create your utility
    utility = Utility()
    # Create your agent
    agent = Agent(utility, 2.0)
    # Create the engine
    engine = UciEngine("negamax engine", "Yea", agent)
    # Run the engine (will loop until the game is done or exited)
    engine.engine_operation()
