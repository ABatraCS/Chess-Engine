# engine strength testing.


import csv, random, time
from engine import * 
from game import *


# solves puzzles from a csv filepath, quite a lot is assumed here
def solve_puzzles(filepath: str, num_puzzles: int = 20, depth=3):
    with open(filepath, 'r') as file:
        csvreader = csv.reader(file)
        next(csvreader) # header

        # setup
        count = 0
        num_correct = 0
        elo = 1400              # initial elo
        kfactor = 500           # max amount gained/lost in a given round (decays over time)
        highest_problem_solved = 0

        start = time.time()

        for _ in range(num_puzzles):
            count += 1
            
            for _ in range(random.randint(10, 50)):
                next(csvreader)

            row = next(csvreader)

            fen, best_move, rating = row[1], row[2], int(row[3])
            print(rating, "...", end=' ', flush=True)

            # get best move
            generated_move, _ = brute_force_best_move(Game(fen), depth)

            # determine result
            if best_move == str(generated_move):
                print('solved! \t', end=' ')
                did_solve = 1
            else:
                print('no.     \t', end=' ')
                did_solve = 0

            # calculate the elo from the result
            num_correct += did_solve
            elo += kfactor * (did_solve - 1 / (1 + 10 ** ( (rating - elo) // 400)))     # this is how it's done
            kfactor = max(32, (kfactor * 0.80))                                         # kfactor decay
            highest_problem_solved = max(highest_problem_solved, rating * did_solve)
            print("New elo = ", int(elo))
        
        # results
        print("\n\n--------------------RESULTS--------------------")
        print(num_puzzles, "puzzles attempted,", num_correct, "correct,", num_puzzles-num_correct, "incorrect in", str(round(time.time()-start, 1)), "seconds")
        print("Highest problem solved:", highest_problem_solved)
        print("Estimated engine ELO:", round(elo), "\n\n")


solve_puzzles("lichess_db_puzzle_with_stockfish_eval.csv", num_puzzles=20, depth=4)