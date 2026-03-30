# Monopoly Game (PyQt6)

## Overview
A desktop GUI implementation of **Monopoly**, built in **Python** using **PyQt6**. The game renders a board UI, handles dice rolls, player movement, property tiles, and core turn-based gameplay.

## Tech Stack
- **Python 3**
- **PyQt6** (GUI)
- Custom game model classes (e.g., `monopoly_model.py`, `PropertyTile`, etc.)

## Features
- Graphical board rendered with Qt graphics (`QGraphicsScene`, `QGraphicsView`, items, brushes/pens/fonts)
- Dice rolling and turn flow
- Player tokens and movement
- Property tiles modeled in code (e.g., `PropertyTile`)
- Dialogs / prompts via Qt widgets (`QMessageBox`, buttons, labels)

> Feature completeness depends on what’s currently implemented in the repo (trading, houses/hotels, AI, etc.).

## Requirements
- Python **3.10+** recommended
- PyQt6

## Installation

### 1) Clone the repository
```bash
git clone https://github.com/ellaro/Monopoly-Game.git
cd Monopoly-Game
```

### 2) (Recommended) Create a virtual environment
**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell)**
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3) Install dependencies
If you have a `requirements.txt`:
```bash
pip install -r requirements.txt
```

If you *don’t* have one yet, install PyQt6 directly:
```bash
pip install PyQt6
```

## Running the Game
Run the main entry point (adjust the filename if your entry script is named differently):
```bash
python main.py
```

## Controls / UI
Typical UI actions include:
- **Roll Dice** button to advance gameplay
- **End Turn** / next player progression
- Property prompts / notifications shown via dialogs (`QMessageBox`)

(Exact controls depend on the current UI implementation.)

## Project Structure (typical)
This is a *suggested* structure based on the imports you shared:

```
Monopoly-Game/
├── main.py                  # App entry point (PyQt6 window + game loop)
├── monopoly_model.py        # Game model (e.g., PropertyTile, board data, rules)
├── assets/                  # Images / icons / sounds (if any)
├── tests/                   # Unit tests (if any)
├── requirements.txt         # Dependencies (recommended)
└── README.md
```

## Development Notes
- UI layer uses Qt Graphics Framework (`QGraphicsScene`, `QGraphicsItem` subclasses, etc.)
- Keep game rules/data separated from UI where possible (model vs. view/controller)

## Contributing
Contributions are welcome:
1. Fork the repo
2. Create a feature branch (`git checkout -b feature/my-change`)
3. Commit changes
4. Open a pull request

## License
Add a `LICENSE` file (MIT/Apache-2.0/etc.) or specify the license here.
