# monopoly_gui.py
# Requires: pip install PyQt6

import sys
import random
import html
from monopoly_model import PropertyTile
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, QTimer, QPointF
from PyQt6.QtGui import QBrush, QColor, QPen, QFont
from PyQt6.QtWidgets import (
    QApplication, QGraphicsScene, QGraphicsView,
    QGraphicsRectItem, QGraphicsSimpleTextItem,
    QGraphicsEllipseItem, QMainWindow,
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QMessageBox
)

from monopoly_model import create_us_monopoly_board_with_cards, try_leave_jail
from monopoly_model import Game


PROPERTY_COLOR_MAP = {
    "sienna": "#8B4513",
    "lightblue": "#87CEFA",
    "pink": "#FF69B4",
    "orange": "#FFA500",
    "red": "#E53935",
    "yellow": "#FDD835",
    "green": "#43A047",
    "darkblue": "#1E3A8A",
    "blue": "#1E88E5",
}


# --------------------------------------------------
# Build House Dialog
# --------------------------------------------------
class BuildHouseDialog(QtWidgets.QDialog):
    def __init__(self, player, main_window):
        super().__init__()
        self.player = player
        self.main_window = main_window

        self.setWindowTitle("Build Houses")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # Title
        title = QLabel(f"🏠 Build Houses - {player.name}")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        # Money info
        money = QLabel(f"💰 Your money: ${player.money}")
        money.setFont(QFont("Arial", 11))
        layout.addWidget(money)

        layout.addWidget(QLabel("\nYour properties:"))

        # List of buildable properties
        from monopoly_model import PropertyTile
        buildable = []
        for p in player.properties:
            if isinstance(p, PropertyTile) and hasattr(p, 'color') and p.color:
                try:
                    if p.has_monopoly(player):
                        buildable.append(p)
                except:
                    pass

        if not buildable:
            no_monopoly = QLabel("❌ You don't have any monopolies yet!\nBuy all properties of the same color to build.")
            no_monopoly.setWordWrap(True)
            layout.addWidget(no_monopoly)
        else:
            for prop in buildable:
                self.add_property_row(layout, prop)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def add_property_row(self, layout, prop):
        row = QHBoxLayout()

        # Property info
        houses_text = ""
        if prop.hotel:
            houses_text = "🏨 Hotel"
        elif prop.houses > 0:
            houses_text = f"{'🏠' * prop.houses} ({prop.houses})"
        else:
            houses_text = "No houses"

        info = QLabel(f"{prop.name}\n{houses_text}\nCost: ${prop.house_price}")
        info.setMinimumWidth(200)
        row.addWidget(info)

        # Build button
        build_btn = QPushButton("Build 🏠")

        if prop.hotel:
            build_btn.setText("Max 🏨")
            build_btn.setEnabled(False)
        elif self.player.money < prop.house_price:
            build_btn.setEnabled(False)
            build_btn.setText(f"Need ${prop.house_price}")
        elif not prop.can_build_evenly(self.player):
            build_btn.setEnabled(False)
            build_btn.setText("Build evenly")

        build_btn.clicked.connect(lambda: self.build_on_property(prop))
        row.addWidget(build_btn)

        layout.addLayout(row)

    def build_on_property(self, prop):
        if prop.build_house(self.player):
            self.main_window.update_status()
            self.main_window.board_view.draw_board()
            # Refresh dialog
            self.accept()
            new_dlg = BuildHouseDialog(self.player, self.main_window)
            new_dlg.exec()


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
        items_to_remove = [item for item in self.scene.items() if not isinstance(item, PlayerToken)]
        for item in items_to_remove:
            self.scene.removeItem(item)
        font = QFont("Arial", 8)
        pen = QPen(Qt.GlobalColor.black, 1)  # מסגרת שחורה דקה

        for i, pos in enumerate(self.tile_positions):
            tile = self.main_window.board.tiles[i]

            # 1. ציור המלבן הראשי
            rect = QGraphicsRectItem(pos.x(), pos.y(), self.tile_size, self.tile_size)

            if hasattr(tile, 'owner') and tile.owner:
                # אם יש בעלים, נשתמש בצבע שלו למסגרת ונעבה אותה (עובי 4)
                owner_pen = QPen(QColor(tile.owner.color), 4)
                rect.setPen(owner_pen)

                # אופציונלי: צביעת הרקע בגוון בהיר מאוד של צבע השחקן
                bg_color = QColor(tile.owner.color)
                bg_color.setAlpha(30)  # שקיפות (0-255)
                rect.setBrush(QBrush(bg_color))
            else:
                # אם אין בעלים, מסגרת שחורה רגילה
                rect.setPen(QPen(Qt.GlobalColor.black, 1))
                rect.setBrush(QBrush(QColor("white")))

            self.scene.addItem(rect)

            # colors and houses
            y_text_offset = 4

            if hasattr(tile, 'color') and tile.color:
                color_rect = QGraphicsRectItem(pos.x(), pos.y(), self.tile_size, 15)
                color_rect.setBrush(QBrush(QColor(tile.color)))
                color_rect.setPen(pen)
                self.scene.addItem(color_rect)

                y_text_offset = 18

                if isinstance(tile, PropertyTile):
                    # Hotel
                    if hasattr(tile, 'hotel') and tile.hotel:
                        hotel_text = QGraphicsSimpleTextItem("🏨")
                        hotel_text.setFont(QFont("Arial", 10))
                        hotel_text.setPos(pos.x() + self.tile_size - 22, pos.y() + 1)
                        self.scene.addItem(hotel_text)
                    # Houses
                    elif hasattr(tile, 'houses') and tile.houses > 0:
                        houses_display = QGraphicsSimpleTextItem("🏠" * tile.houses)
                        houses_display.setFont(QFont("Arial", 7))
                        houses_display.setPos(pos.x() + 2, pos.y() + 2)
                        self.scene.addItem(houses_display)

            # 3.Name of the Tile
            text = QGraphicsSimpleTextItem(self.wrap(tile.name))
            text.setFont(font)
            text.setPos(pos.x() + 4, pos.y() + y_text_offset)  #
            self.scene.addItem(text)

        self.scene.setSceneRect(self.scene.itemsBoundingRect())

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


