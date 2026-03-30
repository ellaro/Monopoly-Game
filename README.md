# Monopoly Game

## Overview
Monopoly is a classic board game where players buy, sell, and trade properties, aiming to bankrupt their opponents. This repository hosts a digital implementation of the Monopoly game.

## Features
- Multiplayer support
- AI opponents
- Property trading and auctioning
- Chance and Community Chest cards
- Dice rolling mechanics
- Player statistics tracking

## Setup
To set up the project, clone the repository:
```bash
git clone https://github.com/ellaro/Monopoly-Game.git
cd Monopoly-Game
```

### Requirements
- Python 3.x
- Required packages can be installed via:
```bash
pip install -r requirements.txt
```

## How to Run
To start the game, run:
```bash
python main.py
```

## How to Play
1. Each player rolls the dice to start.
2. Move around the board based on dice rolls.
3. Buy or trade properties.
4. Draw cards from Chance and Community Chest.
5. Manage your finances wisely to win.

## Controls
- Roll Dice: Press the "Roll Dice" button.
- Trade: Access the trade menu from your player dashboard.
- End Turn: Press the "End Turn" button.

## Project Structure
```
Monopoly-Game/
│
├── main.py          # Main entry point for the game
├── game_logic/      # Contains game logic and mechanics
│   ├── board.py     # Board representation
│   ├── player.py    # Player class and methods
│   └── properties.py # Property logic
├── assets/          # Game assets (images, sounds)
├── tests/           # Unit tests for the game
└── README.md        # Project documentation
```

## Development Notes
- Follow PEP 8 for code styling.
- Use meaningful commit messages.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request with any changes or improvements you wish to make.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.