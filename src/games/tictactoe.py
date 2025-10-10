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
        if self == XO.X:
            return "❌"
        elif self == XO.O:
            return "⭕"
        else:
            return "?"

    @override
    def __repr__(self) -> str:
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
        """Returns name of the game"""
        return "tictactoe"

    @override
    async def description(self) -> str:
        """Returns description of the game"""
        return "A classic notebook game. Players take turns placing Xs and Os. First to place 3 in a line wins."

    @override
    async def initial_state(self) -> TicTacToeState:
        """Returns starting state"""
        return TicTacToeState(
            field=cast(TypeField, tuple(None for _ in range(9))),
            turn=XO.X,
        )

    @override
    async def get_legal_moves(self, state: TicTacToeState) -> list[int]:
        """Returns list of valid moves from this position"""
        _check_state_invariants(state)

        res: list[int] = []
        for i in range(9):
            if state.field[i] is None:
                res.append(i)
        return res

    @override
    async def add_move(self, state: TicTacToeState, move: int) -> TicTacToeState:
        """Returns new position after making move"""
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
        """Returns best move from this position"""
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
        """Check if game is over"""
        _check_state_invariants(state)
        return _get_winner(state.field) is not None

    @override
    async def get_winner(self, state: TicTacToeState) -> int | None:
        """
        Returns winner for terminal positions.
        Returns: 1 (player wins (must be impossible)), -1 (bot wins), 0 (draw)
        Returns None if not terminal.
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
        """Format game state for display to user"""
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
        Parse user input into a move.
        Returns None if input is invalid.
        """
        try:
            res = int(move_str)
        except ValueError:
            return None

        if not (0 <= res < 9):
            return None
        return res


def _check_state_invariants(state: TicTacToeState) -> None:
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
    if xo == XO.X:
        return XO.O
    else:
        return XO.X


def _get_winner(field: TypeField) -> XO | Draw | None:
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
