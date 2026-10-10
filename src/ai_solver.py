"""
ai_solver.py

This module defines the AI agents used to make legal MineSweeper moves.

The solver is layered by difficulty:
- EasyAI: falls back to a random valid move.
- MediumAI: applies the standard single-cell logic used in Minesweeper.
- HardAI: extends MediumAI with additional pattern-based deductions.

The AI does not directly manipulate the board for its own sake; instead, it
creates Move objects describing a legal action (reveal or flag) and then hands
those moves to the GameManager through the public API.

Created on 2026-09-29
Author: Jamareon Davis
"""

import random
from collections import namedtuple

import board_manager

# The Move record stores the action type and target cell, plus a human-readable
# reason so debugging and tests can explain why the AI chose a move.
Move = namedtuple("Move", ["action", "row", "col", "reason"])


class EasyAI:
    """
    Easy difficulty is intentionally simple: it picks a random covered, unflagged
    cell and reveals it. This class also serves as the base behavior for all
    other AI agents because the subclasses only override the deduction step.

    The important design rule is that every move must still be legal when it is
    applied. A hidden cell is only valid if it is covered and not flagged, which
    prevents the AI from drifting out of sync with the board state.
    """

    name = "Easy"

    def __init__(self, game, seed=None):
        """Store the game instance and initialize deterministic random behavior."""
        self.game = game
        self.rng = random.Random(seed)  # A seed keeps tests reproducible.
        self._queue = []  # Moves deduced earlier but not yet consumed.

    def _is_revealed(self, row, col):
        """Return True when the cell has already been revealed by the game."""
        return not self.game.board.is_covered(row, col)

    def _is_unknown(self, row, col):
        """
        Return True only for a cell that is still hidden and not flagged.

        This is the core safety check for the AI. If the solver ever produced a
        move for a flagged or already-revealed square, the mine count and flag
        tracking would be out of sync with the board state.
        """
        return (self.game.board.is_covered(row, col)
                and not self.game.board.is_flagged(row, col))

    def _unknown_cells(self):
        """List every legal candidate cell the AI is allowed to act on."""
        size = board_manager.BOARD_SIZE
        return [(r, c) for r in range(size) for c in range(size)
                if self._is_unknown(r, c)]

    @staticmethod
    def label(row, col):
        """Convert a board coordinate to a user-facing label such as A1 or J10."""
        return f"{chr(ord('A') + col)}{row + 1}"

    def _deduce(self):
        """Return a list of justified, rule-based moves. EasyAI deduces none."""
        return []

    def _random_move(self):
        """Choose a legal random move from the remaining hidden cells."""
        cells = self._unknown_cells()
        if not cells:
            return None
        row, col = self.rng.choice(cells)
        return Move("reveal", row, col, f"random pick: {self.label(row, col)}")

    def _still_valid(self, move):
        """Check whether a queued move is still legal after earlier actions."""
        return self._is_unknown(move.row, move.col)

    def next_move(self):
        """
        Compute the next move, but do not apply it yet.

        This method keeps a queue of recently deduced moves so earlier decisions
        stay consistent if the board changes during the same turn cycle. If a
        queued move is no longer valid, it is discarded before the solver acts.
        """
        if self.game.is_won or self.game.is_lost:
            return None

        # If a previously deduced move is still valid, play it before generating
        # anything new. This preserves a deterministic ordering of actions.
        while self._queue:
            move = self._queue.pop(0)
            if self._still_valid(move):
                return move

        # Generate a fresh batch of deduced moves, then filter out duplicates and
        # stale moves created by earlier board changes.
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

    def apply(self, move):
        """
        Apply a Move using the game's public API.

        The game logic expects a move to be similar to the behavior of the user
        input handlers: reveal cells or place flags, but never mutate the board
        without checking the board state first.
        """
        if move is None:
            return
        if move.action == "flag":
            self.game.flag_cell(move.row, move.col)
            return
        # The first reveal must seed the mine placement. Once mines are set, the
        # board no longer needs to be generated at reveal time.
        if not self.game.are_mines_populated:
            self.game.populate_mines(move.row, move.col)
        self.game.reveal_cell(move.row, move.col)

    def step(self):
        """Play exactly one turn and return the Move that was executed."""
        move = self.next_move()
        self.apply(move)
        return move

    def solve(self, max_steps=5000):
        """
        Continue making moves until the game ends or the step limit is reached.

        Returns a status string: "won", "lost", or "stalled". The solver uses an
        upper bound to avoid infinite loops if the game state becomes inconsistent.
        """
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
    Medium difficulty applies the standard Minesweeper deduction rules.

    Rule 1: if the number of hidden neighbors equals the cell's number,
            every hidden neighbor must be a mine and is flagged.
    Rule 2: if the number of flagged neighbors equals the cell's number,
            every other hidden neighbor must be safe and is revealed.

    These rules are applied to every revealed square and are strong enough to
    solve many boards without resorting to random guessing.
    """

    name = "Medium"

    def _cell_view(self, row, col):
        """
        Build a compact view of a revealed cell's neighborhood.

        Returns: (adjacent_mines, hidden, flagged, unknown)
        where hidden is every covered neighbor, flagged is the subset already
        marked, and unknown is the subset still available to act on.
        """
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
        """Apply the single-cell Minesweeper constraint rules to produce moves."""
        moves = []
        size = board_manager.BOARD_SIZE
        for row in range(size):
            for col in range(size):
                if not self._is_revealed(row, col):
                    continue

                number, hidden, flagged, unknown = self._cell_view(row, col)
                if not unknown:
                    continue  # This cell has no actionable hidden neighbors.

                if len(hidden) == number:
                    # Every hidden neighbor must be a mine.
                    reason = (f"rule 1: {self.label(row, col)} shows {number} "
                              f"with {len(hidden)} hidden neighbor(s)")
                    moves += [Move("flag", r, c, reason) for r, c in unknown]
                elif len(flagged) == number:
                    # The flagged neighbors already satisfy the mine count.
                    reason = (f"rule 2: {self.label(row, col)} shows {number} "
                              f"with {len(flagged)} flag(s) placed")
                    moves += [Move("reveal", r, c, reason) for r, c in unknown]

        return moves


class HardAI(MediumAI):
    """
    Hard difficulty extends the medium solver with an additional pattern-based
    heuristic.

    This class is currently a placeholder for the larger pattern engine, but the
    intended behavior is to preserve the MediumAI rules first and then look for
    more advanced geometric patterns such as the 1-2-1 arrangement along a row
    or column. Those pattern deductions can reduce randomness and improve solve
    performance on complex boards.
    """

    name = "Hard"


def make_ai(game, level="easy", seed=None):
    """Factory method that creates the requested AI difficulty."""
    return {"easy": EasyAI, "medium": MediumAI, "hard": HardAI}[level.lower()](game, seed=seed)
