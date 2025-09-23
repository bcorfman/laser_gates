"""Utility functions for sprite creation and collision handling."""

from collections.abc import Callable

import arcade

from .config import TUNNEL_WALL_COLOR, TUNNEL_WALL_HEIGHT, WINDOW_HEIGHT, WINDOW_WIDTH


def create_tunnel_wall(left, top):
    """Create a tunnel wall sprite."""
    wall = arcade.SpriteSolidColor(WINDOW_WIDTH, TUNNEL_WALL_HEIGHT, color=TUNNEL_WALL_COLOR)
    wall.left = left
    wall.top = top
    return wall


def create_sprite_at_location(file_or_texture, **kwargs):
    """Create a sprite at a specific location."""
    sprite = arcade.Sprite(file_or_texture)
    if kwargs.get("left") is not None and kwargs.get("top") is not None:
        sprite.left = kwargs.get("left")
        sprite.top = kwargs.get("top")
    elif kwargs.get("center_x") is not None and kwargs.get("center_y") is not None:
        sprite.center_x = kwargs.get("center_x")
        sprite.center_y = kwargs.get("center_y")
    return sprite


def handle_hill_collision(sprite, collision_lists, register_damage: Callable[[float], None]):
    """Handle collision with hills by adjusting position and providing visual feedback."""
    # Use CPU-based collision to avoid requiring an active window/context in headless tests
    collision_hit = arcade.check_for_collision_with_lists(sprite, collision_lists, method=3)
    if not collision_hit:
        return False

    # Compute minimum translation vector to resolve all overlaps
    min_overlap = None
    mtv_axis = None  # "x" or "y"

    for collision_sprite in collision_hit:
        dx = sprite.center_x - collision_sprite.center_x
        dy = sprite.center_y - collision_sprite.center_y

        overlap_x = (sprite.width / 2 + collision_sprite.width / 2) - abs(dx)
        overlap_y = (sprite.height / 2 + collision_sprite.height / 2) - abs(dy)

        # Skip if somehow not overlapping (shouldn't happen given collision detection)
        if overlap_x <= 0 or overlap_y <= 0:
            continue

        # Choose axis with smaller overlap to resolve
        if overlap_x < overlap_y:
            if min_overlap is None or overlap_x < min_overlap:
                min_overlap = overlap_x
                mtv_axis = ("x", 1 if dx > 0 else -1)
        else:
            if min_overlap is None or overlap_y < min_overlap:
                min_overlap = overlap_y
                mtv_axis = ("y", 1 if dy > 0 else -1)

    # Always push vertically away from screen center
    # Determine direction: up (1) if in bottom half, down (-1) if in top half
    screen_mid = WINDOW_HEIGHT / 2
    vertical_dir = 1 if sprite.center_y < screen_mid else -1

    # Determine minimal vertical overlap among collisions to move the sprite out
    min_vertical_overlap = None
    for collision_sprite in collision_hit:
        dy = sprite.center_y - collision_sprite.center_y
        overlap_y = (sprite.height / 2 + collision_sprite.height / 2) - abs(dy)
        if overlap_y > 0:
            if min_vertical_overlap is None or overlap_y < min_vertical_overlap:
                min_vertical_overlap = overlap_y

    # Fallback small nudge if calculation failed (shouldn't happen)
    if min_vertical_overlap is None:
        min_vertical_overlap = sprite.height / 2

    sprite.center_y += vertical_dir * (min_vertical_overlap + 1)
    sprite.change_y = 0

    # Visual damage feedback - flash background
    register_damage(0.3)

    return True


def create_forcefield_textures():
    """
    Build a list of textures rolled by 0..H-1 pixels using Arcade's render-to-texture.
    Implementation notes:
        - We render into a RenderTexture of the same size.
        - To achieve a vertical wrap/roll by 'y' pixels, we draw the base texture twice:
            1) at bottom = -y
            2) at bottom = SPRITE_H - y
        so the part that scrolls off the bottom reappears at the top.
        - We then snapshot the render target to an image via rt.get_image()
        and construct an arcade.Texture from that image — all via Arcade API.
    """

    SPRITE_W, SPRITE_H = 35, 109
    PNG_PATH = "res/forcefield.png"
    base_tex = arcade.load_texture(PNG_PATH)
    frames = []

    # A single reusable render target; we overwrite it for each frame
    rt = arcade.RenderTexture(SPRITE_W, SPRITE_H)

    for y in range(SPRITE_H):
        # Render into offscreen target
        with arcade.render_target(rt):
            arcade.start_render()
            # Draw first copy shifted down by y
            arcade.draw_lrwh_rectangle_textured(0, -y, SPRITE_W, SPRITE_H, base_tex)
            # Draw wrapped copy
            arcade.draw_lrwh_rectangle_textured(0, SPRITE_H - y, SPRITE_W, SPRITE_H, base_tex)

        # Snapshot the RT back to an image (Arcade API) and make a texture
        img = rt.get_image()  # returns a PIL Image internally, but we never import PIL
        tex = arcade.Texture(f"roll_{y}", image=img)
        frames.append(tex)

    return frames
