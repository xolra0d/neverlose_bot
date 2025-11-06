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
Module `src/games/game.py` provides interface implementation.
---
It utilizes two external libraries, specifically:

    1. `abc`, which provides the infrastructure for defining abstract base 
        classes. Link: https://en.wikipedia.org/wiki/Abstract_type
        in Python3, as described in PEP 3119. 
        Link: https://docs.python.org/3/library/abc.html
        
        a. `abstractmethod` is a useful function decorator. Link: https://en.wikipedia.org/wiki/Decorator_pattern
            which requires all classes which inherit from this one to implement abstracted method.
            
            For example:
            ```
            class Abstract(ABC):
                @abstractmethod
                def to_be_implemented():
                    pass
            
            class Implementation(Abstract):
                @override
                def to_be_implemented():
                    print("yay")

            my_class = Abstract()
            my_class.to_be_implemented() # <- returns TypeError: Can't instantiate abstract class Abstract without an implementation for abstract method 'to_be_implemented'
            
            my_implemented_class = Implementation()
            my_implemented_class.to_be_implemented() # <- prints "yay"
            ```
            
        b. `abc.ABC` is a helper base class, which provides `abstract` functionality, meaning that every 
            abstracted (`@abstractmethod`, `@abstractstaticmethod`, `@abstractclassmethod`) should be implemented.

    2. `typing` with an alias (`as tp`) to hint types of input variables and output types for functions. 
        Link: https://docs.python.org/3/library/typing.html

        Used types in this file are:
            a. `tp.Any`
            b. `tp.Optional[T]`
---
`Game` class main purpose is to act like an adaptor pattern between main Telegram bot logic described in
`src/main.py` and games described in `src/games/`. Game is complete, when it implements all interface (`Game`) methods.

By default each method inside an interface is asynchronous, to be async-compatible, if it is used in one of the game implementations.

Typical usage example (GameNameState and Move should be implemented by the game):
```
from .game import Game
from typing_extensions import override

class GameName(Game):
    @override
    async def name(self) -> str:
        return "Game name"
    
    @override
    async def description(self) -> str:
        return "Game name description"

    @override
    async def initial_state(self) -> GameNameState:
        return GameNameState()

    @override
    async def get_legal_moves(self, state: GameNameState) -> list[Move]:
        return state.get_legal_moves()
    
    @override
    async def add_move(self, state: GameNameState, move: Move) -> GameNameState:
        return state.add_move(move)

    @override
    async def generate_best_move(self, state: GameNameState) -> Move:
        return state.generate_best_move()
    
    @override
    async def is_terminal(self, state: GameNameState) -> bool:
        return state.is_terminal()

    @override
    async def get_winner(self, state: GameNameState) -> tp.Optional[int]:
        return state.get_winner()

    @override
    async def format_state(self, state: GameNameState) -> str:
        return state.format()

    @override
    async def parse_move(self, move_str: str) -> tp.Optional[Move]:
        return Move.try_parse(move_str)
```
"""

from abc import ABC, abstractmethod
import typing as tp

# Base abstract class for each game to inherit. 
# More precisely, it's an interface, as it is stateless. Unfortunately, Python3 does not provide interface logic.
class Game(ABC):
    """
    Base abstract class for each game to inherit.
    Game implementation is complete, when all `@abstractmethod` methods are implemented.
    """

    @abstractmethod # Mark method as required to implement.
    async def name(self) -> str:
        """
        Returns name of the game. 

        Name should:
            1. Be a valid alpha numeric string. 
            2. Be at least 2 characters long.
            3. Be at max 64 characters long.
            4. Not contain profanity. If game name is not translatable 
and contains profanity (in english language), please explain in PR.

        Returns:
            str: game name in a string format.
        """
        pass

    @abstractmethod # Mark method as required to implement.
    async def description(self) -> str:
        """
        Returns description of the game.

        Description should:
            1. Be a valid alpha numeric string with possible punctuation.
            2. Be at least 2 characters long.
            3. Be at max 256 characters long.
            4. Not contain profanity.

        Returns:
            str: game description in a string format.
        """
        pass

    @abstractmethod # Mark method as required to implement.
    async def initial_state(self) -> tp.Any:
        """
        Initiates and returns starting state. 

        Return type is of `tp.Any`, as each `Game` implementation will have its own state type.

        Returns:
            tp.Any: game initial state.
        """
        pass

    @abstractmethod # Mark method as required to implement.
    async def get_legal_moves(self, state: tp.Any) -> list[tp.Any]:
        """
        Returns list of valid moves from this position. 

        `state` type is of `tp.Any`, as each `Game` implementation will have its own state type.
        Output type is of `list[tp.Any]`, as each `Game` implementation will have its own move type.

        Args:
            state: current state of the game.

        Returns:
            list[tp.Any]: list of all legal moves.
        """
        pass

    @abstractmethod # Mark method as required to implement.
    async def add_move(self, state: tp.Any, move: tp.Any) -> tp.Any:
        """
        Returns new position after making move.

        `state` type is of `tp.Any`, as each `Game` implementation will have its own state type.
        `move` type is of `tp.Any`, as each `Game` implementation will have its own move type.
        Output type is of `tp.Any`, as each `Game` implementation will have its own state type.

        Args:
            state: current state of the game.
            move: move to add to the state.

        Returns:
            tp.Any: new state with added move.
        """
        pass

    @abstractmethod # Mark method as required to implement.
    async def generate_best_move(self, state: tp.Any) -> tp.Any:
        """
        Returns best move from this position.

        `state` type is of `tp.Any`, as each `Game` implementation will have its own state type.
        Output type is of `tp.Any`, as each `Game` implementation will have its own move type.

        Args:
            state: current state of the game.

        Returns:
            tp.Any: best move generated.
        """
        pass

    @abstractmethod # Mark method as required to implement.
    async def is_terminal(self, state: tp.Any) -> bool:
        """
        Returns result of check if game is over.

        `state` type is of `tp.Any`, as each `Game` implementation will have its own state type.
        Game state is said to be terminal when either:
            1. No move is possible.
            2. One of players is a winner.

        Args:
            state: current state of the game.

        Returns:
            bool: boolean value of current state status.
        """
        pass

    @abstractmethod # Mark method as required to implement.
    async def get_winner(self, state: tp.Any) -> tp.Optional[int]:
        """
        Returns winner for terminal position.

        `state` type is of `tp.Any`, as each `Game` implementation will have its own state type.
        Output is optional and could be None if state is not terminal.

        Args:
            state: current state of the game.

        Returns:
            tp.Optional[int]: winner for state. Allowed values:
                1. Return 1, if player has won.
                2. Return -1, if bot has won.
                3. Return 0, if it is draw.
                4. Return None, if state is not terminal.

        """
        pass

    @abstractmethod # Mark method as required to implement.
    async def format_state(self, state: tp.Any) -> str:
        """
        Format game state for display to user.

        `state` type is of `tp.Any`, as each `Game` implementation will have its own state type.

        Args:
            state: current state of the game.

        Returns:
            str: state formatted as a string for user.
        """
        pass

    @abstractmethod # Mark method as required to implement.
    async def parse_move(self, move_str: str) -> tp.Optional[tp.Any]:
        """
        Parse user input into a move.

        Output is optional and could be None if `move_str` is not a valid move.
        Output inner is of `tp.Any`, as each `Game` implementation will have its own move type.

        Args:
            move_str: input user move in str format.

        Returns:
            tp.Optional[tp.Any]: move type. Could be None, if move is invalid.
        """
        pass
 
