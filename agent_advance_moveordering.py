import numpy as np
from GameBoard import GameBoard
import random
import time
import pickle
import os

central_control_kernel = np.array([
    [1, 2, 4, 5, 5, 4, 2 , 1],
    [1, 2, 4, 7, 7, 4, 2 , 1],
    [1, 2, 7, 9, 9, 7, 2 , 1],
    [1, 7, 9, 9, 9, 9, 7 , 1],
    [1, 7, 9, 9, 9, 9, 7 , 1],
    [1, 2, 7, 9, 9, 7, 2 , 1],
    [1, 2, 4, 7, 7, 4, 2 , 1],
    [1, 2, 4, 5, 5, 4, 2 , 1],

])
def advance_moveordered_alpha_beta_action(node, depth, agent_color):
    game = GameBoard(grid = node.copy())
    game.player_to_play = agent_color
    list_actions = moveordering(node = game.grid, player=agent_color, is_reverse=True)            
    utility_each_action = []
    state_count = [0]
    alpha = float('-inf')
    beta = float('inf')
    
    for action in list_actions:
        flag, child_node = game.action_to_state(action)
        utility_each_action.append(alpha_beta_minimax(node = child_node, depth = depth -1, is_maximizing_player=False, agent_color=agent_color, alpha = alpha, beta = beta, state_count = state_count))
        alpha = max(alpha, max(utility_each_action))

    action_index = utility_each_action.index(max(utility_each_action))
    if len(set(utility_each_action)) == 1:
        return random.choice(list_actions), utility_each_action, state_count[0]
    return list_actions[action_index], utility_each_action, state_count[0]

def alpha_beta_minimax(node, depth, is_maximizing_player, agent_color, alpha, beta, state_count):
    state_count[0] += 1
    # develop a local game object
    game = GameBoard(grid = node.copy())
    flag_terminal,_, score = game.if_terminal() # if terminal
    if depth == 0 or flag_terminal:
        return evaluate(node, agent_color, depth)

    if is_maximizing_player:
        game.player_to_play = agent_color
        max_eval = float('-inf')
        # list_actions = game.possible_actions()
        list_actions = moveordering(node=node, player=game.player_to_play, is_reverse=True )
        for action in list_actions:
            flag, child_node = game.action_to_state(action= action)
            eval = alpha_beta_minimax(node = child_node, depth = depth - 1, is_maximizing_player=False, agent_color= agent_color, alpha = alpha, beta = beta, state_count = state_count)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if alpha >= beta:
                break
        return max_eval
    
    else:
        min_eval = float('inf')
        game.player_to_play = int((agent_color + 1) % 2)
        # list_actions = game.possible_actions()
        list_actions = moveordering(node=node, player=game.player_to_play, is_reverse=True)
        for action in list_actions:    
            flag, child_node = game.action_to_state(action= action)
            eval = alpha_beta_minimax(node = child_node, depth = depth -1, is_maximizing_player= True, agent_color= agent_color, alpha = alpha, beta = beta, state_count= state_count)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if alpha >= beta:
                break
        return min_eval   
    
def evaluate(node, player, depth):
    # initialize local game
    game = GameBoard(grid=node)
    game.player_to_play = player
    player_converter = (-1) ** player
    flag, _ , score = game.if_terminal()
    if flag:
        if depth != 0:
            return player_converter * score * depth
        else:
            return player_converter * score
    else:
        utility = advance_heuristic(node, player)
        return utility

