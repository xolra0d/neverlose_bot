from __future__ import annotations
from typing import List, Optional, Tuple
from dataclasses import dataclass
import random
from .game import Game
from typing_extensions import override


@dataclass(frozen=True)
class Move:
    pile: int
    remove: int

    def __str__(self) -> str:
        return f"{self.pile} {self.remove}"


@dataclass(frozen=True)
class NimState:
    piles: Tuple[int, ...]

    def remove_stones(self, pile: int, remove: int) -> NimState:
        """Return a new immutable state after removing stones."""
        if not (0 <= pile < len(self.piles)):
            raise ValueError("Invalid pile index")
        if not (1 <= remove <= self.piles[pile]):
            raise ValueError("Invalid remove count")

        new_piles = list(self.piles)
        new_piles[pile] -= remove
        return NimState(tuple(new_piles))


class Nim(Game):
    def __init__(self):
        self.piles_size = 4

    @override
    async def name(self) -> str:
        return "Nim"

    @override
    async def description(self) -> str:
        return "Remove stones from piles. Last move wins."

    @override
    async def initial_state(self) -> NimState:
        return NimState((1, 3, 5, 7))

    @override
    async def get_legal_moves(self, state: NimState) -> List[Move]:
        moves: List[Move] = []
        for i, count in enumerate(state.piles):
            for remove in range(1, count + 1):
                moves.append(Move(i, remove))
        return moves

    @override
    async def parse_move(self, move_str: str) -> Optional[Move]:
        try:
            parts = move_str.strip().split()
            if len(parts) != 2:
                return None
            pile, remove = int(parts[0]), int(parts[1])
            if 0 <= pile < self.piles_size and remove > 0:
                return Move(pile, remove)
        except ValueError:
            pass
        return None

    @override
    async def add_move(self, state: NimState, move: Move) -> NimState:
        return state.remove_stones(move.pile, move.remove)

    @override
    async def generate_best_move(self, state: NimState) -> Move:
        nim_sum = 0
        for pile in state.piles:
            nim_sum ^= pile

        if nim_sum == 0:
            return random.choice(await self.get_legal_moves(state))

        for i, pile in enumerate(state.piles):
            target = pile ^ nim_sum
            if target < pile:
                return Move(i, pile - target)

        return random.choice(await self.get_legal_moves(state))

    @override
    async def is_terminal(self, state: NimState) -> bool:
        return all(pile == 0 for pile in state.piles)

    @override
    async def get_winner(self, state: NimState) -> Optional[int]:
        if not await self.is_terminal(state):
            return None
        return -1  

    @override
    async def format_state(self, state: NimState) -> str:
        return "\n".join(
            f"Pile {i}: {'●' * pile} ({pile})"
            for i, pile in enumerate(state.piles)
        )