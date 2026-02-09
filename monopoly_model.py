# monopoly_model.py
# Game logic & data model (NO GUI)

import random


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
            return self.rents[5] if len(self.rents) > 5 else self.rents[-1]
        return self.rents[min(self.houses, len(self.rents) - 1)]

    def buy(self, player):
        if self.owner is None and player.money >= self.price:
            player.money -= self.price
            self.owner = player
            player.properties.append(self)
            print(f"{player.name} bought {self.name} for ${self.price}")
            return True
        return False

    def build_house(self, player):
        if self.owner != player:
            return False
        if self.hotel:
            return False  # Already has hotel
        if self.houses >= 4:
            # Convert to hotel
            if player.money < self.house_price:
                return False
            player.money -= self.house_price
            self.houses = 0
            self.hotel = True
            print(f"🏨 {player.name} built a HOTEL on {self.name}!")
            return True

        # Build house
        if player.money < self.house_price:
            return False

        # Check monopoly
        if not self.has_monopoly(player):
            print(f"❌ Need monopoly to build on {self.name}")
            return False

        # Check even building rule
        if not self.can_build_evenly(player):
            print(f"❌ Must build evenly across all properties in {self.color}")
            return False

        player.money -= self.house_price
        self.houses += 1
        print(f"🏠 {player.name} built house #{self.houses} on {self.name}!")
        return True

    def has_monopoly(self, player):
        """בדיקה אם לשחקן יש את כל הנכסים באותו צבע"""
        if not self.color:
            return False

        # Count properties of this color
        same_color = [p for p in player.properties
                      if isinstance(p, PropertyTile) and p.color == self.color]

        # How many properties should exist in this color?
        color_counts = {
            'sienna': 2,  # Brown
            'lightblue': 3,
            'pink': 3,
            'orange': 3,
            'red': 3,
            'yellow': 3,
            'green': 3,
            'darkblue': 2
        }

        required = color_counts.get(self.color, 0)
        has_monopoly = len(same_color) == required

        if has_monopoly:
            print(f"✅ {player.name} has monopoly on {self.color}")

        return has_monopoly

    def can_build_evenly(self, player):
        """בדיקה שבונים שווה על כל הנכסים באותו צבע"""
        same_color = [p for p in player.properties
                      if isinstance(p, PropertyTile) and p.color == self.color]

        # Find minimum houses
        min_houses = min(p.houses for p in same_color)

        # Can only build if this property has minimum houses
        return self.houses == min_houses

    def on_land(self, player, game):
        print(f"\n=== {player.name} landed on {self.name} ===")
        print(f"Owner: {self.owner.name if self.owner else 'None'}")

        if self.owner is None:
            print(f"✅ {self.name} is available for purchase!")
            game.pending_property = self
        elif self.owner != player:
            try:
                rent = self.get_rent()
                print(f"💰 Rent calculated: ${rent}")
                player.money -= rent
                self.owner.money += rent
                print(f"✅ {player.name} paid ${rent} rent to {self.owner.name}")
            except Exception as e:
                print(f"❌ ERROR paying rent: {e}")
        else:
            print(f"✅ {player.name} owns this property")


class RailroadTile(PropertyTile):
    def __init__(self, name, index, price, rents):
        # Don't pass color or house_price for railroads
        super().__init__(name, index, price, rents, color=None, house_price=0)

    def get_rent(self):
        if not self.owner:
            return 0
        railroads_owned = sum(1 for prop in self.owner.properties if isinstance(prop, RailroadTile))
        return self.rents[min(railroads_owned - 1, len(self.rents) - 1)]

    def has_monopoly(self, player):
        # Railroads can't build houses
        return False

    def build_house(self, player):
        # Can't build on railroads
        return False


