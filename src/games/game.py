from abc import ABC, abstractmethod
import typing as tp


class Game(ABC):
    @abstractmethod
    async def name(self) -> str:
        """Returns name of the game"""
        pass

    @abstractmethod
    async def description(self) -> str:
        """Returns description of the game"""
        pass

    @abstractmethod
    async def initial_state(self) -> tp.Any:
        """Returns starting state"""
        pass

    @abstractmethod
    async def get_legal_moves(self, state: tp.Any) -> tp.List[tp.Any]:
        """Returns list of valid moves from this position"""
        pass

    @abstractmethod
    async def add_move(self, state: tp.Any, move: tp.Any) -> tp.Any:
        """Returns new position after making move"""
        pass

    @abstractmethod
    async def generate_best_move(self, state: tp.Any) -> tp.Any:
        """Returns best move from this position"""
        pass

    @abstractmethod
    async def is_terminal(self, state: tp.Any) -> bool:
        """Check if game is over"""
        pass

    @abstractmethod
    async def get_winner(self, state: tp.Any) -> tp.Optional[int]:
        """
        Returns winner for terminal positions.
        Returns: 1 (player wins (must be impossible)), -1 (bot wins), 0 (draw)
        Returns None if not terminal.
        """
        pass

    @abstractmethod
    async def format_state(self, state: tp.Any) -> str:
        """Format game state for display to user"""
        pass

    @abstractmethod
    async def parse_move(self, move_str: str) -> tp.Optional[tp.Any]:
        """
        Parse user input into a move.
        Returns None if input is invalid.
        """
        pass
