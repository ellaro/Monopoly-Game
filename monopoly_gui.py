# monopoly_gui.py
# Requires: pip install PyQt6

import sys
import random
from monopoly_model import PropertyTile
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
from monopoly_model import Game


# --------------------------------------------------
# Helper: positions for 40 tiles around square board
# --------------------------------------------------
def build_tile_positions(board_px=660, margin=20):
    usable = board_px - 2 * margin
    tile = usable / 10
    pos = []

    # TOP (11 tiles)
    for i in range(11):
        pos.append(QPointF(margin + i * tile, margin))

    # RIGHT (9 tiles, without corners)
    for i in range(1, 10):
        pos.append(QPointF(margin + 10 * tile, margin + i * tile))

    # BOTTOM (11 tiles)
    for i in range(10, -1, -1):
        pos.append(QPointF(margin + i * tile, margin + 10 * tile))

    # LEFT (9 tiles, without corners)
    for i in range(9, 0, -1):
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

        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        print("tiles:", len(self.main_window.board.tiles))
        print("positions:", len(self.tile_positions))

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
        self.properties = []


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
        self.game = Game(self.players, self.board)

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
        if step < len(path):
            tile = path[step]
            self.place_token(token, tile, idx)
            token.current_tile = tile

            QTimer.singleShot(
                200,
                lambda: self._animate_path(token, player, path, idx, step + 1)
            )
            return

        player.position = token.current_tile

        tile = self.board.tiles[player.position]
        tile.on_land(player, self.game)

        if isinstance(self.game.pending_property, PropertyTile):
            dlg = PropertyCardDialog(self.game.pending_property, player)
            dlg.exec()
            self.game.pending_property = None

        self.update_status()
        self.roll_btn.setEnabled(True)


class PropertyCardDialog(QtWidgets.QDialog):
    def __init__(self, property_tile, player):
        super().__init__()
        self.tile = property_tile
        self.player = player

        self.setWindowTitle(property_tile.name)
        self.setFixedSize(300, 400)

        layout = QVBoxLayout(self)

        # Color bar
        color_bar = QLabel()
        color_bar.setFixedHeight(40)
        color_bar.setStyleSheet(f"background-color: {property_tile.color}")
        layout.addWidget(color_bar)

        # Title
        title = QLabel(property_tile.name)
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Price
        layout.addWidget(QLabel(f"Price: ${property_tile.price}"))

        # Rent table
        layout.addWidget(QLabel("Rent:"))
        for i, rent in enumerate(property_tile.rents):
            if i == 5:
                text = f"With Hotel: ${rent}"
            else:
                text = f"With {i} house(s): ${rent}"
            layout.addWidget(QLabel(text))

        # Buttons
        btn_layout = QHBoxLayout()
        buy_btn = QPushButton("Buy")
        cancel_btn = QPushButton("Cancel")

        buy_btn.clicked.connect(self.buy)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(buy_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def buy(self):
        if self.tile.buy(self.player):
            pass
        self.accept()


# Add this to your monopoly_gui.py

# New widget to show player properties
class PropertyPanel(QWidget):
    def __init__(self, players):
        super().__init__()
        self.players = players

        layout = QVBoxLayout(self)

        title = QLabel("🏠 Properties Owned")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title)

        self.property_labels = []
        for player in players:
            player_label = QLabel(f"\n{player.name}:")
            player_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            player_label.setStyleSheet(f"color: {player.color.name()};")
            layout.addWidget(player_label)

            props_label = QLabel("No properties yet")
            props_label.setWordWrap(True)
            props_label.setStyleSheet("margin-left: 10px;")
            layout.addWidget(props_label)

            self.property_labels.append((player, props_label))

        layout.addStretch()

    def update_properties(self):
        for player, label in self.property_labels:
            if not player.properties:
                label.setText("No properties yet")
            else:
                prop_list = []
                for prop in player.properties:
                    houses_info = ""
                    if hasattr(prop, 'hotel') and prop.hotel:
                        houses_info = " 🏨"
                    elif hasattr(prop, 'houses') and prop.houses > 0:
                        houses_info = f" {'🏠' * prop.houses}"
                    prop_list.append(f"• {prop.name}{houses_info}")
                label.setText("\n".join(prop_list))

        # Update your MainWindow.__init__() method
        # Add this after creating the side layout and before self.status:

        # Property panel
        self.property_panel = PropertyPanel(self.players)
        side.addWidget(self.property_panel)

        self.status = QLabel("")
        side.addWidget(self.status)
        side.addStretch()

    # Update your MainWindow.update_status() method to also update properties:

    def update_status(self):
        lines = []
        for p in self.players:
            tile = self.board.tiles[p.position].name
            lines.append(f"{p.name}: ${p.money} ({tile})")
        self.status.setText("\n".join(lines))

        # Update property panel
        self.property_panel.update_properties()

    # Also update the property panel after buying in PropertyCardDialog.buy():

    def buy(self):
        if self.tile.buy(self.player):
            # Update the property panel in the main window
            # You'll need to pass main_window reference or use signals
            pass
        self.accept()

# --------------------------------------------------
# Run
# --------------------------------------------------
def main():
    print("APP START")
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
