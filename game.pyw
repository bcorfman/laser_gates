import argparse
import logging
import sys
from pathlib import Path

from actions import set_debug_actions

from laser_gates.app import run


def setup_logging():
    """Configure logging to file."""
    # Determine the directory to place the log file
    if getattr(sys, "frozen", False):
        # Running as compiled executable (e.g., Nuitka, AppImage)
        exe_dir = Path(sys.executable).parent
    else:
        # Running as Python script
        exe_dir = Path(__file__).parent

    # Try to place log file next to executable first
    log_file = exe_dir / "game.log"
    
    # Check if we can write to the executable directory
    # If not (e.g., AppImage read-only mount), use user data directory
    try:
        # Try to create/check write access to the directory
        test_file = exe_dir / ".write_test"
        test_file.touch()
        test_file.unlink()
    except (OSError, PermissionError):
        # Can't write to executable directory, use user data directory
        log_dir = Path.home() / ".local" / "share" / "laser_gates"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "game.log"

    # Configure logging to write to file only
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
        ],
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized. Log file: {log_file}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Laser Gates")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging to file",
    )
    parser.add_argument(
        "--debug-actions",
        action="store_true",
        help="Enable debug output for action creation",
    )
    args = parser.parse_args()

    # Setup logging only if --debug flag is passed
    if args.debug:
        setup_logging()
        logger = logging.getLogger(__name__)
        logger.info("Starting game with debug logging enabled")
    else:
        logger = None

    try:
        # Enable debug action logging if requested.
        # Note: environment variable ARCADEACTIONS_DEBUG is applied automatically
        # at import time; this flag only enables additional logging (does not disable).
        if args.debug_actions:
            set_debug_actions(True)

        if logger:
            logger.info("Starting game")
        run()
    except Exception:
        if logger:
            logger.exception("Fatal error in main")
        raise


if __name__ == "__main__":
    main()
