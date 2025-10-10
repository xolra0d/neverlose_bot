from random import choice
from typing import cast
from .game import Game

from dataclasses import dataclass
from enum import Enum
from typing_extensions import override


DETERMINISTIC = False


class XO(Enum):
    X = 1
    O = 2

    @override
    def __str__(self) -> str:
        """
        Get a single-character emoji representing the player.
        
        Returns:
            str: "❌" for XO.X, "⭕" for XO.O, "?" for any other value.
        """
        if self == XO.X:
            return "❌"
        elif self == XO.O:
            return "⭕"
        else:
            return "?"

    @override
    def __repr__(self) -> str:
        """
        Provide the canonical one-character representation for this XO enum value.
        
        Returns:
            str: "X" if the value is XO.X, "O" if the value is XO.O, "?" for any other/unknown value.
        """
        if self == XO.X:
            return "X"
        elif self == XO.O:
            return "O"
        else:
            return "?"


@dataclass(frozen=True)
class Draw:
    pass


TypeField = tuple[
    XO | None,
    XO | None,
    XO | None,
    XO | None,
    XO | None,
    XO | None,
    XO | None,
    XO | None,
    XO | None,
]


@dataclass(frozen=True)
class TicTacToeState:
    field: TypeField
    turn: XO

    @override
    def __repr__(self) -> str:
        """
        Provide a concise debug representation of the TicTacToeState.
        
        @returns:
            A string of the form "State(<cells>, <turn>)" where <cells> is a 9-character sequence using '.' for empty cells and '❌' or '⭕' for occupied cells, and <turn> is the current player (`XO`).
        """
        return f"State({ ''.join('.' if x is None else str(x) for x in self.field )}, {self.turn})"


_win_patterns = [
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
]


class TicTacToe(Game):
    @override
    async def name(self) -> str:
        """
        Provide the canonical name of the game.
        
        Returns:
            The canonical game name "tictactoe".
        """
        return "tictactoe"

    @override
    async def description(self) -> str:
        """
        Human-readable description of the Tic-Tac-Toe game's rules and objective.
        
        Describes turn-taking, placing X and O on a 3x3 board, the win condition of three symbols in a row, and that the game is a draw if the board fills without a winner.
        
        Returns:
            str: A description of the game's rules and objective.
        """
        return "A clasic notebook game. Players take turn placing Xs and Os. First player to place 3 in a line wins."

    @override
    async def initial_state(self) -> TicTacToeState:
        """
        Create the initial Tic-Tac-Toe state with an empty 3×3 board and X to move.
        
        Returns:
            TicTacToeState: State with all nine cells set to None (empty) and `turn` set to `XO.X`.
        """
        return TicTacToeState(
            field=cast(TypeField, tuple(None for _ in range(9))),
            turn=XO.X,
        )

    @override
    async def get_legal_moves(self, state: TicTacToeState) -> list[int]:
        """
        List available empty cell indices for the given game state.
        
        Parameters:
            state (TicTacToeState): Current board state; cells are indexed 0 (top-left) through 8 (bottom-right).
        
        Returns:
            list[int]: Integers in the range 0–8 corresponding to empty cells where a move can be made.
        """
        _check_state_invariants(state)

        res: list[int] = []
        for i in range(9):
            if state.field[i] is None:
                res.append(i)
        return res

    @override
    async def add_move(self, state: TicTacToeState, move: int) -> TicTacToeState:
        """
        Produce a new TicTacToeState with the given move applied and the turn switched.
        
        Parameters:
            state (TicTacToeState): Current game state (not modified).
            move (int): Index 0–8 of an empty cell to place the current player's mark.
        
        Returns:
            TicTacToeState: New state with the specified cell set to the current player and `turn` set to the opposing player.
        """
        _check_state_invariants(state)
        assert (
            isinstance(move, int) and 0 <= move < 9
        ), "tictactoe: invariant failed: invalid move"
        assert (
            state.field[move] is None
        ), "tictactoe: invariant failed: move overrides occupied cell"

        field = list(state.field)
        field[move] = state.turn
        return TicTacToeState(
            field=cast(TypeField, tuple(field)),
            turn=_other(state.turn),
        )

    @override
    async def generate_best_move(self, state: TicTacToeState) -> int:
        """
        Select an optimal move index for the current player from the given non-terminal state.
        
        Chooses among moves that lead to the best eventual outcome as determined by the game's memoized evaluation. When multiple optimal moves exist, tie-breaking is deterministic if the global DETERMINISTIC flag is set (using a state-derived hash), otherwise a random choice is made.
        
        Parameters:
            state (TicTacToeState): Current game state; must be a non-terminal, valid Tic-Tac-Toe state.
        
        Returns:
            int: Chosen cell index in the range 0–8.
        
        Raises:
            AssertionError: If the state fails invariants or is terminal.
        """
        _check_state_invariants(state)
        assert (
            _get_winner(state.field) is None
        ), "tictactoe: invariant failed: requesting best move on a terminal position"

        target = _compute_memo(state)
        options: list[int] = []
        for i in range(9):
            if state.field[i] is not None:
                continue
            f = list(state.field)
            f[i] = state.turn
            next = TicTacToeState(
                field=cast(TypeField, tuple(f)),
                turn=_other(state.turn),
            )
            if _compute_memo(next) == target:
                options.append(i)

        if DETERMINISTIC:
            # Hash may truncate to system word with. To keep things fully portable, we truncate ourselves.
            # 2 bytes is more then enough
            idx = (hash(state) & 0xFFFF) % len(options)
            return options[idx]
        else:
            return choice(options)

    @override
    async def is_terminal(self, state: TicTacToeState) -> bool:
        """
        Return whether the given game state is terminal.
        
        Returns:
            `true` if the state is terminal (a win or a draw), `false` otherwise.
        """
        _check_state_invariants(state)
        return _get_winner(state.field) is not None

    @override
    async def get_winner(self, state: TicTacToeState) -> int | None:
        """
        Determine the numeric winner for a terminal TicTacToeState.
        
        Returns:
            1 if X wins, -1 if O wins, 0 if the position is a draw, `None` if the state is not terminal.
        """
        if (res := _get_winner(state.field)) == XO.X:
            return 1
        elif res == XO.O:
            return -1
        elif res == Draw():
            return 0
        else:
            return None

    @override
    async def format_state(self, state: TicTacToeState) -> str:
        """
        Render the TicTacToeState as a human-readable 3x3 board.
        
        Returns:
        	formatted (str): Three lines with three space-separated tokens each; occupied cells show the player's symbol, empty cells show the cell index.
        """
        _check_state_invariants(state)
        return "\n".join(
            (
                " ".join(
                    " " + str(i) if state.field[i] is None else str(state.field[i])
                    for i in range(j * 3, (j + 1) * 3)
                )
            )
            for j in range(3)
        )

    @override
    async def parse_move(self, move_str: str) -> int | None:
        """
        Convert a user-provided string into a board index (0–8).
        
        Parameters:
        	move_str (str): The input string to parse as an integer board cell index.
        
        Returns:
        	int | None: The parsed index (0 through 8) if valid, `None` otherwise.
        """
        try:
            res = int(move_str)
        except ValueError:
            return None

        if not (0 <= res < 9):
            return None
        return res


