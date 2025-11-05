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
Module `src/main.py` provides the main entry point for the Telegram bot.
---
This module directs the entire bot functionality.

It utilizes several external libraries and internal modules:

    1. `asyncio` - asynchronous I/O library.
        Provides event loop functionality required for bot's asynchronous message handling.
        Link: https://docs.python.org/3/library/asyncio.html

        a. `asyncio.run` - used for running asynchronous bot 
           by `asyncio.run(dp.start_polling(bot))`

    2. `logging` - logging module for tracking events and debugging.
        Used to output bot activity information to stdout.
        Link: https://docs.python.org/3/library/logging.html

        a. `logging.basicConfig` to setup basic configuration for logging system.
        b. `logging.INFO` to specify logging level as INFO.

    3. `sys` - System-specific parameters and functions.
        Used to access stdout for logging output.
        Link: https://docs.python.org/3/library/sys.html

        a. `sys.stdout` to display information the stdout channel

    4. `os` - Portable operating system interfaces.
        Specifically used to retrieve the bot TOKEN from environment variable,
        for not hardcodding the token.
        Link: https://docs.python.org/3/library/os.html

        a. `os.getenv` to retrieve token variable from local environment.

    5. `typing` - with an alias (`as tp`) to hint types of input variables and output types for functions. 
        Used to specify the type of variables and function return types.
        Link: https://docs.python.org/3/library/typing.html

        Used type in this file is:
            a. `tp.Any` - any input type.

    6. `aiogram` - asynchronous Telegram bot framework.
        Link: https://docs.aiogram.dev/en/v3.22.0/

        Main components used:
            a. `Bot` - Represents a Telegram Bot instance with API methods.
            b. `Dispatcher` - Event handler manager that routes message updates to specific handlers.
            c. `DefaultBotProperties` - Configuration object for bot default settings.
            d. `ParseMode` - Enum for message parsing modes (HTML/Markdown/etc.).
            e. `CommandStart` - Filter for handling /start command.
            f. `FSMContext` - Finite State Machine context for managing user message states.
            g. `State`, `StatesGroup` - Classes for defining bot conversation states.
            h. `Message` - Represents incoming message.
            i. `KeyboardButton` - Custom keyboard button for user interface.
            j. `ReplyKeyboardMarkup` - Custom keyboard layout for user interaction.
    
    7. Internal game modules:
        a. `games.game.Game` - Abstract base interface for games.
        b. `games.tictactoe.TicTacToe` - Tic Tac Toe game implementation.
        c. `games.nim.Nim` - Nim game implementation.

---
Architectural idea:

The bot uses a Finite State Machine (FSM) pattern to manage conversation flow:
    1. `Form.choose_game` - user selects which game to play.
    2. `Form.play_game` - gameplay as whole occurs.

