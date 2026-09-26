A description of how and why AI was used: Claude Sonnet 5 was used to double check the tests met all project requirements
How you validated and revised the AI output: Proofreading, and rereading all project requirements
The challenges or limitations you faced while using AI: Avoiding scope bloat, the AI recommended an additional 60 tests including things such as playing the game hundreds of times 
Authors: Kyle Fleming

## Game Setup

- Test 1 - Start a game and check the grid is 10x10 with labels A to J across and 1 to 10 down. Click the centre of the bottom-left and top-right cells (x=75, y=75 and x=525, y=525). They should map to (row 0, col 0) and (row 9, col 9), and the labels at those spots should match.
    - Reason: This covers the board size, the labels and the click-to-cell mapping together, since a mistake in any of them makes the others misleading. Row 1 is drawn at the bottom, so confirm the team wants that.
- Test 2 - Try mine counts 9, 10, 20, 21, 0, 999, -1, an empty entry and "010", plus letters, symbols and Backspace. 10, 20, "010" and empty (which defaults to 10) should start a game. The others should show "Number of mines must be 10 to 20" and not start one.
    - Reason: The valid range is 10 to 20, so this tests both edges from both sides, and the odd inputs check the setup screen can't pass bad values to the game.
- Test 3 - For every mine count from 10 to 20, make the first click and count the mines on the board. The count should always match the chosen number.
    - Reason: This checks placement produces exactly the right number of mines and is actually random.
- Test 4 - Make the first click at corners, edges and the center, with 10 and 20 mines. The clicked cell and all its neighbours should never be mines, so the first click always opens up.
    - Reason: This is the first-click guarantee. Corners and edges are the risky cases because they have fewer neighbours to exclude.
- Test 5 - On a new game, check every cell is covered, unflagged and not a mine. Also check flags equals 0, mine_count equals num_mines, no mines are placed yet, and the status says "Playing".
    - Reason: This confirms a clean starting state. Mines are placed on the first click rather than "at game start", so the test also confirms that timing.
## Gameplay
- Test 6 - Left-click a covered safe cell, then left-click a mine. The safe cell should uncover, and the mine should set is_lost to True.
    - Reason: These are the two basic outcomes of uncovering a cell.
- Test 7 - Reveal a cell with no adjacent mines in an open area. Every connected zero cell and the numbered cells bordering them should uncover, and nothing spreads through a numbered cell. Repeat with a cascade reaching the corners, and with a flagged safe cell next to the zero cell.
    - Reason: This covers the recursive uncovering requirement and its edge cases: stopping at numbers, no out-of-bounds errors, and skipping flagged cells.
- Test 8 - Click outside the board on all four sides (x=49, x=550, y=49, y=550), click with the middle mouse button, and left-click an already uncovered cell twice. Nothing should change, and cells_to_clear should stay the same.
    - Reason: Bad input must be ignored. Double counting an uncovered cell would also make the win fire early.
## Mine Flagging
- Test 9 - Right-click a covered cell, then right-click it again. The first click should flag it and drop the remaining count by 1, and the second should remove the flag and restore the count.
    - Reason: Flags must toggle and the counter must stay in step.
- Test 10 - Left-click a flagged cell, including a flagged mine. It should stay covered with no loss and no change to cells_to_clear. Unflag it and left-click again, and it should uncover. Right-click an uncovered cell, and nothing should happen.
    - Reason: Flagged cells can't be uncovered until unflagged, and flags apply only to covered cells.
## Player Interface
- Test 11 - Show covered, flagged, uncovered-numbered and uncovered-zero cells, including numbers 1 to 8. Covered should be gray, flagged yellow, uncovered light gray, zero cells blank, and each number should draw in its own colour.
    - Reason: The spec requires all four cell states to be distinguishable, and this catches a missing color entry.
- Test 12 - Place and remove flags and check the on-screen count updates each time. Check the status reads "Playing" at the start, "Game Over: Loss" in red after a loss and "Victory" in green after a win.
    - Reason: These are the two status displays the spec requires, so they must track the game.
- Test 13 - After a win or loss, click and right-click on the board. Nothing should change. Then press R in mid-game and after each ending. A new game should start with the same mine count, a fresh board, zero flags and "Playing".
    - Reason: The game must freeze when it ends, and restart must reset everything.
## Game Conclusion
- Test 14 - Flag one mine and one safe cell, then click another mine. Every mine should show red, including the flagged one, and safe cells should stay covered.
    - Reason: A loss must reveal all mines without solving the rest of the board. Also check the flag counter afterwards, which currently keeps its old value even though the flags are gone.
- Test 15 - Uncover every safe cell. is_won should be True and the status "Victory". Repeat with one safe cell left (no win yet), with no flags placed, and with the last cells uncovered by a cascade.
    - Reason: This covers the win condition, including the early-win risk and the win check inside the recursive path.
## Submission Requirements
- Test 16 - Check the final commit timestamp on master is before the due date, and that master contains all four modules and the documentation with complete headers.
    - Reason: Code freeze is judged on that timestamp, and all code and documentation must be on master.

## Group 5 Testing:

## Sound Effects adding
- Test 1 - play the game normally, purposefully placing flags, winning, losing, and going through all game states to see if configured sound effects all are reached
    - Reason: Check if all sound effects work and are mapped to appropriate action

## UI Development
- Test 2 - check each game mode and AI level to ensure they all highlight when selected. Play the game normally after each on to ensure that no game logic was altered by UI code changes. This was implemented before AI logic or game modes were added, so none of that should be changed yet.
    - Reason: Ensure that no changes were accidentally made to game logic and that the UI is independently added (for now)