class UtilityTile(PropertyTile):
    def __init__(self, name, index, price, rents):
        # Don't pass color or house_price for utilities
        super().__init__(name, index, price, rents, color=None, house_price=0)

    def get_rent(self, dice_roll=7):
        if not self.owner:
            return 0
        utilities_owned = sum(1 for prop in self.owner.properties if isinstance(prop, UtilityTile))
        multiplier = self.rents[min(utilities_owned - 1, len(self.rents) - 1)]
        return multiplier * dice_roll

    def has_monopoly(self, player):
        # Utilities can't build houses
        return False

    def build_house(self, player):
        # Can't build on utilities
        return False

    def on_land(self, player, game):
        print(f"\n=== {player.name} landed on {self.name} ===")
        print(f"Owner: {self.owner.name if self.owner else 'None'}")

        if self.owner is None:
            print(f"✅ {self.name} is available for purchase!")
            game.pending_property = self
        elif self.owner != player:
            try:
                rent = self.get_rent(dice_roll=7)
                print(f"💰 Rent calculated: ${rent}")
                player.money -= rent
                self.owner.money += rent
                print(f"✅ {player.name} paid ${rent} rent to {self.owner.name}")
            except Exception as e:
                print(f"❌ ERROR paying rent: {e}")
        else:
            print(f"✅ {player.name} owns this property")


class SpecialTile(Tile):
    def __init__(self, name, index, action=None):
        super().__init__(name, index)
        self.action = action

    def on_land(self, player, game):
        if self.action:
            self.action(player, game)


# --------------------------------------------------
# Chance & Community Chest Cards
# --------------------------------------------------
class Card:
    def __init__(self, text, action):
        self.text = text
        self.action = action

    def execute(self, player, game):
        print(f"📜 Card: {self.text}")
        self.action(player, game)


def create_chance_cards():
    """כרטיסי צ'אנס"""
    cards = [
        Card("Advance to GO - Collect $200",
             lambda p, g: (setattr(p, 'position', 0), setattr(p, 'money', p.money + 200))),

        Card("Go to Jail - Do not pass GO",
             lambda p, g: go_to_jail(p)),

        Card("Bank pays you dividend of $50",
             lambda p, g: setattr(p, 'money', p.money + 50)),

        Card("Get out of Jail Free",
             lambda p, g: setattr(p, 'get_out_jail_free', p.get_out_jail_free + 1)),

        Card("Go Back 3 Spaces",
             lambda p, g: setattr(p, 'position', (p.position - 3) % 40)),

        Card("Pay poor tax of $15",
             lambda p, g: setattr(p, 'money', p.money - 15)),

        Card("Advance to Boardwalk",
             lambda p, g: setattr(p, 'position', 39)),

        Card("Advance to Illinois Avenue",
             lambda p, g: setattr(p, 'position', 24)),

        Card("Your building loan matures - Collect $150",
             lambda p, g: setattr(p, 'money', p.money + 150)),

        Card("You have won a crossword competition - Collect $100",
             lambda p, g: setattr(p, 'money', p.money + 100)),
    ]
    random.shuffle(cards)
    return cards


def create_community_chest_cards():
    """כרטיסי קופה"""
    cards = [
        Card("Advance to GO - Collect $200",
             lambda p, g: (setattr(p, 'position', 0), setattr(p, 'money', p.money + 200))),

        Card("Go to Jail - Do not pass GO",
             lambda p, g: go_to_jail(p)),

        Card("Bank error in your favor - Collect $200",
             lambda p, g: setattr(p, 'money', p.money + 200)),

        Card("Doctor's fees - Pay $50",
             lambda p, g: setattr(p, 'money', p.money - 50)),

        Card("From sale of stock you get $50",
             lambda p, g: setattr(p, 'money', p.money + 50)),

        Card("Get out of Jail Free",
             lambda p, g: setattr(p, 'get_out_jail_free', p.get_out_jail_free + 1)),

        Card("Holiday Fund matures - Receive $100",
             lambda p, g: setattr(p, 'money', p.money + 100)),

        Card("Income tax refund - Collect $20",
             lambda p, g: setattr(p, 'money', p.money + 20)),

        Card("Life insurance matures - Collect $100",
             lambda p, g: setattr(p, 'money', p.money + 100)),

        Card("Pay hospital fees of $100",
             lambda p, g: setattr(p, 'money', p.money - 100)),
    ]
    random.shuffle(cards)
    return cards


