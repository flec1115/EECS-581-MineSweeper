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
from ai_solver import make_ai  # AI solver: factory for the Easy/Medium/Hard solvers


CELL_SIZE = 50

BOARD_LEFT = 50
BOARD_BOTTOM = 50

WINDOW_WIDTH = 840
WINDOW_HEIGHT = 650

SOUND_X = 522
SOUND_Y = 575
SOUND_SIZE = 48

PANEL_LEFT = 620
PANEL_WIDTH = 200

COLUMN_LABELS = "ABCDEFGHIJ"
#configs for setting buttons for the mode selection and difficulty selection screens
#formatting used chatGPT GPT-5.6 Luna for reference of an easy way to set up buttons and their locations on the screen

# Standard Minesweeper colors for the adjacent mine counts
NUMBER_COLORS = {1: arcade.color.BLUE, 2: arcade.color.GREEN, 3: arcade.color.RED,
                 4: arcade.color.DARK_BLUE, 5: arcade.color.MAROON, 6: arcade.color.TEAL,
                 7: arcade.color.BLACK, 8: arcade.color.GRAY}


AI_LEVELS = ["easy", "medium", "hard"]
AI_MODES = ["off", "interactive", "auto"]
MODE_LABELS = {"off": "Off", "interactive": "Turn", "auto": "Auto"}
MODE_HELP = {"off": "You play alone",
             "interactive": "AI moves after each click",
             "auto": "AI plays by itself"}

class Button:
    """A clickable rectangle with a label."""

    def __init__(self, left, bottom, width, height, label, action, is_active=None):
        self.left, self.bottom, self.width, self.height = left, bottom, width, height
        self.label = label
        self.action = action
        self.is_active = is_active or (lambda: False)

    def contains(self, x, y):
        return (self.left <= x <= self.left + self.width and
                self.bottom <= y <= self.bottom + self.height)

    def draw(self):
        color = arcade.color.LIGHT_BLUE if self.is_active() else arcade.color.LIGHT_GRAY
        arcade.draw_lbwh_rectangle_filled(self.left, self.bottom, self.width, self.height, color)
        arcade.draw_lbwh_rectangle_outline(self.left, self.bottom, self.width, self.height,
                                           arcade.color.BLACK, 2)
        arcade.draw_text(self.label, self.left + self.width / 2, self.bottom + self.height / 2,
                         arcade.color.BLACK, 12, anchor_x="center", anchor_y="center")
        
