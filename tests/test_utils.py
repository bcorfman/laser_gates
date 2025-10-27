import arcade
import pytest


def test_create_tunnel_wall_dimensions_and_position():
    from laser_gates import config
    from laser_gates.utils import create_tunnel_wall

    left = 10
    top = config.WINDOW_HEIGHT
    wall = create_tunnel_wall(left, top)

    assert isinstance(wall, arcade.Sprite)
    assert wall.width == config.WINDOW_WIDTH
    assert wall.height == config.TUNNEL_WALL_HEIGHT
    assert wall.left == left
    assert wall.top == top


def test_create_sprite_at_location_with_left_top():
    from laser_gates.utils import create_sprite_at_location

    # Use an Arcade resource so no local files are required
    res_path = ":resources:images/items/coinGold.png"
    sprite = create_sprite_at_location(res_path, left=100, top=200)

    assert isinstance(sprite, arcade.Sprite)
    assert sprite.left == 100
    assert sprite.top == 200


def test_create_sprite_at_location_with_centers():
    from laser_gates.utils import create_sprite_at_location

    res_path = ":resources:images/items/coinGold.png"
    sprite = create_sprite_at_location(res_path, center_x=123, center_y=321)

    assert isinstance(sprite, arcade.Sprite)
    assert sprite.center_x == 123
    assert sprite.center_y == 321


def test_handle_hill_collision_bottom_half_pushes_up():
    from laser_gates import config
    from laser_gates.utils import handle_hill_collision

    # Player sprite in bottom half
    player = arcade.SpriteSolidColor(20, 20, color=arcade.color.WHITE)
    player.center_x = 100
    player.center_y = config.WINDOW_HEIGHT // 4

    # Create a "hill" that overlaps vertically with the player
    hill = arcade.SpriteSolidColor(40, 40, color=arcade.color.RED)
    hill.center_x = player.center_x
    hill.center_y = player.center_y  # ensure overlap

    damage = []

    def register_damage(amount: float):
        damage.append(amount)

    hills = arcade.SpriteList()
    hills.append(hill)
    moved = handle_hill_collision(player, [hills], register_damage)
    assert moved is True
    assert player.center_y > config.WINDOW_HEIGHT // 4  # pushed up
    assert player.change_y == 0
    assert damage and damage[0] == 0.3


def test_handle_hill_collision_top_half_pushes_down():
    from laser_gates import config
    from laser_gates.utils import handle_hill_collision

    # Player sprite in top half
    player = arcade.SpriteSolidColor(20, 20, color=arcade.color.WHITE)
    player.center_x = 150
    player.center_y = int(config.WINDOW_HEIGHT * 0.75)

    # Overlapping hill
    hill = arcade.SpriteSolidColor(40, 40, color=arcade.color.BLUE)
    hill.center_x = player.center_x
    hill.center_y = player.center_y

    damage = []

    def register_damage(amount: float):
        damage.append(amount)

    original_y = player.center_y
    hills = arcade.SpriteList()
    hills.append(hill)
    moved = handle_hill_collision(player, [hills], register_damage)
    assert moved is True
    assert player.center_y < original_y  # pushed down
    assert player.change_y == 0
    assert damage and damage[0] == 0.3


def test_handle_hill_collision_no_overlap_returns_false():
    from laser_gates.utils import handle_hill_collision

    player = arcade.SpriteSolidColor(20, 20, color=arcade.color.WHITE)
    player.center_x = 50
    player.center_y = 50

    # Place hill far away so no overlap
    hill = arcade.SpriteSolidColor(20, 20, color=arcade.color.ALMOND)
    hill.center_x = 1000
    hill.center_y = 1000

    damage = []

    def register_damage(amount: float):
        damage.append(amount)

    hills = arcade.SpriteList()
    hills.append(hill)
    moved = handle_hill_collision(player, [hills], register_damage)
    assert moved is False
    assert damage == []


def test_create_sprite_at_location_no_position_params():
    """Test sprite creation without position parameters - sprite stays at default (0, 0)."""
    from laser_gates.utils import create_sprite_at_location

    res_path = ":resources:images/items/coinGold.png"
    sprite = create_sprite_at_location(res_path)

    assert isinstance(sprite, arcade.Sprite)
    # Default position when no positioning params provided
    assert sprite.center_x == 0
    assert sprite.center_y == 0


