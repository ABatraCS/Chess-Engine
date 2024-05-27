# class representation of a move


# a move really only needs to know the start and end positions. other classes/functions can handle 
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

