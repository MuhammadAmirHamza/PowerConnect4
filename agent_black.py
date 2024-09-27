from GameBoard import GameBoard
from ConnectServer import ConnectServer
from agent_initial_moveordered import initial_moveordered_alpha_move_beta_action
import numpy as np


client_black = ConnectServer(server_hostname= "156trlinux-1.ece.mcgill.ca", game_id= "game43", color="black", server_port = 12345)
game = GameBoard()

if client_black.connect():
    # start game
    client_black.start_game()
    # receive message 
    reflected_back_message = client_black.receive_message()

    for i in range(10):

        flag, white_move = client_black.receive_message()
        if flag:
            print('black received move from white : ', white_move)
        else:
            break

        # play move
        game.move(white_move)
        game.print_grid()

        flag_terminal, white_flag, white_score = game.if_terminal()
        if flag_terminal:
            if white_score > 0:
                print("white won")
            elif white_score == 0:
                print("Draw")
            else:
                print("black won")
            break

        # now action to be taken by black
        black_move, _, _ = initial_moveordered_alpha_move_beta_action(game.grid, depth = 3, agent_color=1)
        
        # perfom move 
        print('black perfoms move : ', black_move)
        game.move(black_move)
        game.print_grid()

        # send move
        flag = client_black.send_message(black_move)
        if flag:
            print("black sent move : ", black_move)
        client_black.receive_message()

        flag_terminal, white_flag, white_score = game.if_terminal()
        if flag_terminal:
            if white_score > 0:
                print("white won")
            elif white_score == 0:
                print("Draw")
            else:
                print("black won")
            break

    client_black.close_connection()


