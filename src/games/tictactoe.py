"""
                 公共许可证
         版权所有© 除作者外他妈的所有人

任何人都被允许复制、分发、修改、合并、销售、出版、再授权
或其他任何行为，但后果自负


                    前言

作者完全不知道这个项目的代码到底他妈的做了什么。
代码处于可用或不可用状态，没有第三种可能。


           祝你好运公共许可证
      复制、分发和修改的条款与条件

  0. 只要你永远别他妈留下任何能追踪到原作者的线索，
你他妈想做什么就做什么，不能因此责怪原作者或追究
原作者的责任。

在任何情况下，作者均不对因使用或与本软件有关的合同诉讼、
侵权或其他方式产生的任何索赔、损害或其他责任负责。

你他妈自求多福吧。
"""

"""
Module tictactoe provides an implementation of tictactoe as a PvE minigame.
Tic Tac Toe is played on a 3x3 square grid consisting of 9 cells.
Cells are initially empty.
There are 2 players, X (cross) and O (circle).
Current turn alternates between 2 players, starting with X.
During a turn, player must place their respective symbol into a free cell.
If all cells are filled, that is none are empty, a draw is declared.
It can be proven that a game of Tic Tac Toe will last at most 9 turns.
If at any point a win condition is met, respective player is declared the winner.

Win condition is as follows: there are 8 patterns each consisting of 3 spaces.
If a player has filled all cells in a pattern with their respective symbol, they win.
It can be proven that win condition may only hold for one player if other rules are followed.

List of patterns.
@ (at) represents a cell that is part of the pattern.
. (dot) represents a cell that is not part of the pattern.

1. Top horizontal
    @ @ @
    . . .
    . . .

2. Middle horizontal
    . . .
    @ @ @
    . . .

3. Bottom horizontal
    . . .
    . . .
    @ @ @

4. Left vertical
    @ . .
    @ . .
    @ . .

5. Middle vertical
    . @ .
    . @ .
    . @ .

6. Right vertical
    . . @
    . . @
    . . @

7. Top left diagonal
    @ . .
    . @ .
    . . @

8. Top right diagonal
    . . @
    . @ .
    @ . .

The underlying engine supports all states of the fields,
even those not reachable through valid play.
The engine may also predict winning move for either player.
Version that is accessible through the Telegram bot only allows
human player to go first (cross or X) and computer to respond (circle or O).

It can be proven, that a tie may be forced for both players.

The following code assumes a board to be laid out in an 9 element array or tuple.
Here is a diagram showing indices corresponding to cells:
    0 1 2
    3 4 5
    6 7 8
"""

from random import choice  # Required only if DETERMINISTIC is False
from typing import cast
from dataclasses import dataclass
from enum import Enum
from typing_extensions import override

from .game import Game


# DETERMINISTIC determines whether bot algorithm acts deterministically,
# that is the same move will be picked for each state.
DETERMINISTIC = False


# Class XO represents either an X or an O.
# repr(XO) is printable and guaranteed to be ASCII.
# str(XO) is human-printable but may contain multibyte unicode characters.
class XO(Enum):
    """
    Class XO represents either an X or an O.
    repr(XO) is printable and guaranteed to be ASCII.
    str(XO) is human-printable but may contain multibyte unicode characters.
    """

    X = 1  # X represents a cross. This is the opposite of a circle.

    O = 2  # O represents a circle. This is the opposite of a cross.

    # __str__ provides a human readable representation of an XO.
    # This representation is used when printing the game board.
    # Returns ❌ for a cross, ⭕ for a circle and ? in other cases.
    @override  # Mark that a virtual method is overridden.
    def __str__(self) -> str:
        if self == XO.X:  # Check if receiver is a cross.
            return "❌"  # Return a unicode codepoint for a cross.
        elif self == XO.O:  # Check if receiver is a circle.
            return "⭕"  # Return a unicode codepoint for a circle.
        else:  # Receiver is not a cross nor a circle.
            return "?"  # Return a placeholder.

    # __repr__ provides an ASCII human readable representation for an XO.
    # It is guaranteed to return string consisting only of ASCII runes
    # or unicode codepoints less than 128.
    # Returns X for a cross, O for a circle and ? in other cases.
    @override  # Mark that a virtual method is overridden.
    def __repr__(self) -> str:
        if self == XO.X:  # Check if receiver is a cross.
            return "X"  # Return an uppercase x.
        elif self == XO.O:  # Check if receiver is a circle.
            return "O"  # Return an uppercase o, not to be confused with 0.
        else:  # Receiver is not a cross and is not a circle.
            return "?"  # Return a placeholder codepoint.


