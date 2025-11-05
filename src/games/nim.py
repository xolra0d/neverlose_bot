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