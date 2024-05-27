# brute force recursive engine


from piece import *
from move import Move
from game import Game


# returns the best move and the current evaluation. no optimizations, pure search. best depth is probably 4.
def get_best_move(game: Game, depth: int) -> tuple[Move | None, int]:
    # base case evaluates the material on the board
    if depth <= 0: return (None, game.evaluate_board_material()) # returning none looks counterintuitive, but hear me out

    # start off with the worst possible case
    best_move_and_evaluation = (None, -100000) if game.side_to_move == PieceColor.White else (None, 100000)

    for move in game.get_all_legal_moves():
        # first, make the move and save the captured piece for later
        captured_piece = game.make_move(move)

        # now make a recursive call to get the best move for this current game branch
        best_this_branch = get_best_move(game, depth - 1)

        # if we find a move with a better rating than what we currently have, replace the current move.
        # "better rating" is more positive for white, more negative for black. however,
        # keep in mind the player was flipped earlier when we made the initial move; we take this into account.
        if game.side_to_move == PieceColor.White and best_this_branch[1] < best_move_and_evaluation[1]:
            best_move_and_evaluation = (move, best_this_branch[1])
        elif game.side_to_move == PieceColor.Black and best_this_branch[1] > best_move_and_evaluation[1]:
            best_move_and_evaluation = (move, best_this_branch[1])

        # finally, unmake the move using the captured piece from earlier, returning the game to its original state.
        game.un_make_move(move, captured_piece)


    return best_move_and_evaluation


initial_game = Game()

print(initial_game.board[0][2])


print(get_best_move(initial_game, 3))