# Draw is unit type. A unit type is a type that only has a single valid value.
# In this case, the single valid value of Draw is spelled Draw().
# Draw is hashable.
@dataclass(frozen=True)
class Draw:
    """
    Draw is unit type. A unit type is a type that only has a single valid value.
    In this case, the single valid value of Draw is spelled Draw().
    Draw is hashable.
    """


# TypeField is a type alias for a field.
# It consists of a 9-tuple that is homogeneous.
# Each element is of type XO | None.
# Value of XO.X represents that X (cross) is placed in the cell.
# Value of XO.O represents that O (circle) is placed in the cell.
# Value of None represents an empty cell.
TypeField = tuple[
    XO | None,  # Index 0, upper left cell.
    XO | None,  # Index 1, upper central cell.
    XO | None,  # Index 2, upper right cell.
    XO | None,  # Index 3, middle left cell.
    XO | None,  # Index 4, central cell.
    XO | None,  # Index 5, middle right cell.
    XO | None,  # Index 6, bottom left cell.
    XO | None,  # Index 7, bottom central cell.
    XO | None,  # Index 8, bottom right cell.
]


# Class TicTacToeState represents full state of a Tic Tac Toe game.
# TicTacToe may represent unreachable states,
# but all representable states are valid to use in the Engine.
# TicTacToeState is hashable.
@dataclass(frozen=True)
class TicTacToeState:
    """
    Class TicTacToeState represents full state of a Tic Tac Toe game.
    TicTacToe may represent unreachable states,
    but all representable states are valid to use in the Engine.
    TicTacToeState is hashable.
    """

    field: TypeField  # Current state of the field.
    turn: XO  # Current turn. XO.X - cross (player 1) to move, XO.O - circle (player 2) to move.

    # __repr__ provides a human-readable representation of a field.
    # The following holds: (x == y) <=> (repr(x) == repr(y))
    # for all x, y that are valid TicTacToeState's.
    # This representation is only useful for debugging and must not leak to end user.
    @override  # Mark that a virtual method is overridden.
    def __repr__(self) -> str:
        # This statement is equivalent to the following pseudocode:
        # result = ε (empty string)
        # for each cell c of self.field:
        #   if c is X: append "X" to the result
        #   if c is O: append "O" to the result
        #   if c is empty: append "." to the result
        # if self.turn is X: let turn be "X"
        # if self.turn is O: let turn be "O"
        # Resulting string is the concatenation of the following strings:
        #   - "State("
        #   - field
        #   - ", "
        #   - turn
        #   ")"
        return f"State({''.join('.' if x is None else str(x) for x in self.field )}, {self.turn})"


# _win_patterns is an array of win condition patterns.
# It is guaranteed to be 8 elements long.
# It must not be modified.
# Each pattern is represented as a homogeneous 3-int-tuple.
# Each element of the tuple represents a unique index of the pattern.
_win_patterns = [
    (0, 1, 2),  # Top row.
    (3, 4, 5),  # Middle row.
    (6, 7, 8),  # Bottom row.
    (0, 3, 6),  # Left column.
    (1, 4, 7),  # Middle column.
    (2, 5, 8),  # Right column.
    (0, 4, 8),  # Top left diagonal.
    (2, 4, 6),  # Top right diagonal.
]


