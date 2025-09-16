"""Main game view implementation."""

import random

import arcade
from actions import Action, infinite, move_until

from .config import (
    BOTTOM_BOUNDS,
    HILL_SLICES,
    HILL_WIDTH,
    TOP_BOUNDS,
    TUNNEL_VELOCITY,
    TUNNEL_WALL_HEIGHT,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from .contexts import PlayerContext, WaveContext
from .player import PlayerShip
from .utils import create_sprite_at_location, create_tunnel_wall
from .waves import ThickDensePackWave, ThinDensePackWave


class Tunnel(arcade.View):
    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.BLACK
        self.player_list = arcade.SpriteList()
        self.shot_list = arcade.SpriteList()
        self.tunnel_walls = arcade.SpriteList()
        self.hill_tops = arcade.SpriteList()
        self.hill_bottoms = arcade.SpriteList()
        self.left_pressed = self.right_pressed = False
        self.up_pressed = self.down_pressed = False
        self.fire_pressed = False
        self.speed_factor = 1
        self.speed = TUNNEL_VELOCITY * self.speed_factor
        self.damage_flash = 0.0  # Visual feedback for hill collisions
        self._wave_sprites = arcade.SpriteList()
        self._wave_strategy = None
        self._hill_top_action = None
        self._hill_bottom_action = None
        self.setup_walls()
        self.setup_hills()
        self.setup_ship()

        # Don't show the mouse cursor
        self.window.set_mouse_visible(False)

        # Wave classes that can be instantiated
        self.wave_classes = [ThinDensePackWave, ThickDensePackWave]

        # Create context for waves
        self._ctx = WaveContext(
            shot_list=self.shot_list,
            player_ship=self.ship,
            register_damage=self._flash_damage,
            on_cleanup=self._wave_finished,
        )

        self.set_tunnel_velocity(self.speed)
        self._start_random_wave()

    def _start_random_wave(self):
        if not self.wave_classes:
            return
        self._wave_sprites.clear()
        wave_cls = random.choice(self.wave_classes)
        self._wave_strategy = wave_cls()
        self._wave_strategy.build(self._wave_sprites, self._ctx)

    def _wave_finished(self, wave):
        """Callback when a wave signals it is finished.

        Stops all actions associated with *wave* to ensure they no longer
        run once the wave has been cleaned up.
        """
        # Stop movement actions tied to the current wave's sprite list
        Action.stop_actions_for_target(self._wave_sprites, tag="shield_move")
        # Also stop any extra references kept in the wave's local list (defensive)
        for action in wave.actions:
            action.stop()
        self._wave_strategy = None
        self._start_random_wave()

    def _flash_damage(self, amount: float):
        """Register damage and trigger visual flash effect."""
        self.damage_flash = min(self.damage_flash + amount, 1.0)

    def set_tunnel_velocity(self, speed):
        # Reuse existing actions and adjust velocity instead of recreating
        if self._hill_top_action is None or self._hill_top_action.done:
            self._hill_top_action = move_until(
                self.hill_tops,
                velocity=(speed, 0),
                condition=infinite,
                bounds=TOP_BOUNDS,
                boundary_behavior="wrap",
                on_boundary_enter=self.on_hill_top_wrap,
                tag="tunnel_velocity",
            )
        else:
            self._hill_top_action.set_current_velocity((speed, 0))

        if self._hill_bottom_action is None or self._hill_bottom_action.done:
            self._hill_bottom_action = move_until(
                self.hill_bottoms,
                velocity=(speed, 0),
                condition=infinite,
                bounds=BOTTOM_BOUNDS,
                boundary_behavior="wrap",
                on_boundary_enter=self.on_hill_bottom_wrap,
                tag="tunnel_velocity",
            )
        else:
            self._hill_bottom_action.set_current_velocity((speed, 0))

        if self._wave_strategy and self._wave_strategy.actions is not None:
            for action in self._wave_strategy.actions:
                action.set_current_velocity((speed, 0))

    def on_hill_top_wrap(self, sprite, axis, side):
        sprite.position = (HILL_WIDTH * 3, sprite.position[1])

    def on_hill_bottom_wrap(self, sprite, axis, side):
        sprite.position = (HILL_WIDTH * 3, sprite.position[1])

    def setup_ship(self):
        player_ctx = PlayerContext(
            shot_list=self.shot_list,
            hill_tops=self.hill_tops,
            hill_bottoms=self.hill_bottoms,
            tunnel_walls=self.tunnel_walls,
            set_tunnel_velocity=self.set_tunnel_velocity,
            register_damage=self._flash_damage,
        )
        self.ship = PlayerShip(player_ctx)
        self.player_list.append(self.ship)

    def setup_walls(self):
        top_wall = create_tunnel_wall(0, WINDOW_HEIGHT)
        bottom_wall = create_tunnel_wall(0, TUNNEL_WALL_HEIGHT)
        self.tunnel_walls.append(top_wall)
        self.tunnel_walls.append(bottom_wall)

    def setup_hills(self):
        largest_slice_width = arcade.load_texture(HILL_SLICES[0]).width
        for x in [0, HILL_WIDTH * 2]:
            height_so_far = 0
            for i in range(4):
                hill_slice = arcade.load_texture(HILL_SLICES[i])
                hill_top_slice = create_sprite_at_location(
                    hill_slice,
                    left=x + (largest_slice_width - hill_slice.width) / 2,
                    top=WINDOW_HEIGHT - TUNNEL_WALL_HEIGHT - height_so_far,
                )
                trim_width = hill_top_slice.right - hill_top_slice.left
                hill_top_slice.left = x + (hill_slice.width - trim_width) / 2
                self.hill_tops.append(hill_top_slice)
                height_so_far += hill_slice.height
                hill_slice = arcade.load_texture(HILL_SLICES[i]).flip_top_bottom()
                hill_bottom_slice = create_sprite_at_location(
                    hill_slice,
                    left=x + HILL_WIDTH + (largest_slice_width - hill_slice.width) / 2,
                    top=TUNNEL_WALL_HEIGHT + height_so_far,
                )
                hill_bottom_slice.left = x + HILL_WIDTH + (hill_slice.width - trim_width) / 2
                self.hill_bottoms.append(hill_bottom_slice)

    def on_update(self, delta_time: float):
        Action.update_all(delta_time)
        self.tunnel_walls.update()
        self.hill_tops.update()
        self.hill_bottoms.update()
        self.player_list.update()
        self.shot_list.update()
        self._wave_sprites.update()
        if self._wave_strategy:
            self._wave_strategy.update(self._wave_sprites, self._ctx, delta_time)
        self.ship.move(self.left_pressed, self.right_pressed, self.up_pressed, self.down_pressed)
        if self.fire_pressed:
            self.ship.fire_when_ready()

        # Decay damage flash effect
        if self.damage_flash > 0:
            self.damage_flash = max(0, self.damage_flash - delta_time * 5.0)

    def on_draw(self):
        self.background_color = arcade.color.BLACK
        self.clear()
        self._wave_sprites.draw()
        self.tunnel_walls.draw()
        self.hill_tops.draw()
        self.hill_bottoms.draw()
        self.player_list.draw()
        self.shot_list.draw()

        # Draw flash overlay last so it appears over everything
        if self.damage_flash > 0:
            # Create a white overlay using a solid color sprite
            overlay_alpha = int(255 * self.damage_flash)
            arcade.draw_lrbt_rectangle_filled(
                0,
                WINDOW_WIDTH,
                0,
                WINDOW_HEIGHT,
                (255, 255, 255, overlay_alpha),
            )

    def on_key_press(self, key: int, modifiers: int):
        if key == arcade.key.LEFT:
            self.left_pressed = True
            self.right_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
            self.left_pressed = False
        if key == arcade.key.UP:
            self.up_pressed = True
            self.down_pressed = False
        elif key == arcade.key.DOWN:
            self.down_pressed = True
            self.up_pressed = False
        if key == arcade.key.LCTRL or modifiers == arcade.key.MOD_CTRL:
            self.fire_pressed = True
        if key == arcade.key.ESCAPE:
            self.window.set_mouse_visible(True)
            self.window.close()

    def on_key_release(self, key: int, modifiers: int):
        if key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False
        if key == arcade.key.UP:
            self.up_pressed = False
        elif key == arcade.key.DOWN:
            self.down_pressed = False
        if key == arcade.key.LCTRL:
            self.fire_pressed = False

    def on_hide_view(self):
        """Called when this view is hidden or switched away from."""
        # Restore mouse cursor when view is hidden
        try:
            if self.window:
                self.window.set_mouse_visible(True)
        except (AttributeError, RuntimeError):
            # Window might be closed or invalid, ignore cursor restoration errors
            pass

    def __del__(self):
        """Destructor to ensure cursor is restored if view is destroyed unexpectedly."""
        # Only restore cursor if window still exists and is valid
        try:
            if self.window:
                self.window.set_mouse_visible(True)
        except (AttributeError, RuntimeError):
            # Window might be closed or invalid, ignore cursor restoration errors
            pass
