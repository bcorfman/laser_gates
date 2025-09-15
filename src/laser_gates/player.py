"""Player ship implementation."""

from collections.abc import Callable

import arcade
from actions import Action, infinite, move_until

from .config import (
    HILL_WIDTH,
    PLAYER_SHIP_FIRE_SPEED,
    PLAYER_SHIP_HORIZ,
    PLAYER_SHIP_VERT,
    SHIP,
    SHIP_LEFT_BOUND,
    SHIP_RIGHT_BOUND,
    TUNNEL_VELOCITY,
    TUNNEL_WALL_HEIGHT,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from .contexts import PlayerContext
from .utils import handle_hill_collision


class PlayerShip(arcade.Sprite):
    LEFT = -1
    RIGHT = 1

    def __init__(self, ctx: PlayerContext, *, behaviour: Callable[["PlayerShip", float], None] | None = None):
        super().__init__(SHIP, center_x=HILL_WIDTH // 4, center_y=WINDOW_HEIGHT // 2)
        self.ctx = ctx
        self.right_texture = arcade.load_texture(SHIP)
        self.left_texture = self.right_texture.flip_left_right()
        self.texture_red_laser = arcade.load_texture(":resources:images/space_shooter/laserRed01.png").rotate_90()
        self.speed_factor = 1
        self.direction = self.RIGHT
        self.behaviour = behaviour  # Optional AI/attract mode behaviour

        # Input state for velocity provider
        self._input = {"left": False, "right": False, "up": False, "down": False}

        def velocity_provider():
            # Manual control takes priority
            h = 0
            v = 0

            if self._input["right"] and not self._input["left"]:
                h = PLAYER_SHIP_HORIZ
            elif self._input["left"] and not self._input["right"]:
                h = -PLAYER_SHIP_HORIZ

            if self._input["up"] and not self._input["down"]:
                v = PLAYER_SHIP_VERT
            elif self._input["down"] and not self._input["up"]:
                v = -PLAYER_SHIP_VERT

            if h or v:
                # Respect left boundary: no further left when already at edge
                if h < 0 and self.left <= SHIP_LEFT_BOUND:
                    h = 0
                return (h, v)

            # Drift when idle: same as tunnel, unless at left wall
            if self.left <= SHIP_LEFT_BOUND:
                return (0, 0)
            return (TUNNEL_VELOCITY, 0)

        def on_boundary_enter(sprite, axis, side):
            if axis == "x" and side == "right":
                self.speed_factor = 2
                self.ctx.set_tunnel_velocity(TUNNEL_VELOCITY * self.speed_factor)

        def on_boundary_exit(sprite, axis, side):
            if axis == "x" and side == "right":
                self.speed_factor = 1
                self.ctx.set_tunnel_velocity(TUNNEL_VELOCITY)

        # Single long-lived action for all movement
        move_until(
            self,
            velocity=(0, 0),  # ignored when velocity_provider is present
            condition=infinite,
            bounds=(SHIP_LEFT_BOUND, TUNNEL_WALL_HEIGHT, SHIP_RIGHT_BOUND, WINDOW_HEIGHT - TUNNEL_WALL_HEIGHT),
            boundary_behavior="limit",
            velocity_provider=velocity_provider,
            on_boundary_enter=on_boundary_enter,
            on_boundary_exit=on_boundary_exit,
            tag="player_move",
        )

    def move(self, left_pressed, right_pressed, up_pressed, down_pressed):
        # Simply update input state - velocity_provider handles the rest
        self._input.update(left=left_pressed, right=right_pressed, up=up_pressed, down=down_pressed)

        # Update direction and texture for visual feedback
        if right_pressed and not left_pressed:
            self.direction = self.RIGHT
            self.texture = self.right_texture
        elif left_pressed and not right_pressed:
            self.direction = self.LEFT
            self.texture = self.left_texture

        # Always check for hill or wall collisions after movement (whether moving or stationary)
        hill_collision_lists = [self.ctx.hill_tops, self.ctx.hill_bottoms, self.ctx.tunnel_walls]
        if handle_hill_collision(self, hill_collision_lists, self.ctx.register_damage):
            # Stop current movement if we hit hills
            Action.stop_actions_for_target(self, tag="player_move")

    def fire_when_ready(self):
        can_fire = len(self.ctx.shot_list) == 0
        if can_fire:
            self.setup_shot()
        return can_fire

    def setup_shot(self, angle=0):
        shot = arcade.Sprite()
        shot.texture = self.texture_red_laser
        if self.direction == self.RIGHT:
            shot.left = self.right
        else:
            shot.right = self.left
        shot.center_y = self.center_y
        shot_vel_x = PLAYER_SHIP_FIRE_SPEED * self.direction

        move_until(
            shot,
            velocity=(shot_vel_x, 0),
            condition=self.shot_collision_check,
            on_stop=lambda *_: shot.remove_from_sprite_lists(),
        )
        self.ctx.shot_list.append(shot)

    def shot_collision_check(self):
        # Safeguard: if the shot has already been removed, stop the action.
        if not self.ctx.shot_list:
            return True  # Condition met -> stop action

        shot = self.ctx.shot_list[0]
        off_screen = shot.right < 0 or shot.left > WINDOW_WIDTH
        hills_hit = arcade.check_for_collision_with_lists(shot, [self.ctx.hill_tops, self.ctx.hill_bottoms])
        return {"off_screen": off_screen, "hills_hit": hills_hit} if off_screen or hills_hit else None

    def update(self, delta_time):
        super().update(delta_time)
        # Run AI/attract mode behaviour if present
        if self.behaviour:
            self.behaviour(self, delta_time)
