import numpy as np
from copy import deepcopy
import random

class GameBoard:
    def __init__(self, grid = None, player_to_play = 0) -> None:
        # in case a perticular game board needs to be simulated further
        if grid is not None:
            self.grid = grid
            self.player_to_play = player_to_play
        
        else:
            self.grid = np.full(shape = (8,8), fill_value = " ", dtype = "U1")
            self.player_to_play = 0 # white to move first

        self.player_id = {"white": 0, "black": 1}
    
    @staticmethod
    def find_columns_filled_index(grid):
        columns_filled_index = np.zeros(8, dtype=np.int8)
        for i in range(8):
            temp_index = np.where(grid[:, i] == " ")[0]
            if len(temp_index)>0:
                columns_filled_index[i] = int( 8 - len(np.where(grid[:, i] == " ")[0]))
            else:
                columns_filled_index[i] = 8
        return columns_filled_index
    
    def print_grid(self):
        """Grid display function
        """
        print("     ", end = "")
        for i in range(8):
            print("| ", i+1, " |", end="")
        print("\n     =========================================================")

        # display rows and data of grid
        for i in range(8):
            print(f"  {i+1}  ", end="")
            for j in range(8):
                print(f"|  {self.grid[i, j]}  |", end = "")
            print("\n")
        print("     =========================================================")

    def can_drop(self, grid = None,  col = 1):
        """Check if drop at a specific location possible or not

        Args:
            col (_type_): column to drop
        """
        if grid is None:
            columns_fill_index = self.find_columns_filled_index(self.grid)
        else:
            columns_fill_index = self.find_columns_filled_index(grid)

        if columns_fill_index[col - 1] < 8 and 0 <= (col - 1) <= 7:
            return True
        else:
            return False

    def action_drop(self, col = 1):
        """Action that will drop ball in a specific column

        Args:
            col (_type_): column to drop
            grid : if another type of grid to use

        Return:
            Drop successful or not
        """
        columns_fill_index = self.find_columns_filled_index(self.grid)
        if columns_fill_index[col - 1] < 8 and 0 <= (col - 1) <= 7:
            self.grid[ 7 - columns_fill_index[col - 1], col - 1] = str(self.player_to_play)
            return True, self.grid
        else:
            return False, self.grid 
    
    def can_slide(self, x, y, direction):
        """_summary_

        Args:
            x (_type_): value in x
            y (_type_): value in y
            direction (_type_): 'l' or 'r'
        """
        check_num_pieces_flag = True
        max_run = -1 # run = 1 if two pieces and run = 2 if there are three consecutive pieces
        
        # checking if consecutive pieces present or not!
        offset = np.array([0, 1, 2]) * ( (-1) ** int(direction.lower() == 'l'))
        for i in offset:
            if 0<=(x-1+i)<=7:
                if self.grid[y - 1, x - 1 + i] == str(self.player_to_play):
                    max_run += 1
                else:
                    break
            else:
                break
        
        if max_run <= 0:
            return False, max_run
        # now check if the adject player is of opponents or not
        offset = np.array([max_run + 1, max_run + 2]) * ( (-1) ** int(direction.lower() == 'l'))
        # check if opponent is present
        if x - 1 + offset[0] > 7 or x - 1 + offset[0] < 0:
            return False, max_run
        
        if not((0 <= x - 1 + offset[0] <= 7) and self.grid[y - 1, x - 1 + offset[0]] == str((self.player_to_play + 1) % 2)):
            # out of the grid or opponent is not adjacent
            return False, max_run
        elif x - 1 + offset[1] < 0 or x - 1 + offset[1] > 7:
            return True, max_run
        elif not (self.grid[y - 1, x - 1 + offset[1]] == " "): 
            return False, max_run

        return True, max_run
        # 

    def action_slide(self, x, y, direction = 'l'):
        """This function performs the sliding operation. Sliding operation can be performed by two ways.
           1. if opponent is on the edge
           2. if there is a gap after apponent
        Args:
            x (int): rows
            y (int): columns
        """
        flag, max_runs = self.can_slide(x, y, direction)
        original_x, original_y = x - 1, y - 1
        if flag:
            if direction.lower() == 'l': # for left
                # if there is an edge
                if original_x - max_runs - 2 < 0:
                    self.grid[original_y, original_x - max_runs - 1 : original_x ] = self.grid[original_y, original_x - max_runs : original_x + 1]
                # if it's not an edge
                else:
                    self.grid[original_y, original_x - max_runs - 2 : original_x] =  self.grid[original_y, original_x - max_runs - 1 : original_x + 1]
               
                self.grid[original_y, original_x] = " "
            
            elif direction.lower() == 'r': # for right
                # edge case
                if original_x + max_runs + 2 > 7:
                    self.grid[original_y, original_x + 1 : original_x + max_runs + 2] = self.grid[original_y, original_x : original_x + max_runs + 1]
                else:
                    self.grid[original_y, original_x + 1 : original_x + max_runs + 3] = self.grid[original_y, original_x: original_x + max_runs + 2]
                self.grid[original_y, original_x] = " "
            else:
                return False, self.grid.copy()
            # drop function 
            self.action_fill_gap()
            return True, self.grid.copy()
        else:
            return False, self.grid.copy()

    def find_gap(self):
        """Finds the location of gap in the grid

        Returns:
            _type_: _description_
        """
        columns_fill_index = self.find_columns_filled_index(self.grid)
        for col in range(8):
            temp_arr = np.flip(self.grid[8 - columns_fill_index[col] : 8, col], axis = 0)
            if len(temp_arr) > 0:
                # find the gap
                y_gap, x_gap = 7 - np.where(temp_arr == " ")[0], col
                if y_gap.any():
                    return True, x_gap + 1, int(y_gap[0]) + 1
        return False, -1, -1  
    
    def action_fill_gap(self):
        """This fills the gaps found by self.find_gap(). it basically:
        1. Drops the part of column above the gap
        2. reduce the self.columns_fill_index[col] by 1

        Returns:
            True and False
        """
        flag = True
        flag, x_gap, y_gap = self.find_gap()
        while flag:
            y_gap = y_gap - 1
            x_gap = x_gap - 1
            self.grid[1 : y_gap + 1 , x_gap] = self.grid[0 : y_gap, x_gap]
            self.grid[0, x_gap] = " "
            flag, x_gap, y_gap = self.find_gap()
        else:
            return False
        
        return True
    
    def check_player_score(self, player = None):
        """Checks if the state is terminal and the number of 4 connects for the player

        Args:
            player (int, optional): checks the 4-connect for player. Defaults to 1.

        Returns:
            _type_: _description_
        """
        temp_player = deepcopy(self.player_to_play)
        if player is not None:
            self.player_to_play = player
        # directions to search starting each node
        directions = [(0, 1), (1, 1), (1, 0), (1, -1)]
        #directions = [(1, 0)]
        # find the nodes to search starting from top left
        list_nodes_to_check = []
        for i in range(8):
            for j in range(8):
                if self.grid[i, j] == str(self.player_to_play):
                    list_nodes_to_check.append((i, j))
        # now to each node check the combinations of 4 in directions
        count = 0
        for i, j in list_nodes_to_check:
            for k, l  in directions:
                if (0 <= (i + 3 * k) < 8) and (0 <= (j + 3 * l) < 8): # grid boarder condition
                    if self.grid[i + k, j + l] == self.grid[i + 2 * k, j + 2 * l] == self.grid[i + 3 * k, j + 3 * l] == str(self.player_to_play):
                        count += 1
        self.player_to_play = temp_player
        if count == 0:
            return False, 0
        return True, count
    
    def if_terminal(self):
        """checks if the player white won or not.
            Flag will be negative if it's not terminal
        """
        terminal_flag = False
        white_won_flag = False
        white_flag, white_count = self.check_player_score(player = 0)
        black_flag, black_count = self.check_player_score(player = 1)
        if white_flag or black_flag:
            terminal_flag = True
        else:
            terminal_flag = False
        if white_count > black_count:
            white_won_flag = True

        return terminal_flag, white_won_flag, (white_count - black_count) * 100000
        
    def possible_actions(self, grid = None, player = None):
        """Generate Possible actions
        1. drop actions
        2. slide actions
        """
        temp_grid = self.grid.copy()
        temp_player = deepcopy(self.player_to_play)
        if grid is not None:
            self.grid = grid
        if player is not None:
            self.player_to_play = player
        list_actions = []
        # for drop actions
        for i in range(1, 9):
            if self.can_drop(col=i):
                action = "D " + str(i)
                list_actions.append(action)
        # for slide actions
        for x in range(1, 9):
            for y in range(1, 9):
                for d in ['r', 'l']:
                    slide_flag, max_runs = self.can_slide(x = x, y = y, direction = d)
                    if slide_flag:
                        action = d.upper()+ " " + str(x) + " " + str(y)
                        list_actions.append(action)

        # return self.grid to its original value
        self.grid = temp_grid.copy()   
        self.player_to_play = temp_player
        return list_actions

    def can_action(self, action = None, grid = None, player = None):
        """tells if the an action by a player is on grid possible or not

        Args:
            action (_type_, optional): _description_. Defaults to None.
            grid (_type_, optional): _description_. Defaults to None.
            player (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        if action is None:
            return False
        temp_grid = self.grid.copy()
        temp_player = deepcopy(self.player_to_play)
        if grid is not None:
            self.grid = grid
        if player is not None:
            self.player_to_play = player

        list_actions = self.possible_actions()
        is_action_possible = False
        if action.upper() in list_actions:
            is_action_possible = True
        else:
            is_action_possible = False
        

        self.grid = temp_grid.copy()
        self.player_to_play = temp_player
        
        return is_action_possible

    def action_to_state(self, action = None, grid = None, player = None):
        """Outputs a state based on the action provided

        Args:
            action (string, e.g "D 3")
            grid (_type_, optional): _description_. Defaults to None.
            player (int, optional): _description_. Defaults to 0.
        """
        if action is None:
            return False, -1
        # store a local copy of the grid  and important data
        temp_grid = self.grid.copy()
        temp_player = deepcopy(self.player_to_play)
        if grid is not None:
            self.grid = grid
        if player is not None:
            self.player_to_play = player

        invalid_action_flag = False
        result = -1
        # if action is not provided
        if self.can_action(action=action, grid= grid, player=player):
            # if action is possible than we have to decode the action first
            if len(action) == 3 and action[0].lower() == 'd': # drop action
                self.action_drop(int(action[-1]))
                result = self.grid.copy()
            elif len(action) == 5: # slide action
                self.action_slide(x = int(action[2]), y = int(action[-1]), direction= action[0].lower())
                result = self.grid.copy()
            else: # invalid action
                invalid_action_flag = True
            
        self.grid = temp_grid.copy()
        self.player_to_play = temp_player
        if invalid_action_flag:
            return False, 0
        return True, result

    def move(self, action):
        """this function takes a move and outputs the grid
        """
        if self.can_action(action= action):
            # decoding the action
            flag, state = self.action_to_state(action= action)
            self.grid = state
            self.player_to_play = (self.player_to_play + 1) % 2
            return True
        else:
            print("Sorry, this action is not possible!")
            return False

    def test_logic(self):
        list_actions  = self.possible_actions()
        self.player_to_play = 0
        list_actions = self.possible_actions()
        for action in list_actions:
            print(action)
        print(self.check_player_score(player=0))
        print(self.check_player_score(player=1))




if __name__ == "__main__":
    test_grid = np.array([
        [" ", " ", " ", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", " ", " ", " "],
        [" ", "0", " ", " ", " ", " ", " ", " "],
        ["1", " ", " ", " ", " ", " ", " ", " "],
        ["1", "0", " ", " ", "0", "0", " ", " "],
        ["1", "0", " ", "0", " ", " ", "0", "1"],        
    ])
    t = GameBoard(grid = test_grid)
    print(t.action_fill_gap())
    t.print_grid()
    print(t.check_player_score(player = 0))
    print(t.if_terminal())
