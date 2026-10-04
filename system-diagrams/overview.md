# Overview of Diagrams

This file contains the mermaid diagrams to display the diagrams of system components, data flow, and key data structures of our minesweeper program. The file is a .md, despite the mermaid file suffix of .mmd, as most markdown viewers are able to render these mermaid diagrams.
Attribution: These diagrams were created with the aid of Claude Opus 5, and then verified by Kyler Russell.

## Diagram of System Components

This diagram displays the system components of our minesweeper program.

```mermaid
flowchart TB
    ARC["«library»<br/><b>Arcade 3.3.3</b><br/>window, event loop, drawing"]

    subgraph APP[" Minesweeper application "]
      direction TB
      UI["«component»<br/><b>MinesweeperWindow</b><br/><i>user_interface.py</i><br/>mode/difficulty selection<br/>presentation"]
      IH["«component»<br/><b>InputHandler</b><br/><i>input_handler.py</i><br/>input translation"]
      GL["«component»<br/><b>GameManager</b><br/><i>game_logic.py</i><br/>rules"]
      BM["«component»<br/><b>BoardManager + Cell</b><br/><i>board_manager.py</i><br/>state store"]
    end

    RND["«library»<br/><b>random</b><br/>mine sampling"]

    ARC -->|"on_mouse_press<br/>on_key_press"| UI
    UI -->|"handle_click x, y, button"| IH
    IH -->|"populate_mines, reveal_cell<br/>flag_cell, unflag_cell"| GL
    GL -->|"set_mines, uncover_cell<br/>set_flagged, remove_flag, clear_flags"| BM
    GL -.->|"random.sample"| RND
    UI -.->|"reads: is_covered, is_flagged<br/>is_mine, adjacent_mines"| BM
    IH -.->|"reads: is_covered, is_flagged"| BM
    UI -.->|"reads: mine_count, is_won, is_lost"| GL
    UI -->|"arcade.draw_* per frame"| ARC

    classDef comp fill:#eef2f9,stroke:#4a6fa5,stroke-width:1.4px,color:#161a21
    classDef lib fill:#f2f3f5,stroke:#9aa3b0,stroke-width:1.2px,color:#3d4652
    class UI,IH,GL,BM comp
    class ARC,RND lib
```

## Data Flow

This diagram displays the dataflow of our minesweeper program.

```mermaid
flowchart LR
    P(("Player"))

    MP["Mouse press<br/><i>x, y, button</i>"]
    KP["Key press<br/><i>0-9, BACKSPACE<br/>ENTER, R</i>"]

    XL["Coordinate translation<br/>pixels to row, col<br/>plus bounds rejection"]
    MS["Mode / AI selection<br/>Solo, Co-op, Computer Solve<br/>difficulty: Easy, Medium, Hard<br/>Continue or Enter"]
    SES["Session control<br/>mine count entry<br/>validate 10 to 20<br/>construct GameManager"]
    RUL["Rule evaluation<br/>place mines, reveal cascade<br/>flag accounting, win/loss test"]

    BS[("Board state<br/><b>10 x 10 Cell grid</b><br/>covered, flagged, is_mine")]
    GS[("Game state<br/><b>GameManager scalars</b><br/>is_won, is_lost, mine_count<br/>flags, cells_to_clear")]

    DR["Render pass<br/><b>on_draw</b> per frame"]
    SCR["Window<br/>600 x 650 px"]

    P --> MP --> XL --> RUL
    MP --> MS
    P --> KP --> MS
    KP --> SES
    MS -->|"selected mode and AI level"| SES
    SES -->|"fresh board and counters"| BS
    SES --> GS
    RUL -->|"writes covered, flagged, is_mine"| BS
    RUL -->|"updates counters and status"| GS
    BS -->|"is_covered, is_flagged, is_mine<br/>adjacent_mines"| DR
    GS -->|"mine_count, is_won, is_lost"| DR
    DR --> SCR --> P

    classDef proc fill:#eef2f9,stroke:#4a6fa5,stroke-width:1.4px,color:#161a21
    classDef store fill:#fdf4e3,stroke:#b58b3a,stroke-width:1.4px,color:#4a3a18
    classDef io fill:#f2f3f5,stroke:#9aa3b0,stroke-width:1.2px,color:#3d4652
    class XL,MS,SES,RUL,DR proc
    class BS,GS store
    class MP,KP,SCR,P io
```

## Key Data Structures

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
      +handle_click(x, y, button) None
    }

    class MinesweeperWindow {
      +GameManager game
      +InputHandler input_handler
      +str ui_state
      +str mode
      +str ai_difficulty
      +str mine_count_input
      +str setup_error
      +start_game(num_mines) None
      +confirm_mine_count() None
      +draw_mode_select() None
      +draw_setup() None
      +on_draw() None
      +on_key_press(key, modifiers) None
      +on_mouse_press(x, y, button, modifiers) None
    }

    class arcade_Window {
      <<library>>
    }

    BoardManager "1" *-- "100" Cell : board
    GameManager "1" *-- "1" BoardManager : board
    MinesweeperWindow "1" *-- "0..1" GameManager : game
    MinesweeperWindow "1" *-- "0..1" InputHandler : input_handler
    InputHandler "1" --> "1" GameManager : game
    MinesweeperWindow --|> arcade_Window
    InputHandler ..> BoardManager : reads via game.board
    MinesweeperWindow ..> BoardManager : reads via game.board
```
