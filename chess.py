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
    

    def is_not_friendly_piece(self, other_piece) -> bool:
        if not other_piece: return True
        return other_piece.piece_color != self.piece_color


    # returns a unicode string of the piece for board printing
    def symbol(self) -> str:
        symbols = {
            (PieceType.Pawn, PieceColor.White): "♟︎",
            (PieceType.Rook, PieceColor.White): "♜",
            (PieceType.Knight, PieceColor.White): "♞",
            (PieceType.Bishop, PieceColor.White): "♝",
            (PieceType.Queen, PieceColor.White): "♛",
            (PieceType.King, PieceColor.White): "♚",

            (PieceType.Pawn, PieceColor.Black): "♙",
            (PieceType.Rook, PieceColor.Black): "♖",
            (PieceType.Knight, PieceColor.Black): "♘",
            (PieceType.Bishop, PieceColor.Black): "♗",
            (PieceType.Queen, PieceColor.Black): "♕",
            (PieceType.King, PieceColor.Black): "♔"
        }
        return symbols.get((self.piece_type, self.piece_color), '?')



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
        return chr(row + ord('a')) + str(col + 1)



initial_board = [
    [
        Piece(PieceType.Rook, PieceColor.White),
        Piece(PieceType.Knight, PieceColor.White),
        Piece(PieceType.Bishop, PieceColor.White),
        Piece(PieceType.Queen, PieceColor.White),
        Piece(PieceType.King, PieceColor.White),
        Piece(PieceType.Bishop, PieceColor.White),
        Piece(PieceType.Knight, PieceColor.White),
        Piece(PieceType.Rook, PieceColor.White),
    ],

    [ Piece(PieceType.Pawn, PieceColor.White) for _ in range(8) ],

    [ None for _ in range(8)],
    [ None for _ in range(8)],
    [ None for _ in range(8)],
    [ None for _ in range(8)],

    [ Piece(PieceType.Pawn, PieceColor.Black) for _ in range(8) ],

    [
        Piece(PieceType.Rook, PieceColor.Black),
        Piece(PieceType.Knight, PieceColor.Black),
        Piece(PieceType.Bishop, PieceColor.Black),
        Piece(PieceType.Queen, PieceColor.Black),
        Piece(PieceType.King, PieceColor.Black),
        Piece(PieceType.Bishop, PieceColor.Black),
        Piece(PieceType.Knight, PieceColor.Black),
        Piece(PieceType.Rook, PieceColor.Black),
    ],
]



