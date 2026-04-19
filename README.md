# 🎲 Monopoly Desktop Game (Python, PyQt6)

## Overview
A desktop GUI implementation of **Monopoly**, built in **Python** using **PyQt6**.  
The project focuses on delivering a clear, interactive, and user-friendly gameplay experience while simplifying complex game mechanics.

---

## 🧠 Problem

Traditional Monopoly games can be complex, slow, and overwhelming for casual players.

### Goal
Create a digital version that:
- Simplifies gameplay
- Provides clear user guidance
- Maintains engagement through intuitive interaction

---

## 🚀 Solution

- Designed a turn-based system with a clear and structured flow  
- Built an interactive graphical interface using PyQt6  
- Implemented player movement, dice rolling, and property logic  
- Provided real-time user feedback through dialogs and UI prompts  
- Focused on usability and clarity over feature overload  

---

## 🧩 Features

- 🎨 Graphical board using Qt Graphics (QGraphicsScene, QGraphicsView)  
- 🎲 Dice rolling and turn-based progression  
- 👤 Player tokens and movement  
- 🏠 Property tile modeling (PropertyTile)  
- 💬 User prompts via dialogs (QMessageBox)  
- 🔄 Clear gameplay flow  

---

## 🎯 Product Thinking

This project emphasizes **user experience and usability**.

Key decisions:
- Simplified game flow to reduce cognitive load  
- Clear UI feedback to guide user actions  
- Structured turn system to avoid confusion  
- Focus on accessibility rather than full rule complexity  

---

## 🛠 Tech Stack

- Python 3  
- PyQt6  
- Custom game model classes  

---

## 📈 Future Improvements

- 🤖 AI-based opponents  
- 🌐 Online multiplayer  
- 📊 Gameplay analytics  
- ✨ Improved UX (animations, smoother transitions)  

---

## ⚙️ Installation

```bash
git clone https://github.com/ellaro/Monopoly-Game.git
cd Monopoly-Game
```

### Create virtual environment (recommended)

macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows
```bash
py -m venv .venv
.venv\Scripts\activate
```

### Install dependencies
```bash
pip install PyQt6
```

---

## ▶️ Run the Game

```bash
python main.py
```

---

## 🎮 Controls

- Roll Dice – advance gameplay  
- Turn progression between players  
- Dialog prompts guide decisions  

---

## 📂 Project Structure

```
Monopoly-Game/
├── main.py
├── monopoly_model.py
├── assets/
├── tests/
├── requirements.txt
└── README.md
```

---

## 💡 What I Learned

- Designing systems with both technical and user experience considerations  
- Structuring applications with separation of concerns (logic vs UI)  
- Translating complex rules into intuitive interactions  
- Thinking as both a developer and product builder  

---

## 🤝 Contributing

Feel free to fork, improve, and open a pull request!

---

## 📄 License

Add your preferred license (MIT / Apache 2.0 / etc.)
