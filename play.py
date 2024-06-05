# play the engine


from piece import *
from move import Move
from game import Game
from engine import *


def play_engine_from_start(depth=4):
    g = Game()

    while True:
        print(g)
        move_input = Move.from_uci(input("Enter a move in uci format (e.g. e2e4): "))
        g.make_move(move=move_input)

        print(g)
        print("Calculating engine move...")
        engine_move, engine_eval = brute_force_best_move(game=g, depth=depth)
        g.make_move(engine_move)
        print("Engine evaluation is", engine_eval)

play_engine_from_start(3)