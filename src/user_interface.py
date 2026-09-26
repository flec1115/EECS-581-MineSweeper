"""
Module Name: user_interface.py
Description: Display the Minesweeper board using Python Arcade

Class Name: MinesweeperWindow
Description: Draw the board and pass user input to InputHandler

Update Description: Add mine count selection (10-20) with validation, A-J/1-10 board labels,
adjacent mine numbers (0-8), Playing/Victory/Game Over: Loss status, remaining flag counter,
reveal all mines on loss, and R to restart

Inputs: Board state
Outputs: Game window
External Sources: ChatGPT 5.6 Sol High Thinking, DeepSeek V4.1 Flash, ChatGPT 5.6 Luna
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

  
How you validated and revised the AI output: Proofreading, checking for sound logic, and testing, making sure it follows my original intentions and logic for a standard UI library
The challenges or limitations you faced while using AI: Validating logical execution of the UI code and ensuring that the UI functioned as intended took a significant amount of proofreading and testing.

Update 9/16/2026 - Carter Steenhard and DeepSeek V4.1 Flash:
A description of how and why AI was used: DeepSeek V4.1 Flash used to implement the mine count selection, labels, numbers, status, flag counter, reveal mines on loss, and restart update
                                            ChatGPT GPT - 5.6 Luna Used to inplement UI for mode selection and difficulty selection screens. It was used a reference for an easy way to set up buttons and their locations on the screen. Further code related was created manually
How you validated and revised the AI output: Proofreading, logic tests for the board and game logic, and a scripted window test covering setup, revealing, flagging, loss, restart, and win
    UI testing was done when implementing the mode selection and difficulty selection screens. The buttons were tested to ensure they were clickable and that the correct mode and difficulty were selected.
The challenges or limitations you faced while using AI: Keeping the diff minimal while matching the existing code style and validating the arcade API calls against the installed library version
Attributions: 
Authors: Kyler Russell, Blake Pennel, Carter Steenhard
Creation Date: 9/15/2026
"""
import arcade
from game_logic import GameManager
import board_manager
from input_handler import InputHandler


CELL_SIZE = 50

BOARD_LEFT = 50
BOARD_BOTTOM = 50

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 650

COLUMN_LABELS = "ABCDEFGHIJ"
#configs for setting buttons for the mode selection and difficulty selection screens
#formatting used chatGPT GPT-5.6 Luna for reference of an easy way to set up buttons and their locations on the screen
MODE_OPTIONS = (("Solo", 35, 350, 160, 60), ("Co-op", 220, 350, 160, 60),("Computer Solve", 405, 350, 160, 60))
DIFFICULTY_OPTIONS = (("Easy", 115, 205, 110, 55), ("Medium", 245, 205, 110, 55),("Hard", 375, 205, 110, 55))
CONTINUE_BUTTON = (220, 90, 160, 55)

# Standard Minesweeper colors for the adjacent mine counts
NUMBER_COLORS = {1: arcade.color.BLUE, 2: arcade.color.GREEN, 3: arcade.color.RED,
                 4: arcade.color.DARK_BLUE, 5: arcade.color.MAROON, 6: arcade.color.TEAL,
                 7: arcade.color.BLACK, 8: arcade.color.GRAY}