def advance_heuristic(node, player):
    utility = 0
    # check the number of 3 consecutive pieces with and without blanks 
    count_3_pieces_with_blanks, count_3_pieces_without_blanks = three_consecutive_sub_heuristic(node, player)
    utility += (count_3_pieces_with_blanks * 500 + count_3_pieces_without_blanks * 100)

    # penalize if opponent's three consecutive found with blank
    opponent = int((player + 1) % 2)
    count_3_pieces_with_blanks_op, count_3_pieces_without_blanks_op = three_consecutive_sub_heuristic(node, opponent)
    utility -=  (count_3_pieces_with_blanks_op * 450 + count_3_pieces_without_blanks_op * 80)

    # for two consecutive pieces
    count_2_pieces_with_blanks, count_2_pieces_without_blanks = two_consecutive_sub_heuristic(node, player)
    utility += (count_2_pieces_with_blanks * 20 + count_2_pieces_without_blanks * 10)
    
    count_2_pieces_with_blanks_op, count_2_pieces_without_blanks_op = two_consecutive_sub_heuristic(node, opponent)
    utility -= (count_2_pieces_with_blanks_op * 20 + count_2_pieces_without_blanks_op * 10)

    # central control
    utility += central_control_sub_heuristic(node = node, player = player)
    utility -= central_control_sub_heuristic(node = node, player = int((player + 1)%2) )

    # sliding action
    utility += slide_drop_heuristic(node= node, player= player) * 10
    
    return utility

def three_consecutive_sub_heuristic(node, player):
    count_three_consecutive_with_blank = 0
    count_three_consecutive_without_blank = 0
    directions = [(1, 0), (1, 1), (0, 1), (1, -1)]
    # find the positions to check
    list_position = np.where(node == str(player))
    coordinates = list(zip(list_position[0], list_position[1]))
    # check each coordinate
    for k, l in directions:
        for i, j in coordinates:
            # checking if direction possible
            if node[i, j] == " " or node[i,j] == str(int((player + 1) % 2)):
                break
            else:
                if 0 <= i + 2 * k < 8 and 0 <= j + 2 * l < 8:
                    flag = False
                    # for player
                    if node[i + k, j + l] == node[i + 2 * k, j + 2 * l] == str(player):
                        # three consecutive pieces found
                        if 0 <= i - k < 8 and 0 <= j - l < 8:
                            if node[i - k, j - l] == " ":
                                count_three_consecutive_with_blank += 1
                                flag = True
                        if 0 <= i + 3 * k < 8 and 0 <= j + 3 * l < 8:
                            if node[i + 3 * k, j + 3 * l] == " ":
                                count_three_consecutive_with_blank += 1
                                flag = True
                        if not flag:
                            count_three_consecutive_without_blank += 1
    return count_three_consecutive_with_blank, count_three_consecutive_without_blank

def two_consecutive_sub_heuristic(node, player):
    count_two_consecutive_with_blank = 0
    count_two_consecutive_without_blank = 0
    directions = [(1, 0), (1, 1), (0, 1), (1, -1)]
    # find the positions to check
    list_position = np.where(node == str(player))
    coordinates = list(zip(list_position[0], list_position[1]))
    # check each coordinate
    for k, l in directions:
        for i, j in coordinates:
            # checking if direction possible
            if node[i, j] == " " or node[i,j] == str(int((player + 1) % 2)):
                break
            else:
                if 0 <= i + 1 * k < 8 and 0 <= j + 1 * l < 8:
                    flag = False
                    # for player
                    if node[i + k, j + l] == str(player):
                        # three consecutive pieces found
                        if 0 <= i - k < 8 and 0 <= j - l < 8:
                            if node[i - k, j - l] == " ":
                                count_two_consecutive_with_blank += 1
                                flag = True
                        if 0 <= i + 3 * k < 8 and 0 <= j + 3 * l < 8:
                            if node[i + 3 * k, j + 3 * l] == " ":
                                count_two_consecutive_with_blank += 1
                                flag = True
                        if not flag:
                            count_two_consecutive_without_blank += 1
    return count_two_consecutive_with_blank, count_two_consecutive_without_blank

def central_control_sub_heuristic(node, player):
    grid = node.copy()
    grid[grid == " "] = "3"
    grid = grid.astype(int)
    grid[grid == int((player+1)%2)] = 3
    grid[grid == player] = 1
    grid[grid == 3] = 0
    result = grid * central_control_kernel
    score = np.sum(result)
    return score

