# EECS 581 Minesweeper

A desktop Minesweeper game written in Python with the [Arcade](https://api.arcade.academy/) library. It was built by a seven-person team for EECS 581 (Project 1) using Scrum-style sprints.

## Features

- In-game controls for selecting Off, Turn, or Auto AI mode and an Easy, Medium, or Hard AI difficulty
- 10x10 board with a player-selected mine count (10-20)
- Safe first click: mines are never placed on the first cell you reveal or its neighbors, so the first click always opens up some of the board
- Automatic clearing: revealing a cell with no adjacent mines uncovers its neighbors, and so on outward
- Right-click flagging, with a counter showing how many mines remain unflagged
- Adjacent-mine numbers in the standard Minesweeper colors
- A1-J10 style board labels (columns A-J, rows 1-10)
- Status indicator: `Playing`, `Victory`, or `Game Over: Loss`
- All mines are revealed on a loss
- Restart with the same mine count at any time
- Easy, Medium, and Hard AI solvers, with Off, Turn, and Auto modes, adjustable delay, and move explanations
- Sound effects for game actions, with a speaker button to mute or restore them

## Requirements

- Python 3.14 or newer
- [uv](https://docs.astral.sh/uv/) (recommended), or `pip`
- Arcade 3.3.3 or newer (installed automatically by `uv`)

## Setup and Running

Clone the repository, then from the project root:

```bash
uv sync
uv run src/user_interface.py
```

Without `uv`:

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install "arcade>=3.3.3"
python3 src/user_interface.py
```

## How to Play

1. Press `Enter` to activate mine-count entry. Type a number from 10 to 20 and press `Enter`; pressing `Enter` with nothing typed uses the default of 10. `Backspace` edits the entry.
2. Reveal cells with a left click. A number shows how many of the up to eight surrounding cells contain mines.
3. Flag suspected mines with a right click. Right-click a flag again to remove it. Flagged cells can't be revealed until the flag is removed.
4. Win by uncovering every cell that does not contain a mine. Lose by uncovering a mine.
5. Press `R` at any time to start a new game with the same mine count.
6. Use the AI panel to select Off, Turn, or Auto mode and an AI difficulty. Adjust the delay or take a single AI turn from the panel.
7. Click the speaker icon in the bottom-right corner to toggle sound effects.

| Input | Action |
| --- | --- |
| Left click | Reveal a cell |
| Right click | Place or remove a flag |
| `R` | Restart with the same mine count |
| Click AI mode or press `A` | Select Off, Turn, or Auto |
| Click AI difficulty or press `D` | Select Easy, Medium, or Hard |
| Click Slower/Faster | Adjust AI delay |
| Click Step or press `S` | Take one AI turn |
| Click speaker icon | Mute or restore sound effects |
| `Enter` before the game starts | Activate mine-count entry |
| `0`-`9`, `Backspace`, `Enter` | Enter the mine count |

Off mode lets you play alone. Turn mode gives the AI a turn after a player click. Auto mode lets the AI play continuously until the game ends.

Board clicks are ignored once the game has been won or lost.

## Project Structure

```
src/
├── ai_solver.py       # EasyAI, MediumAI, HardAI, and Move
├── board_manager.py   # Cell and BoardManager: the 10x10 grid and its cell state
├── game_logic.py      # GameManager: mine placement, reveal/flag rules, win/loss
├── input_handler.py   # InputHandler: board clicks and sound effects
└── user_interface.py  # Button and MinesweeperWindow: Arcade UI and controls
hours-tracking/        # Per-member hour logs and the team's hour estimates
meeting-notes/         # Scrum meeting notes
system-diagrams/       # Diagrams detailing system schematics
```

### Architecture

Gameplay input and game-state updates follow this flow:

```
Player input -> MinesweeperWindow -> InputHandler -> GameManager -> BoardManager -> MinesweeperWindow draws the board
AI controls -> selected AI solver -> GameManager -> BoardManager
```

- **`BoardManager`** owns the grid. Each `Cell` tracks whether it is covered, flagged, or a mine. The board provides `neighbors()` and `adjacent_mines()` helpers.
- **`GameManager`** owns the game rules: mine placement, revealing, flagging, and win/loss status.
- **`InputHandler`** translates board clicks into game actions and plays sound effects when enabled.
- **`EasyAI`, `MediumAI`, and `HardAI`** choose moves and apply them through `GameManager`; `Move` records the action and explanation.
- **`MinesweeperWindow`** creates the game and AI, draws the board and AI panel, handles keyboard and mouse events, and synchronizes the sound toggle with `InputHandler`.

The board size is set by `BOARD_SIZE` in `src/board_manager.py`. The UI layout constants (`CELL_SIZE`, `BOARD_LEFT`, and so on) are in `src/user_interface.py`. `InputHandler` currently hard-codes a 10x10 bounds check, so changing the board size requires updating it as well.

### Diagram of System Components

This diagram displays the system components of our minesweeper program.

```mermaid
flowchart TB
    ARC["«library»<br/><b>Arcade 3.3.3</b><br/>window, event loop, drawing, audio"]

    subgraph APP[" Minesweeper application "]
      direction TB
      UI["«component»<br/><b>MinesweeperWindow + Button</b><br/><i>user_interface.py</i><br/>setup, board, AI and sound controls"]
      IH["«component»<br/><b>InputHandler</b><br/><i>input_handler.py</i><br/>board input and sound effects"]
      AI["«component»<br/><b>EasyAI / MediumAI / HardAI</b><br/><i>ai_solver.py</i><br/>select and apply moves"]
      GL["«component»<br/><b>GameManager</b><br/><i>game_logic.py</i><br/>game rules"]
      BM["«component»<br/><b>BoardManager + Cell</b><br/><i>board_manager.py</i><br/>board state"]
    end

    RND["«library»<br/><b>random</b><br/>mine sampling and AI fallback"]
    SFX["«assets»<br/><b>sfx/</b><br/>flag, bomb, blip, cheer"]

    ARC -->|"window events"| UI
    UI -->|"board clicks"| IH
    UI -->|"requests AI moves"| AI
    UI -.->|"reads game status"| GL
    UI -.->|"renders board cells"| BM
    IH -->|"reveal and flag actions"| GL
    IH -->|"plays enabled effects"| SFX
    AI -->|"applies moves"| GL
    AI -.->|"random fallback"| RND
    GL -->|"updates cells"| BM
    GL -.->|"random.sample"| RND
    UI -->|"Arcade drawing API"| ARC
    UI -.->|"syncs mute state"| IH

    classDef comp fill:#eef2f9,stroke:#4a6fa5,stroke-width:1.4px,color:#161a21
    classDef lib fill:#f2f3f5,stroke:#9aa3b0,stroke-width:1.2px,color:#3d4652
    class UI,IH,AI,GL,BM comp
    class ARC,RND,SFX lib
```

### Data Flow

This diagram displays the dataflow of our minesweeper program.

```mermaid
flowchart LR
    P(("Player"))

    MP["Mouse press<br/><i>x, y, button</i>"]
    KP["Key press<br/><i>Enter, 0-9, Backspace<br/>R, A, D, S</i>"]

    UI["MinesweeperWindow<br/>routes UI events"]
    SES["Mine-count entry<br/>validate 10 to 20"]
    IH["InputHandler<br/>translate pixels to row/col<br/>reject out-of-board clicks"]
    AI["AI solver<br/>select Easy, Medium, or Hard move"]
    RUL["GameManager<br/>mine placement, reveal cascade,<br/>flagging, win/loss"]

    BS[("Board state<br/><b>10 x 10 Cell grid</b><br/>covered, flagged, is_mine")]
    GS[("Game state<br/><b>GameManager</b><br/>is_won, is_lost, mine_count,<br/>flags, cells_to_clear")]
    SFX["Sound effects<br/>flag, bomb, blip, cheer<br/>played only when enabled"]
    DR["Render pass<br/><b>on_draw</b> per frame"]
    SCR["Window<br/>840 x 650 px"]

    P --> MP --> UI
    P --> KP --> UI
    UI -->|"count entry"| SES
    SES -->|"start_game"| GS
    SES -->|"new game"| BS
    UI -->|"board click"| IH
    IH -->|"reveal or flag action"| RUL
    UI -->|"mode, difficulty, delay, step"| AI
    AI -->|"apply selected move"| RUL
    IH -.->|"if sound is enabled"| SFX
    UI -->|"syncs mute state"| IH
    RUL -->|"updates covered, flagged, is_mine"| BS
    RUL -->|"updates counters and status"| GS
    BS -->|"cell state and adjacent counts"| DR
    GS -->|"mine count and game result"| DR
    DR --> SCR --> P

    classDef proc fill:#eef2f9,stroke:#4a6fa5,stroke-width:1.4px,color:#161a21
    classDef store fill:#fdf4e3,stroke:#b58b3a,stroke-width:1.4px,color:#4a3a18
    classDef io fill:#f2f3f5,stroke:#9aa3b0,stroke-width:1.2px,color:#3d4652
    class UI,SES,IH,AI,RUL,DR proc
    class BS,GS,SFX store
    class MP,KP,SCR,P io
```

### Key Data Structures

This diagram displays the key data structures of our minesweeper program.

```mermaid
classDiagram
    direction TB

    class Cell {
      +bool covered
      +bool flagged
      +bool is_mine
    }

    class BoardManager {
      +List~List~Cell~~ board
      +is_mine(row, col) bool
      +is_covered(row, col) bool
      +is_flagged(row, col) bool
      +adjacent_mines(row, col) int
      +neighbors(row, col) list
      +uncover_cell(row, col) None
      +set_mine(row, col) None
      +set_mines(mines) None
      +set_flagged(row, col) None
      +remove_flag(row, col) None
      +clear_flags() None
    }

    class GameManager {
      +BoardManager board
      +bool is_lost
      +bool is_won
      +bool are_mines_populated
      +int num_mines
      +int mine_count
      +int flags
      +int cells_to_clear
      +populate_mines(user_row, user_col) None
      +reveal_cell(row, col) None
      +flag_cell(row, col) None
      +unflag_cell(row, col) None
    }

    class InputHandler {
      +GameManager game
      +int cell_size
      +int board_left
      +int board_bottom
      +bool sound_enabled
      +Sound flag_sound
      +Sound bomb_sound
      +Sound blip_sound
      +Sound cheer_sound
      +handle_click(x, y, button) None
    }

    class Button {
      +float left
      +float bottom
      +float width
      +float height
      +str label
      +callable action
      +callable is_active
      +contains(x, y) bool
      +draw() None
    }

    class MinesweeperWindow {
      +GameManager game
      +InputHandler input_handler
      +ai
      +List~Button~ buttons
      +str ui_state
      +str ai_level
      +str ai_mode
      +float ai_timer
      +bool ai_pending
      +str ai_reason
      +float ai_delay
      +str mine_count_input
      +str setup_error
      +bool sound_enabled
      +start_game(num_mines) None
      +confirm_mine_count() None
      +draw_sound_button() None
      +toggle_sound() None
      +draw_setup() None
      +draw_ai_panel() None
      +on_draw() None
      +on_update(delta_time) None
      +on_key_press(key, modifiers) None
      +on_mouse_press(x, y, button, modifiers) None
      +set_ai_mode(mode) None
      +set_ai_level(level) None
      +change_ai_delay(amount) None
      +_take_ai_turn() None
    }

    class EasyAI {
      +GameManager game
      +Random rng
      +List~Move~ _queue
      +next_move() Move
      +apply(move) None
      +step() Move
      +solve(max_steps) str
    }

    class MediumAI {
      +_cell_view(row, col) tuple
      +_deduce() List~Move~
    }

    class HardAI {
    }

    class Move {
      +str action
      +int row
      +int col
      +str reason
    }

    class arcade_Window {
      <<library>>
    }

    BoardManager "1" *-- "100" Cell : board
    GameManager "1" *-- "1" BoardManager : board
    MinesweeperWindow "1" *-- "0..1" GameManager : game
    MinesweeperWindow "1" *-- "0..1" InputHandler : input_handler
    MinesweeperWindow "1" o-- "0..1" EasyAI : selected ai
    MinesweeperWindow "1" o-- "0..1" MediumAI : selected ai
    MinesweeperWindow "1" o-- "0..1" HardAI : selected ai
    MinesweeperWindow "1" *-- "0..*" Button : buttons
    InputHandler "1" --> "1" GameManager : game
    MinesweeperWindow ..> InputHandler : synchronizes sound_enabled
    EasyAI "1" --> "1" GameManager : game
    EasyAI ..> Move : creates and applies
    MediumAI --|> EasyAI
    HardAI --|> MediumAI
    arcade_Window <|-- MinesweeperWindow
    InputHandler ..> BoardManager : reads via game.board
    MinesweeperWindow ..> BoardManager : reads via game.board
    MinesweeperWindow ..> EasyAI : creates via make_ai()
    MinesweeperWindow ..> MediumAI : creates via make_ai()
    MinesweeperWindow ..> HardAI : creates via make_ai()
```

## Team

| Member | Role |
| --- | --- |
| Luke Reicherter | Scrum Master |
| Drew Medlock | Board Manager / Game Logic Developer |
| Kyle Fleming | QA Tester and Bug Fixer |
| Alex Rawson | General Developer and Code Reviewer |
| Carter Steenhard | Game Logic / UI Developer |
| Blake Pennel | Lead UI Developer |
| Kyler Russell | General Developer and Code Reviewer |

## Group 5 Team Project 2

| Member | Role |
| --- | --- |
| John Vitha | UI Devlopment |
| Bill Grimsley | Documentation |
| Felix Balandran | Feature Additions |
| Abdulaziz Arab | AI Logic Developer |
| Jamareon Davis | AI Logic Developer |
| Riley Backus | AI Logic Developer |

## AI Usage

Some modules were drafted or revised with generative AI tools (ChatGPT and DeepSeek). Each source file's header documents which tool was used, why, and how the output was validated.

This README was written with the help of Claude (Anthropic's AI assistant, via Claude Code). Claude read the source files and project notes to draft it, and the team reviewed the result.
