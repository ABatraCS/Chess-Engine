# this is essentially the functionality need to start. i omitted a few helper 
# functions, including printing pieces and the board formatted, and i refuse to 
# write the methods to calculate legal moves for pieces (line 121), but this is 
# generally how to set everything up, with a few exceptions.



from enum import Enum



# necessary enum
class PieceColor(Enum):
    White = 1
    Black = 2


    # helper methods
    def value(self):
        if self == PieceColor.White:
            return 1
        else: return -1
    

    # you'd be surprised at how useful this is
    def opponent(self):
        if self == PieceColor.White:
            return PieceColor.Black
        return PieceColor.White



# another necessary enum
class PieceType(Enum):
    Pawn = 1
    Bishop = 2
    Knight = 3
    Rook = 4
    Queen = 5
    King = 6


    # helper methods
    def value(self):
        if self == PieceType.Pawn:
            return 1
        elif self == PieceType.Bishop or self == PieceType.Knight:
            return 3
        elif self == PieceType.Rook:
            return 5
        elif self == PieceType.Queen:
            return 9
        elif self == PieceType.King:
            return 10000 # arbitrary large number
        


# ---------------------------------------------------------------------------------------------------------------------
# our class representations. note that simpicity is key in order for a lot of this to be lightweight, thus fast.



# our piece only needs to know its type and color
class Piece:
    def __init__(self, piece_type: PieceType, piece_color: PieceColor):
        self.piece_type = piece_type
        self.piece_color = piece_color


    # black pieces have negative value
    def get_value(self):
        return self.piece_type.value() * self.piece_color.value() 


    # for easy printing
    def __str__(self):
        return f'{self.piece_color.name} {self.piece_type.name}'



# similarly, a move really only needs to know the start and end positions. other classes/functions can handle 
# captures, castling, en passant, etc. this might seem like a bad decision, but it's actually a good one.
class Move:
    def __init__(self, start_pos: tuple[int, int], end_pos: tuple[int, int]):
        self.start_pos = start_pos # tuple[0] is row, tuple[1] is column
        self.end_pos = end_pos


    # will print move in UCI format, e.g. "e2e4" or "b8c6"
    def __str__(self):
        return self.position_to_notation(self.start_pos) + self.position_to_notation(self.end_pos)


    # helper method
    @staticmethod
    def position_to_notation(position: tuple[int, int]) -> str:
        col, row = position
        return chr(col + ord('a')) + str(row + 1)
        


# our game only needs to know the board and whose turn it is; we will later add castling rights, 
# en passant target squares, move count, etc, but for now this is sufficient.
class Game: 
    # note that the board here is a simple 2D array with no out-of-bounds checks at all. 
    # later we will enforce this, and if we are looking to really get fast, we should 
    # consider changing the fundamental data structure to something like a tree.
    def __init__(self, board: list[list[Piece | None]], side_to_move: PieceColor):
        self.board = board
        self.side_to_move = side_to_move


    # here is our evaluation function. note that it is as simple as it gets.
    def evaluate_board_material(self) -> int:
        material = 0
        for row in self.board: 
            for piece in row:
                if piece is not None:
                    material += piece.get_value()

        return material


    # we might consider moving this function somewhere else, but for now it's fine here.
    def get_piece_legal_moves(self, piece: Piece) -> list[Move]:
        legal_moves = []

        # i despise writing these and thus i refuse to do it
        if piece.piece_type == PieceType.Pawn:
            # todo
        elif piece.piece_type == PieceType.Bishop:
            # todo
        elif piece.piece_type == PieceType.Knight:
            # todo
        elif piece.piece_type == PieceType.Rook:
            # todo
        elif piece.piece_type == PieceType.Queen:
            # todo
        elif piece.piece_type == PieceType.King:
            # todo

        return legal_moves
        

    # heavy lifting function here, gets all legal moves in the current position. simple enough implementation though.
    def get_all_legal_moves(self) -> list[Move]:
        all_legal_moves = []
        
        for row in self.board:
            for piece in row:
                if piece is not None:
                    if piece.piece_color == self.side_to_move:
                        all_legal_moves += self.get_piece_legal_moves(piece)

        return all_legal_moves
    

    # makes a move on the given board, returns a captured piece if any.
    def make_move(self, move: Move) -> Piece | None:
        captured_piece = self.board[move.end_pos[0]][move.end_pos[1]]
        moving_piece = self.board[move.start_pos[0]][move.start_pos[1]]

        # move the moving piece to the end location
        self.board[move.end_pos[0]][move.end_pos[1]] = moving_piece
        
        # remove the moving piece from the start location
        self.board[move.start_pos[0]][move.start_pos[1]] = None

        # flip the side to move
        self.side_to_move = self.side_to_move.opponent()

        return captured_piece


    # unmakes a move on the given board, replacing the captured piece.
    def un_make_move(self, move: Move, captured_piece: Piece | None):
        # "pick up" the moving piece at the END location
        moving_piece = self.board[move.end_pos[1], move.end_pos[0]]

        # put the captured piece at the END location
        self.board[move.end_pos[1], move.end_pos[0]] = captured_piece

        # "put down" the moving piece at the START location
        self.board[move.start_pos[1], move.start_pos[0]] = moving_piece

        # change back the player to move 
        self.side_to_move = self.side_to_move.opponent()



# ---------------------------------------------------------------------------------------------------------------------
# the "engine"



# returns the best move and the current evaluation. no optimizations, pure search. best depth is probably 4.
def get_best_move(game: Game, depth: int) -> tuple[Move | None, int]:
    # base case evaluates the material on the board
    if depth <= 0: return (None, game.evaluate_board_material()) # returning none looks counterintuitive, but hear me out

    # start off with the worst possible case
    best_move_and_evaluation = (None, -100000) if game.player_to_move == PieceColor.White else (None, 100000)

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