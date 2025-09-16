"""Pure game logic functions that can be unit tested without Arcade dependencies."""

from .config import (
    PLAYER_SHIP_FIRE_SPEED,
    PLAYER_SHIP_HORIZ,
    PLAYER_SHIP_VERT,
    SHIP_LEFT_BOUND,
    TUNNEL_VELOCITY,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)


def calculate_player_velocity(input_state, current_left_position: float) -> tuple[float, float]:
    """
    Calculate player velocity based on input state and current position.

    The input_state object must provide boolean attributes: left, right, up, down.
    """
    horizontal_velocity = 0
    vertical_velocity = 0

    if getattr(input_state, "right", False) and not getattr(input_state, "left", False):
        horizontal_velocity = PLAYER_SHIP_HORIZ
    elif getattr(input_state, "left", False) and not getattr(input_state, "right", False):
        horizontal_velocity = -PLAYER_SHIP_HORIZ

    if getattr(input_state, "up", False) and not getattr(input_state, "down", False):
        vertical_velocity = PLAYER_SHIP_VERT
    elif getattr(input_state, "down", False) and not getattr(input_state, "up", False):
        vertical_velocity = -PLAYER_SHIP_VERT

    if horizontal_velocity or vertical_velocity:
        # Respect left boundary: no further left when already at edge
        if horizontal_velocity < 0 and current_left_position <= SHIP_LEFT_BOUND:
            horizontal_velocity = 0
        return (horizontal_velocity, vertical_velocity)

    # Drift when idle: same as tunnel, unless at left wall
    if current_left_position <= SHIP_LEFT_BOUND:
        return (0, 0)
    return (TUNNEL_VELOCITY, 0)


def calculate_hill_collision_mtv(
    sprite_center_x: float,
    sprite_center_y: float,
    sprite_width: float,
    sprite_height: float,
    collision_center_x: float,
    collision_center_y: float,
    collision_width: float,
    collision_height: float,
) -> tuple[float, str]:
    """Calculate minimum translation vector magnitude and axis for collision resolution."""
    dx = sprite_center_x - collision_center_x
    dy = sprite_center_y - collision_center_y

    overlap_x = (sprite_width / 2 + collision_width / 2) - abs(dx)
    overlap_y = (sprite_height / 2 + collision_height / 2) - abs(dy)

    if overlap_x <= 0 or overlap_y <= 0:
        return (0, "none")

    if overlap_x < overlap_y:
        return (overlap_x, "x")
    else:
        return (overlap_y, "y")


def get_vertical_push_direction(sprite_center_y: float) -> int:
    """Get the vertical direction to push sprite away from screen center."""
    screen_mid = WINDOW_HEIGHT / 2
    return 1 if sprite_center_y < screen_mid else -1


def calculate_shot_velocity(direction: int) -> float:
    """Calculate shot horizontal velocity from player direction (-1 or 1)."""
    return PLAYER_SHIP_FIRE_SPEED * direction


def is_shot_off_screen(shot_left: float, shot_right: float) -> bool:
    """Check if a shot is off screen (fully outside viewport)."""
    return shot_right < 0 or shot_left > WINDOW_WIDTH


def should_wave_cleanup_on_completion(sprite_count: int) -> bool:
    """Determine if wave cleanup should trigger based on remaining sprites."""
    return sprite_count == 0
