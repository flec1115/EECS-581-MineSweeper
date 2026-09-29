#AI_mode
#Abdulaziz Arab, 10:30 pm, 23september
#ended 1:58 AM 

#4:57 pm 26 sep, ended 12:28 sep 27th



import arcade
import random
from game_logic import GameManager
from board_manager import BoardManager
from input_handler import InputHandler
from board_manager import Cell
from user_interface import MinesweeperWindow

import user_interface 
import game_logic
import board_manager
import input_handler
import board_manager

'''
#board size set to default 10

BOARD_SIZE = 10 # Default board size initialization

x = random.randint(0,10) # define board coordinates as random numbers with respect to board size
y = x = random.randint(0,10)



#board = [[Cell() for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)] #initializes board, but this initialization is disconnected from the one from other codes

#board = board_manager.BoardManager.__init__(board) #refrences 

for row in range(BOARD_SIZE):
    for col in range(BOARD_SIZE):
        #given the board as an iteration/loop
        
        
        pass
        
    
locations = [(row, col) for row in range(board_manager.BOARD_SIZE) for col in range(board_manager.BOARD_SIZE)]    

#Code written by a random and discord and modified by me
def pick(board, Cell):
  pick_x = random(0, BOARD_SIZE)
  pick_y = random(0, BOARD_SIZE)
  
  if not Cell(pick_x, pick_y).is_opened() or not Cell(pick_x, pick_y).is_flagged():
    pick()
  else:
    Cell(pick_x, pick_y).open()


BoardManager.board[row][col]

for y in range(board):
    for x in range(board):
        print(board[y][x], " ", end="")
    print()
'''


##################################################################################################




#work from first draft modified today

import arcade
import random
from game_logic import GameManager
from board_manager import BoardManager
from input_handler import InputHandler
from board_manager import Cell
from user_interface import MinesweeperWindow as mw

import user_interface 
import game_logic
import board_manager
import input_handler
import board_manager


neighbor = BoardManager.neighbors  
board = BoardManager
is_flagged = BoardManager.is_flagged
uncover_cell = BoardManager.uncover_cell
mine = BoardManager.is_mine

mode = tuple(input("solo or ai? ")) # UI teammates change this
mode = list(mode)



board = BoardManager()

#mode = input("solo or ai? ") # UI teammates change this

click = MinesweeperWindow.on_mouse_press




row = random.randint(0,10)
col = random.randint(0,10)

x = random.randint(0,10)
y = random.randint(0,10)

#REVISE

class AI_Multiplayer:
    def __init__(self):
        self.ai_waiting = True
        self.ai_playing = False
        
        self.player_waiting = False 
        self.player_playing = input_handler.InputHandler.handle_click = True
        
    
    def choose_mode(mode):
        if mode == "solo":
            print("solo mode")
            return user_interface.MinesweeperWindow.start_game()
        elif mode == "ai":
            print("ai mode")
            return AI_Multiplayer.AI_start()
        
    def AI_Methods(row, col):
        reveal_cell = game_logic.GameManager.reveal_cell(row, col)
        flag_cell = game_logic.GameManager.flag_cell(row, col)
        unflag_cell = game_logic.GameManager.unflag_cell(row, col)
        
        uncover_cell = board_manager.BoardManager.uncover_cell(row, col)
        #set_flagged = board_manager.BoardManager.set_flagged(row, col) # AI GENERATED, REVISE
        
        return reveal_cell, flag_cell, unflag_cell, uncover_cell
        
        
    
    def AI_MOVE_LOGIC(row, col):
        #Assuming player plays first
        included_cell = [(row, col)]
        # GPT-4 recommended that the list of included cells has a tuple inside of it since every position consists of two elements, row and col, GPT-4 logic implemented by Abdulaziz
        
        while AI_Multiplayer.ai_playing == True:
            for row in range(board_manager.BOARD_SIZE):
                for col in range(board_manager.BOARD_SIZE):
                    if board.is_covered(row, col) and not board.is_flagged(row, col):
                        included_cell.append((row, col)) #list of cells ai can choose from, needs to work with random
                        
                        random_cell = random.choice(included_cell)
                        revealed_cell = game_logic.GameManager.reveal_cell(random_cell[0], random_cell[1])
                        # Reveal a cell with respected coordinates
                        
            return revealed_cell
                        

    
    
    
    def AI_start():
        print("AI mode started")
        return AI_Multiplayer.AI_MOVE_LOGIC(row, col) #ai generated
    
    
    
    
    
    
    
    
    
    
    

'''for row in range(board_manager.BOARD_SIZE):
            for col in range(board_manager.BOARD_SIZE):
                print(board[y][x], " ", end="")
                confirmed today it doesnt work since y and x are pixels for the board
                print()'''
                
'''
#mini testing enviornment code
BOARD_SIZE = 10
x = random.randint(0,10)
y = x = random.randint(0,10)
#mini testing enviornment 

col = int((x - self.board_left) // self.cell_size)
row = int((y - self.board_bottom) // self.cell_size)

board = [[Cell() for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

#board = board_manager.BoardManager()


    
locations = [(row, col) for row in range(board_manager.BOARD_SIZE) for col in range(board_manager.BOARD_SIZE)]    

#drafted picking logic 
def pick():
  pick_x = random(0, BOARD_SIZE)
  pick_y = random(0, BOARD_SIZE)
  
  if not Cell(pick_x, pick_y).is_opened() or not Cell(pick_x, pick_y).is_flagged():
    pick()
  else:
    Cell(pick_x, pick_y).open()'''
    
'''                            print("AI is playing")
                        return AI_Multiplayer.AI_Methods(row, col)
                    else:
                        print("AI is waiting")
                        return None'''