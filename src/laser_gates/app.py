"""Application window and runner."""

import arcade
from actions import center_window

from .config import WINDOW_HEIGHT, WINDOW_WIDTH
from .view import Tunnel


class LaserGates(arcade.Window):
    def __init__(self):
        import logging

        logger = logging.getLogger(__name__)

        logger.debug("Initializing LaserGates window")

        try:
            # Create the window hidden so we can move it before it ever appears.
            logger.debug(f"Creating window with size {WINDOW_WIDTH}x{WINDOW_HEIGHT}")
            super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, "Laser Gates", visible=False)

            # Center while the window is still invisible to avoid a visible jump.
            logger.debug("Centering window")
            center_window(self)

            # Now make the window visible and proceed normally.
            logger.debug("Showing window and view")
            self.set_visible(True)
            logger.debug("Creating Tunnel view")
            self.show_view(Tunnel())
            logger.debug("Window initialization complete")
        except Exception:
            logger.exception("Error initializing window")
            raise


def run():
    """Run the Laser Gates game."""
    import logging

    logger = logging.getLogger(__name__)

    logger.info("Creating window")
    window = LaserGates()

    try:
        logger.info("Starting Arcade run loop")
        arcade.run()
        logger.info("Arcade run loop ended normally")
    except Exception:
        logger.exception("Error during game execution")
        raise
    finally:
        # Ensure mouse cursor is restored even if the game exits unexpectedly
        try:
            window.set_mouse_visible(True)
        except (AttributeError, RuntimeError):
            # Window might be closed or invalid, ignore cursor restoration errors
            pass
