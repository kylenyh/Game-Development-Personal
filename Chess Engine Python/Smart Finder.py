import random
import os
from stockfish import Stockfish

pieceScore = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}
CHECKMATE = 1000
STALEMATE = 0

# Initialize the Stockfish engine
stockfish = Stockfish(path=r"C:\Users\user\OneDrive\Desktop\stockfish\stockfish-windows-x86-64-avx2.exe")
stockfish.update_engine_parameters({"Threads": 5, "Hash": 512})  # Update as needed

def findRandomMove(validMoves):
    """
    Picks and returns a random valid move.
    """
    return validMoves[random.randint(0, len(validMoves)-1)]

def findBestMove(game_state, validMoves, depth=15, elo=1500):
    """
    Finds the best move using Stockfish.
    :param game_state: Current state of the game.
    :param validMoves: List of valid moves.
    :param depth: Depth to which Stockfish should search.
    :param elo: ELO rating to set for Stockfish.
    :return: The best move according to Stockfish.
    """
    stockfish.set_depth(depth)
    stockfish.set_elo_rating(elo)
    fen = game_state.fen()
    stockfish.set_fen_position(fen)
    best_move = stockfish.get_best_move()
    
    if best_move:
        start_square = best_move[:2]
        end_square = best_move[2:4]
        start_row, start_col = 8 - int(start_square[1]), ord(start_square[0]) - ord('a')
        end_row, end_col = 8 - int(end_square[1]), ord(end_square[0]) - ord('a')
        
        for move in validMoves:
            if move.startRow == start_row and move.startCol == start_col and move.endRow == end_row and move.endCol == end_col:
                return move
                
    return None
