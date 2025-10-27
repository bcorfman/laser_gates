"""Enemy wave implementations."""

from abc import ABC, abstractmethod

import arcade
from actions import (
    Action,
    BlinkUntil,
    CallbackUntil,
    MoveUntil,
    MoveXUntil,
    MoveYUntil,
    arrange_grid,
    cycle_textures_until,
    infinite,
    move_until,
    parallel,
)

from . import resources
from .config import (
    FORCEFIELD,
    FORCEFIELD_SOLID_COLORS,
    HILL_HEIGHT,
    TUNNEL_VELOCITY,
    TUNNEL_WALL_HEIGHT,
    WALL_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from .contexts import WaveContext
from .resources import SpritePool


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
    def cleanup(self) -> None:
        """Clean up the wave and release all sprites back to the pool."""
        pass


class _DensePackWave(EnemyWave):
    def __init__(self, wall_width: int):
        super().__init__()

        def make_shield_block() -> arcade.Sprite:
            """Factory that creates a single shield block sprite."""
            return arcade.SpriteSolidColor(10, 12, color=arcade.color.GRAY)

        self._width = wall_width
        self._shield_pool = SpritePool(make_shield_block, size=300)  # 10 width * 30 height = 300 max
        self._shield_sprites = arcade.SpriteList()

    def build(self, ctx: WaveContext) -> arcade.SpriteList:
        """Populate enemy sprites and add actions (move_until, etc.)."""
        # Acquire sprites from our instance pool
        num_blocks = self._width * 30  # rows=30, cols=width
        self._shield_sprites = self._shield_pool.acquire(num_blocks)

        # Position the sprites in a grid via ArcadeActions (layout-only)
        arrange_grid(
            rows=30,
            cols=self._width,
            start_x=WINDOW_WIDTH + WALL_WIDTH,
            start_y=TUNNEL_WALL_HEIGHT,
            spacing_x=10,
            spacing_y=12,
            sprites=self._shield_sprites,
        )

        # Make sprites visible and add to the main sprite list
        for sprite in self._shield_sprites:
            sprite.visible = True

        # Use the player's current speed factor to set initial velocity
        current_velocity = TUNNEL_VELOCITY * ctx.player_ship.speed_factor

        action = move_until(
            self._shield_sprites,
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
        self._scroll_actions.append(action)  # Track for velocity updates

    def add_draw_order(self) -> list[tuple[int, arcade.SpriteList]]:
        return [(5, self._shield_sprites)]

    def update(self, ctx: WaveContext) -> None:
        """Per-frame logic (collision tests, win/loss checks)."""
        # Handle collisions between player shots and the dense pack sprites
        if not self._shield_sprites:
            return
        self._shield_sprites.update()
        # Shot collisions
        destroyed_blocks = []
        for shot in tuple(ctx.shot_list):
            hits = arcade.check_for_collision_with_list(shot, self._shield_sprites)
            if hits:
                shot.remove_from_sprite_lists()  # remove shot immediately
                destroyed_blocks.extend(hits)  # defer block cleanup to pool

        # Release destroyed blocks back to the pool
        if destroyed_blocks:
            self._shield_pool.release(destroyed_blocks)

        # Player collisions
        if arcade.check_for_collision_with_list(ctx.player_ship, self._shield_sprites):
            ctx.register_damage(0.8)
            ctx.on_cleanup(self)
            return

    def cleanup(self, ctx: WaveContext) -> None:
        """Release all sprites back to the pool and clean up the wave."""
        for action in self._actions:
            action.stop()
        self._actions.clear()
        self._shield_pool.release_all()


class ThinDensePackWave(_DensePackWave):
    def __init__(self):
        super().__init__(wall_width=5)


class ThickDensePackWave(_DensePackWave):
    def __init__(self):
        super().__init__(wall_width=10)


class ForcefieldWave(EnemyWave):
    def __init__(self, total_forcefields):
        super().__init__()
        self._total_forcefields = total_forcefields
        self._forcefield_spacing = 220
        self._forcefield_textures = resources.create_forcefield_textures(FORCEFIELD)
        self._top_forcefields = arcade.SpriteList()
        self._bottom_forcefields = arcade.SpriteList()
        self._top_mid_forcefields = arcade.SpriteList()
        self._bottom_mid_forcefields = arcade.SpriteList()
        for _ in range(self._total_forcefields):
            self._top_forcefields.append(arcade.SpriteSolidColor(53, HILL_HEIGHT, color=FORCEFIELD_SOLID_COLORS[0]))
            self._bottom_forcefields.append(arcade.SpriteSolidColor(53, HILL_HEIGHT, color=FORCEFIELD_SOLID_COLORS[0]))
            self._top_mid_forcefields.append(arcade.Sprite(FORCEFIELD, scale=(1.5, 1)))
            self._bottom_mid_forcefields.append(arcade.Sprite(FORCEFIELD, scale=(1.5, 1)))
        self._initial_forcefields = arcade.SpriteList()
        self._last_forcefield = arcade.SpriteList()
        self._current_color_index = 0
        self._num_forcefield_colors = len(FORCEFIELD_SOLID_COLORS)
        for i in range(self._total_forcefields - 1):
            self._initial_forcefields.append(self._top_forcefields[i])
            self._initial_forcefields.append(self._top_mid_forcefields[i])
            self._initial_forcefields.append(self._bottom_mid_forcefields[i])
            self._initial_forcefields.append(self._bottom_forcefields[i])
        self._last_forcefield.append(self._top_forcefields[self._total_forcefields - 1])
        self._last_forcefield.append(self._top_mid_forcefields[self._total_forcefields - 1])
        self._last_forcefield.append(self._bottom_mid_forcefields[self._total_forcefields - 1])
        self._last_forcefield.append(self._bottom_forcefields[self._total_forcefields - 1])

    def cleanup(self, ctx: WaveContext) -> None:
        for action in self._actions:
            action.stop()
        self._initial_forcefields.visible = False
        self._last_forcefield.visible = False
        self._current_color_index = 0
        self._actions.clear()

    def _update_color(self):
        self._current_color_index = (self._current_color_index + 1) % self._num_forcefield_colors
        for i in range(self._total_forcefields):
            self._top_forcefields[i].color = FORCEFIELD_SOLID_COLORS[self._current_color_index]
            self._bottom_forcefields[i].color = FORCEFIELD_SOLID_COLORS[self._current_color_index]

    def _position_forcefield(self, i: int):
        self._bottom_forcefields[i].left = WINDOW_WIDTH + WALL_WIDTH + i * self._forcefield_spacing
        self._bottom_forcefields[i].bottom = TUNNEL_WALL_HEIGHT
        self._bottom_mid_forcefields[i].left = WINDOW_WIDTH + WALL_WIDTH + i * self._forcefield_spacing
        self._bottom_mid_forcefields[i].bottom = TUNNEL_WALL_HEIGHT + HILL_HEIGHT
        self._top_mid_forcefields[i].left = WINDOW_WIDTH + WALL_WIDTH + i * self._forcefield_spacing
        self._top_mid_forcefields[i].bottom = TUNNEL_WALL_HEIGHT + HILL_HEIGHT + 109
        self._top_forcefields[i].left = WINDOW_WIDTH + WALL_WIDTH + i * self._forcefield_spacing
        self._top_forcefields[i].bottom = TUNNEL_WALL_HEIGHT + HILL_HEIGHT + 109 * 2

    def _create_move_action(self, i: int, vel: int, ctx: WaveContext) -> MoveUntil:
        if i < self._total_forcefields - 1:
            return MoveUntil(velocity=(vel, 0), condition=infinite)
        return MoveUntil(
            velocity=(vel, 0),
            condition=infinite,
            bounds=(
                -WALL_WIDTH,
                0,
                WINDOW_WIDTH + WALL_WIDTH + WALL_WIDTH,
                WINDOW_HEIGHT,
            ),
            boundary_behavior="limit",
            on_boundary_enter=lambda sprite, axis, side: ctx.on_cleanup(self),
        )

    def _add_color_update_callback(self) -> None:
        call_action = CallbackUntil(
            seconds_between_calls=0.1,
            callback=self._update_color,
            condition=infinite,
        )
        call_action.apply(self._top_forcefields)
        self._actions.append(call_action)

    def _add_middle_animation_actions(self) -> None:
        cycle_top = cycle_textures_until(
            self._top_mid_forcefields,
            textures=self._forcefield_textures,
            frames_per_second=100,
            direction=-1,
            condition=infinite,
        )
        self._actions.append(cycle_top)
        cycle_bottom = cycle_textures_until(
            self._bottom_mid_forcefields,
            textures=self._forcefield_textures,
            frames_per_second=100,
            direction=1,
            condition=infinite,
        )
        self._actions.append(cycle_bottom)


class FlashingForcefieldWave(ForcefieldWave):
    def __init__(self, total_forcefields):
        super().__init__(total_forcefields)
        self._forcefields_active = False  # Track whether forcefields are currently active for collisions

    def _forcefields_on(self, spritelist: arcade.SpriteList):
        self._forcefields_active = True

    def _forcefields_off(self, spritelist: arcade.SpriteList):
        self._forcefields_active = False

    def _setup_forcefield_action(self, i: int, vel: int, ctx: WaveContext):
        move_action = self._create_move_action(i, vel, ctx)

        blink_action = BlinkUntil(
            seconds_until_change=0.5,
            condition=infinite,
            on_blink_enter=self._forcefields_on,
            on_blink_exit=self._forcefields_off,
        )
        combined_actions = parallel(move_action, blink_action)
        if i < self._total_forcefields - 1:
            combined_actions.apply(self._initial_forcefields)
        else:
            combined_actions.apply(self._last_forcefield)
        self._actions.append(combined_actions)
        self._scroll_actions.append(move_action)  # Track scroll action for velocity updates
        if i == self._total_forcefields - 1:
            self._add_color_update_callback()
            self._add_middle_animation_actions()

    def build(self, ctx: WaveContext) -> arcade.SpriteList:
        """Populate enemy sprites and add actions (move_until, etc.)."""
        current_velocity = TUNNEL_VELOCITY * ctx.player_ship.speed_factor

        for i in range(self._total_forcefields):
            self._position_forcefield(i)
        for i in range(self._total_forcefields - 2, self._total_forcefields):
            self._setup_forcefield_action(i, current_velocity, ctx)

        self._initial_forcefields.visible = True
        self._last_forcefield.visible = True
        self._forcefields_active = True

    def add_draw_order(self) -> list[tuple[int, arcade.SpriteList]]:
        return [(5, self._initial_forcefields), (6, self._last_forcefield)]

    def update(self, ctx: WaveContext) -> None:
        """Per-frame logic (collision tests, win/loss checks)."""
        # Handle collisions between player shots and the forcefields
        if not self._last_forcefield:
            return
        self._initial_forcefields.update()
        self._last_forcefield.update()

        # Shot collisions - only check when forcefields are active
        if self._forcefields_active:
            for shot in tuple(ctx.shot_list):
                hits = arcade.check_for_collision_with_list(
                    shot, self._initial_forcefields
                ) or arcade.check_for_collision_with_list(shot, self._last_forcefield)
                if hits:
                    shot.remove_from_sprite_lists()  # remove shot immediately

        # Player collisions - only check when forcefields are active
        if self._forcefields_active and (
            arcade.check_for_collision_with_list(ctx.player_ship, self._initial_forcefields)
            or arcade.check_for_collision_with_list(ctx.player_ship, self._last_forcefield)
        ):
            ctx.register_damage(1.0)
            ctx.on_cleanup(self)
            return

    def cleanup(self, ctx: WaveContext) -> None:
        self._forcefields_active = False
        super().cleanup(ctx)


class FlexingForcefieldWave(ForcefieldWave):
    def __init__(self, total_forcefields):
        super().__init__(total_forcefields)

    def _setup_forcefield_action(self, i: int, vel: int, ctx: WaveContext):
        # Horizontal scroll (all four bars in this slice)
        # Only attach cleanup callback to the LAST forcefield
        def cleanup_wrapper(s, axis, side):
            # Only cleanup when hitting the LEFT boundary (sprites scrolling off-screen)
            if axis == "x" and side == "left":
                ctx.on_cleanup(self)

        on_boundary_callback = cleanup_wrapper if i == self._total_forcefields - 1 else None

        scroll_x = MoveXUntil(
            velocity=(vel, 0),  # vel is already negative
            condition=infinite,
            bounds=(
                -WALL_WIDTH,
                0,
                WINDOW_WIDTH + WALL_WIDTH + self._forcefield_spacing * self._total_forcefields,
                WINDOW_HEIGHT,
            ),
            boundary_behavior="limit",
            on_boundary_enter=on_boundary_callback,
        )

        # Apply X scroll to the correct sprite-list slice
        target = self._initial_forcefields if i < self._total_forcefields - 1 else self._last_forcefield
        scroll_x.apply(target)
        self._actions.append(scroll_x)
        self._scroll_actions.append(scroll_x)  # Track horizontal scroll action for velocity updates

        # Only set up Y-bounce actions once (on the last iteration)
        if i == self._total_forcefields - 1:
            # Vertical bounces – apply to their own mid-bars only
            bounce_top = MoveYUntil(
                velocity=(0, -2),
                condition=infinite,
                bounds=(
                    -WALL_WIDTH,
                    TUNNEL_WALL_HEIGHT + HILL_HEIGHT + 109 + 109 / 2,
                    WINDOW_WIDTH + WALL_WIDTH + self._forcefield_spacing * self._total_forcefields,
                    TUNNEL_WALL_HEIGHT + HILL_HEIGHT + 109 * 2 + 109 / 2,
                ),
                boundary_behavior="bounce",
            )
            bounce_top.apply(self._top_mid_forcefields)

            bounce_bottom = MoveYUntil(
                velocity=(0, 2),
                condition=infinite,
                bounds=(
                    -WALL_WIDTH,
                    TUNNEL_WALL_HEIGHT + HILL_HEIGHT - 109 / 2,
                    WINDOW_WIDTH + WALL_WIDTH + self._forcefield_spacing * self._total_forcefields,
                    TUNNEL_WALL_HEIGHT + HILL_HEIGHT + 109 / 2,
                ),
                boundary_behavior="bounce",
            )
            bounce_bottom.apply(self._bottom_mid_forcefields)

            self._actions.extend([bounce_top, bounce_bottom])
            self._add_color_update_callback()
            self._add_middle_animation_actions()

    def build(self, ctx: WaveContext) -> arcade.SpriteList:
        """Populate enemy sprites and add actions (move_until, etc.)."""
        current_velocity = TUNNEL_VELOCITY * ctx.player_ship.speed_factor
        for i in range(self._total_forcefields):
            self._position_forcefield(i)
        for i in range(self._total_forcefields - 2, self._total_forcefields):
            self._setup_forcefield_action(i, current_velocity, ctx)

        self._initial_forcefields.visible = True
        self._last_forcefield.visible = True

    def add_draw_order(self) -> list[tuple[int, arcade.SpriteList]]:
        return [
            (5, self._top_forcefields),
            (6, self._bottom_forcefields),
            (7, self._top_mid_forcefields),
            (8, self._bottom_mid_forcefields),
        ]

    def update(self, ctx: WaveContext) -> None:
        """Per-frame logic (collision tests, win/loss checks)."""
        # Handle collisions between player shots and the forcefields
        if not self._last_forcefield:
            return
        self._initial_forcefields.update()
        self._last_forcefield.update()

        # Shot collisions
        for shot in tuple(ctx.shot_list):
            hits = arcade.check_for_collision_with_list(
                shot, self._initial_forcefields
            ) or arcade.check_for_collision_with_list(shot, self._last_forcefield)
            if hits:
                shot.remove_from_sprite_lists()  # remove shot immediately

        # Player collisions
        if arcade.check_for_collision_with_list(
            ctx.player_ship, self._initial_forcefields
        ) or arcade.check_for_collision_with_list(ctx.player_ship, self._last_forcefield):
            ctx.register_damage(1.0)
            ctx.on_cleanup(self)
            return

    def cleanup(self, ctx: WaveContext) -> None:
        for action in self._actions:
            action.stop()
        self._initial_forcefields.visible = False
        self._last_forcefield.visible = False
        self._current_color_index = 0
        self._actions.clear()
