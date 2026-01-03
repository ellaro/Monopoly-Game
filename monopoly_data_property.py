from monopoly_model import PropertyTile

PROPERTIES = [
    #Brown
    PropertyTile(
        "Mediterranean Avenue", 1,
        price=60,
        rents=[2, 10, 30, 90, 160, 250],
        color="sienna",
        house_price=50
    ),
    PropertyTile(
        "Baltic Avenue", 3,
        price=60,
        rents=[4, 20, 60, 180, 320, 450],
        color="sienna",
        house_price=50
    ),

    #Light Blue
    PropertyTile(
        "Oriental Avenue", 6,
        price=100,
        rents=[6, 30, 90, 270, 400, 550],
        color="lightblue",
        house_price=50
    ),
    PropertyTile(
        "Vermont Avenue", 8,
        price=100,
        rents=[6, 30, 90, 270, 400, 550],
        color="lightblue",
        house_price=50
    ),
    PropertyTile(
        "Connecticut Avenue", 9,
        price=120,
        rents=[8, 40, 100, 300, 450, 600],
        color="lightblue",
        house_price=50
    ),

    #Pink
    PropertyTile(
        "St. Charles Place", 11,
        price=140,
        rents=[10, 50, 150, 450, 625, 750],
        color="pink",
        house_price=100
    ),
    PropertyTile(
        "States Avenue", 13,
        price=140,
        rents=[10, 50, 150, 450, 625, 750],
        color="pink",
        house_price=100
    ),
    PropertyTile(
        "Virginia Avenue", 14,
        price=160,
        rents=[12, 60, 180, 500, 700, 900],
        color="pink",
        house_price=100
    ),
    #Orenge
    PropertyTile(
        "St. James Place", 16,
        price=180,
        rents=[14, 70, 200, 550, 750, 950],
        color="orange",
        house_price=100
    ),
    PropertyTile(
        "Tennessee Avenue", 18,
        price=180,
        rents=[14, 70, 200, 550, 750, 950],
        color="orange",
        house_price=100
    ),
    PropertyTile(
        "New York Avenue", 19,
        price=200,
        rents=[16, 80, 220, 600, 800, 1000],
        color="orange",
        house_price=100
    ),

    #Red

    PropertyTile(
        "Kentucky Avenue", 21,
        price=220,
        rents=[18, 90, 250, 700, 875, 1050],
        color="red",
        house_price=150
    ),
    PropertyTile(
        "Indiana Avenue", 23,
        price=220,
        rents=[18, 90, 250, 700, 875, 1050],
        color="red",
        house_price=150
    ),
    PropertyTile(
        "Illinois Avenue", 24,
        price=240,
        rents=[20, 100, 300, 750, 925, 1100],
        color="red",
        house_price=150
    ),

    #Yellow

    PropertyTile(
        "Atlantic Avenue", 26,
        price=260,
        rents=[22, 110, 330, 800, 975, 1150],
        color="yellow",
        house_price=150
    ),
    PropertyTile(
        "Ventnor Avenue", 27,
        price=260,
        rents=[22, 110, 330, 800, 975, 1150],
        color="yellow",
        house_price=150
    ),
    PropertyTile(
        "Marvin Gardens", 29,
        price=280,
        rents=[24, 120, 360, 850, 1025, 1200],
        color="yellow",
        house_price=150
    ),

    #Green

    PropertyTile(
        "Pacific Avenue", 31,
        price=300,
        rents=[26, 130, 390, 900, 1100, 1275],
        color="green",
        house_price=200
    ),
    PropertyTile(
        "North Carolina Avenue", 32,
        price=300,
        rents=[26, 130, 390, 900, 1100, 1275],
        color="green",
        house_price=200
    ),
    PropertyTile(
        "Pennsylvania Avenue", 34,
        price=320,
        rents=[28, 150, 450, 1000, 1200, 1400],
        color="green",
        house_price=200
    ),

    #Dark Blue
    PropertyTile(
        "Park Place", 37,
        price=350,
        rents=[35, 175, 500, 1100, 1300, 1500],
        color="darkblue",
        house_price=200
    ),
    PropertyTile(
        "Boardwalk", 39,
        price=400,
        rents=[50, 200, 600, 1400, 1700, 2000],
        color="darkblue",
        house_price=200
    )]