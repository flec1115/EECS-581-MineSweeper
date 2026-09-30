#Infinity

'''

this file is for implementing an infinite minesweeper feature for the game.
If the user types inf instead of a number of mines, it will be an adjustable window where the player can zoom out and drag to see more of the board.
if the player zooms out too far, the game will simplify the look of the board, to show how the game looks with respect to how many cells have been uncovered

'''

import arcade
import user_interface
from game_logic import GameManager
from user_interface import MinesweeperWindow
from board_manager import BoardManager
from board_manager import Cell

'''methods={
    "on_key_press": user_interface.MinesweeperWindow.on_key_press,
    "on_draw": user_interface.MinesweeperWindow.on_draw,
    "draw_setup": user_interface.MinesweeperWindow.draw_setup,
    "confirm_mine_count": user_interface.MinesweeperWindow.confirm_mine_count,
    "start_game": user_interface.MinesweeperWindow.start_game,
    "window": user_interface.MinesweeperWindow.window,
}

variables={
    
    "won": user_interface.MinesweeperWindow.won,
    "lost": user_interface.MinesweeperWindow.lost,
    "camera": arcade.Camera2D(user_interface.MinesweeperWindow.width, user_interface.MinesweeperWindow.height),
    "window": user_interface.MinesweeperWindow.window,
    
    }'''



class Inf_mode:
    
    def __init__(self, window, game): 
        self.window = window
        self.game = game
        self.camera = arcade.Camera2D(window=window)
        self.expansion_pending = False
        
    def inf_mode(self):
        if (self.window.game.is_lost):
            return
                

        if self.window.game.cells_to_clear == 0 and not self.expansion_pending:
                self.camera.zoom/=2
                self.expansion_pending = True
                return self.camera.zoom

    def expand_board(self):
        # if the board is expanding (status true), 
        board = self.window.game.board.board
        old_board = len(board)
        new_board = old_board * 2
        
        for row in board:
            row.extend([Cell() for i in range(new_board - old_board)])
            
        for i in range(new_board - old_board):
            board.append([Cell() for i in range(new_board)])   
            
        
        print("Rows:", len(board))
        print("Row widths:", {len(row) for row in board})
        
        return new_board
    
    
    
    


import board_manager
print(board_manager.BOARD_SIZE)

