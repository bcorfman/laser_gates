"""Game configuration constants."""

import os
import sys
from pathlib import Path


def get_resource_path(relative_path: str) -> str:
    """Get the absolute path to a resource file.

    Works both when running as a Python script and when compiled with Nuitka.

    For Nuitka onefile mode:
    - Data files are inside the onefile binary and extracted to __file__'s directory
    - Use __file__ to locate resources that were included with include-data-dir

    For Nuitka standalone mode:
    - Resources are in the same directory as the executable
    
    For Python development:
    - Resources are in the project root, which is two levels up from config.py
    """
    # Check if running under Nuitka (onefile or standalone)
    try:
        # __compiled__ is only available in Nuitka-compiled code
        import __compiled__  # type: ignore # noqa: F401

        # In onefile mode, resources are extracted to the same temp directory as Python modules
        # __file__ will be something like: /tmp/onefile_xxx/laser_gates/config.py
        # We need to go up to the extraction root: /tmp/onefile_xxx/
        # Then access res/ from there

        # Get the directory containing this module file
        module_dir = Path(__file__).parent  # .../laser_gates/

        # In Nuitka onefile, the structure is typically:
        # temp_dir/
        #   laser_gates/  (package)
        #   res/          (data from include-data-dir)
        # So we need to go up from laser_gates/ to temp_dir/
        extraction_root = module_dir.parent
        full_path = extraction_root / relative_path

        return str(full_path)
    except ImportError:
        # Not running under Nuitka
        pass

    # Running as Python script
    # Find the project root (parent of src/)
    # __file__ is: project_root/src/laser_gates/config.py
    script_dir = Path(__file__).parent  # src/laser_gates
    project_root = script_dir.parent.parent  # project root
    full_path = project_root / relative_path
    return str(full_path)


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
