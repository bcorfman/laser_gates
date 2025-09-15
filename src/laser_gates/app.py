"""Application window and runner."""

import arcade
from actions import center_window

from .config import WINDOW_HEIGHT, WINDOW_WIDTH
from .view import Tunnel


class LaserGates(arcade.Window):
    def __init__(self):
        # Create the window hidden so we can move it before it ever appears.
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, "Laser Gates", visible=False)

        # Center while the window is still invisible to avoid a visible jump.
        center_window(self)

        # Now make the window visible and proceed normally.
        self.set_visible(True)
        self.show_view(Tunnel())


def run():
    """Run the Laser Gates game."""
    window = LaserGates()
    arcade.run()
