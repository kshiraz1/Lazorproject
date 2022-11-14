'''
EN.540.635 Software Carpentry
Fall 2022
Lazor Project: Program that finds solution to different maps of the Lazor game
Author: Kiran
'''

# Import needed packages
import re
import copy
import matplotlib.pyplot as plt
import time
import itertools

class lazor_game():

    def __init__(self, bff_file):
        ''' Initialize lazor game. Takes in bff file to define grid information.'''
        # Define grid_blocks lists (original blocks)
        self.grid_blocks_allowed = []
        self.grid_blocks_notallowed = []
        self.grid_blocks_reflect = []
        self.grid_blocks_opaque = []
        self.grid_blocks_refract = []

        # Define movable block count and set movable blocks in grid to empty
        self.reflect_block_count = 0
        self.refract_block_count = 0
        self.opaque_block_count = 0
        self.blocks_reflect = []
        self.blocks_refract = []
        self.blocks_opaque = []
       
        # Define lazors list
        self.lazors = []

        # Define goals list 
        self.goals = []

        # Read in lines, remove lines that start with # (comments), only contains \n (empty line), or contains 'GRID START'
        with open(bff_file) as f:
            lines = [line.rstrip() for line in f if '#' not in line and line != '\n' and 'GRID START' not in line]
        
        # Find start and end index of grid
        index_grid_start = 0
        index_grid_end = lines.index('GRID STOP')

        # Define number of rows and columns of grid
        self.num_rows = (index_grid_end - index_grid_start) * 2
        self.num_cols = len(lines[index_grid_start].replace(' ', '')) * 2

        # Iterate through grid to fill in grid_blocks lists
        for row in range(index_grid_start, index_grid_end):
            line = lines[row].replace(' ', '')
            cur_y = row * 2 + 1
            for col in range(0, len(line)):
                char = line[col]
                cur_x = col * 2 + 1
                if char == 'o':
                    self.grid_blocks_allowed.append((cur_x, cur_y))
                elif char == 'x':
                    self.grid_blocks_notallowed.append((cur_x, cur_y))
                elif char == 'A':
                    self.grid_blocks_reflect.append((cur_x, cur_y))
                elif char == 'B':
                    self.grid_blocks_opaque.append((cur_x, cur_y))
                elif char == 'C':
                    self.grid_blocks_refract.append((cur_x, cur_y))
        
        # Determine number of movable reflect, opaque, and refract blocks
        all_lines = ', '.join(lines[index_grid_end:])
        all_movable_blocks = re.findall('[ABC] \\d', all_lines)
        for cur_movable_block in all_movable_blocks:
            if 'A' in cur_movable_block:
                self.reflect_block_count = int(re.findall('\\d', cur_movable_block)[0])
            elif 'B' in cur_movable_block:
                self.opaque_block_count = int(re.findall('\\d', cur_movable_block)[0])
            elif 'C' in cur_movable_block:
                self.refract_block_count = int(re.findall('\\d', cur_movable_block)[0])
    
        # Determine lazor information
        all_lazors = re.findall('[L] \\d \\d [-]?\\d [-]?\\d', all_lines)
        for cur_lazor in all_lazors:
            cur_lazor_info = re.findall('\\d \\d [-]?\\d [-]?\\d', cur_lazor)[0].split(' ')
            cur_lazor_info_int = []
            for info in cur_lazor_info:
                cur_lazor_info_int.append(int(info))
            self.lazors.append(cur_lazor_info_int)

        # Determine goal information
        all_goals = re.findall('[P] \\d \\d', all_lines)
        for cur_goal in all_goals:
            cur_goal_info = re.findall('\\d \\d', cur_goal)[0].split(' ')
            cur_goal_info_int = []
            for info in cur_goal_info:
                cur_goal_info_int.append(int(info))
            self.goals.append((cur_goal_info_int[0], cur_goal_info_int[1]))
    
    def valid_pos(self, position):
        valid = True
        pos_x = position[0]
        pos_y = position[1]
        if pos_x < 0 or pos_y < 0 or pos_x > self.num_cols or pos_y > self.num_rows:
            valid = False
        return valid

    def determine_lazor_positions(self):
        '''Determine the lazor positions given the positions for the movable
        blocks.'''
        # Intialization lazor positions, lazor history, lazor queue, and lazor plotting
        lazor_positions = [(pos[0], pos[1]) for pos in self.lazors]
        lazor_history = []
        lazor_queue = copy.deepcopy(self.lazors)

        # While positions are still in lazor queue, continue
        while len(lazor_queue) > 0:
            # Current lazor is first position in queue
            cur_lazor = lazor_queue[0];
            lazor_pos = (cur_lazor[0], cur_lazor[1])
            lazor_dx = cur_lazor[2]
            lazor_dy = cur_lazor[3]

            # New lazor position, adding dx and dy
            new_lazor_pos = (lazor_pos[0] + lazor_dx, lazor_pos[1] + lazor_dy)

            # If current lazor is not in lazor history
            if cur_lazor not in lazor_history:
                lazor_history.append(cur_lazor)

                # If new lazor is not out of bounds
                if self.valid_pos(new_lazor_pos):
                    lazor_x_move_only = (lazor_pos[0] + lazor_dx, lazor_pos[1])
                    lazor_y_move_only = (lazor_pos[0], lazor_pos[1] + lazor_dy)
                    
                    # If new lazor is not opaque
                    is_opaque_block = lazor_x_move_only in self.blocks_opaque or lazor_x_move_only in self.grid_blocks_opaque or \
                    lazor_y_move_only in self.blocks_opaque or lazor_y_move_only in self.grid_blocks_opaque
                    
                    if not is_opaque_block:
                        # Add same lazor with new lazor direction if blocks are reflect or refract
                        if lazor_x_move_only in self.blocks_reflect or lazor_x_move_only in self.grid_blocks_reflect:
                            lazor_queue.append([lazor_pos[0], lazor_pos[1], -lazor_dx, lazor_dy])
                        elif lazor_y_move_only in self.blocks_reflect or lazor_y_move_only in self.grid_blocks_reflect:
                            lazor_queue.append([lazor_pos[0], lazor_pos[1], lazor_dx, -lazor_dy])
                        elif lazor_x_move_only in self.blocks_refract or lazor_x_move_only in self.grid_blocks_refract:
                            lazor_queue.append([lazor_pos[0], lazor_pos[1], -lazor_dx, lazor_dy])
                            lazor_queue.append([new_lazor_pos[0], new_lazor_pos[1], lazor_dx, lazor_dy])
                            lazor_positions.append(new_lazor_pos)
                        elif lazor_y_move_only in self.blocks_refract or lazor_y_move_only in self.grid_blocks_refract:
                            lazor_queue.append([lazor_pos[0], lazor_pos[1], lazor_dx, -lazor_dy])
                            lazor_queue.append([new_lazor_pos[0], new_lazor_pos[1], lazor_dx, lazor_dy])
                            lazor_positions.append(new_lazor_pos)
                        # Otherwise, add new lazor with same direction
                        else:
                            lazor_queue.append([new_lazor_pos[0], new_lazor_pos[1], lazor_dx, lazor_dy])  
                            lazor_positions.append(new_lazor_pos)  
            # Pop the first lazor off the queue
            lazor_queue.pop(0)
        return lazor_positions
                    
    def output_solution(self, lazor_positions, filename):
        '''Draw the solution and output.'''
        
        # Set block, goal, and lazor size
        block_size = 900
        goal_size = 70
        lazor_size = 30

        # Set background color to green
        ax = plt.axes()
        ax.set_facecolor([0.5647, 0.933, 0.5647])

        # Plot goals as yellow circles
        x_goals = [goal[0] for goal in self.goals]
        y_goals = [self.num_rows - goal[1] for goal in self.goals]
        plt.scatter(x_goals, y_goals, color='yellow', s = goal_size)

        # Plot grid blocks allowed as hollow black squares
        x_blocks_allowed = [block[0] for block in self.grid_blocks_allowed]
        y_blocks_allowed = [self.num_rows - block[1] for block in self.grid_blocks_allowed]
        plt.scatter(x_blocks_allowed, y_blocks_allowed, edgecolors='black', s = block_size,  marker = 's', facecolors = 'none')

        # Plot blocks reflect
        blocks_reflect = self.blocks_reflect + self.grid_blocks_reflect
        x_blocks_reflect = [block[0] for block in blocks_reflect]
        y_blocks_reflect = [self.num_rows - block[1] for block in blocks_reflect]
        plt.scatter(x_blocks_reflect, y_blocks_reflect, color='blue', s = block_size,  marker = 's')

        # Plot movable blocks refract
        blocks_refract = self.blocks_refract + self.grid_blocks_refract
        x_blocks_refract = [block[0] for block in blocks_refract]
        y_blocks_refract = [self.num_rows - block[1] for block in blocks_refract]
        plt.scatter(x_blocks_refract, y_blocks_refract, color='white', s = block_size,  marker = 's')

        # Plot movable blocks opaque
        blocks_opaque = self.blocks_opaque + self.grid_blocks_opaque
        x_blocks_opaque = [block[0] for block in blocks_opaque]
        y_blocks_opaque = [self.num_rows - block[1] for block in blocks_opaque]
        plt.scatter(x_blocks_opaque, y_blocks_opaque, color='gray', s = block_size,  marker = 's')

        # Plot lazor as red stars
        x_lazors = [lazor[0] for lazor in lazor_positions]
        y_lazors = [self.num_rows - lazor[1] for lazor in lazor_positions]
        plt.scatter(x_lazors, y_lazors, color='red', s = lazor_size,  marker = '*')

        # Plot X's on original grid, unmovable reflect, refract, and opaque blocks
        blocks_grid_original = self.grid_blocks_reflect + self.grid_blocks_refract + self.grid_blocks_opaque
        x_blocks_grid_original = [block[0] for block in blocks_grid_original]
        y_blocks_grid_original = [self.num_rows - block[1] for block in blocks_grid_original]
        plt.scatter(x_blocks_grid_original, y_blocks_grid_original, color='white', s = block_size,  marker = 'x')

        # Change x and y lims
        buffer = 0.25
        plt.xlim([-buffer, self.num_cols + buffer])
        plt.ylim([-buffer, self.num_rows + buffer])
        ax.set_aspect('equal', adjustable = 'box')
        filename = filename.split(".bff")[0]
        plt.savefig('solved_lazor_' + filename + '.png')

    def solve_lazor(self):
        ''' Solve the lazor game and return the solution.'''
       
        # Compute all possible scenarios
        number_of_blocks = self.reflect_block_count + self.opaque_block_count + self.refract_block_count
        block_types = [1]*self.reflect_block_count + [2]*self.opaque_block_count + [3]*self.refract_block_count
        scenarios = list(itertools.combinations(self.grid_blocks_allowed, number_of_blocks))
        block_permutations = list(set(itertools.permutations(list(block_types))))
        
        # Iterate through all possible scenarios
        for i in range(len(scenarios)):
            cur_scenario = scenarios[i]
            
            # Iterate through all possible block permutations
            for j in range(len(block_permutations)):
                cur_block_permutation = block_permutations[j]
                
                # Make a deepcopy of the grid_blocks_allowed list
                grid_blocks_allowed = copy.deepcopy(self.grid_blocks_allowed)
                
                # Assign blocks and solve for lazor positions
                for k in range(len(cur_block_permutation)):
                    cur_block = cur_block_permutation[k]
                    if cur_block == 1:
                        self.blocks_reflect.append(cur_scenario[k])
                        grid_blocks_allowed.remove(cur_scenario[k])
                    elif cur_block == 2:
                        self.blocks_opaque.append(cur_scenario[k])
                        grid_blocks_allowed.remove(cur_scenario[k])
                    elif cur_block == 3:
                        self.blocks_refract.append(cur_scenario[k])
                        grid_blocks_allowed.remove(cur_scenario[k])
                lazor_positions = self.determine_lazor_positions()
                        
                # If solved, break
                if all(goal in lazor_positions for goal in self.goals):
                    self.grid_blocks_allowed = grid_blocks_allowed
                    return lazor_positions
                        
                # Reset movable reflect, opaque, and refract blocks
                else:
                    self.blocks_reflect = []
                    self.blocks_opaque = []
                    self.blocks_refract = []
        
        
if __name__ == '__main__':
    # Update filename here
    file = 'mad_1.bff'

    # Create lazor class and run solver
    start_time = time.time()
    lazor = lazor_game(file)
    lazor_positions = lazor.solve_lazor()

    # Outputs if and if no solution were found
    if lazor_positions != []:
        lazor.output_solution(lazor_positions, file) # Plot solution
        txtoutput = "Completed in {totalTime:.2f} seconds. The solution png is outputted!".format(totalTime = time.time() - start_time)
        print(txtoutput)
    else:
        print("Solution for lazors could not be solved!")
