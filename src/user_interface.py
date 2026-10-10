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
How you validated and revised the AI output: Proofreading, logic tests for the board and game logic, and a scripted window test covering setup, revealing, flagging, loss, restart, and win
The challenges or limitations you faced while using AI: Keeping the diff minimal while matching the existing code style and validating the arcade API calls against the installed library version

Update 9/26/2026 - Felix Balandran
Added sound button to gameplay screen

Update 9/29/2026 = Jamareon Davis
Added logic for AI agent to play the game

Update 9/30/2026 - Riley Backus
Added UI for handling the AI agent

Attributions: 
Authors: Kyler Russell, Blake Pennel, Carter Steenhard
Creation Date: 9/15/2026
"""
import arcade
from game_logic import GameManager
import board_manager
from input_handler import InputHandler
from ai_solver import make_ai  # AI solver: factory for the Easy/Medium/Hard solvers


# Board and window sizing constants.
# These values control the grid layout, the overall window proportions, and the
# placement of the status and AI-control panel.
CELL_SIZE = 50

BOARD_LEFT = 50
BOARD_BOTTOM = 50

#This is the size of the game window
WINDOW_WIDTH = 840
WINDOW_HEIGHT = 650

# Sound toggle controls. The speaker icon sits in the upper-right corner of the
# game window and can be clicked to mute or unmute audio effects.
SOUND_SIZE = 48
SOUND_X = WINDOW_WIDTH - SOUND_SIZE - 12
SOUND_Y = 12

# The AI control panel is anchored to the right side of the board.
PANEL_LEFT = 620
PANEL_WIDTH = 200

COLUMN_LABELS = "ABCDEFGHIJ"
# UI config for the mode-selection and difficulty-selection controls.
# This pattern keeps the button layout consistent and easy to modify later.

# Standard Minesweeper colors for showing the number of nearby mines.
NUMBER_COLORS = {1: arcade.color.BLUE, 2: arcade.color.GREEN, 3: arcade.color.RED,
                 4: arcade.color.DARK_BLUE, 5: arcade.color.MAROON, 6: arcade.color.TEAL,
                 7: arcade.color.BLACK, 8: arcade.color.GRAY}

# Supported AI difficulties and operating modes.
# "off" means the player controls every move, while the other modes let the AI
# take turns either after each click or automatically on a timer.
AI_LEVELS = ["easy", "medium", "hard"]
AI_MODES = ["off", "interactive", "auto"]
MODE_LABELS = {"off": "Off", "interactive": "Turn", "auto": "Auto"}
MODE_HELP = {"off": "You play alone",
             "interactive": "AI moves after each click",
             "auto": "AI plays by itself"}

#This class is in charge of the Panel that the player can click in to change the AI solver
class Button:
    """A clickable rectangular UI control with a text label."""

    def __init__(self, left, bottom, width, height, label, action, is_active=None):
        # Store the button's geometry and behavior.
        self.left, self.bottom, self.width, self.height = left, bottom, width, height
        self.label = label
        self.action = action
        self.is_active = is_active or (lambda: False)

    def contains(self, x, y):
        # Mouse events use the button's rectangular bounds to determine clicks.
        return (self.left <= x <= self.left + self.width and
                self.bottom <= y <= self.bottom + self.height)

    def draw(self):
        # Active buttons are highlighted, while inactive buttons appear muted.
        color = arcade.color.LIGHT_BLUE if self.is_active() else arcade.color.LIGHT_GRAY
        arcade.draw_lbwh_rectangle_filled(self.left, self.bottom, self.width, self.height, color)
        arcade.draw_lbwh_rectangle_outline(self.left, self.bottom, self.width, self.height,
                                           arcade.color.BLACK, 2)
        arcade.draw_text(self.label, self.left + self.width / 2, self.bottom + self.height / 2,
                         arcade.color.BLACK, 12, anchor_x="center", anchor_y="center")


class MinesweeperWindow(arcade.Window):
    """Main Arcade window for the Minesweeper game and AI controls."""

    def __init__(self):
        # Arcade windows need a size and title before any rendering can happen.
        # The actual gameplay state is created later, after the player selects a
        # mine count and the game starts.
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, "Minesweeper")

        # The game is created once the player confirms a mine count.
        self.game = None
        self.input_handler = None

        # ui_state tracks where the user is in the startup flow. The app starts in
        # the mode-selection screen, then moves to a mine-count input screen.
        self.ui_state = "mode_select"

        # AI state: a solver instance, selected difficulty, current mode, and a
        # small timer used for pacing automatic/interactive turns.
        self.ai = None
        self.ai_level = "easy"
        self.ai_mode = "Solo"      # "Solo" | "Co-op" | "Computer Solve"
        self.ai_timer = 0.0
        self.ai_pending = False   # interactive: the AI owes a turn
        self.ai_reason = ""
        self.mine_count_input = ""
        self.setup_error = ""

        # Sound is on by default; the speaker icon is loaded from the Arcade
        # resource library so the UI looks consistent with the rest of the app.
        self.sound_enabled = True
        self.sound_icon = arcade.load_texture(":resources:/onscreen_controls/flat_dark/sound_on.png")

        # Reset AI details to the active runtime values used by the board state.
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
        # The GameManager owns the board rules, and InputHandler translates user
        # clicks into reveal/flag actions in the correct board-space coordinates.
        self.game = GameManager(num_mines)
        self.input_handler = InputHandler(self.game, CELL_SIZE, BOARD_LEFT, BOARD_BOTTOM, sound_enabled=self.sound_enabled)

        # Rebind the AI to the new board and reset per-game turn state so the AI
        # starts fresh on the current board rather than carrying state from the last round.
        self.ai = make_ai(self.game, self.ai_level)
        self.ai_pending = False
        self.ai_reason = ""

    def confirm_mine_count(self):
        """Start a game with the typed mine count, or report that it is invalid."""
        # Use the typed value if provided; otherwise keep the default of 10 mines.
        num_mines = int(self.mine_count_input or 10)
        if not (10 <= num_mines <= 20):
            self.setup_error = "Number of mines must be 10 to 20"
            return

        self.start_game(num_mines)


    def draw_sound_button(self):
        """Draw the speaker icon with a red line when muted."""
        # Render the default speaker image in the upper-right corner of the window.
        arcade.draw_texture_rect(
            self.sound_icon,
            arcade.LBWH(
                SOUND_X,
                SOUND_Y,
                SOUND_SIZE,
                SOUND_SIZE
            )
        )

        # When audio is disabled, overlay a red diagonal line to make the muted
        # state visually obvious without changing the rest of the UI layout.
        if not self.sound_enabled:
            arcade.draw_line(
                SOUND_X + 6,
                SOUND_Y + 6,
                SOUND_X + SOUND_SIZE - 6,
                SOUND_Y + SOUND_SIZE - 6,
                arcade.color.RED,
                4
            )

    def toggle_sound(self):
        """Toggle sound effects on or off."""
        # The toggle updates both the UI state and the input handler so that any
        # gameplay sound effects honor the same setting.
        self.sound_enabled = not self.sound_enabled
        if self.input_handler is not None:
            self.input_handler.sound_enabled = self.sound_enabled

    def on_draw(self):
        """Draw the setup screen or the current board."""
        # Clear the screen each frame so the board can re-render from the current
        # game state without leaving stale pixels behind.
        self.clear(arcade.color.WHITE)

        if self.game is None:
            self.draw_setup()
            self.draw_sound_button()
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
        self.draw_sound_button()


    def draw_setup(self):
        """Draw the mine count selection screen."""
        # This setup screen serves as a lightweight pre-game form. It lets the
        # player choose the board difficulty before the game begins.
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
            # The startup flow is intentionally simple: press Enter to move from the
            # mode screen into the mine-count input screen.
            if self.ui_state == "mode_select":
                if key == arcade.key.ENTER:
                    self.ui_state = "mine_setup"
                return

            # Number input is validated before the game starts so invalid counts do
            # not create an unusable board state.
            if arcade.key.KEY_0 <= key <= arcade.key.KEY_9:
                self.mine_count_input += chr(key)
                self.setup_error = ""
            elif key == arcade.key.BACKSPACE:
                self.mine_count_input = self.mine_count_input[:-1]
                self.setup_error = ""
            elif key == arcade.key.ENTER:
                self.confirm_mine_count()
        elif key == arcade.key.R:
            # R restarts the current board with the same mine count instead of
            # resetting the entire application.
            self.start_game(self.game.num_mines)
        # AI solver: hotkeys share the same logic as the panel buttons.
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
            # Each mode button toggles the AI mode and highlights the active state.
            buttons.append(Button(PANEL_LEFT + i * 69, 450, 62, 30, MODE_LABELS[mode],
                                  lambda m=mode: self.set_ai_mode(m),
                                  lambda m=mode: self.ai_mode == m))
        for i, level in enumerate(AI_LEVELS):
            # Difficulty buttons swap the AI solver implementation while keeping the same board.
            buttons.append(Button(PANEL_LEFT + i * 69, 380, 62, 30, level.capitalize(),
                                  lambda l=level: self.set_ai_level(l),
                                  lambda l=level: self.ai_level == l))
        buttons.append(Button(PANEL_LEFT, 310, 90, 30, "Slower", lambda: self.change_ai_delay(0.05)))
        buttons.append(Button(PANEL_LEFT + 110, 310, 90, 30, "Faster", lambda: self.change_ai_delay(-0.05)))
        buttons.append(Button(PANEL_LEFT, 250, PANEL_WIDTH, 30, "Step (S)", self._take_ai_turn))
        return buttons

    def set_ai_mode(self, mode):
        # Switching modes resets any pending turn so the AI does not continue from
        # stale state after the user changes its behavior.
        self.ai_mode = mode
        self.ai_timer = 0.0
        self.ai_pending = False

    def set_ai_level(self, level):
        # Rebind the solver to the current board at the selected skill level.
        self.ai_level = level
        if self.game is not None:
            self.ai = make_ai(self.game, self.ai_level)  # rebind, same board

    def change_ai_delay(self, amount):
        # The delay is clamped to a safe range so the AI can be slowed down or sped
        # up without breaking the pacing logic.
        self.ai_delay = round(min(1.0, max(0.05, self.ai_delay + amount)), 2)

    def draw_ai_panel(self):
        """Draw the AI control panel."""
        # The panel lives on the right side of the window and allows the player to
        # inspect and adjust the AI's operating mode, difficulty, and move speed.
        arcade.draw_text("AI Agent", PANEL_LEFT, 520, arcade.color.BLACK, 20)
        arcade.draw_text("Mode", PANEL_LEFT, 490, arcade.color.BLACK, 14)
        arcade.draw_text(MODE_HELP[self.ai_mode], PANEL_LEFT, 430, arcade.color.DARK_GRAY, 11)
        arcade.draw_text("Level", PANEL_LEFT, 420, arcade.color.BLACK, 14)
        arcade.draw_text(f"Delay: {self.ai_delay:.2f}s", PANEL_LEFT, 350, arcade.color.BLACK, 14)
        for button in self.buttons:
            button.draw()

    # AI solver: play a single AI turn and record its justification.
    def _take_ai_turn(self):
        """Play one AI move and record why it was made."""
        if self.game is None or self.game.is_won or self.game.is_lost:
            return
        # The AI returns a Move object with a reason string; this shows the player
        # why the solver chose a particular action.
        move = self.ai.step()
        self.ai_reason = move.reason if move else "no moves available"

    # AI solver: Arcade calls this every frame to pace automatic solving.
    def on_update(self, delta_time):
        """Pace AI turns so the moves are watchable."""
        # Auto mode advances continuously, while interactive mode waits for the user
        # to trigger the next AI move after a click.
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
        # The sound button is always checked first so it can be toggled even when
        # the board is not active.
        if (button == arcade.MOUSE_BUTTON_LEFT and
                SOUND_X <= x <= SOUND_X + SOUND_SIZE and
                SOUND_Y <= y <= SOUND_Y + SOUND_SIZE):
            self.toggle_sound()
            return

        if self.game is None:
            return

        # AI panel buttons work at any time, including after a win or loss.
        for ui_button in self.buttons:
            if ui_button.contains(x, y):
                ui_button.action()
                return

        # Board clicks are only allowed while the game is still running.
        if self.game.is_lost or self.game.is_won:
            return

        self.input_handler.handle_click(x, y, button)

        # In interactive mode, a left click hands the turn to the AI after the
        # player's action has been applied.
        if self.ai_mode == "interactive" and button == arcade.MOUSE_BUTTON_LEFT:
            self.ai_pending = True
            self.ai_timer = 0.0


def main():
    MinesweeperWindow()
    arcade.run()


if __name__ == "__main__":
    main()
