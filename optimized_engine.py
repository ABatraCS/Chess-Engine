# brute force recursive engine


from piece import *
from move import Move
from game import Game

transposition_table = {}

# returns the best move and the current evaluation. no optimizations, pure search. best depth is probably 4.
def minimax(game: Game, depth: int) -> int:
    global transposition_table

    # check if the position is already in the transposition table
    if game.zobrist_hash in transposition_table:
        return transposition_table[game.zobrist_hash]

    # base case evaluates the material on the board, inserts into transposition table
    if depth <= 0: 
        board_material = game.evaluate_board_material()
        transposition_table[game.zobrist_hash] = board_material
        return board_material

    # start off with the worst possible case
    best_evaluation = -100000 if game.side_to_move == PieceColor.White else 100000

    for move in game.get_all_legal_moves():
        # first, make the move and save the captured piece for later
        captured_piece = game.make_move(move)

        # now make a recursive call to get the best move for this current game branch
        best_this_branch = minimax(game, depth - 1)

        # unmake the move using the captured piece from earlier, returning the game to its original state.
        game.un_make_move(move, captured_piece)

        # if we find a move with a better rating than what we currently have, replace the current move.
        # "better rating" is more positive for white, more negative for black. however,
        # keep in mind the player was flipped earlier when we made the initial move; we take this into account.
        if game.side_to_move == PieceColor.White and best_this_branch > best_evaluation:
            best_evaluation = best_this_branch
        elif game.side_to_move == PieceColor.Black and best_this_branch < best_evaluation:
            best_evaluation = best_this_branch


    # update the transposition table for this position
    transposition_table[game.zobrist_hash] = best_evaluation

    return best_evaluation



def get_best_move(game: Game, depth: int) -> tuple[Move | None, int]:
    global transposition_table

    best_move = None
    best_evaluation = -100000 if game.side_to_move == PieceColor.White else 100000

    for move in game.get_all_legal_moves():
        # first, make the move and save the captured piece for later
        captured_piece = game.make_move(move)

        # now make a recursive call to get the best move for this current game branch
        evaluation = minimax(game, depth - 1)

        # if we find a move with a better rating than what we currently have, replace the current move.
        # "better rating" is more positive for white, more negative for black. however,
        # keep in mind the player was flipped earlier when we made the initial move; we take this into account.
        if game.side_to_move == PieceColor.White and evaluation < best_evaluation:
            best_move = move
            best_evaluation = evaluation
        elif game.side_to_move == PieceColor.Black and evaluation > best_evaluation:
            best_move = move
            best_evaluation = evaluation

        # finally, unmake the move using the captured piece from earlier, returning the game to its original state.
        game.un_make_move(move, captured_piece)

    transposition_table = {}
    return (best_move, best_evaluation)



# start = time.time()
# get_best_move(Game(), depth=6)
# end = time.time()
# print(num_positions_evaluated / (end-start), "positions per second")