# class representation of a game


from piece import *
from move import Move


# our game only needs to know the board and whose turn it is; we will later add castling rights, 
# en passant target squares, move count, etc, but for now this is sufficient.
class Game: 
    # note that the board here is read in as FEN representation. There are no bounds checks,
    # later we will enforce this. Also, it's just a 2D array. If we are looking to really get 
    # fast, we should consider changing the fundamental data structure to something like a tree.
    def __init__(self, fen: str="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
        rows = fen.split("/")   
        self.side_to_move = (PieceColor.White if rows[1] == 'w' else PieceColor.Black)

        self.board = [[0 for _ in range(8)] for _ in range(8)]

        # populate the game board
        for row in range(1, 9):
            current_column = 1
            for character in rows[row]:
                # if there is a number, there is an n-square gap in the row
                if character in ['1', '2', '3', '4', '5', '6', '7', '8']:
                    current_column += int(character)
                
                # otherwise, parse the piece and add it to the board
                else:
                    self.board[8-row, current_column] = Piece.from_character(character)
                    current_column += 1


    # pretty printing
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


    # converts to a fen string (some issues with last few bits but board/side is accurate)
    def to_fen(self) -> str:
        fen = ""

        # boards
        for row in range(7, -1, -1):
            column_offset = 0
            for column in range(1, 9):
                if self.board[row, column]:
                    if column_offset != 0: fen += str(column_offset)
                    fen += Piece.to_character(self.board[row, column])
                    column_offset = 0
                else:
                    column_offset += 1

            if column_offset != 0: fen += str(column_offset)
            if row != 1: fen += "/"

        # player
        fen += " " + ("w" if self.player_to_move == PieceColor.White else "b")
        fen += " - - 0 1"
        return fen


