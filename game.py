# class representation of a game


import random
from piece import *
from move import Move


# our game only needs to know the board and whose turn it is; we will later add castling rights, 
# en passant target squares, move count, etc, but for now this is sufficient.
class Game: 
    # note that the board here is read in as FEN representation. There are no bounds checks,
    # later we will enforce this. Also, it's just a 2D array. If we are looking to really get 
    # fast, we should consider changing the fundamental data structure to something like a tree.
    def __init__(self, fen: str="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
        splitted = fen.split(' ')
        self.side_to_move = (PieceColor.White if splitted[1] == 'w' else PieceColor.Black)

        self.white_castle_kingside: bool = 'K' in splitted[2]
        self.white_castle_queenside: bool = 'Q' in splitted[2]
        self.black_castle_kingside: bool = 'k' in splitted[2]
        self.black_castle_queenside: bool = 'q' in splitted[2]

        self.en_passant_target_square: str = splitted[3] # should change to Piece but i'm lazy

        self.halfmove_clock: int = int(splitted[4])
        self.fullmove_number: int = int(splitted[5])

        rows = splitted[0].split('/')
        self.board = [[None for _ in range(8)] for _ in range(8)]

        # populate the game board
        for row in range(8):
            current_column = 0
            for character in rows[row]:
                # if there is a number, there is an n-square gap in the row
                if character in ['1', '2', '3', '4', '5', '6', '7', '8']:
                    current_column += int(character)
                
                # otherwise, parse the piece and add it to the board
                else:
                    self.board[7-row][current_column] = Piece.from_character(character)
                    current_column += 1

        self.zobrist_table = [random.getrandbits(64) for _ in range(768+1)] # 768 = pieces on square, 4 = castling rights, 1 = side to move. no EP target square = todo
        self.zobrist_hash = self.hash()


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


    # gets the zobrist hash for a given board state (unique 64-bit int).
    # this is used for a transposition table during engine eval (dp)
    def hash(self) -> int:
        hash = 0
        
        # each piece on each square
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    hash = hash ^ self.zobrist_table[row*64 + col*12 + piece.zobrist_index()]

        # side to move
        if self.side_to_move == PieceColor.Black:
            hash = hash ^ self.zobrist_table[-1]

        return hash


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
                    # check promotions
                    if row+1 == 7: 
                        legal_moves += [Move(location, (row+1, col), promotion=promotion_type) for promotion_type in [1, 2, 3, 4]]
                    else:
                        legal_moves.append(Move(location, (row+1, col)))
                    
                    # second push if on the start row
                    if row == 1 and not self.board[row+2][col]:
                        legal_moves.append(Move(location, (row+2, col)))

            else:
                # first push
                if not self.board[row-1][col]:
                    if row-1 == 0: 
                        legal_moves += [Move(location, (row-1, col), promotion=promotion_type) for promotion_type in [1, 2, 3, 4]]
                    else:
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
                    
                    # stop the path once we run into a piece. note that we add the piece if it's not friendly (i.e. we can take it)
                    if self.board[curr_row][curr_col]: break

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
                    
                    # stop the path once we run into a piece. note that we add the piece if it's not friendly (i.e. we can take it)
                    if self.board[curr_row][curr_col]: break

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

                    # stop the path once we run into a piece. note that we add the piece if it's not friendly (i.e. we can take it)
                    if self.board[curr_row][curr_col]: break
                    
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

            
            # check castling rights. this involves knowing if it's legal to castle
            if self.side_to_move == PieceColor.White:
                if self.white_castle_kingside:
                    if self.board[0][5] == None and self.board[0][6] == None:
                        legal_moves.append(Move(location, (0, 6)))
                if self.white_castle_queenside:
                    if self.board[0][1] == None and self.board[0][2] == None and self.board[0][3] == None:
                        legal_moves.append(Move(location, (0, 2)))

            else:
                if self.black_castle_kingside:
                    if self.board[7][5] == None and self.board[7][6] == None:
                        legal_moves.append(Move(location, (7, 6)))

                if self.black_castle_queenside:
                    if self.board[7][1] == None and self.board[7][2] == None and self.board[7][3] == None:
                        legal_moves.append(Move(location, (7, 2)))


        return legal_moves
        

    # heavy lifting function here, gets all legal moves in the current position. simple enough implementation though.
    def get_all_legal_moves(self) -> list[Move]:
        all_legal_moves = []
        
        for row in range(0, 8):
            for col in range(0, 8):
                piece = self.board[row][col]
                if piece is not None:
                    if piece.piece_color == self.side_to_move:
                        all_legal_moves += self.get_piece_legal_moves((row, col))

        return all_legal_moves
    

    # makes a move on the given board, returns a captured piece if any.
    # also updates the zobrist hash based on the new game state.
    def make_move(self, move: Move) -> Piece | None:
        captured_piece = self.board[move.end_pos[0]][move.end_pos[1]]
        if captured_piece: self.zobrist_hash = self.zobrist_hash ^ self.zobrist_table[move.end_pos[0]*96 + move.end_pos[1]*12 + captured_piece.zobrist_index()]

        moving_piece = self.board[move.start_pos[0]][move.start_pos[1]]

        # handle promotions
        if move.promotion != 0:
            promoted_piece = Piece(Move.promotion_to_piecetype(move.promotion), moving_piece.piece_color)
            self.board[move.end_pos[0]][move.end_pos[1]] = promoted_piece
            self.zobrist_hash = self.zobrist_hash ^ self.zobrist_table[move.end_pos[0]*96 + move.end_pos[1]*12 + promoted_piece.zobrist_index()] 

        # move the moving piece to the end location
        else:
            self.board[move.end_pos[0]][move.end_pos[1]] = moving_piece
            self.zobrist_hash = self.zobrist_hash ^ self.zobrist_table[move.end_pos[0]*96 + move.end_pos[1]*12 + moving_piece.zobrist_index()]
        
        # remove the moving piece from the start location
        self.board[move.start_pos[0]][move.start_pos[1]] = None
        self.zobrist_hash = self.zobrist_hash ^ self.zobrist_table[move.start_pos[0]*96 + move.start_pos[1]*12 + moving_piece.zobrist_index()]

        # handling castling, specifically moving the rook
        # white kingside
        if moving_piece.matches(Piece(PieceType.King, PieceColor.White)) and move.start_pos == (0, 4) and move.end_pos == (0, 6):
            rook = self.board[0][7]
            self.board[0][5] = rook
            self.zobrist_hash = self.zobrist_hash ^ self.zobrist_table[0*96 + 5*12 + rook.zobrist_index()]
            self.board[0][7] = None
            self.zobrist_hash = self.zobrist_hash ^ self.zobrist_table[0*96 + 7*12 + rook.zobrist_index()]
            self.white_castle_kingside = False
        
        # white queenside
        elif moving_piece.matches(Piece(PieceType.King, PieceColor.White)) and move.start_pos == (0, 4) and move.end_pos == (0, 2):
            rook = self.board[0][0]
            self.board[0][3] = rook
            self.zobrist_hash = self.zobrist_hash ^ self.zobrist_table[0*96 + 3*12 + rook.zobrist_index()]
            self.board[0][0] = None
            self.zobrist_hash = self.zobrist_hash ^ self.zobrist_table[0*96 + 0*12 + rook.zobrist_index()]
            self.white_castle_queenside = False

        # black kingside
        elif moving_piece.matches(Piece(PieceType.King, PieceColor.Black)) and move.start_pos == (7, 4) and move.end_pos == (7, 6):
            rook = self.board[7][7]
            self.board[7][5] = rook
            self.zobrist_hash = self.zobrist_hash ^ self.zobrist_table[7*96 + 5*12 + rook.zobrist_index()]
            self.board[7][7] = None
            self.zobrist_hash = self.zobrist_hash ^ self.zobrist_table[7*96 + 7*12 + rook.zobrist_index()]
            self.black_castle_kingside = False

        # black queenside
        elif moving_piece.matches(Piece(PieceType.King, PieceColor.Black)) and move.start_pos == (7, 4) and move.end_pos == (7, 2):
            rook = self.board[7][0]
            self.board[7][3] = rook
            self.zobrist_hash = self.zobrist_hash ^ self.zobrist_table[7*96 + 3*12 + rook.zobrist_index()]
            self.board[7][0] = None
            self.zobrist_hash = self.zobrist_hash ^ self.zobrist_table[7*96 + 0*12 + rook.zobrist_index()]
            self.black_castle_queenside = False


        # flip the side to move
        self.side_to_move = self.side_to_move.opponent()
        self.zobrist_hash = self.zobrist_hash ^ self.zobrist_table[-1]

        return captured_piece


    # unmakes a move on the given board, replacing the captured piece.
    # also reverts the zobrist hash made by the move.
    def un_make_move(self, move: Move, captured_piece: Piece | None):
        # "pick up" the moving piece at the END location
        moving_piece = self.board[move.end_pos[0]][move.end_pos[1]]

        # handling un-promotions
        if move.promotion != 0:
            pawn = Piece(PieceType.Pawn, moving_piece.piece_color)
            self.board[move.start_pos[0]][move.start_pos[1]] = pawn
            self.zobrist_hash = self.zobrist_hash ^ self.zobrist_table[move.start_pos[0]*96 + move.start_pos[1]*12 + pawn.zobrist_index()]
        else:
            # "put down" the moving piece at the START location
            self.board[move.start_pos[0]][move.start_pos[1]] = moving_piece
            self.zobrist_hash = self.zobrist_hash ^ self.zobrist_table[move.start_pos[0]*96 + move.start_pos[1]*12 + moving_piece.zobrist_index()]

        # set the original end to be none
        self.board[move.end_pos[0]][move.end_pos[1]] = None
        self.zobrist_hash = self.zobrist_hash ^ self.zobrist_table[move.end_pos[0]*96 + move.end_pos[1]*12 + moving_piece.zobrist_index()]

        # put the captured piece at the END location
        if captured_piece:
            self.board[move.end_pos[0]][move.end_pos[1]] = captured_piece
            self.zobrist_hash = self.zobrist_hash ^ self.zobrist_table[move.end_pos[0]*96 + move.end_pos[1]*12 + captured_piece.zobrist_index()]

        # handling castling, specifically moving the rook back
        # white kingside
        if moving_piece.matches(Piece(PieceType.King, PieceColor.White)) and move.start_pos == (0, 4) and move.end_pos == (0, 6):
            rook = self.board[0][5]
            self.board[0][7] = rook
            self.zobrist_hash = self.zobrist_hash ^ self.zobrist_table[0*96 + 7*12 + rook.zobrist_index()]
            self.board[0][5] = None
            self.zobrist_hash = self.zobrist_hash ^ self.zobrist_table[0*96 + 5*12 + rook.zobrist_index()]
            self.white_castle_kingside = False
        
        # white queenside
        elif moving_piece.matches(Piece(PieceType.King, PieceColor.White)) and move.start_pos == (0, 4) and move.end_pos == (0, 2):
            rook = self.board[0][3]
            self.board[0][0] = rook
            self.zobrist_hash = self.zobrist_hash ^ self.zobrist_table[0*96 + 0*12 + rook.zobrist_index()]
            self.board[0][3] = None
            self.zobrist_hash = self.zobrist_hash ^ self.zobrist_table[0*96 + 3*12 + rook.zobrist_index()]
            self.white_castle_queenside = False

        # black kingside
        elif moving_piece.matches(Piece(PieceType.King, PieceColor.Black)) and move.start_pos == (7, 4) and move.end_pos == (7, 6):
            rook = self.board[7][5]
            self.board[7][7] = rook
            self.zobrist_hash = self.zobrist_hash ^ self.zobrist_table[7*96 + 7*12 + rook.zobrist_index()]
            self.board[7][5] = None
            self.zobrist_hash = self.zobrist_hash ^ self.zobrist_table[7*96 + 5*12 + rook.zobrist_index()]
            self.black_castle_kingside = False

        # black queenside
        elif moving_piece.matches(Piece(PieceType.King, PieceColor.Black)) and move.start_pos == (7, 4) and move.end_pos == (7, 2):
            rook = self.board[7][3]
            self.board[7][0] = rook
            self.zobrist_hash = self.zobrist_hash ^ self.zobrist_table[7*96 + 0*12 + rook.zobrist_index()]
            self.board[7][3] = None
            self.zobrist_hash = self.zobrist_hash ^ self.zobrist_table[7*96 + 3*12 + rook.zobrist_index()]
            self.black_castle_queenside = False


        # change back the player to move 
        self.side_to_move = self.side_to_move.opponent()
        self.zobrist_hash = self.zobrist_hash ^ self.zobrist_table[-1]


    # converts to a fen string (some issues with last few bits but board/side is accurate)
    def to_fen(self) -> str:
        board = ""

        # boards
        for row in range(7, -1, -1):
            column_offset = 0
            for column in range(0, 8):
                if self.board[row][column]:
                    if column_offset != 0: board += str(column_offset)
                    board += Piece.to_character(self.board[row][column])
                    column_offset = 0
                else:
                    column_offset += 1

            if column_offset != 0: board += str(column_offset)
            if row != 0: board += "/"

        # player
        side = ("w" if self.side_to_move == PieceColor.White else "b")
        
        # castling
        castling_rights = []
        if self.white_castle_kingside:
            castling_rights.append('K')
        if self.white_castle_queenside:
            castling_rights.append('Q')
        if self.black_castle_kingside:
            castling_rights.append('k')
        if self.black_castle_queenside:
            castling_rights.append('q')
        castle = ''.join(castling_rights) or '-'
    
        # en passant target square
        en_passant = self.en_passant_target_square or '-'

        # move numbers
        halfmove = str(self.halfmove_clock)
        fullmove = str(self.fullmove_number)

        return " ".join([board, side, castle, en_passant, halfmove, fullmove])


    # converts the board into a 3D matrix which is readable by a CNN.
    def to_cnn_representation(self) -> list[list[list[int]]]:
        rep = []

        piece_types = [
            Piece(PieceType.Pawn, PieceColor.White),
            Piece(PieceType.Rook, PieceColor.White),
            Piece(PieceType.Knight, PieceColor.White),
            Piece(PieceType.Bishop, PieceColor.White),
            Piece(PieceType.Queen, PieceColor.White),
            Piece(PieceType.King, PieceColor.White),
            Piece(PieceType.Pawn, PieceColor.Black),
            Piece(PieceType.Rook, PieceColor.Black),
            Piece(PieceType.Knight, PieceColor.Black),
            Piece(PieceType.Bishop, PieceColor.Black),
            Piece(PieceType.Queen, PieceColor.Black),
            Piece(PieceType.King, PieceColor.Black)
        ]

        # a matrix for the location of every piece type
        for piece_type in piece_types:
            rep.append([[1 if piece_type.matches(piece) else 0 for piece in row] for row in self.board])
        

        # a matrix for where white has legal moves and where black has legal moves
        
        # if it's white's turn, do a quick piececolor switch when doing black
        if self.side_to_move == PieceColor.White:
            white_matrix = [[0 for _ in range(8)] for _ in range(8)]
            legal_moves = self.get_all_legal_moves()
            for move in legal_moves:
                end_row, end_col = move.end_pos[0], move.end_pos[1]
                white_matrix[end_row][end_col] = 1
            rep.append(white_matrix)

            # a matrix for where black can move
            black_matrix = [[0 for _ in range(8)] for _ in range(8)]
            self.side_to_move == PieceColor.Black
            legal_moves = self.get_all_legal_moves()
            self.side_to_move == PieceColor.White
            for move in legal_moves:
                end_row, end_col = move.end_pos[0], move.end_pos[1]
                black_matrix[end_row][end_col] = 1
            rep.append(black_matrix)


        # if it's black's turn, do a quick piececolor switch when doing white
        else:
            white_matrix = [[0 for _ in range(8)] for _ in range(8)]
            self.side_to_move == PieceColor.White
            legal_moves = self.get_all_legal_moves()
            self.side_to_move == PieceColor.Black
            for move in legal_moves:
                end_row, end_col = move.end_pos[0], move.end_pos[1]
                white_matrix[end_row][end_col] = 1
            rep.append(white_matrix)

            # a matrix for where black can move
            black_matrix = [[0 for _ in range(8)] for _ in range(8)]
            self.side_to_move == PieceColor.Black
            legal_moves = self.get_all_legal_moves()
            self.side_to_move == PieceColor.White
            for move in legal_moves:
                end_row, end_col = move.end_pos[0], move.end_pos[1]
                black_matrix[end_row][end_col] = 1
            rep.append(black_matrix)

        return rep
