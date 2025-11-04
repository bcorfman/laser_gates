"""Forcefield wave implementations."""

import arcade
from actions import (
    BlinkUntil,
    CallbackUntil,
    MoveUntil,
    MoveXUntil,
    MoveYUntil,
    cycle_textures_until,
    infinite,
    parallel,
)

from .. import resources
from ..config import (
    FORCEFIELD,
    FORCEFIELD_SOLID_COLORS,
    HILL_HEIGHT,
    TUNNEL_VELOCITY,
    TUNNEL_WALL_HEIGHT,
    WALL_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from ..contexts import WaveContext
from .wave_base import EnemyWave


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

        return arcade.SpriteList()  # Forcefield waves manage their own sprite lists

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

        return arcade.SpriteList()  # Forcefield waves manage their own sprite lists

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
