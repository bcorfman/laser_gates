import arcade


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