def _check_state_invariants(state: TicTacToeState) -> None:
    """
    Validate invariants of a TicTacToeState and raise an AssertionError if any invariant is violated.
    
    Checks performed:
    - `state` is an instance of `TicTacToeState`.
    - `state.field` has length 9.
    - every element of `state.field` is either an `XO` or `None`.
    - `state.turn` is an `XO`.
    
    Parameters:
        state (TicTacToeState): The game state to validate.
    
    Raises:
        AssertionError: If any invariant fails; messages start with "tictactoe: invariant failed: ..." to indicate the specific violation.
    """
    assert isinstance(
        state, TicTacToeState
    ), "tictactoe: invariant failed: state is not of type TicTacToeState"
    assert len(state.field) == 9, "tictactoe: invariant failed: invalid field size"
    assert all(
        isinstance(x, XO) or x is None for x in state.field
    ), "tictactoe: invariant failed: field contains invalid elements"
    assert isinstance(
        state.turn, XO
    ), "tictactoe: invariant failed: current turn is not X or O"


def _other(xo: XO) -> XO:
    """
    Return the opposing XO player for the given player.
    
    Parameters:
        xo (XO): The current player.
    
    Returns:
        XO: `XO.O` if `xo` is `XO.X`, `XO.X` otherwise.
    """
    if xo == XO.X:
        return XO.O
    else:
        return XO.X


def _get_winner(field: TypeField) -> XO | Draw | None:
    """
    Determine the terminal outcome for a Tic-Tac-Toe board.
    
    Parameters:
        field (TypeField): 9-cell board tuple where each element is an XO or None.
    
    Returns:
        XO | Draw | None: `XO` (X or O) if that player has three in a row, `Draw()` if the board is full with no winner, or `None` if the game is not yet decided.
    """
    for pat in _win_patterns:
        if (
            field[pat[0]] is not None
            and field[pat[0]] == field[pat[1]]
            and field[pat[1]] == field[pat[2]]
        ):
            return field[pat[0]]

    if all(x is not None for x in field):
        return Draw()
    return None


_winner_memo: dict[TicTacToeState, XO | Draw] = {}


def _compute_memo(s: TicTacToeState) -> XO | Draw:
    """
    Determine the eventual terminal outcome reachable from the given TicTacToe state assuming optimal play.
    
    Parameters:
        s (TicTacToeState): The current game state to evaluate.
    
    Returns:
        XO | Draw: `XO` if that player can force a win from the state, `Draw()` if optimal play leads to a draw, or the opposing `XO` if the opponent can force a win.
    """
    _check_state_invariants(s)

    global _winner_memo
    if s in _winner_memo:
        return _winner_memo[s]

    if (winner := _get_winner(s.field)) is not None:
        _winner_memo[s] = winner
        return winner

    foundDraw = False
    foundWin = False
    for move in range(9):
        if s.field[move] is not None:
            continue

        field = list(s.field)
        field[move] = s.turn
        next = TicTacToeState(
            field=cast(TypeField, tuple(field)),
            turn=_other(s.turn),
        )
        res = _compute_memo(next)
        foundDraw = foundDraw or res == Draw()
        foundWin = foundWin or res == s.turn

    if foundWin:
        _winner_memo[s] = s.turn
    elif foundDraw:
        _winner_memo[s] = Draw()
    else:
        _winner_memo[s] = _other(s.turn)

    return _winner_memo[s]