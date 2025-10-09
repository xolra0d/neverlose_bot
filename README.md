Neverlose Telegram Bot
---
Bot that will never lose to you, no matter how hard you try.
---
## Add a game:
1. Create a dir `src/games/<game_name>`.
2. Game should inherit from `Game` class in `src/games/game.py` and implement every abstract method.
3. After game is written, add game object (e.g., `Nim()`) to the `GAMES_TO_PLAY` list in `src/main.py`.
4. Be happy.
