"""Game configuration constants."""

import sys
from pathlib import Path


def get_resource_path(relative_path: str) -> str:
    """Get the absolute path to a resource file.

    Works both when running as a Python script and when compiled with Nuitka.
    When frozen (Nuitka), resources are extracted to the temporary directory.
    """
    # Check if we're in a frozen environment (PyInstaller, Nuitka, etc.)
    if getattr(sys, "frozen", False):
        # Running as compiled executable (Nuitka or PyInstaller)
        # sys._MEIPASS is set by both PyInstaller and Nuitka to the temp extraction directory
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            base_path = Path(meipass)
        else:
            # For Nuitka standalone, resources are in the same directory as the executable
            exe_path = Path(sys.executable).resolve()
            base_path = exe_path.parent

        full_path = base_path / relative_path
        # Resolve the path here to avoid arcade having to resolve it later
        resolved_path = full_path.resolve(strict=False)
        return str(resolved_path)

    # Check if we're in a deployed Nuitka environment
    # In deployed builds, __file__ contains "laser_gates/laser_gates" (or laser_gates\laser_gates on Windows)
    # and the executable is in the same directory (not in a standard Python installation path)
    file_path = Path(__file__).resolve()
    exe_path = Path(sys.executable).resolve()
    exe_parent = exe_path.parent

    # Check if __file__ contains the laser_gates/laser_gates pattern (normalize for cross-platform)
    # and if sys.executable and __file__ are in the same parent directory
    # This indicates a Nuitka standalone build where everything is bundled together
    file_parent = file_path.parent.parent  # Go up to the dist directory
    has_nested_laser_gates = file_path.parts[-3:-1] == ("laser_gates", "laser_gates")

    if has_nested_laser_gates and exe_parent == file_parent:
        # Deployed environment - use executable directory
        return str(exe_parent / relative_path)

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