# --------------------------------------------------
# Jail Functions
# --------------------------------------------------
def go_to_jail(player):
    """שולח שחקן לכלא"""
    player.position = 10  # Jail position
    player.in_jail = True
    player.jail_turns = 0
    print(f"🚔 {player.name} goes to JAIL!")


def try_leave_jail(player, dice1, dice2):
    """מנסה לצאת מהכלא"""
    if not player.in_jail:
        return True

    # אפשרות 1: זרק דאבל
    if dice1 == dice2:
        print(f"🎲 {player.name} rolled doubles! Gets out of jail!")
        player.in_jail = False
        player.jail_turns = 0
        return True

    # אפשרות 2: השתמש בכרטיס "צא מהכלא"
    if player.get_out_jail_free > 0:
        print(f"🎟️ {player.name} uses 'Get out of Jail Free' card!")
        player.get_out_jail_free -= 1
        player.in_jail = False
        player.jail_turns = 0
        return True

    # אפשרות 3: שלם $50
    player.jail_turns += 1
    if player.jail_turns >= 3:
        print(f"💰 {player.name} must pay $50 to leave jail")
        player.money -= 50
        player.in_jail = False
        player.jail_turns = 0
        return True

    print(f"🔒 {player.name} stays in jail (turn {player.jail_turns}/3)")
    return False


# --------------------------------------------------
# Updated Tiles for Cards
# --------------------------------------------------
class ChanceTile(Tile):
    def __init__(self, name, index, deck):
        super().__init__(name, index)
        self.deck = deck
        self.current_card = 0

    def on_land(self, player, game):
        card = self.deck[self.current_card]
        self.current_card = (self.current_card + 1) % len(self.deck)
        card.execute(player, game)
        game.last_card = card


class CommunityChestTile(Tile):
    def __init__(self, name, index, deck):
        super().__init__(name, index)
        self.deck = deck
        self.current_card = 0

    def on_land(self, player, game):
        card = self.deck[self.current_card]
        self.current_card = (self.current_card + 1) % len(self.deck)
        card.execute(player, game)
        game.last_card = card


class GoToJailTile(Tile):
    def on_land(self, player, game):
        go_to_jail(player)


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
        self.jail_turns = 0
        self.get_out_jail_free = 0


class Dice:
    @staticmethod
    def roll():
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
        self.last_card = None

    def current_player(self):
        return self.players[self.current_player_idx]

    def next_turn(self):
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)

class SmartAI(Player):
    def __init__(self, name, color, weights):
        super().__init__(name, color)
        self.weights = weights  # מילון של משקולות (למשל: 'cash_reserve': 200)

    def evaluate_buy(self, property_tile):
        score = 100
        if self.money - property_tile.price < self.weights['cash_reserve']:
            score -= 200

        color_priority = {'orange': 1.5, 'red': 1.4, 'lightblue': 1.1}
        score *= color_priority.get(property_tile.color, 1.0)

        return score > 50  # if its worth buying return True