# TicTacToe is an implementation of a Game for a game of TicTacToe.
class TicTacToe(Game):
    """
    TicTacToe is an implementation of a Game for a game of TicTacToe.
    """

    @override  # Mark that a virtual method is overridden.
    async def name(self) -> str:
        """
        Returns name of the game.
        Always returns string "tictactoe"
        Time complexity: O(1)
        """
        return "tictactoe"

    @override  # Mark that a virtual method is overridden.
    async def description(self) -> str:
        """
        Returns a short description of Tic Tac Toe.
        For a comprehensive description of the rules, see module level documentation.
        String is guaranteed to be constant between invocations.
        String is not guaranteed to be constant between different versions of the library.
        Time complexity: O(1)
        """
        return (
            "A classic notebook game. "
            "Players take turns placing Xs and Os. "
            "First to place 3 in a line wins."
        )

    @override  # Mark that a virtual method is overridden.
    async def initial_state(self) -> TicTacToeState:
        """
        Returns starting state.
        Starting state is empty field (None, None, None, None, None, None, None, None, None)
        with X (cross, player 1) to move.
        Time complexity: O(1)
        """
        return TicTacToeState(
            # Equivalent to (None, None, None, None, None, None, None, None, None)
            field=cast(TypeField, tuple(None for _ in range(9))),
            # X to move.
            turn=XO.X,
        )

    @override  # Mark that a virtual method is overridden.
    async def get_legal_moves(self, state: TicTacToeState) -> list[int]:
        """
        Returns list of valid moves from the provided position.
        This function is not aware of win conditions.
        It can be proven that this function may return at most 9 elements.
        Returned list is guaranteed to contain integers in range [0; 8].
        Returned list is guaranteed to be sorted in strictly ascending order.
        Time complexity: O(1)
        """

        _check_state_invariants(state)  # Verify that state is valid.

        res: list[int] = []  # Accumulator for the result.
        for i in range(9):  # For each cell. range(9) will iterate from 0 to 8.
            if state.field[i] is None:  # Cell i is empty.
                res.append(i)  # Add it to the accumulator
        return res  # Return the accumulated result.

    @override  # Mark that a virtual method is overridden.
    async def add_move(self, state: TicTacToeState, move: int) -> TicTacToeState:
        """
        Performs a state transition.
        Provided move must have been returned by get_legal_moves,
        otherwise an exception will be raised.
        Time complexity: O(1)
        """
        _check_state_invariants(state)  # Verify that provided state is valid.
        assert (  # Verify that move is in bounds.
            isinstance(move, int) and 0 <= move < 9
        ), "tictactoe: invariant failed: invalid move"
        assert (  # Verify that replaced cell is empty.
            state.field[move] is None
        ), "tictactoe: invariant failed: move overrides occupied cell"

        # Copy the state.
        # Tuples are immutable so a list has to be used.
        field = list(state.field)

        field[move] = state.turn  # Make the move.

        return TicTacToeState(
            # Static analyzers may miss that tuple(field) is of type TypeField,
            # so an explicit cast is required.
            field=cast(TypeField, tuple(field)),
            # Flip the turn. This makes player alternate.
            turn=_other(state.turn),
        )

    @override  # Mark that a virtual method is overridden.
    async def generate_best_move(self, state: TicTacToeState) -> int:
        """
        Returns one of optimal moves in the state.
        If at least one valid move is possible, return index of the cell that should be filled.
        If no moves are possible, returns None.
        Note that first query computes the whole game tree,
        but subsequent results may be cached for performance.
        This cache may leak memory, but the game tree is not that large.
        (at most 6000 for normal gameplay)
        Time complexity: O(1)
        """
        _check_state_invariants(state)  # Verify that state is valid.
        assert (  # Verify that position is not terminal.
            _get_winner(state.field) is None
        ), "tictactoe: invariant failed: requesting best move on a terminal position"

        # General description of the algorithm:
        # 1. Determine whether position is winning, losing or a draw.
        # 2. Collect all possible moves that lead to the best possible outcome.
        # 3. Select some move from the list depending on value of DETERMINISTIC.

        # Determine winner of the position.
        # This is the most expensive part of the function,
        # but will be cached on subsequent calls.
        target = _compute_memo(state)

        options: list[int] = []  # Accumulator for best possible moves.
        for i in range(9):  # range(9) iterates integers from 0 to 8.
            if state.field[i] is not None:  # Current cell is occupied.
                continue  # We can only make moves in empty cells, so this option is not valid.

            # Make a move and determine the next state.

            f = list(state.field)  # List instead of tuple for modification.
            f[i] = state.turn  # Override cell number i.
            next_state = TicTacToeState(  # Construct a new state.
                field=cast(
                    TypeField, tuple(f)
                ),  # Static analyzers are not smart enough to determine that this is fine.
                turn=_other(state.turn),  # Don't forget to flip the turn!
            )

            # This call is guaranteed to not recurse, because it is already cached.
            # Check that result is what we are searching for.
            if _compute_memo(next_state) == target:
                options.append(i)  # Remember it for later.

        # Due to the position not being terminal, at least one move is possible.
        # Because of this, len(options) >= 1.

        if DETERMINISTIC:
            # Here, a pseudo-random value is generated based on the current state.
            # It does not have to be cryptographically secure or even unpredictable,
            # so the built-in hash will do.
            # Hash may truncate to system word width. To keep things portable to 32 bit,
            # we truncate it ourselves.
            # 2 bytes is more than enough for our use case, given that len(options) is at most 9.
            # Expression of the form A % B yields a value in interval [0; B-1]
            # (for non-negative integers A and B)
            # Because of this, options[idx] will never access out of bounds.
            idx = (hash(state) & 0xFFFF) % len(options)
            return options[idx]
        else:
            return choice(options)  # Select a random value from options.

    @override  # Mark that a virtual method is overridden.
    async def is_terminal(self, state: TicTacToeState) -> bool:
        """
        Check if game is over.
        If any empty cells still remain, returns true.
        Semantically equivalent to len(get_legal_moves()) > 0 but more efficient.
        Time complexity: O(1)
        """
        _check_state_invariants(state)  # Check that provided state is valid.

        # This expression will yield True for the following cases:
        #  - XO.X (X, player 1, human won)
        #  - XO.O (O, player 2, computer won)
        #  - Draw() (game ended in a draw)
        # and False for the following:
        #  - None (winner is not determined yet)
        return _get_winner(state.field) is not None

    @override  # Mark that a virtual method is overridden.
    async def get_winner(self, state: TicTacToeState) -> int | None:
        """
        Returns winner for terminal positions.
        If the human won, returns 1. This is impossible through normal gameplay.
        If the computer won, returns -1.
        If game ended in a draw, returns 0.
        If more moves are possible, returns None.
        Time complexity: O(1)
        """

        # Uses walrus operator (:=) for more compact and clean notation.
        # Walrus operator (:=) is semantically equivalent to the following:
        #
        # lhs = None
        # def walrus(rhs):
        #    lhs = rhs
        #    return rhs
        #
        # lhs stands for left hand side of the walrus operator (:=).
        # rhs stands for right hand side of the walrus operator (:=).

        if (res := _get_winner(state.field)) == XO.X:  # X (cross) has won.
            return 1  # Return positive one (human won).
        elif res == XO.O:  # O (circle) has won.
            return -1  # Return negative one (computer won).
        elif res == Draw():  # Game ended in a draw.
            return 0  # Return zero (draw).
        else:  # Winner is not XO.X, XO.O or Draw(), that is game is ongoing.
            return None  # Return None.

    @override  # Mark that a virtual method is overridden.
    async def format_state(self, state: TicTacToeState) -> str:
        """
        Format game state for display to user.
        Returns a string consisting of a human-readable representation of the game board.
        Return string will be multiline and may contain unicode characters.
        Returned string should be rendered in monospace font.
        Time complexity: O(1)
        """
        _check_state_invariants(state)  # Check that provided state is valid.

        # The following list comprehension is a little terse.
        # But basically it collects each row into a string
        # and then joins the strings into a multiline string.

        # Here is equivalent pseudocode:
        # Let f(x) be a cross glyph if field[x] is an X.
        # Let f(x) be a circle glyph if field[x] is an O.
        # Let f(x) be a str(x) otherwise, padded to 2 glyphs using spaces.
        # Return concatenation of the following strings:
        #   - f(0)
        #   - " "
        #   - f(1)
        #   - " "
        #   - f(2)
        #   - "\n"
        #   - f(3)
        #   - " "
        #   - f(4)
        #   - " "
        #   - f(5)
        #   - "\n"
        #   - f(6)
        #   - " "
        #   - f(7)
        #   - " "
        #   - f(8)

        # As a result, something like this should be emitted:
        #   0  1  X
        #   3  O  5
        #   X  7  O
        # (Unicode glyphs substituted to closest ASCII)
        return "\n".join(  # Join rows
            (
                " ".join(  # Join columns of a single row
                    (
                        " " + str(i) if state.field[i] is None else str(state.field[i])
                    )  # Render a singular cell
                    for i in range(j * 3, (j + 1) * 3)
                )
            )
            for j in range(3)
        )

    @override  # Mark that a virtual method is overridden.
    async def parse_move(self, move_str: str) -> int | None:
        """
        Parse user input into a move.
        Returns None if input is invalid.
        If an int is returned, it is guaranteed to be in range [0; 8].
        Time complexity: O(n) where n is length of the input string.
        """
        try:
            res = int(move_str)  # Trying parsing an integer value.
        except ValueError:
            return None  # Provided input is not an integer.

        if (
            not 0 <= res < 9
        ):  # Check that res is element of the set {0, 1, 2, 3, 4, 5, 6, 7, 8}
            return None  # Provided value is out of range.
        return res  # Provided value is valid.


