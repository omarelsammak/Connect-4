import random
import string
import math
import pygame
import sys
import numpy as np
from treelib import Node, Tree
import copy
from random import randint
from ctypes import sizeof
import time

BLUE = (0, 0, 205)
GREY = (128, 128, 128)
RED = (255, 0, 0)
YELLOW = (238, 238, 0)

pygame.init()
myfont = pygame.font.SysFont("Times", 40)

ROW_COUNT = 6
COLUMN_COUNT = 7

COMPUTER = 1
PLAYER = 2

def draw_GUI(screen, board):
    board = int_2_array(board)
    np.flip(board, 0)
    color = GREY
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, (r+1)
                                            * SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, color, ((
                c*SQUARESIZE + SQUARESIZE//2), (r*SQUARESIZE + SQUARESIZE + SQUARESIZE//2)), RADIUS)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == 2:
                pygame.draw.circle(screen, RED, ((
                    c*SQUARESIZE + SQUARESIZE//2), (r*SQUARESIZE + SQUARESIZE//2 + SQUARESIZE)), RADIUS)
            elif board[r][c] == 1:
                pygame.draw.circle(screen, YELLOW, ((
                    c*SQUARESIZE + SQUARESIZE//2), (r*SQUARESIZE + SQUARESIZE//2 + SQUARESIZE)), RADIUS)
    pygame.display.update()
    board = array_2_int(board)

def array_2_int(array):
    state_int = 0b1
    top = 0
    for j in range(7):
        top = 0
        for i in range(6):
            piece = array[i][j]
            if (piece == 0):
                top = i + 1
            if piece == 1:
                piece = 0
            if piece == 2:
                piece = 1
            state_int = state_int << 1
            state_int = state_int | piece
            # print(piece)
        state_int = state_int << 3
        state_int = state_int | top
        # print(bin(state_int))
        # print(f'top of {j} column is {top}')
    return state_int

def int_2_array(state_int):
    # print("int_2_array")
    state_array = [[0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0]]

    copy_state_int = state_int

    for j in range(6, -1, -1):
        top = copy_state_int & 0b111
        # print(top)

        copy_state_int = copy_state_int >> 3
        for i in range(5, -1, -1):
            if (i < top):
                state_array[i][j] = 0
            else:
                piece = copy_state_int & 0b1
                if piece == 0:
                    state_array[i][j] = 1
                else:
                    state_array[i][j] = 2
            copy_state_int = copy_state_int >> 1

    return state_array

def get_playable_row(state_int, col):
    copy_state_int = state_int
    copy_state_int = copy_state_int >> (6-col)*9
    top = copy_state_int & 0b111
    if top == 0:
        return None
    return top - 1

def get_playable_columns(state_int):
    available = []
    for i in range(7):
        if get_playable_row(state_int, i) != None:
            available.append(i)
    return available
    # print(available)

def get_checker(state_int, row, col):
    top = get_playable_row(state_int, col)
    if top != None:
        if row < top+1:
            return 0
    copy_state_int = state_int
    copy_state_int = copy_state_int >> ((6-col)*9 + 3 + 5 - row)
    piece = copy_state_int & 0b1
    return piece+1

def drop_checker(state_int, col, piece):
    copy_state_int = state_int
    masking = 0b111111111
    reseting = 0b000000000
    masking = masking << (6 - col)*9
    # print(f'masking = {bin(masking)}')
    column = copy_state_int & masking
    copy_state_int = copy_state_int ^ column
    column = column >> (6 - col)*9
    # print(f'column = {bin(column)}')
    # print(f'state after reseting = {bin(copy_state_int)}')

    top = column & 0b111
    if piece == 2:
        setting = 0b1
        setting = setting << 3 + (6-top)
        column = column | setting
        # print(f'column after setting {bin(column)}')
    column = column ^ top
    top = top - 1
    column = column | top
    column = column << (6 - col)*9
    copy_state_int = copy_state_int | column
    # print("A7a")
    # print(bin(copy_state_int))
    return copy_state_int

def print_arr(arr):
    print("\n\n\n\n\n\n\n\n\n\n\n")
    for row in range(6):
        print("-"*35)
        for col in range(7):
            if arr[row][col] == 0:
                print("|   |", end="")
            else:
                print("| " + str(arr[row][col]) + " |", end="")
        print()
    print("-"*35)

def calculate_score(board):
    player_fours = get_fours(board, PLAYER)
    player_three = get_threes(board, PLAYER)
    player_two = get_twos(board, PLAYER)
    AI_fours = get_fours(board, COMPUTER)
    AI_three = get_threes(board, COMPUTER)
    AI_two = get_twos(board, COMPUTER)
    return 11*(AI_fours-player_fours)+(AI_three-player_three)*7+(AI_two-player_two)*3

def get_threes(board, turn):
    threes = 0
    board = int_2_array(board)
    for i in range(len(board)):
        for j in range(len(board[0])):
            if j < len(board[0])-3:
                # horizontal right
                if board[i][j] == board[i][j+1] == board[i][j+2] == turn and board[i][j+3] == 0:
                    threes += 1
                if i < len(board)-3:
                    # diagonal right down
                    if board[i][j] == board[i+1][j+1] == board[i+2][j+2] == turn and board[i+3][j+3] == 0:
                        threes += 1
            if j >= 3:
                # horizontal left
                if board[i][j] == board[i][j-1] == board[i][j-2] == turn and board[i][j-3] == 0:
                    threes += 1
                if i < len(board)-3:
                    # diagonal left down
                    if board[i][j] == board[i+1][j-1] == board[i+2][j-2] == turn and board[i+3][j-3] == 0:
                        threes += 1
            if i >= 3:
                # vertical
                if board[i][j] == board[i-1][j] == board[i-2][j] == turn and board[i-3][j] == 0:
                    threes += 1
    return threes

def get_fours(board, turn):
    fours = 0
    board = int_2_array(board)
    for i in range(len(board)):
        for j in range(len(board[0])):
            if j < len(board[0])-3:
                # horizontal right
                if board[i][j] == board[i][j+1] == board[i][j+2] == turn == board[i][j+3]:
                    fours += 1
                if i < len(board)-3:
                    # diagonal right down
                    if board[i][j] == board[i+1][j+1] == board[i+2][j+2] == board[i+3][j+3] == turn:
                        fours += 1
            if j >= 3:
                if i < len(board)-3:
                    # diagonal left down
                    if board[i][j] == board[i+1][j-1] == board[i+2][j-2] == turn == board[i+3][j-3]:
                        fours += 1
            if i >= 3:
                # vertical
                if board[i][j] == board[i-1][j] == board[i-2][j] == turn == board[i-3][j]:
                    fours += 1
    return fours

def get_twos(board, turn):
    twos = 0
    board = int_2_array(board)
    for i in range(len(board)):
        for j in range(len(board[0])):
            if j < len(board[0])-3:
                # horizontal right
                if board[i][j] == board[i][j+1] == turn and board[i][j+2] == board[i][j+3] == 0:
                    twos += 1
                if i < len(board)-3:
                    # diagonal right down
                    if board[i][j] == board[i+1][j+1] == turn and board[i+3][j+3] == board[i+2][j+2] == 0:
                        twos += 1
            if j >= 3:
                # horizontal left
                if board[i][j] == board[i][j-1] == turn and board[i][j-3] == board[i][j-2] == 0:
                    twos += 1
                if i < len(board)-3:
                    # diagonal left down
                    if board[i][j] == board[i+1][j-1] == turn and board[i+3][j-3] == board[i+2][j-2] == 0:
                        twos += 1
            if i >= 3:
                # vertical
                if board[i][j] == board[i-1][j] == turn and board[i-3][j] == board[i-2][j] == 0:
                    twos += 1
    return twos

def minimax(board, depth, alpha, beta, Maximizing, p, search_tree, pr):
    pruning = 0
    availabe_colomns = get_playable_columns(board)
    terminal, winner = if_game_ended(board)
    if depth == 0 or terminal:
        if terminal:
            if winner == COMPUTER:
                if pr == 1:
                    stringg = f"terminal, alpha: {alpha} beta: {beta} score: 1000000"
                else:
                    stringg = f"terminal, score: 1000000"
                return(None, 1000000)
            if winner == PLAYER:
                if pr == 1:
                    stringg = f"terminal, alpha: {alpha} beta: {beta} score: -1000000"
                else:
                    stringg = f"terminal, score: -1000000"

                return(None, -1000000)
            else:
                if pr == 1:
                    stringg = f"terminal, alpha: {alpha} beta: {beta} score: 0"
                else:
                    stringg = f"terminal, score: 0"
                return(None, 0)

        else:
            if pr == 1:
                stringg = f"maximum depth,alpha: {alpha} beta: {beta} score: {calculate_score(board)}"
            else:
                stringg = f"maximum depth, score: {calculate_score(board)}"
            return(None, calculate_score(board))
    if Maximizing:
        pruning = 0
        maxscore = -math.inf
        colomn = 0
        for j in availabe_colomns:
            # row = get_available_row(board, j)
            temp_board = board
            # play_move(temp_board, row, j, COMPUTER)
            temp_board = drop_checker(temp_board, j, COMPUTER)
            if pr == 1:
                stringg = f"Maximizing node, alpha: {alpha} beta: {beta} score: {maxscore}"
            else:
                stringg = f"Maximizing node,score: {maxscore}"
            S = 10
            ran = ''.join(random.choices(
                string.ascii_uppercase + string.digits, k=S))
            search_tree.create_node(stringg, ran, parent=p)
            new_score = minimax(temp_board, depth-1, alpha,
                                beta, False, ran, search_tree, pr)[1]
            if new_score > maxscore:
                maxscore = new_score
                colomn = j
            alpha = max(alpha, maxscore)
            if alpha >= beta and pr == 1:
                pruning = 1
                break
        if pr == 1:
            if pruning == 1:
                stringg = f"Maximizing node (pruning occured), alpha: {alpha} beta: {beta} score: {maxscore}"
                search_tree.update_node(ran, tag=stringg)
            else:
                stringg = f"Maximizing node (no pruning occured), alpha: {alpha} beta: {beta} score: {maxscore}"
                search_tree.update_node(ran, tag=stringg)
        else:
            stringg = f"Maximizing node, score: {maxscore}"
            search_tree.update_node(ran, tag=stringg)
        return colomn, maxscore
    else:
        pruning = 0
        minscore = math.inf
        colomn = 0
        for j in availabe_colomns:
            # row = get_available_row(board, j)
            temp_board = board
            # play_move(temp_board, row, j, PLAYER)
            temp_board = drop_checker(temp_board, j, PLAYER)
            if pr == 1:
                stringg = f"Minimizing node, alpha: {alpha} beta: {beta} score: {minscore}"
            else:
                stringg = f"Minimizing node, score: {minscore}"
            S = 10  # number of characters in the string.
            ran = ''.join(random.choices(
                string.ascii_uppercase + string.digits, k=S))
            search_tree.create_node(stringg, ran, parent=p)
            new_score = minimax(temp_board, depth-1, alpha,
                                beta, True, ran, search_tree, pr)[1]
            if new_score < minscore:
                minscore = new_score
                colomn = j
            beta = min(beta, minscore)
            if alpha >= beta and pr == 1:
                pruning = 1
                break
        if pr == 1:
            if pruning == 1:
                stringg = f"Minimzing node (pruning occured), alpha: {alpha} beta: {beta} score: {minscore}"
                search_tree.update_node(ran, tag=stringg)
            else:
                stringg = f"Minimizing node (no pruning occured), alpha: {alpha} beta: {beta} score: {minscore}"
                search_tree.update_node(ran, tag=stringg)
        else:
            stringg = f"Minimizing node, score: {minscore}"
            search_tree.update_node(ran, tag=stringg)
        return colomn, minscore

def if_game_ended(board):
    if len(get_playable_columns(board)) != 0:
        return False, 0
    playerfours = get_fours(board, PLAYER)
    print(f"PLayer fours: {playerfours}")
    AIfours = get_fours(board, COMPUTER)
    print(f"COMPUTER fours: {AIfours}")
    if playerfours == AIfours:
        return True, 0
    elif playerfours > AIfours:
        return True, PLAYER
    else:
        return True, COMPUTER


board = 0b1000000110000000110000000110000000110000000110000000110000000110

SQUARESIZE = 90
width = COLUMN_COUNT*SQUARESIZE
height = (ROW_COUNT+1)*SQUARESIZE
RADIUS = SQUARESIZE//2 - 5

size = (width, height)

screen = pygame.display.set_mode(size)
draw_GUI(screen, board)
pygame.display.update()
col = 0
game_over = False
K = int(input('Enter number of levels: '))
prune = int(input('for minimax without pruning press zero for with pruning press one: '))
if (K>0and (prune==1) or (prune==0)) :
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, GREY, (0, 0, width, SQUARESIZE))
                posx = event.pos[0]
                pygame.draw.circle(screen, RED, (posx, SQUARESIZE//2), RADIUS)
                pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(screen, GREY, (0, 0, width, SQUARESIZE))
                posx = event.pos[0]
                col = posx//SQUARESIZE
                status = if_game_ended(board)
                if get_playable_row(board, col) != None:
                    board = drop_checker(board, col, 2)
                    print_arr(int_2_array(board))
                    draw_GUI(screen, board)
                    search_tree = Tree()
                    search_tree.create_node("Parent", 0)
                    start_time = time.time()
                    nextcol, score = minimax(
                        board,K, -math.inf, math.inf, True, 0, search_tree, prune)
                    end_time = time.time()
                    runtime = end_time - start_time
                    print(f'Runtime of minmax = {runtime} seconds')
                    number_of_nodes = search_tree.size()-1
                    print(f"number of nodes {number_of_nodes}")
                    stringg = f"Max score:{score}, Next colomn: {nextcol}"
                    search_tree.update_node(0, tag=stringg)
                    # search_tree.show()
                    if nextcol == None:
                        if score == 1000000:
                            print("COMPUTER WINS")
                            label = myfont.render("COMPUTER Wins !!!", 1, YELLOW)
                            screen.blit(label, (130, 100))
                            draw_GUI(screen, board)
                            pygame.time.wait(3000)
                            quit()
                        elif score == -1000000:
                            print("PLAYER WINS")
                            label = myfont.render("Player 2 Wins !!!", 1, RED)
                            screen.blit(label, (130, 10))
                            draw_GUI(screen, board)
                            pygame.time.wait(3000)
                            quit()
                        else:
                            print("TIE")
                            label = myfont.render("TIW !!!", 1, YELLOW)
                            screen.blit(label, (130, 10))
                            draw_GUI(screen, board)
                            pygame.time.wait(3000)
                            quit()
                        # print_arr(int_2_array(board))
                        # pygame.time.wait(3000)
                        # break
                    else:
                        board = drop_checker(board, nextcol, COMPUTER)
                        print_arr(int_2_array(board))
                        draw_GUI(screen, board)
                        status = if_game_ended(board)
                        if status[0] == True:
                            if status[1] == COMPUTER:
                                print("COMPUTER WINS ")
                                label = myfont.render("COMPUTER Wins !!!", 1, YELLOW)
                                screen.blit(label, (130, 10))
                                draw_GUI(screen, board)
                                pygame.time.wait(3000)
                                quit()
                            elif status[1] == PLAYER:
                                print("PLAYER WINS")
                                label = myfont.render("Player 2 Wins !!!", 1, RED)
                                screen.blit(label, (130, 10))
                                draw_GUI(screen, board)
                                pygame.time.wait(3000)
                                quit()
                            else:
                                print("TIE")
                                label = myfont.render("TIE !!!", 1, YELLOW)
                                screen.blit(label, (130, 10))
                                draw_GUI(screen, board)
                                pygame.time.wait(3000)
                                quit()
