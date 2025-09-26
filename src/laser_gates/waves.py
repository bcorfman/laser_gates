"""Enemy wave implementations."""

from abc import ABC, abstractmethod

import arcade
from actions import Action, arrange_grid, infinite, move_until

from . import resources
from .config import FORCEFIELD, TUNNEL_VELOCITY, TUNNEL_WALL_HEIGHT, WALL_WIDTH, WINDOW_HEIGHT, WINDOW_WIDTH
from .contexts import WaveContext
from .resources import SpritePool


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
    def build(self, ctx: WaveContext) -> arcade.SpriteList:
        """Populate *sprites* and add actions (move_until, etc.)."""
        pass

    @abstractmethod
    def update(self, sprites: arcade.SpriteList, ctx: WaveContext, dt: float) -> None:
        """Per-frame logic (collision tests, win/loss checks)."""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Clean up the wave and release all sprites back to the pool."""
        pass


class _DensePackWave(EnemyWave):
    def __init__(self, wall_width: int):
        self._width = wall_width
        self._actions = []

        def make_shield_block() -> arcade.Sprite:
            """Factory that creates a single shield block sprite."""
            return arcade.SpriteSolidColor(10, 12, color=arcade.color.GRAY)

        self._shield_pool = SpritePool(make_shield_block, size=300)  # 10 width * 30 height = 300 max

    @property
    def actions(self) -> list[Action]:
        """Return a list of actions that are currently active for this wave."""
        return self._actions

    def build(self, ctx: WaveContext) -> arcade.SpriteList:
        """Populate enemy sprites and add actions (move_until, etc.)."""
        # Acquire sprites from our instance pool
        num_blocks = self._width * 30  # rows=30, cols=width
        shield_sprites = self._shield_pool.acquire(num_blocks)

        # Position the sprites in a grid via ArcadeActions (layout-only)
        arrange_grid(
            rows=30,
            cols=self._width,
            start_x=WINDOW_WIDTH + WALL_WIDTH,
            start_y=TUNNEL_WALL_HEIGHT,
            spacing_x=10,
            spacing_y=12,
            sprites=shield_sprites,
        )

        # Make sprites visible and add to the main sprite list
        for sprite in shield_sprites:
            sprite.visible = True

        # Use the player's current speed factor to set initial velocity
        current_velocity = TUNNEL_VELOCITY * ctx.player_ship.speed_factor

        action = move_until(
            shield_sprites,
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
        return shield_sprites

    def update(self, sprites: arcade.SpriteList, ctx: WaveContext, dt: float) -> None:
        """Per-frame logic (collision tests, win/loss checks)."""
        # Handle collisions between player shots and the dense pack sprites
        if not sprites:
            return

        # Shot collisions
        destroyed_blocks = []
        for shot in tuple(ctx.shot_list):
            hits = arcade.check_for_collision_with_list(shot, sprites)
            if hits:
                shot.remove_from_sprite_lists()  # remove shot immediately
                destroyed_blocks.extend(hits)  # defer block cleanup to pool

        # Release destroyed blocks back to the pool
        if destroyed_blocks:
            self._shield_pool.release(destroyed_blocks)

        # Player collisions
        if arcade.check_for_collision_with_list(ctx.player_ship, sprites):
            print("player collision")
            ctx.register_damage(0.8)
            ctx.on_cleanup(self)
            return

    def cleanup(self, ctx: WaveContext) -> None:
        """Release all sprites back to the pool and clean up the wave."""
        self._shield_pool.release_all()


class ThinDensePackWave(_DensePackWave):
    def __init__(self):
        super().__init__(wall_width=5)


class ThickDensePackWave(_DensePackWave):
    def __init__(self):
        super().__init__(wall_width=10)


class FlashingForcefieldWave(EnemyWave):
    def __init__(self):
        self.forcefield_textures = resources.create_forcefield_textures(FORCEFIELD)
        self._actions = []

    @property
    def actions(self) -> list[Action]:
        """Return a list of actions that are currently active for this wave."""
        return self._actions