def _check_state_invariants(state: TicTacToeState) -> None:
    """
    _check_state_invariants verifies basic properties of the provided state.
    Raises an exception if anything is wrong.
    Note that this function does not verify whether state is reachable in normal gameplay.
    It only tries to offset dynamic nature of python.
    This function assumes that all instances of XO class are valid.
    Time complexity: O(1).
    """

    # Check that state is of expected type.
    assert isinstance(
        state, TicTacToeState
    ), "tictactoe: invariant failed: state is not of type TicTacToeState"

    # Check that field is exactly 9 cells (3 by 3 grid).
    assert len(state.field) == 9, "tictactoe: invariant failed: invalid field size"

    # Check that all elements are of expected types.
    assert all(
        isinstance(x, XO) or x is None for x in state.field
    ), "tictactoe: invariant failed: field contains invalid elements"

    # Check that current turn is of expected type.
    assert isinstance(
        state.turn, XO
    ), "tictactoe: invariant failed: current turn is not X or O"


def _other(xo: XO) -> XO:
    """
    _other returns complementary symbol to xo.
    For input XO.X returns XO.O.
    For input XO.O returns XO.X.
    Undefined behaviour in any other case.
    Time complexity: O(n) where n is total number of valid states of XO, for this case 2.
    """
    if xo == XO.X:  # Provided input is a cross.
        return XO.O  # Return a circle.
    else:  # Provided input is a circle.
        return XO.X  # Return a cross.


