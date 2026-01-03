
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
    def __init__(self, name, index, price, rents, color=None, house_price=50):
        super().__init__(name, index)

        # static data
        self.price = price
        self.rents = rents
        self.color = color
        self.house_price = house_price

        # dynamic game state
        self.owner = None
        self.houses = 0
        self.hotel = False

    def get_rent(self):
        if self.hotel:
            return self.rents[5]
        return self.rents[self.houses]

    def buy(self, player):
        if self.owner is None and player.money >= self.price:
            player.money -= self.price
            self.owner = player
            player.properties.append(self)
            return True
        return False

    def build_house(self, player):
        if self.owner != player:
            return False
        if self.hotel or self.houses >= 4:
            return False
        if player.money < self.house_price:
            return False

        player.money -= self.house_price
        self.houses += 1

        if self.houses == 4:
            self.houses = 0
            self.hotel = True

        return True

    def on_land(self, player, game):
        print(f"{player.name} landed on {self.name}")

        if self.owner is None:
            print(f"{self.name} is available for purchase!")
            game.pending_property = self
        elif self.owner != player:
            # Use the last dice roll - you'll need to pass this from the game
            rent = self.get_rent(dice_roll=7)  # Default to 7, or pass actual dice roll
            player.money -= rent
            self.owner.money += rent
            print(f"{player.name} paid ${rent} rent to {self.owner.name}")
        else:
            print(f"{player.name} owns this property")


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
# monopoly_model.py - Updated create_us_monopoly_board() function
def create_us_monopoly_board():
    board = Board()

    # 0–10
    board.add_tile(SpecialTile("GO", 0))
    board.add_tile(PropertyTile("Mediterranean Avenue", 1, 60, [2, 10, 30, 90, 160, 250], "sienna", 50))
    board.add_tile(SpecialTile("Community Chest", 2))
    board.add_tile(PropertyTile("Baltic Avenue", 3, 60, [4, 20, 60, 180, 320, 450], "sienna", 50))
    board.add_tile(SpecialTile("Income Tax", 4, lambda p, g: setattr(p, "money", p.money - 200)))
    board.add_tile(RailroadTile("Reading Railroad", 5, 200, [25, 50, 100, 200]))
    board.add_tile(PropertyTile("Oriental Avenue", 6, 100, [6, 30, 90, 270, 400, 550], "lightblue", 50))
    board.add_tile(SpecialTile("Chance", 7))
    board.add_tile(PropertyTile("Vermont Avenue", 8, 100, [6, 30, 90, 270, 400, 550], "lightblue", 50))
    board.add_tile(PropertyTile("Connecticut Avenue", 9, 120, [8, 40, 100, 300, 450, 600], "lightblue", 50))
    board.add_tile(SpecialTile("Jail / Just Visiting", 10))

    # 11–20
    board.add_tile(PropertyTile("St. Charles Place", 11, 140, [10, 50, 150, 450, 625, 750], "pink", 100))
    board.add_tile(UtilityTile("Electric Company", 12, 150, [4, 10]))  # 4x or 10x dice roll
    board.add_tile(PropertyTile("States Avenue", 13, 140, [10, 50, 150, 450, 625, 750], "pink", 100))
    board.add_tile(PropertyTile("Virginia Avenue", 14, 160, [12, 60, 180, 500, 700, 900], "pink", 100))
    board.add_tile(RailroadTile("Pennsylvania Railroad", 15, 200, [25, 50, 100, 200]))
    board.add_tile(PropertyTile("St. James Place", 16, 180, [14, 70, 200, 550, 750, 950], "orange", 100))
    board.add_tile(SpecialTile("Community Chest", 17))
    board.add_tile(PropertyTile("Tennessee Avenue", 18, 180, [14, 70, 200, 550, 750, 950], "orange", 100))
    board.add_tile(PropertyTile("New York Avenue", 19, 200, [16, 80, 220, 600, 800, 1000], "orange", 100))
    board.add_tile(SpecialTile("Free Parking", 20))

    # 21–30
    board.add_tile(PropertyTile("Kentucky Avenue", 21, 220, [18, 90, 250, 700, 875, 1050], "red", 150))
    board.add_tile(SpecialTile("Chance", 22))
    board.add_tile(PropertyTile("Indiana Avenue", 23, 220, [18, 90, 250, 700, 875, 1050], "red", 150))
    board.add_tile(PropertyTile("Illinois Avenue", 24, 240, [20, 100, 300, 750, 925, 1100], "red", 150))
    board.add_tile(RailroadTile("B&O Railroad", 25, 200, [25, 50, 100, 200]))
    board.add_tile(PropertyTile("Atlantic Avenue", 26, 260, [22, 110, 330, 800, 975, 1150], "yellow", 150))
    board.add_tile(PropertyTile("Ventnor Avenue", 27, 260, [22, 110, 330, 800, 975, 1150], "yellow", 150))
    board.add_tile(UtilityTile("Water Works", 28, 150, [4, 10]))  # 4x or 10x dice roll
    board.add_tile(PropertyTile("Marvin Gardens", 29, 280, [24, 120, 360, 850, 1025, 1200], "yellow", 150))
    board.add_tile(SpecialTile("Go To Jail", 30, lambda p, g: setattr(p, "position", 10)))

    # 31–39
    board.add_tile(PropertyTile("Pacific Avenue", 31, 300, [26, 130, 390, 900, 1100, 1275], "green", 200))
    board.add_tile(PropertyTile("North Carolina Avenue", 32, 300, [26, 130, 390, 900, 1100, 1275], "green", 200))
    board.add_tile(SpecialTile("Community Chest", 33))
    board.add_tile(PropertyTile("Pennsylvania Avenue", 34, 320, [28, 150, 450, 1000, 1200, 1400], "green", 200))
    board.add_tile(RailroadTile("Short Line", 35, 200, [25, 50, 100, 200]))
    board.add_tile(SpecialTile("Chance", 36))
    board.add_tile(PropertyTile("Park Place", 37, 350, [35, 175, 500, 1100, 1300, 1500], "darkblue", 200))
    board.add_tile(SpecialTile("Luxury Tax", 38, lambda p, g: setattr(p, "money", p.money - 100)))
    board.add_tile(PropertyTile("Boardwalk", 39, 400, [50, 200, 600, 1400, 1700, 2000], "darkblue", 200))

    return board


# -------------------------
# Quick sanity test
# -------------------------
if __name__ == "__main__":
    board = create_us_monopoly_board()
    for tile in board.tiles:
        print(tile.index, tile.name)

