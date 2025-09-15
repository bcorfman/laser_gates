"""Enemy wave implementations."""

from abc import ABC, abstractmethod

import arcade
from actions import Action, arrange_grid, infinite, move_until

from .config import TUNNEL_VELOCITY, TUNNEL_WALL_HEIGHT, WALL_WIDTH, WINDOW_HEIGHT, WINDOW_WIDTH
from .contexts import WaveContext


class EnemyWave(ABC):
    """
    Behaviour strategy for a wave.

    A wave owns NO sprites—it receives the SpriteList that Tunnel created.
    """

    @property
    @abstractmethod
    def actions(self) -> list[Action]:
        """Return a list of actions that are currently active for this wave."""
        pass

    @abstractmethod
    def build(self, sprites: arcade.SpriteList, ctx: WaveContext) -> None:
        """Populate *sprites* and add actions (move_until, etc.)."""
        pass

    @abstractmethod
    def update(self, sprites: arcade.SpriteList, ctx: WaveContext, dt: float) -> None:
        """Per-frame logic (collision tests, win/loss checks)."""
        pass


def make_shield(width):
    """Create shield blocks"""

    def make_shield_block() -> arcade.Sprite:
        """Factory that creates a single shield block sprite."""
        return arcade.SpriteSolidColor(10, 12, color=arcade.color.GRAY)

    # Build shield by creating a small grid of blocks
    shield_grid = arrange_grid(
        rows=30,
        cols=width,
        start_x=WINDOW_WIDTH + WALL_WIDTH,
        start_y=TUNNEL_WALL_HEIGHT,  # Position shields between player and enemies
        spacing_x=10,
        spacing_y=12,
        sprite_factory=make_shield_block,
    )
    return shield_grid


class DensePackWave(EnemyWave):
    def __init__(self, wall_width: int):
        self._width = wall_width
        self._actions = []

    @property
    def actions(self) -> list[Action]:
        """Return a list of actions that are currently active for this wave."""
        return self._actions

    def build(self, sprites: arcade.SpriteList, ctx: WaveContext) -> None:
        """Populate enemy sprites and add actions (move_until, etc.)."""
        shield = make_shield(self._width)
        sprites.extend(shield)

        # Use the player's current speed factor to set initial velocity
        current_velocity = TUNNEL_VELOCITY * ctx.player_ship.speed_factor

        action = move_until(
            sprites,
            velocity=(current_velocity, 0),
            condition=infinite,
            bounds=(
                -WALL_WIDTH,
                0,
                WINDOW_WIDTH + WALL_WIDTH + WALL_WIDTH,
                WINDOW_HEIGHT,
            ),
            boundary_behavior="limit",
            on_boundary_enter=lambda sprite, axis, side: ctx.on_cleanup(self),
            tag="shield_move",
        )
        self._actions.append(action)

    def update(self, sprites: arcade.SpriteList, ctx: WaveContext, dt: float) -> None:
        """Per-frame logic (collision tests, win/loss checks)."""
        # Handle collisions between player shots and the dense pack sprites
        if not sprites:
            return

        # Shot collisions
        for shot in tuple(ctx.shot_list):
            hits = arcade.check_for_collision_with_list(shot, sprites)
            if hits:
                shot.remove_from_sprite_lists()
                for block in hits:
                    block.remove_from_sprite_lists()

        # Player collisions
        if arcade.check_for_collision_with_list(ctx.player_ship, sprites):
            ctx.register_damage(0.3)
            ctx.on_cleanup(self)
            return

        # Wave complete?
        if len(sprites) == 0:
            ctx.on_cleanup(self)


class ThinDensePackWave(DensePackWave):
    def __init__(self):
        super().__init__(wall_width=5)


class ThickDensePackWave(DensePackWave):
    def __init__(self):
        super().__init__(wall_width=10)