def _get_winner(field: TypeField) -> XO | Draw | None:
    """
    _get_winner checks if field is a terminal position.
    If position is terminal, returns the winner (or draw).
    No type checks are performed on the input.
    Time complexity: O(nm) where n is size of a pattern and m is amount of patterns.
    For the game of Tic Tac Toe, n = 3 and m = 8.
    """

    for pat in _win_patterns:  # Iterate all patterns.
        # Verify that a pattern matches.
        # Due to == being a transitive operator, the following holds:
        #   a == b and b == c => a == c
        # Assuming the above, this holds:
        #  (a == b and b == c => a == c) => ((a == b and b == c) <=> (a == b and a == c and b == c))
        # Because of this, we only need to compare 2 cells and the third comparison can be skipped.
        # See https://en.wikipedia.org/wiki/Transitive_relation for more info.
        if (
            field[pat[0]] is not None  # There is a symbol in first cell.
            and field[pat[0]] == field[pat[1]]  # First and second cells are the same.
            and field[pat[1]] == field[pat[2]]  # Second and third cells are the same.
        ):
            # Pattern matches. First cell is guaranteed to contain either XO.X or XO.O.
            return field[pat[0]]

    # None of the patterns matched. Game is either a draw or not finished yet.

    # Check that all cells are not empty.
    if all(x is not None for x in field):
        return Draw()  # No free cells - draw.

    return None  # At least one move is possible - non terminal.