# our game only needs to know the board and whose turn it is; we will later add castling rights, 
# en passant target squares, move count, etc, but for now this is sufficient.
class Game: 
    # note that the board here is a simple 2D array with no out-of-bounds checks at all. 
    # later we will enforce this, and if we are looking to really get fast, we should 
    # consider changing the fundamental data structure to something like a tree.
    def __init__(self, board: list[list[Piece | None]] = initial_board, side_to_move: PieceColor = PieceColor.White):
        self.board = board
        self.side_to_move = side_to_move
    


    def __str__(self) -> str:
        s = ""
        if self.side_to_move == PieceColor.White: 
            s += "Side to move: White \n" 
        else: 
            s += "Side to move: Black \n" 
            
        
        s += "   -----------------------------------\n"

        for row in range(7, -1, -1):
            s += str(row+1) + "   | "
            for column in range(0, 8):
                if self.board[row][column]:
                    s += self.board[row][column].symbol()
                else:
                    s += " "
                s += " | "

            s += "\n   -----------------------------------\n"
        
        s += "      A   B   C   D   E   F   G   H   \n"

        return s


    # here is our evaluation function. note that it is as simple as it gets.
    def evaluate_board_material(self) -> int:
        material = 0
        for row in self.board: 
            for piece in row:
                if piece is not None:
                    material += piece.get_value()

        return material


    # we might consider moving this function somewhere else, but for now it's fine here.
    # i hating writing these, so for now we are good but this can be optimized
    def get_piece_legal_moves(self, location: tuple[int, int]) -> list[Move]:
        legal_moves = []

        row, col = location
        piece = self.board[row][col]
        if not piece: return []

        # pawn
        if piece.piece_type == PieceType.Pawn:
            if piece.piece_color == PieceColor.White:
                # first push
                if not self.board[row+1][col]:
                    legal_moves.append(Move(location, (row+1, col)))
                    
                    # second push if on the start row
                    if row == 1 and not self.board[row+2][col]:
                        legal_moves.append(Move(location, (row+2, col)))

            else:
                # first push
                if not self.board[row-1][col]:
                    legal_moves.append(Move(location, (row-1, col)))
                    
                    # second push if on the start row
                    if row == 6 and not self.board[row-2][col]:
                        legal_moves.append(Move(location, (row-2, col)))


        # bishop
        elif piece.piece_type == PieceType.Bishop:
            offsets = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

            # check all offset directions
            for offset in offsets:
                # start square
                curr_row, curr_col = row+offset[0], col+offset[1]
                
                # while there is nothing in the way, keep adding the moves until we hit something (or out of bounds)
                while 0 <= curr_row < 8 and 0 <= curr_col < 8 and piece.is_not_friendly_piece(self.board[curr_row][curr_col]):
                    legal_moves.append(Move(location, (curr_row, curr_col)))
                    curr_row += offset[0]
                    curr_col += offset[1]


        # knight
        elif piece.piece_type == PieceType.Knight:
            offsets = [(2,1), (1,2), (-1,2), (-2,1), (-2,-1), (-1,-2), (1,-2), (2,-1)]

            for offset in offsets:
                curr_row, curr_col = row+offset[0], col+offset[1]

                # quick bounds/friendly piece check (no path checking here)
                if  0 <= curr_row < 8 and 0 <= curr_col < 8 and piece.is_not_friendly_piece(self.board[curr_row][curr_col]):
                    legal_moves.append(Move(location, (curr_row, curr_col)))

       
        # rooks
        elif piece.piece_type == PieceType.Rook:
            offsets = [(-1, 0), (0, -1), (1, 0), (0, 1)]
            
            # check all offset directions
            for offset in offsets:
                # start square
                curr_row, curr_col = row+offset[0], col+offset[1]
                
                # while there is nothing in the way, keep adding the moves until we hit something (or out of bounds)
                while 0 <= curr_row < 8 and 0 <= curr_col < 8 and piece.is_not_friendly_piece(self.board[curr_row][curr_col]):
                    legal_moves.append(Move(location, (curr_row, curr_col)))
                    curr_row += offset[0]
                    curr_col += offset[1]


        # queen
        elif piece.piece_type == PieceType.Queen:
            offsets = [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (0, -1), (1, 0), (0, 1)]
            
            # check all offset directions
            for offset in offsets:
                # start square
                curr_row, curr_col = row+offset[0], col+offset[1]
                
                # while there is nothing in the way, keep adding the moves until we hit something (or out of bounds)
                while 0 <= curr_row < 8 and 0 <= curr_col < 8 and piece.is_not_friendly_piece(self.board[curr_row][curr_col]):
                    legal_moves.append(Move(location, (curr_row, curr_col)))
                    curr_row += offset[0]
                    curr_col += offset[1]


        # king
        elif piece.piece_type == PieceType.King:
            offsets = [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (0, -1), (1, 0), (0, 1)]

            for offset in offsets:
                curr_row, curr_col = row+offset[0], col+offset[1]

                # quick bounds/friendly piece check (no path checking here)
                if  0 <= curr_row < 8 and 0 <= curr_col < 8 and piece.is_not_friendly_piece(self.board[curr_row][curr_col]):
                    legal_moves.append(Move(location, (curr_row, curr_col)))


        return legal_moves
        


    # heavy lifting function here, gets all legal moves in the current position. simple enough implementation though.
    def get_all_legal_moves(self) -> list[Move]:
        all_legal_moves = []
        
        for row in range(0, 8):
            for col in range(0, 8):
                if self.board[row][col] is not None:
                    piece = self.board[row][col]
                    if piece.piece_color == self.side_to_move:
                        all_legal_moves += self.get_piece_legal_moves((row, col))

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
        moving_piece = self.board[move.end_pos[1]][move.end_pos[0]]

        # put the captured piece at the END location
        self.board[move.end_pos[1]][move.end_pos[0]] = captured_piece

        # "put down" the moving piece at the START location
        self.board[move.start_pos[1]][move.start_pos[0]] = moving_piece

        # change back the player to move 
        self.side_to_move = self.side_to_move.opponent()


# ---------------------------------------------------------------------------------------------------------------------
# the "engine"



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
