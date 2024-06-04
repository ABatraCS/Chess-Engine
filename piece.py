# class represenation of a piece


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
    

    # for reading FEN
    @staticmethod
    def from_character(char: str):
        char_to_piece = {
            'P': (PieceType.Pawn, PieceColor.White),
            'R': (PieceType.Rook, PieceColor.White),
            'N': (PieceType.Knight, PieceColor.White),
            'B': (PieceType.Bishop, PieceColor.White),
            'Q': (PieceType.Queen, PieceColor.White),
            'K': (PieceType.King, PieceColor.White),
            'p': (PieceType.Pawn, PieceColor.Black),
            'r': (PieceType.Rook, PieceColor.Black),
            'n': (PieceType.Knight, PieceColor.Black),
            'b': (PieceType.Bishop, PieceColor.Black),
            'q': (PieceType.Queen, PieceColor.Black),
            'k': (PieceType.King, PieceColor.Black)
        }
        
        piece_type, piece_color = char_to_piece.get(char, (None, None))
        
        if piece_type is None or piece_color is None:
            raise ValueError(f"Invalid character for piece: {char}")
        
        return Piece(piece_type, piece_color)
    

    # for printing FEN
    def to_character(self) -> str:
        piece_to_char = {
            (PieceType.Pawn, PieceColor.White): 'P',
            (PieceType.Rook, PieceColor.White): 'R',
            (PieceType.Knight, PieceColor.White): 'N',
            (PieceType.Bishop, PieceColor.White): 'B',
            (PieceType.Queen, PieceColor.White): 'Q',
            (PieceType.King, PieceColor.White): 'K',
            (PieceType.Pawn, PieceColor.Black): 'p',
            (PieceType.Rook, PieceColor.Black): 'r',
            (PieceType.Knight, PieceColor.Black): 'n',
            (PieceType.Bishop, PieceColor.Black): 'b',
            (PieceType.Queen, PieceColor.Black): 'q',
            (PieceType.King, PieceColor.Black): 'k'
        }

        return piece_to_char.get((self.piece_type, self.piece_color), '?')


    # returns true if matches both color and type
    def matches(self, other_piece):
        if not other_piece: return False
        return self.piece_color == other_piece.piece_color and self.piece_type == other_piece.piece_type