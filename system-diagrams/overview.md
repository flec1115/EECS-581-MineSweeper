# Overview of Diagrams

This file contains the mermaid diagrams for the system components, data flow, and key data structures of our Minesweeper program. `Inf_mode.py` is intentionally excluded for now.
Attribution: These diagrams were created with the aid of Claude Opus 5, and then verified by Kyler Russell.

The opening screen accepts the mine count immediately (10-20; blank Enter uses 10). The gameplay clock starts with each new game and freezes at win/loss. In Turn mode, only a player's left-click reveal of a covered, unflagged cell hands off the turn; flags do not. The AI may flag multiple cells during its turn and completes that turn after revealing a cell. Hard AI adds a horizontal 1-2-1 deduction to the Medium rules.

## Diagram of System Components

This diagram displays the system components of our Minesweeper program.

```mermaid
flowchart TB
    ARC["«library»<br/><b>Arcade 3.3.3+</b><br/>window, events, drawing, audio"]
    RND["«library»<br/><b>random</b><br/>mine placement and AI fallback choices"]
    CLOCK["«library»<br/><b>time.perf_counter</b><br/>elapsed gameplay time"]
    SFX["«assets»<br/><b>sfx/</b><br/>flag, bomb, blip, cheer"]

    subgraph APP["Minesweeper application"]
      direction TB
      UI["«component»<br/><b>MinesweeperWindow</b><br/><i>user_interface.py</i><br/>mine setup, board, play clock and AI controls"]
      BTN["«component»<br/><b>Button</b><br/><i>user_interface.py</i><br/>AI panel controls"]
      IH["«component»<br/><b>InputHandler</b><br/><i>input_handler.py</i><br/>board clicks and SFX"]
      AI["«component»<br/><b>EasyAI / MediumAI / HardAI</b><br/><i>ai_solver.py</i><br/>random fallback, single-cell rules, horizontal 1-2-1; flags do not end AI Turn"]
      MOVE["«data»<br/><b>Move</b><br/><i>ai_solver.py</i><br/>action, cell, reason"]
      GL["«component»<br/><b>GameManager</b><br/><i>game_logic.py</i><br/>game rules and status"]
      BM["«component»<br/><b>BoardManager + Cell</b><br/><i>board_manager.py</i><br/>10 x 10 board state"]
    end

    ARC -->|"window events and draw calls"| UI
    UI -->|"creates and handles callbacks"| BTN
    UI -->|"board click"| IH
    UI -->|"creates selected solver via make_ai"| AI
    UI -.->|"reads game status"| GL
    UI -.->|"reads board cells for rendering"| BM
    UI -.->|"requests an AI turn"| AI
    UI -->|"reads monotonic clock"| CLOCK
    IH -->|"reveal, flag, unflag"| GL
    IH -->|"loads and plays"| SFX
    IH -->|"audio API"| ARC
    UI -.->|"syncs mute state"| IH
    AI -->|"applies reveal or flag move"| GL
    AI -.->|"creates and returns"| MOVE
    AI -.->|"reads cells via game.board"| BM
    GL -->|"updates cells"| BM
    GL -.->|"random.sample"| RND
    AI -.->|"random fallback"| RND

    classDef comp fill:#eef2f9,stroke:#4a6fa5,stroke-width:1.4px,color:#161a21
    classDef data fill:#fdf4e3,stroke:#b58b3a,stroke-width:1.4px,color:#4a3a18
    classDef lib fill:#f2f3f5,stroke:#9aa3b0,stroke-width:1.2px,color:#3d4652
    class UI,BTN,IH,AI,GL,BM comp
    class MOVE data
    class ARC,RND,CLOCK,SFX lib
```

## Data Flow

This diagram displays the data flow of our Minesweeper program.