# Player Token
class PlayerToken(QGraphicsEllipseItem):
    def __init__(self, color):
        super().__init__(-10, -10, 20, 20)
        self.setBrush(QBrush(color))
        self.setPen(QPen(Qt.GlobalColor.black))
        self.current_tile = 0


# Simple Player + Engine
class SimplePlayer:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.position = 0
        self.money = 1500
        self.properties = []
        self.in_jail = False
        self.jail_turns = 0
        self.get_out_jail_free = 0
        self.doubles_count = 0


class GameEngine(QtCore.QObject):
    moveSteps = QtCore.pyqtSignal(int, int, int, int)  # player_idx, steps, dice1, dice2
    diceRolled = QtCore.pyqtSignal(int, int)

    def __init__(self, players):
        super().__init__()
        self.players = players
        self.turn = 0

    def roll(self):
        d1, d2 = random.randint(1, 6), random.randint(1, 6)
        steps = d1 + d2
        is_double = (d1 == d2)

        self.diceRolled.emit(d1, d2)
        self.moveSteps.emit(self.turn, steps, d1, d2)

        if not is_double:
            self.turn = (self.turn + 1) % len(self.players)

# Property Panel Widget
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
            props_label.setTextFormat(Qt.TextFormat.RichText)
            props_label.setStyleSheet("margin-left: 10px; font-size: 9pt;")
            layout.addWidget(props_label)

            self.property_labels.append((player, props_label))

        layout.addStretch()

    def update_properties(self):
        for player, label in self.property_labels:
            jail_status = " 🚔" if player.in_jail else ""
            if not player.properties:
                label.setText(f"No properties yet{jail_status}")
            else:
                prop_list = []
                for prop in player.properties:
                    houses_info = ""
                    if hasattr(prop, 'hotel') and prop.hotel:
                        houses_info = " 🏨"
                    elif hasattr(prop, 'houses') and prop.houses > 0:
                        houses_info = f" {'🏠' * prop.houses}"

                    color_hex = "#9E9E9E"  # Neutral fallback
                    if hasattr(prop, 'color') and prop.color:
                        color_hex = PROPERTY_COLOR_MAP.get(prop.color.lower(), color_hex)

                    # Uniform circular marker rendered by QLabel RichText.
                    circle_html = f'<span style="color:{color_hex}; font-weight:700;">&#9679;</span>&nbsp;'
                    safe_name = html.escape(prop.name)
                    prop_list.append(f"{circle_html}{safe_name}{houses_info}")

                label.setText("<br>".join(prop_list) + jail_status)


