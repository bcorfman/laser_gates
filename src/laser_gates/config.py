"""Game configuration constants."""

import sys
from pathlib import Path


def get_resource_path(relative_path: str) -> str:
    """Get the absolute path to a resource file.

    Works both when running as a Python script and when compiled with Nuitka.
    When frozen (Nuitka), resources are extracted to the temporary directory.
    """
    # Debug logging at start
    import logging

    logger = logging.getLogger(__name__)
    logger.info(f"get_resource_path called with: {relative_path}")
    logger.info(f"sys.frozen: {getattr(sys, 'frozen', 'Not set')}")
    logger.info(f"__file__: {__file__}")
    logger.info(f"sys.executable: {sys.executable}")

    # Check if we're in a frozen environment (PyInstaller, Nuitka, etc.)
    if getattr(sys, "frozen", False):
        # Running as compiled executable (Nuitka or PyInstaller)
        # sys._MEIPASS is set by both PyInstaller and Nuitka to the temp extraction directory
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            base_path = Path(meipass)
            exe_path = None
        else:
            # For Nuitka standalone, resources are in the same directory as the executable
            # Resolve sys.executable to handle symlinks, then get parent
            exe_path = Path(sys.executable).resolve()
            base_path = exe_path.parent

        # Debug logging
        logger.info(f"Frozen build - sys._MEIPASS: {getattr(sys, '_MEIPASS', 'Not set')}")
        logger.info(f"Frozen build - sys.executable: {sys.executable}")
        if exe_path:
            logger.info(f"Frozen build - exe_path (resolved): {exe_path}")
        logger.info(f"Frozen build - base_path: {base_path}")

        full_path = base_path / relative_path
        logger.info(f"Looking for resource at: {full_path}")
        # Resolve the path here to avoid arcade having to resolve it later
        # This handles symlinks and ensures the path is absolute
        resolved_path = full_path.resolve(strict=False)
        logger.info(f"Resolved resource path: {resolved_path}")
        return str(resolved_path)

    # Check if we're running from a Nuitka executable (even if sys.frozen is False)
    # Nuitka sometimes doesn't set sys.frozen, but we can detect it by checking if
    # __file__ points to a module in a dist directory structure, or if sys.executable
    # doesn't look like a regular Python interpreter
    try:
        file_path = Path(__file__)
        # Check if __file__ looks like it's in a Nuitka dist structure
        # Typically: contains .dist or similar build artifacts
        file_str = str(file_path)
        exe_name = Path(sys.executable).name

        # Detected if __file__ contains .dist/build OR sys.executable is not a standard Python interpreter
        # Standard interpreters: python, python3, python.exe, python3.exe, python3.x, etc.
        is_nuitka_build = any(indicator in file_str.lower() for indicator in [".dist", "build"])
        # Check if executable name looks like a standard Python interpreter
        is_standard_python = exe_name.startswith("python")
        is_non_standard_exe = not is_standard_python

        if is_nuitka_build or is_non_standard_exe:
            # Likely a Nuitka build where sys.frozen wasn't set
            # Use sys.executable to find the directory
            exe_dir = Path(sys.executable).resolve().parent
            full_path = exe_dir / relative_path
            logger.info(
                f"Nuitka build detected - is_nuitka_build: {is_nuitka_build}, is_non_standard_exe: {is_non_standard_exe}, exe_name: {exe_name}"
            )
            logger.info(f"Using exe_dir: {exe_dir}")
            logger.info(f"Looking for resource at: {full_path}")
            resolved_path = full_path.resolve(strict=False)
            logger.info(f"Resolved resource path: {resolved_path}")
            return str(resolved_path)
    except Exception:
        pass

    # Running as Python script
    # Find the project root (parent of src/)
    script_dir = Path(__file__).parent  # src/laser_gates
    project_root = script_dir.parent.parent  # project root

    # Debug logging for development mode
    logger.info(f"Development mode - __file__: {__file__}")
    logger.info(f"Development mode - script_dir: {script_dir}")
    logger.info(f"Development mode - project_root: {project_root}")

    result_path = str(project_root / relative_path)
    logger.info(f"Development mode - final path: {result_path}")
    return result_path


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