```mermaid
flowchart LR
    P(("Player"))

    KP["Keyboard<br/><i>0-9, Backspace, Enter<br/>R, A, D, S</i>"]
    MP["Mouse<br/><i>board, AI controls<br/>sound button</i>"]
    UI["MinesweeperWindow<br/><b>Arcade event handling</b>"]
    SETUP["Mine-count entry<br/>digits accepted immediately<br/>validate 10 to 20; blank Enter = 10"]
    CREATE["start_game<br/>create GameManager,<br/>InputHandler and AI"]
    HIT["InputHandler<br/>pixels to row/column<br/>bounds check"]
    TOGGLE["Sound button click"]
    PANEL["AI controls<br/>mode, level, AI delay,<br/>single step"]
    TURN["Turn-mode handoff<br/>player left-click reveal of a covered,<br/>unflagged cell only; flags do not hand off"]
    AI["EasyAI / MediumAI / HardAI<br/>random fallback, single-cell rules,<br/>horizontal 1-2-1; AI flags continue its turn"]
    RULES["GameManager<br/>mine placement, reveal cascade,<br/>flags and win/loss"]

    BS[("BoardManager<br/><b>10 x 10 Cell grid</b><br/>covered, flagged, is_mine")]
    GS[("Game state<br/><b>GameManager</b><br/>is_won, is_lost, mine_count,<br/>flags, cells_to_clear")]
    AUDIO["InputHandler SFX<br/>flag, bomb, blip, cheer"]
    CLOCK["Gameplay clock<br/>time.perf_counter<br/>starts on game creation;<br/>freezes at win/loss"]
    RENDER["MinesweeperWindow.on_draw<br/>board, status, AI panel,<br/>sound button"]
    SCREEN["840 x 650 Arcade window"]

    P --> KP --> UI
    P --> MP --> UI
    UI -->|"count keys / Enter"| SETUP --> CREATE
    CREATE --> GS
    CREATE --> BS
    CREATE --> HIT
    CREATE --> AI
    CREATE -->|"start / reset"| CLOCK

    UI -->|"board click"| HIT -->|"GameManager API"| RULES
    UI -->|"sound button click"| TOGGLE -->|"syncs mute state"| HIT
    UI -->|"mode, level, speed or step"| PANEL --> AI
    UI -->|"valid Turn-mode reveal"| TURN --> AI
    HIT -.->|"if enabled"| AUDIO
    RULES -->|"writes cells"| BS
    RULES -->|"updates counters and result"| GS
    AI -->|"Move: reveal or flag"| RULES
    RULES -->|"board and game state"| RENDER
    BS -->|"cell values and adjacent counts"| RENDER
    GS -->|"counter and game status"| RENDER
    CLOCK -->|"elapsed MM:SS"| RENDER
    RENDER --> SCREEN --> P

    classDef proc fill:#eef2f9,stroke:#4a6fa5,stroke-width:1.4px,color:#161a21
    classDef store fill:#fdf4e3,stroke:#b58b3a,stroke-width:1.4px,color:#4a3a18
    classDef io fill:#f2f3f5,stroke:#9aa3b0,stroke-width:1.2px,color:#3d4652
    class UI,SETUP,CREATE,HIT,TOGGLE,PANEL,TURN,AI,RULES,RENDER proc
    class BS,GS,AUDIO,CLOCK store
    class KP,MP,SCREEN,P io
```

## Key Data Structures

This diagram displays the key data structures of our Minesweeper program.

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
      +str ai_level
      +str ai_mode
      +float ai_timer
      +bool ai_pending
      +str ai_reason
      +float ai_delay
      +str mine_count_input
      +str setup_error
      +bool sound_enabled
      +float timer_start
      +float timer_elapsed
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
      +_take_ai_turn() Move
      +_timer_text() str
      +_freeze_timer_if_game_over() None
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
      +_deduce() List~Move~
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

    class time_perf_counter {
      <<library>>
      +perf_counter() float
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
    MinesweeperWindow --|> arcade_Window
    Button ..> MinesweeperWindow : invokes callbacks
    InputHandler ..> BoardManager : reads via game.board
    MinesweeperWindow ..> BoardManager : reads via game.board
    MinesweeperWindow ..> EasyAI : creates via make_ai()
    MinesweeperWindow ..> MediumAI : creates via make_ai()
    MinesweeperWindow ..> HardAI : creates via make_ai()
    MinesweeperWindow ..> time_perf_counter : gameplay clock
```
