
import numpy as np
from GameBoard import GameBoard
import pickle
import os
import random
import time

def initial_moveordered_alpha_move_beta_action(node, depth, agent_color):
    game = GameBoard(grid = node.copy())
    game.player_to_play = agent_color
    list_actions = move_ordering(node = game.grid, player = agent_color, is_reverse=True)
    utility_each_action = []
    alpha = float('-inf')
    beta = float('inf')
    state_count = [0]

    for action in list_actions:
        flag, child_node = game.action_to_state(action)
        utility_each_action.append(alpha_beta_minimax(node = child_node, depth = depth - 1, is_maximizing_player = False, agent_color = agent_color, alpha = alpha, beta = beta, state_count=state_count))
        alpha = max(alpha, max(utility_each_action))
    
    action_index = utility_each_action.index(max(utility_each_action))
    if len(set(utility_each_action)) == 1:
        actions = move_ordering(node = node, player=agent_color, is_reverse=True)
        return actions[0], utility_each_action, state_count[0]

    return list_actions[action_index], utility_each_action, state_count[0]

def alpha_beta_minimax(node, depth, is_maximizing_player, agent_color, alpha, beta, state_count):
    state_count[0] += 1
    # develop a local game object
    game = GameBoard(grid = node.copy())
    flag_terminal, _ , _ = game.if_terminal() # if terminal
    if depth == 0 or flag_terminal:
        return evaluate(game.grid, agent_color)

    if is_maximizing_player:
        game.player_to_play = agent_color
        max_eval = float('-inf')
        list_actions = move_ordering(node = node, player=agent_color, is_reverse=True)
        for action in list_actions:
            flag, child_node = game.action_to_state(action= action)
            eval = alpha_beta_minimax(child_node, depth - 1, False, agent_color= agent_color, alpha = alpha, beta = beta, state_count= state_count)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if alpha >= beta:
                break
        return max_eval
    
    else:
        game.player_to_play = int((agent_color + 1) % 2)
        min_eval = float('inf')
        list_actions = move_ordering(node = node, player=int((agent_color + 1) % 2), is_reverse=False)
        for action in list_actions:    
            flag, child_node = game.action_to_state(action= action)
            eval = alpha_beta_minimax(child_node, depth -1, True, agent_color= agent_color, alpha = alpha, beta = beta, state_count=state_count)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if alpha >= beta:
                break
        return min_eval    

# heuristic function
def evaluate(node, agent_color):
    # local copy
    game = GameBoard(grid=node.copy())
    game.player_to_play = agent_color
    player_converter = (-1) ** agent_color
    terminal_flag, flag_white, score_white = game.if_terminal()
    if terminal_flag:
        return player_converter * score_white
    else:
        return heuristic(game.grid, agent_color)

def heuristic(node, agent_color):
    """this function will calculate the number of runs of 2 and more in the grid

    Args:
        node (_type_): _description_
    """
    player_converter = (-1) ** agent_color
    list_white_positions = []
    list_black_positions = []
    runs_count_white = 0
    runs_count_black = 0
    for i in range(0, 8):
        for j in range(0, 8):
            if node[i, j] == "0":
                list_white_positions.append([i, j])
            elif node[i, j] == "1":
                list_black_positions.append([i, j])
            else:
                pass
    directions = [(0, 1), (1, 1), (1, 0), (1, -1)]
    # check the runs for white
    for i, j in list_white_positions:
        for k, l in directions:
            if (0<=(i + k) < 8) and (0<=(j + l) < 8): # grid boarder condition
                if node[i + k, j + l] == "0":
                    runs_count_white += 1

    # check the runs for black
    for i, j in list_black_positions:
        for k, l in directions:
            if (0<=(i + k) < 8) and (0<=(j + l) < 8): # grid boarder condition
                if node[i + k, j + l] == "1":
                    runs_count_black += 1

    return player_converter * (runs_count_white - runs_count_black)

def move_ordering(node, player, is_reverse):
    # create a local copy
    game = GameBoard(grid=node)
    game.player_to_play = player
    list_actions = game.possible_actions()
    generate_child = []
    for action in list_actions:
        flag, child = game.action_to_state(action)
        generate_child.append(child)
    # for each child find the corresponding heuristic function
    utility_childs = []
    for child in generate_child:
        utility_childs.append(heuristic(child, agent_color= player))
    
    pair_action_utility = zip(utility_childs, list_actions)
    pair_action_utility_sorted = sorted(pair_action_utility, reverse=is_reverse)
    list_utility, list_actions = zip(*pair_action_utility_sorted)
    list_actions = list(list_actions)
    return list_actions 

if __name__ == "__main__":


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
        agent_color = 0
        # consider 
        if agent_color == 0:
            print("agent to play first")
        else:
            print('you to play first')

        for i in range(40):
            if game.player_to_play == agent_color:
                state_count = 0
                start = time.time()
                agent_action, list_utility, state_count = initial_moveordered_alpha_move_beta_action(game.grid, depth = depth, agent_color=agent_color)
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
                    my_action = input("input your move : ")
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

    print("Agent wins : ", agent_win_count)
    print("states visited : ", states_visited_each_depth)

    # sub_folder = "Result_variables_initial"
    # path1 = os.path.join(sub_folder, 'initial_alpha_beta_moveordering_timedata_3moves.pkl')
    # path2 = os.path.join(sub_folder, 'initial_alpha_beta_moveordering_depths_3moves.pkl')
    # path3 = os.path.join(sub_folder, "initial_alpha_beta_moveordering_states_3moves.pkl")

    # with open(path1, 'wb') as file1:
    #     pickle.dump(time_taken_by_each_depths, file1)
    
    # with open(path2, 'wb') as file2:
    #     pickle.dump(considered_depths, file2)
    
    # with open(path3, 'wb') as file3:
    #     pickle.dump(states_visited_each_depth, file3)