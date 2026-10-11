"""
Module Name: input_handler.py
Description: Handle mouse input and send actions to GameManager

Class Name: InputHandler
Description: Convert mouse clicks into board actions

Inputs: Mouse clicks
Outputs: Calls to GameManager
External Sources: ChatGPT
LLM AND GENERATIVE AI TOOLS:
A description of how and why AI was used: ChatGPT used for drafting and revising code with new, unfamiliar UI library
The specific prompts you entered: 
Vamos escribir el code en ingles para este proyecto sobre los minesweeper en una forma agile. Vamos seguir derechos de la proyecto y la forma de el code y nosotros implementacion solo necesita estar simlpe para este commit. Tambien nosotros usamos el bilbilitecha pyarcade por el UI y el input. Dame un Ui simple y un input handler simple para el proyecto pero, por favor, no implemente las caracteristicas por el juego todo, solo el UI y input handler por este generacion. Nosotros solomente neceistamos code corta y simple tabien. Por favor y gracias! Este es mi code y derechos por el proyecto: HINT: System Architecture 

Purpose: Describes the high-level structure to facilitate feature extensions by the Project 2 team

Components: 

Board Manager: Manages the 10x10 grid as a 2D array, tracking cell states (covered, flagged, uncovered, mine)

Game Logic: Handles gameplay rules, including mine placement, cell uncovering, recursive revealing, and win/loss detection

User Interface: Renders the grid, status indicators (e.g., mine count, game state), and user inputs (clicks for uncovering/flagging)

Input Handler: Processes user inputs (e.g., clicks, key presses) and communicates with Game Logic to update the Board

Data Flow: 

User input (click) → Input Handler validates and sends to Game Logic

Game Logic updates Board state (e.g., uncover cell, place flag)

Board state changes trigger UI updates (e.g., render number, flag, or mine)

Key Data Structures: 

2D array (10x10) for grid: stores cell states (0 = covered, 1 = flagged, 2 = uncovered number, 3 = mine)

Game state object: tracks mine count, flags remaining, and win/loss status


Assumptions: 

Fixed 10x10 grid size

Mine count user-specified (10–20) at game start

Update 9/26/2026 - Felix
Add sound effects capability to the game for win, loss, and flagging actions. This includes loading sound files and triggering them at appropriate game events.

  
How you validated and revised the AI output: Proofreading, testing, and validating accuracy with intentions
The challenges or limitations you faced while using AI: Validating logical execution of the input handler code and ensuring that the input handler functioned as intended took a significant amount of proofreading and testing.
Attributions: 
Authors: Blake Pennel, Felix
Creation Date: 9/15/2026
"""
import arcade


class InputHandler:
    """Handles simple mouse input for the Minesweeper board."""
        #inialization features for the input handler, including sound effects for flagging, losing, and winning
    def __init__(self, game, cell_size, board_left, board_bottom, sound_enabled=True):
        self.game = game
        self.cell_size = cell_size
        self.board_left = board_left
        self.board_bottom = board_bottom
        self.sound_enabled = sound_enabled
        #sound effect variables from the arcade library, loaded from the sfx folder
        self.flag_sound = arcade.load_sound("./sfx/flag.wav")
        self.bomb_sound = arcade.load_sound("./sfx/bomb.mp3")
        self.blip_sound = arcade.load_sound("./sfx/blip.wav")
        self.cheer_sound = arcade.load_sound("./sfx/cheer.wav")

    def handle_click(self, x, y, button):
        """Convert a mouse click into a board row and column."""

        col = int((x - self.board_left) // self.cell_size)
        row = int((y - self.board_bottom) // self.cell_size)

        # Ignore clicks outside the board
        if row < 0 or row >= 10 or col < 0 or col >= 10:
            return

        # Left click reveals a covered cell
        if button == arcade.MOUSE_BUTTON_LEFT:
            if not self.game.are_mines_populated:
                self.game.populate_mines(row, col)
            if self.game.board.is_covered(row, col):
                self.game.reveal_cell(row, col)

                # Only play sound effects if sound is enabled
                if self.sound_enabled:
                    if self.game.is_lost:
                        arcade.play_sound(self.bomb_sound)
                    elif self.game.is_won:
                        arcade.play_sound(self.cheer_sound)
                    else:
                        arcade.play_sound(self.blip_sound)

        # Right click toggles a flag
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            if self.game.board.is_covered(row, col):
                if self.game.board.is_flagged(row, col):
                    self.game.unflag_cell(row, col)
                else:
                    self.game.flag_cell(row, col)
                if self.sound_enabled:
                    arcade.play_sound(self.flag_sound)
