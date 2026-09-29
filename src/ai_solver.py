"""
 ai_solver.py

Class: EasyAI - Uncovers a uniformly random covered, unflagged cell

Class: MediumAI -Applies the two single-cell constraint rules, falling back to random

Class Name: HardAI - Extension point for the Medium rules plus the 1-2-1 pattern

Inputs:  A GameManager instance (game_logic.py)
Outputs: Move records describing each turn, applied through GameManager's public API
"""

import random
from collections import namedtuple

import board_manager

#"reveal" or "flag"
Move = namedtuple("Move", ["action", "row", "col", "reason"])


class EasyAI:
    """
    Easy difficulty picka a uniformly random cell that is still covered and
    unflagged, and uncover it, Also the base class for the other difficulties. Subclasses override
    _deduce(); the random pick stays as the fallback when no rule fires.
    """

    name = "Easy"

    def __init__(self, game, seed=None):
        self.game = game
        self.rng = random.Random(seed)  # seeded so test runs are reproducible
        self._queue = []                # moves deduced but not yet played

    #  board

    def _is_revealed(self, row, col):
        return not self.game.board.is_covered(row, col)

    def _is_unknown(self, row, col):
        """Covered and unflagged: a cell the AI is still allowed to act on.  GameManager.flag_cell does not prive  arguments,  every move
        this solver gives must satisfy this predicate or the flag counter and
        mine_count will drift out of sync with the board.
        """
        return (self.game.board.is_covered(row, col)
                and not self.game.board.is_flagged(row, col))

    def _unknown_cells(self):
        size = board_manager.BOARD_SIZE
        return [(r, c) for r in range(size) for c in range(size)
                if self._is_unknown(r, c)]

    @staticmethod
    def label(row, col):
        """A1-J10 label matching the UI"""
        return f"{chr(ord('A') + col)}{row + 1}"

    # move generation 

    def _deduce(self):
        """Return justified Moves. Easy deduces nothing."""
        return []

    def _random_move(self):
        cells = self._unknown_cells()
        if not cells:
            return None
        row, col = self.rng.choice(cells)
        return Move("reveal", row, col, f"random pick: {self.label(row, col)}")

    def _still_valid(self, move):
        """A queued move can be invalidated by an earlier move in the same batch"""
        return self._is_unknown(move.row, move.col)

    def next_move(self):
        """Work out the next move without playing it. None if nothing to do."""
        if self.game.is_won or self.game.is_lost:
            return None

        # Remove previously deduced moves, discarding any now stale.
        while self._queue:
            move = self._queue.pop(0)
            if self._still_valid(move):
                return move

        # fresh batch, filtering and de-duplicating it.
        seen, batch = set(), []
        for move in self._deduce():
            key = (move.action, move.row, move.col)
            if key not in seen and self._still_valid(move):
                seen.add(key)
                batch.append(move)

        if batch:
            self._queue = batch[1:]
            return batch[0]

        return self._random_move()

    #  move application 

    def apply(self, move):
        """Play a Move through GameManager, mirroring InputHandler.handle_click."""
        if move is None:
            return
        if move.action == "flag":
            self.game.flag_cell(move.row, move.col)
            return
        # reveal_cell does not seed the board; the caller must do it first
        if not self.game.are_mines_populated:
            self.game.populate_mines(move.row, move.col)
        self.game.reveal_cell(move.row, move.col)

    def step(self):
        """Take exactly one turn. Returns the Move played, or None."""
        move = self.next_move()
        self.apply(move)
        return move

    def solve(self, max_steps=5000):
        """Play to completion. Returns 'won', 'lost', or 'stalled'."""
        for _ in range(max_steps):
            if self.game.is_won:
                return "won"
            if self.game.is_lost:
                return "lost"
            if self.step() is None:
                return "stalled"
        return "stalled"


class MediumAI(EasyAI):
    """
    Medium difficulty: two single-cell constraint rules, then random fallback.

      Rule 1 (all mines): hidden neighbors == the cell's number, so every
                          unflagged hidden neighbor is a mine. Flag them.
      Rule 2 (all safe):  flagged neighbors == the cell's number, so every
                          other hidden neighbor is safe. Reveal them.

    "hidden" counts flagged cells, per the spec. Moves are only  for
    cells that are covered and unflagged, a rule that is already satisfied
    produces nothing.
    """

    name = "Medium"

    def _cell_view(self, row, col):
        """(number, hidden, flagged, unknown) for one revealed cell."""
        hidden, flagged, unknown = [], [], []
        for n_row, n_col in self.game.board.neighbors(row, col):
            if self._is_revealed(n_row, n_col):
                continue
            hidden.append((n_row, n_col))
            if self.game.board.is_flagged(n_row, n_col):
                flagged.append((n_row, n_col))
            else:
                unknown.append((n_row, n_col))
        return self.game.board.adjacent_mines(row, col), hidden, flagged, unknown

    def _deduce(self):
        moves = []
        size = board_manager.BOARD_SIZE
        for row in range(size):
            for col in range(size):
                if not self._is_revealed(row, col):
                    continue

                number, hidden, flagged, unknown = self._cell_view(row, col)
                if not unknown:
                    continue  # nothing actionable left around this cell

                if len(hidden) == number:
                    reason = (f"rule 1: {self.label(row, col)} shows {number} "
                              f"with {len(hidden)} hidden neighbor(s)")
                    moves += [Move("flag", r, c, reason) for r, c in unknown]
                elif len(flagged) == number:
                    reason = (f"rule 2: {self.label(row, col)} shows {number} "
                              f"with {len(flagged)} flag(s) placed")
                    moves += [Move("reveal", r, c, reason) for r, c in unknown]

        return moves


class HardAI(MediumAI):
    """
    Hard difficulty: the Medium rules plus 1-2-1 pattern.

   override _deduce() to call super()._deduce() first and, only
    if that comes back empty, scan each row and column for three side byside
    revealed cells reading 1-2-1 and eit flags on the outer hidden neighbors
    and a reveal on the inner one.
    """

    name = "Hard"


def make_ai(game, level="easy", seed=None):
    """Factory. level is 'easy', 'medium', or 'hard'."""
    return {"easy": EasyAI, "medium": MediumAI, "hard": HardAI}[level.lower()](game, seed=seed)
