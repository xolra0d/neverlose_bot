"""
               GLWT(Good Luck With That) Public License
                 Copyright (c) Everyone, except Author

Everyone is permitted to copy, distribute, modify, merge, sell, publish,
sublicense or whatever they want with this software but at their OWN RISK.

                            Preamble

The author has absolutely no clue what the code in this project does.
It might just work or not, there is no third option.


                GOOD LUCK WITH THAT PUBLIC LICENSE
   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION, AND MODIFICATION

  0. You just DO WHATEVER YOU WANT TO as long as you NEVER LEAVE A
TRACE TO TRACK THE AUTHOR of the original product to blame for or hold
responsible.

IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

Good luck and Godspeed.
"""

"""
Module src/games/nim.py implements the Nim game logic for the Telegram bot.


Overview:

This module uses an asynchronous, object-oriented design to implement all of the Nim game mechanics. 
It operates using the `Game` interface.

Nim is a mathematical game where players take turns removing objects from piles. 
The player who takes the last object wins.


Dependencies:

    `__future__.annotations`
      Import hints before their class definitions.

    `typing`
    - Import typing for various function inputs/outputs.

    `dataclasses`
    - Import @dataclass(frozen=True) for defining immutable game classes.

    `random`
    - Import random for moves when optimal move cannot be found.

    `games.game.Game`
    - Import base class which provide common structure for all games.

    `typing_extensions.override`
    - Import `@override` decorator for marking overridden methods.


Architectural idea:

    `Move` dataclass:
    Represents a single move: removing a given number of stones from a specific pile.

    `NimState` dataclass:
    Represents the immutable game state (tuple of piles).

    `Nim` class:
    Implements all core game logic according to the `Game` interface.


Gameplay Summary:
    1. Game starts with predefined piles `(1, 3, 5, 7)`.
    2. Players alternate removing 1 or more stones from a single pile.
    3. The player making the last move wins.
    4. Bot uses **Nim-sum (XOR strategy)** for optimal moves.
"""

from __future__ import annotations
from typing import List, Optional, Tuple
from dataclasses import dataclass
import random
from .game import Game
from typing_extensions import override

# Dataclass representing a player's move.
# Each move removes 'remove' stones from pile index 'pile'.
@dataclass(frozen=True)
class Move:
    pile: int
    remove: int


    def __str__(self) -> str:
        """Return human-readable representation of a move.
        Example: "1 3" means remove 3 stones from pile #1.
        """
        return f"{self.pile} {self.remove}"


# Dataclass representing immutable game state of Nim.
# `piles` stores the number of stones in each pile.
# The class provides a helper to create a new state after a move.
@dataclass(frozen=True)
class NimState:
    piles: Tuple[int, ...]


    def remove_stones(self, pile: int, remove: int) -> NimState:
        """
        Return a new immutable state after removing stones from a given pile.

        Args:
            pile: Index of the pile to remove stones from.
            remove: Number of stones to remove.

        Raises:
            ValueError: If pile index or remove count is invalid.

        Returns:
            NimState: New immutable state with updated pile sizes.

        """
        if not (0 <= pile < len(self.piles)):
            raise ValueError("Invalid pile index")
        if not (1 <= remove <= self.piles[pile]):
            raise ValueError("Invalid remove count")

        # Convert tuple -> list -> modify -> tuple again
        new_piles = list(self.piles)
        new_piles[pile] -= remove
        return NimState(tuple(new_piles))


# Main Nim game logic implementing the abstract Game interface.
class Nim(Game):
    def __init__(self):
        # Total number of piles in the game.
        self.piles_size = 4


    # Returns official game name.
    @override
    async def name(self) -> str:
        """Return the game's display name."""
        return "Nim"


    # Returns a short description for the /start game list.
    @override
    async def description(self) -> str:
        """Return a short textual description of the game."""
        return "Remove stones from piles. Last move wins."


    # Defines the initial starting state of the Nim game.
    @override
    async def initial_state(self) -> NimState:
        """Return the initial configuration of piles."""
        return NimState((1, 3, 5, 7))


    # Generates all legal moves from a given state.
    @override
    async def get_legal_moves(self, state: NimState) -> List[Move]:
        """
        Generate all valid moves for the current state.

        Args:
            state: Current NimState.

        Returns:
            List[Move]: All valid moves.

        Example:
            For piles (1, 3, 5, 7), returns 1+3+5+7 = 16 total moves.
        """
        moves: List[Move] = []
        for i, count in enumerate(state.piles):
            for remove in range(1, count + 1):
                moves.append(Move(i, remove))
        return moves


    # Parse a string input into a Move object.
    @override
    async def parse_move(self, move_str: str) -> Optional[Move]:
        """
        Convert user's text input into a valid Move.

        Input format: "<pile_index> <stones_to_remove>"

        Returns:
            Move if valid, None otherwise.
        """
        try:
            parts = move_str.strip().split()
            if len(parts) != 2:
                return None

            pile, remove = int(parts[0]), int(parts[1])
            if 0 <= pile < self.piles_size and remove > 0:
                return Move(pile, remove)
        except ValueError:
            # Handle non-integer inputs gracefully.
            pass
        return None


    # Apply a move and return new game state.
    @override
    async def add_move(self, state: NimState, move: Move) -> NimState:
        """Return a new state after applying the move."""
        return state.remove_stones(move.pile, move.remove)


    # Generate optimal move using XOR (Nim-sum) strategy.
    @override
    async def generate_best_move(self, state: NimState) -> Move:
        """
        Compute the bot's best move using the Nim-sum algorithm.

        Algorithm:
            - Compute XOR of all pile sizes.
            - If result == 0 -> losing position -> choose random move.
            - Otherwise -> find a pile that can be reduced to make Nim-sum = 0.
        """
        nim_sum = 0
        for pile in state.piles:
            nim_sum ^= pile  # XOR of all piles

        # If nim_sum == 0, no winning move -> pick random move
        if nim_sum == 0:
            return random.choice(await self.get_legal_moves(state))

        # Otherwise, find move to force nim_sum to 0
        for i, pile in enumerate(state.piles):
            target = pile ^ nim_sum
            if target < pile:
                return Move(i, pile - target)

        # random move
        return random.choice(await self.get_legal_moves(state))


    # Check if game reached terminal (end) state.
    @override
    async def is_terminal(self, state: NimState) -> bool:
        """Return True if all piles are empty (game over)."""
        return all(pile == 0 for pile in state.piles)


    # Determine the winner.
    @override
    async def get_winner(self, state: NimState) -> Optional[int]:
        """
        Determine winner of the current state.

        Returns:
            - None -> game not over
            - -1 -> bot wins (last move by bot)
            - 1 -> player wins (not used in this logic since bot moves last)
        """
        if not await self.is_terminal(state):
            return None
        return -1  # Last move (bot) wins


    # Format game state into readable string with stone symbols.
    @override
    async def format_state(self, state: NimState) -> str:
        """
        Return a human-readable board visualization.

        Example output:
            Pile 0: ● (1)
            Pile 1: ●●● (3)
            Pile 2: ●●●●● (5)
            Pile 3: ●●●●●●● (7)
        """
        return "\n".join(
            f"Pile {i}: {'●' * pile} ({pile})"
            for i, pile in enumerate(state.piles)
        )