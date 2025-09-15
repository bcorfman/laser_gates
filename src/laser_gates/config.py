"""Game configuration constants."""

# Window and world dimensions
HILL_WIDTH = 512
HILL_HEIGHT = 57
WINDOW_WIDTH = HILL_WIDTH * 2
WINDOW_HEIGHT = 432

# Resource paths
HILL_SLICES = ["./res/hill_slice1.png", "./res/hill_slice2.png", "./res/hill_slice3.png", "./res/hill_slice4.png"]
SHIP = "./res/dart.png"
PLAYER_SHOT = ":resources:/images/space_shooter/laserRed01.png"

# Player ship configuration
PLAYER_SHIP_VERT = 5
PLAYER_SHIP_HORIZ = 8
PLAYER_SHIP_FIRE_SPEED = 15

# Tunnel configuration
WALL_WIDTH = 200
TUNNEL_VELOCITY = -3
TUNNEL_WALL_HEIGHT = 50
TUNNEL_WALL_COLOR = (141, 65, 8)

# Ship movement bounds
SHIP_LEFT_BOUND = HILL_WIDTH // 4
SHIP_RIGHT_BOUND = WINDOW_WIDTH - HILL_WIDTH / 1.5

# World bounds for different areas
TOP_BOUNDS = (-HILL_WIDTH, WINDOW_HEIGHT // 2, HILL_WIDTH * 5, WINDOW_HEIGHT)
BOTTOM_BOUNDS = (
    -HILL_WIDTH,
    0,
    HILL_WIDTH * 5,
    WINDOW_HEIGHT // 2,
)
