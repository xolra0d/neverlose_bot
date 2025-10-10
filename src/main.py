import asyncio
import logging
import sys
from os import getenv
from typing import Any

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

GAMES_TO_PLAY: list[Game] = [
    TicTacToe(),
]

TOKEN = getenv("TOKEN")
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


class Form(StatesGroup):
    choose_game = State()
    play_game = State()


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.choose_game)

    keyboard = []

    text = f"Hi {message.from_user.first_name}! Choose a game to play:\n"

    for index, game in enumerate(GAMES_TO_PLAY, 1):
        name = await game.name()
        text += f"{index}. {name}\n{await game.description()}\n\n"
        keyboard.append(KeyboardButton(text=name,))

    await message.answer(
        text,
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[keyboard],
            one_time_keyboard=True,
            resize_keyboard=True,
        ),
    )

@dp.message(Form.choose_game)
async def choose_game(message: Message, state: FSMContext) -> None:
    game_name = message.text
    
    selected_game = None
    for game in GAMES_TO_PLAY:
        if await game.name() == game_name:
            selected_game = game
            break
    
    if not selected_game:
        game_buttons = []
        for game in GAMES_TO_PLAY:
            game_buttons.append(KeyboardButton(text=await game.name()))
        
        await message.answer(
            "Invalid game selection. Please choose from the list.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[game_buttons],
                one_time_keyboard=True,
                resize_keyboard=True,
            ),
        )
        return
    
    game_state = await selected_game.initial_state()
    await state.update_data(game=selected_game, game_state=game_state)
    await state.set_state(Form.play_game)
    
    state_text = await selected_game.format_state(game_state)
    legal_moves = await selected_game.get_legal_moves(game_state)
    
    keyboard = [[KeyboardButton(text=str(move))] for move in legal_moves]
    
    await message.answer(
        f"Let's play {await selected_game.name()}!\n\n{state_text}\n\nYour move:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=keyboard,
            one_time_keyboard=True,
            resize_keyboard=True,
        ),
    )


@dp.message(Form.play_game)
async def play_game(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    game: Game = data["game"]
    game_state = data["game_state"]

    move_str = message.text.strip()
    parsed_move = await game.parse_move(move_str)
    
    legal_moves = await game.get_legal_moves(game_state)
    keyboard = [[KeyboardButton(text=str(move))] for move in legal_moves]
    
    if parsed_move is None:
        await message.answer(
            "Invalid move format. Please try again:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=keyboard,
                one_time_keyboard=True,
                resize_keyboard=True,
            ),
        )
        return
    
    if parsed_move not in legal_moves:
        await message.answer(
            f"Invalid move. Legal moves are: {', '.join(str(m) for m in legal_moves)}\nPlease try again:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=keyboard,
                one_time_keyboard=True,
                resize_keyboard=True,
            ),
        )
        return
    
    game_state = await game.add_move(game_state, parsed_move)
    
    if await game.is_terminal(game_state):
        await state.update_data(game_state=game_state)
        await send_game_over(message, state, game, game_state)
        return
    
    bot_move = await game.generate_best_move(game_state)
    game_state = await game.add_move(game_state, bot_move)
    
    await state.update_data(game_state=game_state)
    
    state_text = await game.format_state(game_state)
    
    if await game.is_terminal(game_state):
        await message.answer(f"Bot played: {bot_move}\n\n{state_text}")
        await send_game_over(message, state, game, game_state)
        return
    
    legal_moves = await game.get_legal_moves(game_state)
    keyboard = [[KeyboardButton(text=str(move))] for move in legal_moves]
    
    await message.answer(
        f"Bot played: {bot_move}\n\n{state_text}\n\nYour move:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=keyboard,
            one_time_keyboard=True,
            resize_keyboard=True,
        ),
    )


async def send_game_over(message: Message, state: FSMContext, game: Game, game_state: Any) -> None:
    winner = await game.get_winner(game_state)
    
    if winner == 1:
        result_text = "You won!"
    elif winner == -1:
        result_text = "You lost, kill yourself!"
    else:
        result_text = "It's a draw."
    
    await message.answer(result_text)
    await start(message, state)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(dp.start_polling(bot))
