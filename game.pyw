import argparse
import logging
import os
import sys
from pathlib import Path

# Allow imports from src/ without installing the package
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from actions import set_debug_actions

from laser_gates.app import run


def setup_logging():
    """Configure logging to file."""
    # Determine the directory to place the log file
    if getattr(sys, "frozen", False):
        # Running as compiled executable (e.g., Nuitka)
        if sys.platform == "win32":
            # On Windows with Nuitka, executable is typically in dist/ or build/
            exe_dir = Path(sys.executable).parent
        else:
            exe_dir = Path(sys.executable).parent
    else:
        # Running as Python script
        exe_dir = Path(__file__).parent

    # Place log file directly next to executable
    log_file = exe_dir / "game.log"

    # Configure logging to write to both file and stderr
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stderr),  # Still try to log to stderr if possible
        ],
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized. Log file: {log_file}")


def main():
    """Main function."""
    # Setup logging first so we can capture any errors
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        parser = argparse.ArgumentParser(description="Laser Gates")
        parser.add_argument(
            "--debug-actions",
            action="store_true",
            help="Enable debug output for action creation",
        )
        args = parser.parse_args()

        # Enable debug action logging if requested.
        # Note: environment variable ARCADEACTIONS_DEBUG is applied automatically
        # at import time; this flag only enables additional logging (does not disable).
        if args.debug_actions:
            set_debug_actions(True)

        logger.info("Starting game")
        run()
    except Exception:
        logger.exception("Fatal error in main")
        raise


if __name__ == "__main__":
    main()
