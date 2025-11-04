"""Base class for enemy wave implementations."""

from abc import ABC, abstractmethod

import arcade
from actions import Action

from ..contexts import WaveContext


class EnemyWave(ABC):
    """
    Behaviour strategy for a wave.

    A wave owns NO sprites—it receives the SpriteList that Tunnel created.
    """

    def __init__(self):
        self._actions = []
        self._scroll_actions = []  # Track horizontal scroll actions separately

    @property
    def actions(self) -> list[Action]:
        """Return a list of actions that are currently active for this wave."""
        return self._actions

    def update_scroll_velocity(self, speed: float) -> None:
        """Update horizontal scroll velocity for wave actions.

        Updates only the scroll actions tracked in _scroll_actions.
        Subclasses should add actions to _scroll_actions when creating them.

        Args:
            speed: New horizontal scroll velocity in pixels per frame
        """
        for action in self._scroll_actions:
            action.set_current_velocity((speed, 0))

    @abstractmethod
    def build(self, ctx: WaveContext) -> arcade.SpriteList:
        """Populate *sprites* and add actions (move_until, etc.)."""
        pass

    @abstractmethod
    def add_draw_order(self) -> tuple[int, arcade.SpriteList]:
        pass

    @abstractmethod
    def update(self, ctx: WaveContext) -> None:
        """Per-frame logic (collision tests, win/loss checks)."""
        pass

    @abstractmethod
    def cleanup(self, ctx: WaveContext) -> None:
        """Clean up the wave and release all sprites back to the pool."""
        pass