def slide_drop_heuristic(node, player):
    game = GameBoard(grid = node)
    game.player_to_play = player
    count = 0
    list_actions = game.possible_actions()
    for action in list_actions:
        if action[0] == 'R':
            if int(action[2]) + 1 == 7 and game.grid[int(action[-1]) - 1, 7] == str(int((player + 1)%2)):
                count +=1
            elif int(action[2]) + 2 == 7 and game.grid[int(action[-1]) - 1, 7] == str(int((player + 1)%2)):
                count +=1
            else:
                pass
        if action[0] == 'L':
            if int(action[2]) - 3 == 0 and game.grid[int(action[-1]) - 1, 0] == str(int((player + 1)%2)):
                count +=1
            elif int(action[2]) - 4 == 0 and game.grid[int(action[-1]) - 1, 0] == str(int((player + 1)%2)):
                count +=1
            else:
                pass
    return count 

def moveordering(node, player, is_reverse):
    # create a local copy
    game = GameBoard(grid = node)
    game.player_to_play = player
    list_actions = game.possible_actions()
    generate_child = []
    for action in list_actions:
        flag, child = game.action_to_state(action)
        generate_child.append(child)
    # utility of each child
    utility_child = []
    for child in generate_child:
        utility_child.append(evaluate(child, player=player, depth = 1))
    
    pair_action_utility = zip(utility_child, list_actions)
    pair_action_utility_sorted = sorted(pair_action_utility, reverse=is_reverse)
    list_utility, list_actions = zip(*pair_action_utility_sorted)
    list_actions = list(list_actions)
    return list_actions


def test_play():    
    # considered_depths = [1, 2, 3, 4, 5, 6]
    considered_depths = [4]
    time_taken_by_each_depths = []
    states_visited_each_depth = []
    agent_win_count = 0
    
    for depth in considered_depths:
        total_time = 0
        total_states_visited = 0
        game = GameBoard()
        # adding the freedom to choose the color 
        # agent_color = random.choice([0, 1])
        agent_color = 1
        # consider 
        if agent_color == 0:
            print("agent to play first")
        else:
            print('you to play first')

        for i in range(40):
            if game.player_to_play == agent_color:
                state_count = 0
                start = time.time()
                # list_actions = game.possible_actions()
                agent_action, list_utility, state_count = advance_moveordered_alpha_beta_action(game.grid, depth = depth, agent_color=agent_color)
                total_states_visited += state_count
                game.move(agent_action)
                stop = time.time()
                total_time = total_time + (stop - start)
                game.print_grid()
                terminal_flag, _, _ = game.if_terminal()
                if terminal_flag:
                    print("agent won")
                    agent_win_count += 1
                    break

            else:
                # my turn
                list_actions = game.possible_actions()
                # my_action = random.choice(list_actions)
                while True:
                    my_action = input("Input Action : ")
                    if my_action in list_actions:
                        break
                game.move(my_action)
                game.print_grid()
                terminal_flag, _, _ = game.if_terminal()
                if terminal_flag:
                    print("you won")
                    break             
        time_taken_by_each_depths.append(total_time)
        states_visited_each_depth.append(total_states_visited)
    
    
    # sub_folder = "Result_variables_advance"
    # path1 = os.path.join(sub_folder, 'advance_alpha_beta_moveordering_timedata_3moves.pkl')
    # path2 = os.path.join(sub_folder, 'advance_alpha_beta_moveordering_depths_3moves.pkl')
    # path3 = os.path.join(sub_folder, "advance_alpha_beta_moveordering_3moves.pkl")

    # with open(path1, 'wb') as file1:
    #     pickle.dump(time_taken_by_each_depths, file1)
    
    # with open(path2, 'wb') as file2:
    #     pickle.dump(considered_depths, file2)
    
    # with open(path3, 'wb') as file3:
    #     pickle.dump(states_visited_each_depth, file3)


if __name__ == "__main__":
    test_grid = np.array([
        [" ", " ", " ", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", " ", " ", " "],        
    ])
    # game = GameBoard(grid = test_grid)
    # game.player_to_play = 0
    # list_actions = game.possible_actions()
    # advance_minimax_action(node=test_grid, list_actions = list_actions, depth=4, agent_color=0)
    # slide_drop_heuristic(test_grid, player=0)
    # print(central_control_sub_heuristic(test_grid, player=1))
    # print(moveordering(test_grid, player= 0, is_reverse= True))
    test_play()