class MinesweeperWindow(arcade.Window):
    """Simple Arcade UI for Minesweeper."""

    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, "Minesweeper")

        # The game is created once the player confirms a mine count
        self.game = None
        self.input_handler = None
        #states for AI selection screen
        self.ui_state = "mode_select"
        self.mode = "Solo"
        self.ai_difficulty = "Easy"
        self.mine_count_input = ""
        self.setup_error = ""

    def start_game(self, num_mines):
        """Create a new game and rebuild the input handler for it."""
        self.game = GameManager(num_mines)
        self.input_handler = InputHandler(self.game, CELL_SIZE, BOARD_LEFT, BOARD_BOTTOM)

    def confirm_mine_count(self):
        """Start a game with the typed mine count, or report that it is invalid."""
        num_mines = int(self.mine_count_input or 10)
        if not (10 <= num_mines <= 20):
            self.setup_error = "Number of mines must be 10 to 20"
            return

        self.start_game(num_mines)

    def on_draw(self):
        """Draw the setup screen or the current board."""
        self.clear(arcade.color.WHITE)

        if self.game is None:
            #if no mode has been selected, draw the mode selection screen
            if self.ui_state == "mode_select":
                self.draw_mode_select()
                return
            #if no mine count has been selected, draw the mine count selection screen
            self.draw_setup()
            return

        board_top = BOARD_BOTTOM + board_manager.BOARD_SIZE * CELL_SIZE

        for row in range(board_manager.BOARD_SIZE):
            for col in range(board_manager.BOARD_SIZE):

                left = BOARD_LEFT + col * CELL_SIZE
                bottom = BOARD_BOTTOM + row * CELL_SIZE
                covered = self.game.board.is_covered(row, col)
                is_mine = self.game.board.is_mine(row, col)

                if self.game.board.is_flagged(row, col):
                    color = arcade.color.YELLOW

                # Uncovered mines are shown, and all mines are shown when the game is lost
                elif is_mine and (self.game.is_lost or not covered):
                    color = arcade.color.RED

                elif covered:
                    color = arcade.color.GRAY

                else:
                    color = arcade.color.LIGHT_GRAY

                arcade.draw_lbwh_rectangle_filled(
                    left + 1,
                    bottom + 1,
                    CELL_SIZE - 2,
                    CELL_SIZE - 2,
                    color
                )

                # Uncovered safe cells show how many mines are adjacent
                if not covered and not is_mine:
                    adjacent = self.game.board.adjacent_mines(row, col)
                    if adjacent > 0:
                        arcade.draw_text(str(adjacent), left + CELL_SIZE / 2, bottom + CELL_SIZE / 2,
                                         NUMBER_COLORS[adjacent], 20, anchor_x="center", anchor_y="center")

        # Column and row labels: columns A-J, rows 1-10
        for col, label in enumerate(COLUMN_LABELS):
            arcade.draw_text(label, BOARD_LEFT + col * CELL_SIZE + CELL_SIZE / 2, board_top + 6,
                             arcade.color.BLACK, 14, anchor_x="center")

        for row in range(board_manager.BOARD_SIZE):
            arcade.draw_text(str(row + 1), BOARD_LEFT - 10, BOARD_BOTTOM + row * CELL_SIZE + CELL_SIZE / 2,
                             arcade.color.BLACK, 14, anchor_x="right", anchor_y="center")

        arcade.draw_text(f"Flags: {self.game.mine_count}", BOARD_LEFT, board_top + 30, arcade.color.BLACK, 18)

        if self.game.is_lost:
            status, status_color = "Game Over: Loss", arcade.color.RED
        elif self.game.is_won:
            status, status_color = "Victory", arcade.color.GREEN
        else:
            status, status_color = "Playing", arcade.color.BLACK

        arcade.draw_text(status, BOARD_LEFT + board_manager.BOARD_SIZE * CELL_SIZE, board_top + 30,
                         status_color, 18, anchor_x="right")

    def draw_setup(self):
        """Draw the mine count selection screen."""
        arcade.draw_text("Minesweeper", WINDOW_WIDTH / 2, 420, arcade.color.BLACK, 32, anchor_x="center")
        arcade.draw_text("Type the number of mines (10-20) and press Enter", WINDOW_WIDTH / 2, 360,
                         arcade.color.BLACK, 16, anchor_x="center")
        arcade.draw_text(f"Mines: {self.mine_count_input or 10}", WINDOW_WIDTH / 2, 300,
                         arcade.color.BLUE, 28, anchor_x="center")

        if self.setup_error:
            arcade.draw_text(self.setup_error, WINDOW_WIDTH / 2, 260, arcade.color.RED, 16, anchor_x="center")


    def draw_mode_select(self):
        """Draw the game mode and computer difficulty selection screen."""
        #draw minesweeper title and mode selection text
        arcade.draw_text("Minesweeper", WINDOW_WIDTH / 2, 525, arcade.color.BLACK, 32, anchor_x="center")
        arcade.draw_text("Select Game Mode", WINDOW_WIDTH / 2, 430, arcade.color.BLACK, 20, anchor_x="center")

        for label, left, bottom, width, height in MODE_OPTIONS:
            selected = label == self.mode
            #highlight selected feature in dark blue, unselected features in light gray, with white text for selected and black text for unselected
            if selected:
                color = arcade.color.DARK_BLUE 
                text_color = arcade.color.WHITE
            else:
                text_color = arcade.color.BLACK
                color = arcade.color.LIGHT_GRAY
            #draw the button and text for the button
            arcade.draw_lbwh_rectangle_filled(left, bottom, width, height, color)
            arcade.draw_text(label, left + width / 2, bottom + height / 2, text_color, 16, anchor_x="center", anchor_y="center")
            #this screen will create the self.mode variable that will be used to determine the game mode when the player continues to the next screen
       
        #draw computer difficulty section
        arcade.draw_text("Computer Difficulty", WINDOW_WIDTH / 2, 285, arcade.color.BLACK, 20,
                         anchor_x="center")
        #draw corresponding buttons, highlight selected button in dark blue
        for label, left, bottom, width, height in DIFFICULTY_OPTIONS:
            selected = label == self.ai_difficulty
            if selected:
                color = arcade.color.DARK_BLUE 
                text_color = arcade.color.WHITE
            else:
                text_color = arcade.color.BLACK
                color = arcade.color.LIGHT_GRAY
            arcade.draw_lbwh_rectangle_filled(left, bottom, width, height, color)
            arcade.draw_text(label, left + width / 2, bottom + height / 2, text_color, 16, anchor_x="center", anchor_y="center")
            #this will create the self.ai_difficulty variable that will be used to determine the computer difficulty when the player continues to the next screen

        #draw continue button to move on to next page
        left, bottom, width, height = CONTINUE_BUTTON
        arcade.draw_lbwh_rectangle_filled(left, bottom, width, height, arcade.color.GREEN)
        arcade.draw_text("Continue", left + width / 2, bottom + height / 2, arcade.color.WHITE, 18, anchor_x="center", anchor_y="center")

    def on_key_press(self, key, modifiers):
        """Handle mode/AI selection, mine count entry, game start, and restart."""
        if self.game is None:
            #add config for mode selection screen.
            if self.ui_state == "mode_select":
                #if you hit enter, move to mine setup screen
                if key == arcade.key.ENTER:
                    self.ui_state = "mine_setup"
                return
            if arcade.key.KEY_0 <= key <= arcade.key.KEY_9:
                self.mine_count_input += chr(key)
                self.setup_error = ""
            elif key == arcade.key.BACKSPACE:
                self.mine_count_input = self.mine_count_input[:-1]
                self.setup_error = ""
            elif key == arcade.key.ENTER:
                self.confirm_mine_count()
        elif key == arcade.key.R:
            # R starts a new game with the same mine count
            self.start_game(self.game.num_mines)

    def on_mouse_press(self, x, y, button, modifiers):
        """Send mouse input to the input handler."""
        #if no game has been started and we are still in the mode selection screen...
        if self.game is None:
            if button == arcade.MOUSE_BUTTON_LEFT and self.ui_state == "mode_select":
                for label, left, bottom, width, height in MODE_OPTIONS:
                    #this formula gets the label of the place you clicked. If there isn't a button there, it won't do anything. If there is a button, it will update the selected mode accordingly
                    if left <= x <= left + width and bottom <= y <= bottom + height:
                        self.mode = label
                        return
                for label, left, bottom, width, height in DIFFICULTY_OPTIONS:
                    #same formula as above, but for the difficulty selection buttons
                    if left <= x <= left + width and bottom <= y <= bottom + height:
                        self.ai_difficulty = label
                        return
                #same formula as above, but for the continue button. If you click it, it will move to the mine setup screen
                left, bottom, width, height = CONTINUE_BUTTON
                if left <= x <= left + width and bottom <= y <= bottom + height:
                    self.ui_state = "mine_setup"
            return

        #if the game is over, don't allow any more input
        if self.game.is_lost or self.game.is_won:
            return

        self.input_handler.handle_click(x, y, button)


def main():
    MinesweeperWindow()
    arcade.run()


if __name__ == "__main__":
    main()
