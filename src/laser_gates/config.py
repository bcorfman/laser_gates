"""Game configuration constants."""

import os
import sys
from pathlib import Path


def get_resource_path(relative_path: str) -> str:
    """Get the absolute path to a resource file.
    
    Works both when running as a Python script and when compiled with Nuitka.
    When frozen (Nuitka), resources are extracted to the same directory as the executable.
    """
    if getattr(sys, "frozen", False):
        # Running as compiled executable
        exe_dir = Path(sys.executable).parent
        return str(exe_dir / relative_path)
    else:
        # Running as Python script
        # Find the project root (parent of src/)
        script_dir = Path(__file__).parent  # src/laser_gates
        project_root = script_dir.parent.parent  # project root
        return str(project_root / relative_path)


# Window and world dimensions
HILL_WIDTH = 512
HILL_HEIGHT = 57
WINDOW_WIDTH = HILL_WIDTH * 2
WINDOW_HEIGHT = 432

# Resource paths
HILL_SLICES = [
    get_resource_path("res/hill_slice1.png"),
    get_resource_path("res/hill_slice2.png"),
    get_resource_path("res/hill_slice3.png"),
    get_resource_path("res/hill_slice4.png"),
]
SHIP = get_resource_path("res/dart.png")
PLAYER_SHOT = ":resources:/images/space_shooter/laserRed01.png"
FORCEFIELD = get_resource_path("res/forcefield.png")
FORCEFIELD_SOLID_COLORS = [
    (6, 102, 17),
    (57, 23, 1),
    (230, 230, 230),
    (196, 217, 69),
    (2, 53, 15),
    (171, 171, 171),
    (68, 97, 3),
    (188, 188, 188),
    (255, 174, 56),
    (28, 92, 17),
    (74, 159, 46),
    (97, 208, 112),
    (255, 152, 28),
    (244, 95, 245),
    (254, 109, 255),
    (192, 194, 255),
    (105, 226, 122),
    (252, 183, 92),
    (57, 57, 57),
    (88, 79, 218),
    (154, 255, 166),
    (255, 197, 29),
    (255, 145, 29),
    (107, 100, 255),
    (255, 116, 76),
    (97, 89, 236),
]

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