Message handlers are decorated with `@dp.message()` (read more at: https://en.wikipedia.org/wiki/Decorator_pattern) 
to register them with the dispatcher. Handlers are matched based on state and command filters.

Userflow:
    1. User sends `/start` message
    2. Bot displays game list and switches to `choose_game` state
    3. User selects a game from keyboard
    4. Bot initializes game state and switches to `play_game` state
    5. User makes moves, bot responds with counter-moves
    6. When game ends, winner is announced and bot returns to step 2

Global Constants:
    - GAMES_TO_PLAY: List of available game instances
    - TOKEN: Telegram bot authentication token from environment variable
    - bot: Bot instance configured with HTML parse mode
    - dp: Dispatcher instance for handling updates
"""

import asyncio
import logging
import sys
import os
import typing as tp

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)

from games.game import Game
from games.tictactoe import TicTacToe
from games.nim import Nim

# Global list of available games that users can choose from.
# To add a new game: 
#   1. Create a class implementing the Game interface in src/games/
#   2. Import it above
#   3. Add an instance to this list
GAMES_TO_PLAY: list[Game] = [
    TicTacToe(),
    Nim(),
]

# Retrieve bot token from environment variable for security.
# The TOKEN should be set in the environment before running the bot.
# For example: TOKEN=your_bot_token_here python3 src/main.py
TOKEN = os.getenv("TOKEN")

# Validate that the token was successfully retrieved.
# Raise RuntimeError to prevent bot from starting, if TOKEN is not set.
if TOKEN is None:
    raise RuntimeError('Token is not set. Use `TOKEN=your_bot_token_here python3 src/main.py`')

# Initialize Bot instance with authentication token.
# DefaultBotProperties configures the bot's default behavior:
#   - parse_mode=ParseMode.HTML: Allows HTML formatting in messages.
# read more about it: https://core.telegram.org/bots/api#formatting-options
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

# Initialize Dispatcher to handle incoming updates from Telegram.
dp = Dispatcher()


# StatesGroup defines all possible states in the conversation FSM.
# Aiogram utilizes these states to specify user state. 
class Form(StatesGroup):
    # User is selecting which game to play from the menu.
    choose_game = State()
    
    # User is actively playing a game.
    play_game = State()


# CommandStart() is a filter that matches messages starting with /start.
@dp.message(CommandStart()) # Include method into handlers.
async def start(message: Message, state: FSMContext):
    """
    Handle `/start` and display game selection menu.
    
    This is the entry point for user interaction. It:
        1. Sets FSM state to choose_game.
        2. Creates a custom keyboard with game names as buttons.
        3. Sends welcome message with game options.
    
    Args:
        message: Incoming message containing user info and message data.
        state: FSM context for managing conversation state and storing data.
    
    Returns:
        None.
    Expected time complexity: O(n) where n is number of games in GAMES_TO_PLAY
    """
    # Initiate state in choose_game state.
    await state.set_state(Form.choose_game)

    # Initialize list to hold keyboard buttons.
    keyboard = []

    # Build welcome text.
    text = f"Hi {message.from_user.first_name}! Choose a game to play:\n" # message.from_user.first_name is guranteed to exist. 

    # Iterate through all available games to build menu.
    for index, game in enumerate(GAMES_TO_PLAY, 1): # enumerate(GAMES_TO_PLAY, 1) starts counting from 1 instead of 0.
        # Retrieve game name.
        name = await game.name()
        
        # Append game info: number, name, and description.
        # Example formatted: "1. TicTacToe\nTicTacToe description"
        text += f"{index}. {name}\n{await game.description()}\n\n"

        # Create a keyboard button with the game name.
        keyboard.append(KeyboardButton(text=name,))

    # Send the constructed message to the user.
    await message.answer(
        text, # add text to the message
        reply_markup=ReplyKeyboardMarkup( # add a keyboard to the message.
            keyboard=[keyboard],  # in `aiogram``, keyboard is a list of rows
            one_time_keyboard=True,  # Keyboard disappears after user chooses game
            resize_keyboard=True,  # Keyboard resizes to fit. (shorter height)
        ),
    )


# Function used to parse user's chosen game from string.
@dp.message(Form.choose_game) # Include method into handlers.
async def choose_game(message: Message, state: FSMContext):
    """
    Parse game selection from user input.

    This function validates the user's game choice and initializes the game session:
        1. Extract game name from message text.
        2. Search for matching game in GAMES_TO_PLAY list.
            a. If invalid, resend game menu with error message.
            b. If valid,
                I. Initialize game state and transition to play_game state.
                II. Display initial game board with legal moves.

    Args:
        message: Incoming message containing user info and message data.
        state: FSM context for managing conversation state and storing data.

    Returns:
        None.
    Expected time complexity: O(n) where n is number of games
    """
    # Get game name from user's message.
    game_name = message.text
    
    # Search for the selected game in GAMES_TO_PLAY list.
    selected_game = None
    for game in GAMES_TO_PLAY:
        if await game.name() == game_name: # Compare user input with game name.
            selected_game = game # once game is found, update `selected_game`
            break  # Exit loop early once game name is found
    
    if not selected_game: # Handle when game name is invalid
        # Build erorr text.
        text = "Invalid game selection. Please choose from the list.\n"
        # Initialize list to hold keyboard buttons.
        keyboard = []
        # Iterate through all available games to build menu.
        for index, game in enumerate(GAMES_TO_PLAY, 1): # enumerate(GAMES_TO_PLAY, 1) starts counting from 1 instead of 0.
            # Retrieve game name.
            name = await game.name()
            
            # Append game info: number, name, and description.
            # Example formatted: "1. TicTacToe\nTicTacToe description"
            text += f"{index}. {name}\n{await game.description()}\n\n"

            # Create a keyboard button with the game name.
            keyboard.append(KeyboardButton(text=name,))

        # Send the constructed message to the user.
        await message.answer(
            text, # add text to the message
            reply_markup=ReplyKeyboardMarkup( # add a keyboard to the message.
                keyboard=[keyboard],  # in `aiogram``, keyboard is a list of rows
                one_time_keyboard=True,  # Keyboard disappears after user chooses game
                resize_keyboard=True,  # Keyboard resizes to fit. (shorter height)
            ),
        )
        return  # Exit function early

    # If we reach this line, we received valid game name.

    # Initialize the selected game's starting state.
    game_state = await selected_game.initial_state()
    
    # Store game instance and current state in FSM context.
    await state.update_data(game=selected_game, game_state=game_state)
    
    # Transition FSM to play_game state.
    await state.set_state(Form.play_game)
    
    # Format game state for display to user.
    state_text = await selected_game.format_state(game_state)
    
    # Get all valid moves from current position.
    legal_moves = await selected_game.get_legal_moves(game_state)
    
    # Create keyboard with all legal moves.
    # Example: [[move1], [move2], [move3], ...]
    keyboard = [[KeyboardButton(text=str(move))] for move in legal_moves]
    
    # Send message with initial board state and move options.
    await message.answer(
        f"Let's play {await selected_game.name()}!\n\n{state_text}\n\nYour move:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=keyboard,  # Each legal move
            one_time_keyboard=True,  # Keyboard will refresh after each move
            resize_keyboard=True,  # Keyboard resizes to fit. (shorter height)
        ),
    )


# Function used to play the whole game.
@dp.message(Form.play_game) # Include method into handlers.
async def play_game(message: Message, state: FSMContext):
    """
    Handle gameplay.
    
    This is the main game loop handler that:
        1. Retrieves game and state from FSM context
        2. Parses and validates user's move
        3. Adds user's move to game state
        4. Checks if game ended.
            a. If state is terminal, displays the result.
            b. If state is not terminal, generates and adds bot's move
        6. Checks if game ended.
            a. If state is terminal, displays the result
            b. If the state is not terminal, diplay the state with moves.
    Args:
        message: Incoming message containing user info and message data.
        state: FSM context for managing conversation state and storing data.
    
    Returns:
        None.
    Expected time complexity: O(n) where n depends on game move generation
    """
    # Retrieve data from FSM context.
    data = await state.get_data()
    
    # Extract game instance.
    game: Game = data["game"]
    
    # Extract game state.
    game_state = data["game_state"]

    # Get user's move as string and remove starting/ending probels.
    move_str = message.text.strip()
    
    # Parse move string into game move.
    parsed_move = await game.parse_move(move_str)
    
    # Get list of all legal moves from current position.
    legal_moves = await game.get_legal_moves(game_state)
            
    # Validate if parsed move is an actual move and is legal.
    if parsed_move is None or parsed_move not in legal_moves:
        # if we reach this line, then move is invalid.

        # Build keyboard with legal moves.
        # Example: [[move1], [move2], [move3], ...]
        keyboard = [[KeyboardButton(text=str(move))] for move in legal_moves]

        # Send error with list of legal moves.
        await message.answer(
            "Invalid move. Please try again.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=keyboard,  # Show legal moves 
                one_time_keyboard=True,  # Refresh after selection
                resize_keyboard=True,  # Keyboard resizes to fit. (shorter height)
            ),
        )
        return  # Exit early, so that we dont parse invalid for current state move
    
    # Apply user's move to the game state.
    game_state = await game.add_move(game_state, parsed_move)
    
    # Check if game ended.
    if await game.is_terminal(game_state):
        # Update stored state before showing game over screen.
        await state.update_data(game_state=game_state)
        
        # Display game result and restart game selection.
        await send_game_over(message, state, game, game_state)
        return  # Exit, game is over
    
    # Game has not ended - generating bot's response-move.
    bot_move = await game.generate_best_move(game_state)
    
    # Apply bot's move to the game state.
    game_state = await game.add_move(game_state, bot_move)
    
    # Update FSM context with new state after bot's move.
    await state.update_data(game_state=game_state)
    
    # Format current game state.
    state_text = await game.format_state(game_state)
    
    # Check if game ended after bot's move.
    if await game.is_terminal(game_state):
        # Display bot's move and final board state.
        await message.answer(f"Bot played: {bot_move}\n\n{state_text}")
        
        # Show game result.
        await send_game_over(message, state, game, game_state)
        return  # Exit, game is over
    
    # Game continues - get next legal user moves.
    legal_moves = await game.get_legal_moves(game_state)
    
    # Create keyboard with new legal user moves.
    keyboard = [[KeyboardButton(text=str(move))] for move in legal_moves]
    
    # Send response with bot's move and legal moves.
    await message.answer(
        f"Bot played: {bot_move}\n\n{state_text}\n\nYour move:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=keyboard,  # Show current legal moves
            one_time_keyboard=True,  # Refresh after each move
            resize_keyboard=True,  # Keyboard resizes to fit. (shorter height)
        ),
    )


# Handles game-overs.
async def send_game_over(message: Message, state: FSMContext, game: Game, game_state: tp.Any):
    """
    Display winner and restart game selection.
    
    This helper function is called when a terminal game state is reached.
    It:
        1. Retrieves the winner from the terminal game state.
        2. Formats appropriate message based on winner.
        3. Displays result message to user.
        4. Restarts game selection by calling start() function.
    
    Args:
        message: Incoming message containing user info and message data.
        state: FSM context for managing conversation state and storing data.
        game: Game instance.
        game_state: Terminal game state.
    
    Returns:
        None.
    Expected time complexity: O(n) for start() function
    """
    # Determine who won the game.
    winner = await game.get_winner(game_state)
    
    # Format result message based on winner.
    if winner == 1:
        # Player (user) won the game
        result_text = "You won!"
    elif winner == -1:
        # Bot won the game
        result_text = "You lost."
    elif winner == 0:
        # Draw
        result_text = "It's a draw."
    
    # Send game result message to user.
    await message.answer(result_text)
    
    # Restart game selection process.
    await start(message, state)


# Standard Python technique to check if script is run directly.
# Prevents code from executing when file is imported elsewhere.
# Link: https://docs.python.org/3/library/__main__.html
if __name__ == "__main__":
    # Configure logging to output INFO level messages to stdout.
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    # Start the bot's event loop.
    # asyncio.run() creates new event loop, runs the coroutine, and closes the loop.
    # dp.start_polling(bot) begins long-polling for updates from Telegram servers.
    # Link: https://docs.aiogram.dev/en/latest/dispatcher/index.html
    asyncio.run(dp.start_polling(bot))
