from game import *
from piece import *
from move import *
import csv

def zobrist_testing(game: Game):
    moves1 = game.get_all_legal_moves()
    initial_hash = game.hash()

    for m1 in moves1:
        # count += 1
        # if count > 5: break
        hash_before = game.zobrist_hash
        captured1 = game.make_move(m1)
        game.un_make_move(m1, captured1)
        hash_after = game.zobrist_hash

        if hash_before != hash_after:
            print("Hashes do not match after", m1, ":")
            print("Hash before:", hash_before)
            print("Hash after:", hash_after)

            print(game)

    final_hash = game.hash()
    if initial_hash == final_hash:
        print("Initial and final hashes match.")
        return True
    else:
        print("Initial and final hashes DO NOT match.")
        return False


# solves puzzles from a csv filepath, quite a lot is assumed here
def random_position_zobrist_testing(filepath: str, num_puzzles: int = 20):
    with open(filepath, 'r') as file:
        csvreader = csv.reader(file)
        next(csvreader) # header

        count = 0

        for _ in range(num_puzzles):
            
            # for _ in range(random.randint(10, 50)):
            #     next(csvreader)

            row = next(csvreader)

            fen, best_move, rating = row[1], row[2], int(row[3])
            # print(rating, "...", end=' ', flush=True)

            # get best move
            count += zobrist_testing(Game(fen))

        
        # results
        print("\n\n--------------------RESULTS--------------------")
        print(num_puzzles, "positions hashed,", count, "correctly.")


random_position_zobrist_testing("lichess_db_puzzle_with_stockfish_eval.csv", num_puzzles=1000)