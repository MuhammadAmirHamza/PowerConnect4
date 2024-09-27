from GameBoard import GameBoard
from ConnectServer import ConnectServer
from agent_advance_moveordering import advance_moveordered_alpha_beta_action
import numpy as np
import random

client_white = ConnectServer(server_hostname= "156trlinux-1.ece.mcgill.ca", game_id= "game43", color="white", server_port = 12345)

agent_color = 0
# initialize the game object
game = GameBoard()

if client_white.connect():
    client_white.start_game()
    reflected_back_message = client_white.receive_message()

    for i in range(10):

        if i == 0:
            list_actions = game.possible_actions()
            white_move = random.choice(list_actions)
            white_move = "D 1"
        else:
            white_move , _, _ = advance_moveordered_alpha_beta_action(game.grid, depth = 3, agent_color= agent_color)

        # make move
        print('white performs move : ', white_move)
        game.move(white_move)
        game.print_grid()

        # send initial move
        sent_flag = client_white.send_message(white_move)
        client_white.receive_message() # reflected back message
        if sent_flag:
            print("white sent move : ", white_move)
        
        # checking if terminal
        terminal_flag, white_flag, white_score = game.if_terminal()
        if terminal_flag:
            if white_score > 0:
                print("white won")
            elif white_score == 0:
                print("draw")
            else:
                print('black won')
            break
        
        # now receive messge from the opponent player
        flag, black_move = client_white.receive_message()
        if flag:
            print("white received move from black : ", black_move)
        else:
            break

        game.move(black_move)
        game.print_grid()

        # checking if terminal
        terminal_flag, white_flag, white_score = game.if_terminal()
        if terminal_flag:
            if white_score > 0:
                print("white won")
            elif white_score == 0:
                print("draw")
            else:
                print('black won')
            break

    client_white.close_connection()