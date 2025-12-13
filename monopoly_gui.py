# monopoly_gui.py
# Requires: pip install PyQt6

import sys
import random
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, QTimer, QPointF
from PyQt6.QtGui import QBrush, QColor, QPen, QFont
from PyQt6.QtWidgets import (
    QApplication, QGraphicsScene, QGraphicsView,
    QGraphicsRectItem, QGraphicsSimpleTextItem,
    QGraphicsEllipseItem, QMainWindow,
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel
)

from monopoly_model import create_us_monopoly_board


# --------------------------------------------------
# Helper: positions for 40 tiles around square board
# --------------------------------------------------
def build_tile_positions(board_px=660, margin=20):
    usable = board_px - 2 * margin
    tile = usable / 10
    pos = []

    # top
    for i in range(10):
        pos.append(QPointF(margin + i * tile, margin))

    # right
    for i in range(1, 10):
        pos.append(QPointF(margin + 9 * tile, margin + i * tile))

    # bottom
    for i in range(9, -1, -1):
        pos.append(QPointF(margin + i * tile, margin + 9 * tile))

    # left
    for i in range(8, 0, -1):
        pos.append(QPointF(margin, margin + i * tile))

    return pos, tile


# --------------------------------------------------
# Board View
# --------------------------------------------------
class BoardView(QGraphicsView):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setBackgroundBrush(QBrush(QColor("#f2efe9")))
        self.setRenderHints(QtGui.QPainter.RenderHint.Antialiasing)

        self.tile_positions, self.tile_size = build_tile_positions()
        self.draw_board()

    def draw_board(self):
        self.scene.clear()
        font = QFont("Arial", 8)
        pen = QPen(Qt.GlobalColor.black)

        for i, pos in enumerate(self.tile_positions):
            tile = self.main_window.board.tiles[i]

            rect = QGraphicsRectItem(
                pos.x(), pos.y(),
                self.tile_size, self.tile_size
            )
            rect.setPen(pen)
            rect.setBrush(QBrush(QColor("white")))
            self.scene.addItem(rect)

            text = QGraphicsSimpleTextItem(self.wrap(tile.name))
            text.setFont(font)
            text.setPos(pos.x() + 4, pos.y() + 4)
            self.scene.addItem(text)

        self.scene.setSceneRect(0, 0, 720, 720)

    @staticmethod
    def wrap(text, n=12):
        words = text.split()
        lines, cur = [], ""
        for w in words:
            if len(cur) + len(w) <= n:
                cur += " " + w
            else:
                lines.append(cur.strip())
                cur = w
        lines.append(cur.strip())
        return "\n".join(lines)


# --------------------------------------------------
# Player Token
# --------------------------------------------------
class PlayerToken(QGraphicsEllipseItem):
    def __init__(self, color):
        super().__init__(-10, -10, 20, 20)
        self.setBrush(QBrush(color))
        self.setPen(QPen(Qt.GlobalColor.black))
        self.current_tile = 0


# --------------------------------------------------
# Simple Player + Engine
# --------------------------------------------------
class SimplePlayer:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.position = 0
        self.money = 1500


class GameEngine(QtCore.QObject):
    moveSteps = QtCore.pyqtSignal(int, int)  # player_idx, steps
    diceRolled = QtCore.pyqtSignal(int, int)

    def __init__(self, players):
        super().__init__()
        self.players = players
        self.turn = 0

    def roll(self):
        d1, d2 = random.randint(1, 6), random.randint(1, 6)
        steps = d1 + d2

        self.diceRolled.emit(d1, d2)
        self.moveSteps.emit(self.turn, steps)

        self.turn = (self.turn + 1) % len(self.players)


# --------------------------------------------------
# Main Window
# --------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Monopoly – PyQt6")
        self.resize(900, 750)

        self.board = create_us_monopoly_board()

        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        self.board_view = BoardView(self)
        layout.addWidget(self.board_view, 3)

        # Right panel
        side = QVBoxLayout()
        layout.addLayout(side, 1)

        self.info = QLabel("🎲 Monopoly Game")
        side.addWidget(self.info)

        self.dice = QLabel("Dice: - -")
        self.dice.setFont(QFont("Arial", 18))
        side.addWidget(self.dice)

        self.roll_btn = QPushButton("Roll Dice")
        self.roll_btn.clicked.connect(self.roll)
        side.addWidget(self.roll_btn)

        self.status = QLabel("")
        side.addWidget(self.status)
        side.addStretch()

        # Game setup
        self.players = [
            SimplePlayer("Alice", QColor("blue")),
            SimplePlayer("Bob", QColor("red"))
        ]

        self.engine = GameEngine(self.players)
        self.engine.diceRolled.connect(self.update_dice)
        self.engine.moveSteps.connect(self.animate_player)


        self.tokens = []
        for i, p in enumerate(self.players):
            token = PlayerToken(p.color)
            self.place_token(token, 0, i)
            self.board_view.scene.addItem(token)
            self.tokens.append(token)

        self.update_status()

    def roll(self):
        self.roll_btn.setEnabled(False)
        self.engine.roll()

    def update_dice(self, d1, d2):
        self.dice.setText(f"Dice: {d1} + {d2}")

    def move_player(self, idx, pos):
        token = self.tokens[idx]
        self.place_token(token, pos, idx)
        token.current_tile = pos
        self.update_status()
        self.roll_btn.setEnabled(True)

    def place_token(self, token, tile_idx, offset):
        base = self.board_view.tile_positions[tile_idx]
        center = QPointF(
            base.x() + self.board_view.tile_size / 2,
            base.y() + self.board_view.tile_size / 2
        )
        token.setPos(center + QPointF(offset * 8, offset * 8))

    def update_status(self):
        lines = []
        for p in self.players:
            tile = self.board.tiles[p.position].name
            lines.append(f"{p.name}: ${p.money} ({tile})")
        self.status.setText("\n".join(lines))

    def animate_player(self, player_idx, steps):
        token = self.tokens[player_idx]
        player = self.players[player_idx]

        path = []
        cur = token.current_tile
        for _ in range(steps):
            cur = (cur + 1) % 40
            path.append(cur)

        self._animate_path(token, player, path, player_idx)

    def _animate_path(self, token, player, path, idx, step=0):
        if step >= len(path):
            player.position = token.current_tile
            self.update_status()
            self.roll_btn.setEnabled(True)
            return

        tile = path[step]
        self.place_token(token, tile, idx)
        token.current_tile = tile

        QTimer.singleShot(
            200,
            lambda: self._animate_path(token, player, path, idx, step + 1)
        )


# --------------------------------------------------
# Run
# --------------------------------------------------
def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