# --------------------------------------------------
# Card Display Dialog
# --------------------------------------------------
class CardDialog(QtWidgets.QDialog):
    def __init__(self, card_text):
        super().__init__()
        self.setWindowTitle("Card")
        self.setFixedSize(350, 200)

        layout = QVBoxLayout(self)

        # Card icon
        icon = QLabel("🎴")
        icon.setFont(QFont("Arial", 48))
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)

        # Card text
        text = QLabel(card_text)
        text.setFont(QFont("Arial", 12))
        text.setWordWrap(True)
        text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(text)

        # OK button
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn)


# --------------------------------------------------
# Jail Options Dialog
# --------------------------------------------------
class JailDialog(QtWidgets.QDialog):
    def __init__(self, player):
        super().__init__()
        self.player = player
        self.choice = None

        self.setWindowTitle("In Jail")
        self.setFixedSize(300, 250)

        layout = QVBoxLayout(self)

        # Jail icon
        icon = QLabel("🚔")
        icon.setFont(QFont("Arial", 48))
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)

        # Info
        info = QLabel(f"{player.name} is in JAIL!\nTurn {player.jail_turns}/3")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)

        # Options
        roll_btn = QPushButton("Roll Dice (try for doubles)")
        roll_btn.clicked.connect(lambda: self.make_choice("roll"))
        layout.addWidget(roll_btn)

        if player.get_out_jail_free > 0:
            card_btn = QPushButton(f"Use Get Out of Jail Free Card ({player.get_out_jail_free})")
            card_btn.clicked.connect(lambda: self.make_choice("card"))
            layout.addWidget(card_btn)

        if player.money >= 50:
            pay_btn = QPushButton("Pay $50")
            pay_btn.clicked.connect(lambda: self.make_choice("pay"))
            layout.addWidget(pay_btn)

    def make_choice(self, choice):
        self.choice = choice
        self.accept()