# _winner_memo is the global memoization table for _compute_memo.
# For each TicTacToeState it stores the outcome of the state:
#   XO.X means X (cross) may force a win.
#   XO.O means O (circle) may force a win.
#   Draw() means current player may force a draw.
# This table only grows, elements are never removed.
# For normal usage, this table will stay under 6000 entries.
# Theoretically, through direct usage of _compute_memo, it may grow to 39366 entries.
_winner_memo: dict[TicTacToeState, XO | Draw] = {}


def _compute_memo(s: TicTacToeState) -> XO | Draw:
    """
    The Engine behind the game.
    For each state returns the best outcome that current player may force.
    If result == s.turn, a win is forcible.
    If result == Draw(), a draw is forcible.
    If result == _other(s.turn), any and all game paths lead to a loss.

    This function uses a global cache (_winner_memo).
    Because of this, first invocation may be slow,
    but all subsequent invocations will be memoized.

    Time complexity:
        first invocation: O(n) where n is the size of game tree that is not yet
        subsequent invocation: O(x) where x is the dictionary lookup time.
        Assumed to be close to a constant.

    Due to the fact that this is Tic Tac Toe we are talking about, the game state graph
    is tiny (n < 6000) and may be considered constant size.

    """
    _check_state_invariants(s)  # Check that provided state is valid.

    # Pylint is stupid in this case.
    # I don't care that I don't assign to this variable.
    # I want the intent of accessing a global to be explicit.
    global _winner_memo  # pylint: disable=global-variable-not-assigned

    if s in _winner_memo:  # Is state already memoized?
        return _winner_memo[s]  # It is! Return it.

    # Uses walrus operator (:=) for more compact and clean notation.
    # Walrus operator (:=) is semantically equivalent to the following:
    #
    # lhs = None
    # def walrus(rhs):
    #    lhs = rhs
    #    return rhs
    #
    # lhs stands for left hand side of the walrus operator (:=).
    # rhs stands for right hand side of the walrus operator (:=).

    if (winner := _get_winner(s.field)) is not None:  # Check if position is terminal.
        # Position is terminal!
        _winner_memo[s] = winner  # Save the result for further invocations.
        return winner  # Return the result as well.

    found_draw = False  # Stores whether a move that leads to a draw was found.
    found_win = False  # Stores whether a move that leads to a win was found.
    for move in range(9):  # Check all possible moves. range(9) iterates from 0 to 8.
        if s.field[move] is not None:  # Not a valid move, cell is already occupied.
            continue  # Skip this iteration.

        # Generate next state.
        field = list(s.field)  # List is required because tuple is immutable.
        field[move] = s.turn  # Make the actual move.
        next_state = TicTacToeState(
            field=cast(TypeField, tuple(field)),
            turn=_other(s.turn),  # Don't forget to flip the turn!
        )

        # Compute the winner of the next position.
        # Usually, such recursive memoization may lead to infinite recursion.
        # We are safe in this case, because it can be proven that TicTacToe game graph
        # is a DAG and even a Rooted Tree!
        # More info here: https://en.wikipedia.org/wiki/Directed_acyclic_graph
        #                 https://en.wikipedia.org/wiki/Tree_(graph_theory)#Rooted_tree

        # Hopefully, we will not hit the recursion stack depth limit.
        # This should not happen, because maximum length of a game of Tic Tac Toe is 9 moves.
        # And if your system cannot handle 9 stack frames, God help you.
        res = _compute_memo(next_state)

        # We found a draw if current result is a draw OR we found a draw previously.
        found_draw = found_draw or res == Draw()

        # We found a win if current result is a win OR we found a win previously.
        found_win = found_win or res == s.turn

    if found_win:  # Did we find a win?
        # We did! It can be proven that this result is optimal.
        _winner_memo[s] = s.turn  # Memoize the result.
    elif found_draw:  # Did we at least find a draw?
        # We did find a draw and no win is possible.
        # That means that optimal result is a draw.
        _winner_memo[s] = Draw()  # Memoize the result.
    else:
        # We did not find a win, did not find a draw.
        # We also know that position is not terminal.
        # That means that there exists at least one move which is neither
        # a draw nor a win.
        # We also know that none of the existing moves are wins or draws.
        # That means that all remaining moves are losses.
        _winner_memo[s] = _other(s.turn)  # Memoize the result.

    return _winner_memo[s]  # Return the memoized result.
