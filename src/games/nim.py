from .game import Game
import typing as tp
import random

class Nim(Game):
    def __init__(self):
        self.piles_size = 4

    async def name(self) -> str:
        return "Nim"

    async def description(self) -> str:
        return "Remove stones from piles. Last move wins."

    async def initial_state(self) -> tp.List[int]:
        return [1, 3, 5, 7]

    async def get_legal_moves(self, state: tp.List[int]) -> tp.List[str]:
        moves = []
        for i, count in enumerate(state):
            for remove in range(1, count + 1):
                moves.append(f"{i} {remove}")
        return moves

    async def parse_move(self, move_str: str) -> tp.Optional[str]:
        try:
            parts = move_str.strip().split()
            if len(parts) != 2:
                return None
            pile, remove = int(parts[0]), int(parts[1])
            if 0 <= pile < self.piles_size and remove > 0:
                return f"{pile} {remove}"
        except Exception:
            pass
        return None

    async def add_move(self, state: tp.List[int], move: str) -> tp.List[int]:
        pile_str, remove_str = move.split()
        pile, remove = int(pile_str), int(remove_str)
        new_state = state.copy()
        if 0 <= pile < self.piles_size and 1 <= remove <= new_state[pile]:
            new_state[pile] -= remove
        return new_state

    async def generate_best_move(self, state: tp.List[int]) -> str:
        nim_sum = 0
        for pile in state:
            nim_sum ^= pile

        if nim_sum == 0:
            legal_moves = await self.get_legal_moves(state)
            return random.choice(legal_moves)

        for i, pile in enumerate(state):
            target = pile ^ nim_sum
            if target < pile:
                return f"{i} {pile - target}"

        return random.choice(await self.get_legal_moves(state))

    async def is_terminal(self, state: tp.List[int]) -> bool:
        return all(pile == 0 for pile in state)

    async def get_winner(self, state: tp.List[int]) -> tp.Optional[int]:
        if not await self.is_terminal(state):
            return None
        return -1  

    async def format_state(self, state: tp.List[int]) -> str:
        return "\n".join([f"Pile {i}: {'●' * pile} ({pile})" for i, pile in enumerate(state)])