class MinesweeperWindow(arcade.Window):
    """Simple Arcade UI for Minesweeper."""

    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, "Minesweeper")

        # The game is created once the player confirms a mine count
        self.game = None
        self.input_handler = None
        #states for AI selection screen
        self.ui_state = "mode_select"
        # AI solver: solver instance, difficulty, and turn-taking state
        self.ai = None
        self.ai_level = "easy"
        self.ai_mode = "Solo"      # "Solo" | "Co-op" | "Computer Solve"
        self.ai_timer = 0.0
        self.ai_pending = False   # interactive: the AI owes a turn
        self.ai_reason = ""
        self.mine_count_input = ""
        self.setup_error = ""
        # Sound is on by default
        self.sound_enabled = True
        # Load Arcade's built-in speaker icon
        self.sound_icon = arcade.load_texture(":resources:/onscreen_controls/flat_dark/sound_on.png")

        # AI solver: solver instance, difficulty, and turn-taking state
        self.ai = None
        self.ai_level = "easy"
        self.ai_mode = "off"      # "off" | "interactive" | "auto"
        self.ai_timer = 0.0
        self.ai_pending = False   # interactive: the AI owes a turn
        self.ai_reason = ""
        self.ai_delay = 0.25
        self.buttons = self.build_buttons()

    def start_game(self, num_mines):
        """Create a new game and rebuild the input handler for it."""
        self.game = GameManager(num_mines)
        self.input_handler = InputHandler(self.game, CELL_SIZE, BOARD_LEFT, BOARD_BOTTOM, sound_enabled=self.sound_enabled)
        # AI solver: rebind to the new game and clear per-game turn state
        self.ai = make_ai(self.game, self.ai_level)
        self.ai_pending = False
        self.ai_reason = ""

    def confirm_mine_count(self):
        """Start a game with the typed mine count, or report that it is invalid."""
        num_mines = int(self.mine_count_input or 10)
        if not (10 <= num_mines <= 20):
            self.setup_error = "Number of mines must be 10 to 20"
            return

        self.start_game(num_mines)


    def draw_sound_button(self):
        """Draw the speaker icon with a red line when muted."""
        # Draw the speaker
        arcade.draw_texture_rect(
            self.sound_icon,
            arcade.LBWH(
                SOUND_X,
                SOUND_Y,
                SOUND_SIZE,
                SOUND_SIZE
            )
        )

    # Draw a red diagonal line when muted
        if not self.sound_enabled:
            arcade.draw_line(
                SOUND_X + 6,
                SOUND_Y + 6,
                SOUND_X + SOUND_SIZE - 6,
                SOUND_Y + SOUND_SIZE - 6,
                arcade.color.RED,
                4
            )

    def on_draw(self):
        """Draw the setup screen or the current board."""
        self.clear(arcade.color.WHITE)

        if self.game is None:
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
            arcade.draw_text("Press R to restart", BOARD_LEFT + board_manager.BOARD_SIZE * CELL_SIZE / 2, 30,
            arcade.color.BLACK, 18, anchor_x="center", bold=True)
        elif self.game.is_won:
            status, status_color = "Victory", arcade.color.GREEN
            arcade.draw_text("Press R to restart", BOARD_LEFT + board_manager.BOARD_SIZE * CELL_SIZE / 2, 30,
            arcade.color.BLACK, 18, anchor_x="center", bold=True)
        else:
            status, status_color = "Playing", arcade.color.BLACK

        arcade.draw_text(status, BOARD_LEFT + board_manager.BOARD_SIZE * CELL_SIZE, board_top + 30,
                         status_color, 18, anchor_x="right")
        self.draw_ai_panel()
        arcade.draw_text(self.ai_reason, BOARD_LEFT, 10, arcade.color.DARK_BLUE, 12)


    def draw_setup(self):
        """Draw the mine count selection screen."""
        arcade.draw_text("Minesweeper", WINDOW_WIDTH / 2, 420, arcade.color.BLACK, 32, anchor_x="center")
        arcade.draw_text("Type the number of mines (10-20) and press Enter", WINDOW_WIDTH / 2, 360,
                         arcade.color.BLACK, 16, anchor_x="center")
        arcade.draw_text(f"Mines: {self.mine_count_input or 10}", WINDOW_WIDTH / 2, 300,
                         arcade.color.BLUE, 28, anchor_x="center")

        if self.setup_error:
            arcade.draw_text(self.setup_error, WINDOW_WIDTH / 2, 260, arcade.color.RED, 16, anchor_x="center")

    def on_key_press(self, key, modifiers):
        """Handle mine count entry, game start, restart, and AI hotkeys."""
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
        # AI solver: hotkeys share their logic with the panel buttons
        elif key == arcade.key.D:
            self.set_ai_level(AI_LEVELS[(AI_LEVELS.index(self.ai_level) + 1) % len(AI_LEVELS)])
        elif key == arcade.key.A:
            self.set_ai_mode(AI_MODES[(AI_MODES.index(self.ai_mode) + 1) % len(AI_MODES)])
        elif key == arcade.key.S:
            self._take_ai_turn()

    def build_buttons(self):
        """Create the AI panel buttons."""
        buttons = []
        for i, mode in enumerate(AI_MODES):
            buttons.append(Button(PANEL_LEFT + i * 69, 450, 62, 30, MODE_LABELS[mode],
                                  lambda m=mode: self.set_ai_mode(m),
                                  lambda m=mode: self.ai_mode == m))
        for i, level in enumerate(AI_LEVELS):
            buttons.append(Button(PANEL_LEFT + i * 69, 380, 62, 30, level.capitalize(),
                                  lambda l=level: self.set_ai_level(l),
                                  lambda l=level: self.ai_level == l))
        buttons.append(Button(PANEL_LEFT, 310, 90, 30, "Slower", lambda: self.change_ai_delay(0.05)))
        buttons.append(Button(PANEL_LEFT + 110, 310, 90, 30, "Faster", lambda: self.change_ai_delay(-0.05)))
        buttons.append(Button(PANEL_LEFT, 250, PANEL_WIDTH, 30, "Step (S)", self._take_ai_turn))
        return buttons

    def set_ai_mode(self, mode):
        self.ai_mode = mode
        self.ai_timer = 0.0
        self.ai_pending = False

    def set_ai_level(self, level):
        self.ai_level = level
        if self.game is not None:
            self.ai = make_ai(self.game, self.ai_level)  # rebind, same board

    def change_ai_delay(self, amount):
        self.ai_delay = round(min(1.0, max(0.05, self.ai_delay + amount)), 2)

    def draw_ai_panel(self):
        """Draw the AI control panel."""
        arcade.draw_text("AI Agent", PANEL_LEFT, 520, arcade.color.BLACK, 20)
        arcade.draw_text("Mode", PANEL_LEFT, 490, arcade.color.BLACK, 14)
        arcade.draw_text(MODE_HELP[self.ai_mode], PANEL_LEFT, 430, arcade.color.DARK_GRAY, 11)
        arcade.draw_text("Level", PANEL_LEFT, 420, arcade.color.BLACK, 14)
        arcade.draw_text(f"Delay: {self.ai_delay:.2f}s", PANEL_LEFT, 350, arcade.color.BLACK, 14)
        for button in self.buttons:
            button.draw()

      # AI solver: play a single AI turn and record its justification
    def _take_ai_turn(self):
        """Play one AI move and record why it was made."""
        if self.game is None or self.game.is_won or self.game.is_lost:
            return
        move = self.ai.step()
        self.ai_reason = move.reason if move else "no moves available"

    # AI solver: arcade calls this every frame; used to pace automatic solving
    def on_update(self, delta_time):
        """Pace AI turns so the moves are watchable."""
        if self.game is None or self.game.is_won or self.game.is_lost:
            return
        if self.ai_mode == "auto":
            self.ai_timer += delta_time
            if self.ai_timer >= self.ai_delay:
                self.ai_timer = 0.0
                self._take_ai_turn()
        elif self.ai_mode == "interactive" and self.ai_pending:
            self.ai_timer += delta_time
            if self.ai_timer >= self.ai_delay:
                self.ai_timer = 0.0
                self.ai_pending = False
                self._take_ai_turn()

    def on_mouse_press(self, x, y, button, modifiers):
        """Send mouse input to the AI panel or the input handler."""
        if self.game is None:
            return

        # AI panel buttons work at any time, including after a win or loss
        for ui_button in self.buttons:
            if ui_button.contains(x, y):
                ui_button.action()
                return

        # Board clicks are only allowed while the game is still running
        if self.game.is_lost or self.game.is_won:
            return

        self.input_handler.handle_click(x, y, button)

        # AI solver: in interactive mode a left click hands the turn to the AI
        if self.ai_mode == "interactive" and button == arcade.MOUSE_BUTTON_LEFT:
            self.ai_pending = True
            self.ai_timer = 0.0


def main():
    MinesweeperWindow()
    arcade.run()


if __name__ == "__main__":
    main()
