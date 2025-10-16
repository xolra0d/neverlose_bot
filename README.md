# Neverlose Telegram Bot

A Telegram bot designed to play various games where the bot never loses.

## Requirements

- Python 3.13+
- Aiogram

## Run
1. Clone the repository:
```bash
git clone https://github.com/xolra0d/neverlose_bot.git
cd neverlose_bot
```

### Locally
Install dependencies and run:
```bash
pip install -r requirements.txt 
export BOT_TOKEN="your_bot_token_here"
python3 src/main.py
```

### Using Docker
```bash
docker build -t neverlose-bot .
docker run -e BOT_TOKEN="your_bot_token_here" neverlose-bot
```

## Adding new game

1. Create a new directory: `src/games/<game_name>`
2. Implement your game class by inheriting from `Game` class in `src/games/game.py`
3. Implement all abstract methods required by the base class
4. Add your game instance to the `GAMES_TO_PLAY` list in `src/main.py`