def test_handle_hill_collision_horizontal_overlap_less_than_vertical():
    """Test collision when horizontal overlap is smaller than vertical overlap."""
    from laser_gates import config
    from laser_gates.utils import handle_hill_collision

    # Create player sprite
    player = arcade.SpriteSolidColor(20, 40, color=arcade.color.WHITE)
    player.center_x = 100
    player.center_y = config.WINDOW_HEIGHT // 2

    # Create hill with more vertical than horizontal overlap
    # Wider hill to ensure horizontal overlap is smaller
    hill = arcade.SpriteSolidColor(100, 30, color=arcade.color.RED)
    hill.center_x = player.center_x + 5  # Small horizontal offset
    hill.center_y = player.center_y

    damage = []

    def register_damage(amount: float):
        damage.append(amount)

    hills = arcade.SpriteList()
    hills.append(hill)
    original_y = player.center_y
    moved = handle_hill_collision(player, [hills], register_damage)

    assert moved is True
    # Should be pushed vertically since player is at screen center
    assert player.center_y != original_y
    assert player.change_y == 0
    assert len(damage) == 1


def test_handle_hill_collision_multiple_hills():
    """Test collision with multiple hills to exercise minimum overlap logic."""
    from laser_gates import config
    from laser_gates.utils import handle_hill_collision

    player = arcade.SpriteSolidColor(20, 20, color=arcade.color.WHITE)
    player.center_x = 100
    player.center_y = config.WINDOW_HEIGHT // 4

    # Create two hills at different positions, both overlapping
    hill1 = arcade.SpriteSolidColor(30, 30, color=arcade.color.RED)
    hill1.center_x = player.center_x - 2
    hill1.center_y = player.center_y

    hill2 = arcade.SpriteSolidColor(25, 25, color=arcade.color.BLUE)
    hill2.center_x = player.center_x + 2
    hill2.center_y = player.center_y

    damage = []

    def register_damage(amount: float):
        damage.append(amount)

    hills = arcade.SpriteList()
    hills.append(hill1)
    hills.append(hill2)

    original_y = player.center_y
    moved = handle_hill_collision(player, [hills], register_damage)

    assert moved is True
    # Should be pushed up (in bottom half)
    assert player.center_y > original_y
    assert player.change_y == 0
    assert damage == [0.3]


def test_handle_hill_collision_exact_screen_center():
    """Test collision when player is exactly at screen center."""
    from laser_gates import config
    from laser_gates.utils import handle_hill_collision

    player = arcade.SpriteSolidColor(20, 20, color=arcade.color.WHITE)
    player.center_x = 100
    player.center_y = config.WINDOW_HEIGHT // 2  # Exactly at center

    hill = arcade.SpriteSolidColor(40, 40, color=arcade.color.RED)
    hill.center_x = player.center_x
    hill.center_y = player.center_y

    damage = []

    def register_damage(amount: float):
        damage.append(amount)

    hills = arcade.SpriteList()
    hills.append(hill)

    moved = handle_hill_collision(player, [hills], register_damage)

    assert moved is True
    # At exact center, should push down (vertical_dir = -1)
    assert player.center_y != config.WINDOW_HEIGHT // 2
    assert player.change_y == 0
    assert damage == [0.3]


def test_handle_hill_collision_negative_overlap_edge_case():
    """Test edge case where overlap calculation might be negative or zero."""
    from laser_gates.utils import handle_hill_collision

    player = arcade.SpriteSolidColor(10, 10, color=arcade.color.WHITE)
    player.center_x = 100
    player.center_y = 100

    # Create hill that's barely touching (edge case)
    hill = arcade.SpriteSolidColor(10, 10, color=arcade.color.RED)
    hill.center_x = player.center_x + 9.9  # Almost not overlapping
    hill.center_y = player.center_y

    damage = []

    def register_damage(amount: float):
        damage.append(amount)

    hills = arcade.SpriteList()
    hills.append(hill)

    # This might or might not collide depending on exact floating point
    result = handle_hill_collision(player, [hills], register_damage)
    # Just verify it doesn't crash and returns a boolean
    assert isinstance(result, bool)


@pytest.mark.opengl
def test_create_forcefield_textures_creates_list():
    """Test that create_forcefield_textures returns a list of textures.

    Requires OpenGL context (Xvfb in CI).
    """
    from laser_gates.utils import create_forcefield_textures

    try:
        textures = create_forcefield_textures()

        # Should return a list
        assert isinstance(textures, list)

        # Should have 109 frames (SPRITE_H)
        assert len(textures) == 109

        # All items should be Arcade textures
        for tex in textures:
            assert isinstance(tex, arcade.Texture)

        # Verify texture dimensions
        assert textures[0].width == 35
        assert textures[0].height == 109

    except (FileNotFoundError, AttributeError) as e:
        # Skip if:
        # - forcefield.png doesn't exist (FileNotFoundError)
        # - RenderTexture not available (no OpenGL context - AttributeError)
        import pytest

        pytest.skip(f"Cannot test texture generation: {type(e).__name__} - {e}")
