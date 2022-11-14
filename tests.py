import lazor_proj
import os
import time

# Tests all bff files in current folder
files = [f for f in os.listdir('.') if os.path.isfile(f) and '.bff' in f]
for file in files:
    start_time = time.time()
    lazor = lazor_proj.lazor_game(file)
    lazor_positions = lazor.solve_lazor()
    if lazor_positions != []:
        lazor.output_solution(lazor_positions, file) # Plot solution
        txtoutput = "Completed solving {filename} in {totalTime:.2f} seconds." \
            "The solution png is outputted!".format(filename = file, totalTime = time.time() - start_time)
        print(txtoutput)
    else:
        print("Solution for lazors could not be solved!")