# --------------------------------------------------
# Property Card Dialog
# --------------------------------------------------
class PropertyCardDialog(QtWidgets.QDialog):
    def __init__(self, property_tile, player, main_window):
        super().__init__()
        self.tile = property_tile
        self.player = player
        self.main_window = main_window

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

        # Money info
        money_label = QLabel(f"\nYour money: ${player.money}")
        money_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(money_label)

        # Buttons
        btn_layout = QHBoxLayout()
        buy_btn = QPushButton("Buy")
        cancel_btn = QPushButton("Pass")

        if player.money < property_tile.price:
            buy_btn.setEnabled(False)

        buy_btn.clicked.connect(self.buy)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(buy_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def buy(self):
        if self.tile.buy(self.player):
            self.main_window.update_status()
        self.accept()


# --------------------------------------------------
# Main Window
# --------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Monopoly – PyQt6")
        self.resize(900, 750)

        self.board = create_us_monopoly_board_with_cards()

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

        self.build_btn = QPushButton("🏠 Build Houses")
        self.build_btn.clicked.connect(self.open_build_dialog)
        side.addWidget(self.build_btn)

        # Game setup
        self.players = [
            SimplePlayer("Alice", QColor("blue")),
            SimplePlayer("Bob", QColor("red")),
            SimplePlayer("Charlie", QColor("green")),
            SimplePlayer("Diana", QColor("purple"))
        ]

        # Property panel
        self.property_panel = PropertyPanel(self.players)
        side.addWidget(self.property_panel)

        self.status = QLabel("")
        side.addWidget(self.status)
        side.addStretch()

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
        self.last_dice = (0, 0)
        self.game = Game(self.players, self.board)
        self.update_status()

    def roll(self):
        current_player = self.players[self.engine.turn]

        # Handle jail
        if current_player.in_jail:
            dlg = JailDialog(current_player)
            dlg.exec()

            if dlg.choice == "pay":
                current_player.money -= 50
                current_player.in_jail = False
                current_player.jail_turns = 0
                self.update_status()
            elif dlg.choice == "card":
                current_player.get_out_jail_free -= 1
                current_player.in_jail = False
                current_player.jail_turns = 0
                self.update_status()
            # If "roll", continue to normal roll

        self.roll_btn.setEnabled(False)
        self.engine.roll()

    def open_build_dialog(self):
        current_player = self.players[self.engine.turn]
        dlg = BuildHouseDialog(current_player, self)
        dlg.exec()
        self.update_status()

    def update_dice(self, d1, d2):
        self.last_dice = (d1, d2)
        self.dice.setText(f"Dice: {d1} + {d2}")

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
            jail = " 🚔" if p.in_jail else ""
            cards = f" 🎟️x{p.get_out_jail_free}" if p.get_out_jail_free > 0 else ""
            lines.append(f"{p.name}: ${p.money} ({tile}){jail}{cards}")
        self.status.setText("\n".join(lines))

        self.property_panel.update_properties()

    def animate_player(self, player_idx, steps, dice1, dice2):
        token = self.tokens[player_idx]
        player = self.players[player_idx]

        # Check if in jail
        if player.in_jail:
            can_move = try_leave_jail(player, dice1, dice2)
            if not can_move:
                self.update_status()
                self.roll_btn.setEnabled(True)
                return

        path = []
        cur = token.current_tile
        passed_go = False

        for _ in range(steps):
            cur = (cur + 1) % 40
            path.append(cur)
            # בדיקה אם עברנו את GO
            if cur == 0:
                passed_go = True

        self._animate_path(token, player, path, player_idx, passed_go)

    def _animate_path(self, token, player, path, idx, passed_go=False, step=0):
        if step < len(path):
            tile = path[step]
            self.place_token(token, tile, idx)
            token.current_tile = tile
            QTimer.singleShot(
                200,
                lambda: self._animate_path(token, player, path, idx, passed_go, step + 1)
            )
            return

        player.position = token.current_tile

        # תשלום עבור מעבר ב-GO
        if passed_go:
            player.money += 200
            print(f"💰 {player.name} passed GO and collected $200!")

        tile = self.board.tiles[player.position]
        tile.on_land(player, self.game)

        if player.position != token.current_tile:
            token.current_tile = player.position
            self.place_token(token, player.position, idx)

        # Show card if there was one
        if hasattr(self.game, 'last_card') and self.game.last_card:
            card_dlg = CardDialog(self.game.last_card.text)
            card_dlg.exec()

            # בדיקה: האם הכרטיס הזיז את השחקן למקום אחר? (למשל "לך ל-Boardwalk")
            if player.position != token.current_tile:
                token.current_tile = player.position
                self.place_token(token, player.position, idx)

                # אופציונלי: הפעלת הלוגיקה של המשבצת החדשה (אם נחתנו על נכס אחרי הכרטיס)
                new_tile = self.board.tiles[player.position]
                new_tile.on_land(player, self.game)

            self.game.last_card = None

        # Show property purchase dialog
        if isinstance(self.game.pending_property, PropertyTile):
            dlg = PropertyCardDialog(self.game.pending_property, player, self)
            dlg.exec()
            self.game.pending_property = None

        self.update_status()

        d1, d2 = self.last_dice
        is_double = (d1 == d2)

        if is_double and not player.in_jail:
            player.doubles_count += 1
            print(f"🎲 {player.name} rolled DOUBLES! ({d1},{d2}) - Count: {player.doubles_count}")

            if player.doubles_count >= 3:
                # 3 דאבלים ברצף = כלא!
                print(f"🚔 {player.name} rolled 3 doubles in a row - GO TO JAIL!")
                from monopoly_model import go_to_jail
                go_to_jail(player)
                token.current_tile = player.position
                self.place_token(token, player.position, idx)
                player.doubles_count = 0
                self.engine.turn = (self.engine.turn + 1) % len(self.players)
                self.update_status()
            else:
                # תור נוסף!
                print(f"✨ {player.name} gets another turn!")
        else:
            # לא דאבל - אפס את המונה
            player.doubles_count = 0

        self.roll_btn.setEnabled(True)


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


