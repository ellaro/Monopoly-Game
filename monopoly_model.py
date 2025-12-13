
# monopoly_model.py
# Game logic & data model (NO GUI)

# -------------------------
# Base Tiles
# -------------------------
class Tile:
    def __init__(self, name, index):
        self.name = name
        self.index = index

    def on_land(self, player, game):
        """What happens when a player lands here"""
        pass


class PropertyTile(Tile):
    def __init__(self, name, index, price, rent, color=None):
        super().__init__(name, index)
        self.price = price
        self.rent = rent
        self.color = color
        self.owner = None
        self.houses = 0
        self.hotel = False

    def on_land(self, player, game):
        if self.owner is None:
            # GUI will ask: buy or skip
            game.pending_property = self
        elif self.owner != player:
            player.money -= self.rent
            self.owner.money += self.rent


class RailroadTile(PropertyTile):
    pass


class UtilityTile(PropertyTile):
    pass


class SpecialTile(Tile):
    def __init__(self, name, index, action=None):
        super().__init__(name, index)
        self.action = action

    def on_land(self, player, game):
        if self.action:
            self.action(player, game)


# -------------------------
# Player & Game
# -------------------------
class Player:
    def __init__(self, name, start_money=1500):
        self.name = name
        self.position = 0
        self.money = start_money
        self.properties = []
        self.in_jail = False


class Dice:
    @staticmethod
    def roll():
        import random
        return random.randint(1, 6), random.randint(1, 6)


class Board:
    def __init__(self):
        self.tiles = []

    def add_tile(self, tile):
        self.tiles.append(tile)

    def get_tile(self, index):
        return self.tiles[index % 40]


class Game:
    def __init__(self, players, board):
        self.players = players
        self.board = board
        self.current_player_idx = 0
        self.pending_property = None

    def current_player(self):
        return self.players[self.current_player_idx]

    def next_turn(self):
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)


# -------------------------
# US Monopoly Board (40 tiles)
# -------------------------
def create_us_monopoly_board():
    board = Board()

    # 0–10
    board.add_tile(SpecialTile("GO", 0))
    board.add_tile(PropertyTile("Mediterranean Avenue", 1, 60, 2, "sienna"))
    board.add_tile(SpecialTile("Community Chest", 2))
    board.add_tile(PropertyTile("Baltic Avenue", 3, 60, 4, "sienna"))
    board.add_tile(SpecialTile("Income Tax", 4, lambda p, g: setattr(p, "money", p.money - 200)))
    board.add_tile(RailroadTile("Reading Railroad", 5, 200, 25))
    board.add_tile(PropertyTile("Oriental Avenue", 6, 100, 6, "lightblue"))
    board.add_tile(SpecialTile("Chance", 7))
    board.add_tile(PropertyTile("Vermont Avenue", 8, 100, 6, "lightblue"))
    board.add_tile(PropertyTile("Connecticut Avenue", 9, 120, 8, "lightblue"))
    board.add_tile(SpecialTile("Jail / Just Visiting", 10))

    # 11–20
    board.add_tile(PropertyTile("St. Charles Place", 11, 140, 10, "pink"))
    board.add_tile(UtilityTile("Electric Company", 12, 150, 10))
    board.add_tile(PropertyTile("States Avenue", 13, 140, 10, "pink"))
    board.add_tile(PropertyTile("Virginia Avenue", 14, 160, 12, "pink"))
    board.add_tile(RailroadTile("Pennsylvania Railroad", 15, 200, 25))
    board.add_tile(PropertyTile("St. James Place", 16, 180, 14, "orange"))
    board.add_tile(SpecialTile("Community Chest", 17))
    board.add_tile(PropertyTile("Tennessee Avenue", 18, 180, 14, "orange"))
    board.add_tile(PropertyTile("New York Avenue", 19, 200, 16, "orange"))
    board.add_tile(SpecialTile("Free Parking", 20))

    # 21–30
    board.add_tile(PropertyTile("Kentucky Avenue", 21, 220, 18, "red"))
    board.add_tile(SpecialTile("Chance", 22))
    board.add_tile(PropertyTile("Indiana Avenue", 23, 220, 18, "red"))
    board.add_tile(PropertyTile("Illinois Avenue", 24, 240, 20, "red"))
    board.add_tile(RailroadTile("B&O Railroad", 25, 200, 25))
    board.add_tile(PropertyTile("Atlantic Avenue", 26, 260, 22, "yellow"))
    board.add_tile(PropertyTile("Ventnor Avenue", 27, 260, 22, "yellow"))
    board.add_tile(UtilityTile("Water Works", 28, 150, 10))
    board.add_tile(PropertyTile("Marvin Gardens", 29, 280, 24, "yellow"))
    board.add_tile(SpecialTile("Go To Jail", 30, lambda p, g: setattr(p, "position", 10)))

    # 31–39
    board.add_tile(PropertyTile("Pacific Avenue", 31, 300, 26, "green"))
    board.add_tile(PropertyTile("North Carolina Avenue", 32, 300, 26, "green"))
    board.add_tile(SpecialTile("Community Chest", 33))
    board.add_tile(PropertyTile("Pennsylvania Avenue", 34, 320, 28, "green"))
    board.add_tile(RailroadTile("Short Line", 35, 200, 25))
    board.add_tile(SpecialTile("Chance", 36))
    board.add_tile(PropertyTile("Park Place", 37, 350, 35, "darkblue"))
    board.add_tile(SpecialTile("Luxury Tax", 38, lambda p, g: setattr(p, "money", p.money - 100)))
    board.add_tile(PropertyTile("Boardwalk", 39, 400, 50, "darkblue"))

    return board


# -------------------------
# Quick sanity test
# -------------------------
if __name__ == "__main__":
    board = create_us_monopoly_board()
    for tile in board.tiles:
        print(tile.index, tile.name)