# -------------------------
# US Monopoly Board (NEW - with cards & jail)
# -------------------------
def create_us_monopoly_board_with_cards():
    board = Board()

    # יצירת חפיסות
    chance_deck = create_chance_cards()
    community_deck = create_community_chest_cards()

    # 0–10
    board.add_tile(SpecialTile("GO", 0))
    board.add_tile(PropertyTile("Mediterranean Avenue", 1, 60, [2, 10, 30, 90, 160, 250], "sienna", 50))
    board.add_tile(CommunityChestTile("Community Chest", 2, community_deck))
    board.add_tile(PropertyTile("Baltic Avenue", 3, 60, [4, 20, 60, 180, 320, 450], "sienna", 50))
    board.add_tile(SpecialTile("Income Tax", 4, lambda p, g: setattr(p, "money", p.money - 200)))
    board.add_tile(RailroadTile("Reading Railroad", 5, 200, [25, 50, 100, 200]))
    board.add_tile(PropertyTile("Oriental Avenue", 6, 100, [6, 30, 90, 270, 400, 550], "lightblue", 50))
    board.add_tile(ChanceTile("Chance", 7, chance_deck))
    board.add_tile(PropertyTile("Vermont Avenue", 8, 100, [6, 30, 90, 270, 400, 550], "lightblue", 50))
    board.add_tile(PropertyTile("Connecticut Avenue", 9, 120, [8, 40, 100, 300, 450, 600], "lightblue", 50))
    board.add_tile(SpecialTile("Jail / Just Visiting", 10))

    # 11–20
    board.add_tile(PropertyTile("St. Charles Place", 11, 140, [10, 50, 150, 450, 625, 750], "pink", 100))
    board.add_tile(UtilityTile("Electric Company", 12, 150, [4, 10]))
    board.add_tile(PropertyTile("States Avenue", 13, 140, [10, 50, 150, 450, 625, 750], "pink", 100))
    board.add_tile(PropertyTile("Virginia Avenue", 14, 160, [12, 60, 180, 500, 700, 900], "pink", 100))
    board.add_tile(RailroadTile("Pennsylvania Railroad", 15, 200, [25, 50, 100, 200]))
    board.add_tile(PropertyTile("St. James Place", 16, 180, [14, 70, 200, 550, 750, 950], "orange", 100))
    board.add_tile(CommunityChestTile("Community Chest", 17, community_deck))
    board.add_tile(PropertyTile("Tennessee Avenue", 18, 180, [14, 70, 200, 550, 750, 950], "orange", 100))
    board.add_tile(PropertyTile("New York Avenue", 19, 200, [16, 80, 220, 600, 800, 1000], "orange", 100))
    board.add_tile(SpecialTile("Free Parking", 20))

    # 21–30
    board.add_tile(PropertyTile("Kentucky Avenue", 21, 220, [18, 90, 250, 700, 875, 1050], "red", 150))
    board.add_tile(ChanceTile("Chance", 22, chance_deck))
    board.add_tile(PropertyTile("Indiana Avenue", 23, 220, [18, 90, 250, 700, 875, 1050], "red", 150))
    board.add_tile(PropertyTile("Illinois Avenue", 24, 240, [20, 100, 300, 750, 925, 1100], "red", 150))
    board.add_tile(RailroadTile("B&O Railroad", 25, 200, [25, 50, 100, 200]))
    board.add_tile(PropertyTile("Atlantic Avenue", 26, 260, [22, 110, 330, 800, 975, 1150], "yellow", 150))
    board.add_tile(PropertyTile("Ventnor Avenue", 27, 260, [22, 110, 330, 800, 975, 1150], "yellow", 150))
    board.add_tile(UtilityTile("Water Works", 28, 150, [4, 10]))
    board.add_tile(PropertyTile("Marvin Gardens", 29, 280, [24, 120, 360, 850, 1025, 1200], "yellow", 150))
    board.add_tile(GoToJailTile("Go To Jail", 30))

    # 31–39
    board.add_tile(PropertyTile("Pacific Avenue", 31, 300, [26, 130, 390, 900, 1100, 1275], "green", 200))
    board.add_tile(PropertyTile("North Carolina Avenue", 32, 300, [26, 130, 390, 900, 1100, 1275], "green", 200))
    board.add_tile(CommunityChestTile("Community Chest", 33, community_deck))
    board.add_tile(PropertyTile("Pennsylvania Avenue", 34, 320, [28, 150, 450, 1000, 1200, 1400], "green", 200))
    board.add_tile(RailroadTile("Short Line", 35, 200, [25, 50, 100, 200]))
    board.add_tile(ChanceTile("Chance", 36, chance_deck))
    board.add_tile(PropertyTile("Park Place", 37, 350, [35, 175, 500, 1100, 1300, 1500], "darkblue", 200))
    board.add_tile(SpecialTile("Luxury Tax", 38, lambda p, g: setattr(p, "money", p.money - 100)))
    board.add_tile(PropertyTile("Boardwalk", 39, 400, [50, 200, 600, 1400, 1700, 2000], "darkblue", 200))

    return board


# -------------------------
# Quick sanity test
# -------------------------
if __name__ == "__main__":
    board = create_us_monopoly_board_with_cards()
    for tile in board.tiles:
        print(tile.index, tile.name)