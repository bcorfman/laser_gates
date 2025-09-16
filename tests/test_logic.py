import pytest


class DummyInput:
    def __init__(self, left=False, right=False, up=False, down=False):
        self.left = left
        self.right = right
        self.up = up
        self.down = down


def test_calculate_player_velocity_moves_right():
    from laser_gates import config, logic

    input_state = DummyInput(right=True)
    # well away from left boundary
    vx, vy = logic.calculate_player_velocity(input_state, current_left_position=config.SHIP_LEFT_BOUND + 50)
    assert vx == config.PLAYER_SHIP_HORIZ
    assert vy == 0


def test_calculate_player_velocity_moves_left_until_left_bound():
    from laser_gates import config, logic

    input_state = DummyInput(left=True)
    # at left boundary -> horizontal should clamp to 0
    vx, vy = logic.calculate_player_velocity(input_state, current_left_position=config.SHIP_LEFT_BOUND)
    assert vx == 0
    assert vy == 0


def test_calculate_player_velocity_vertical_moves():
    from laser_gates import config, logic

    input_state = DummyInput(up=True)
    vx, vy = logic.calculate_player_velocity(input_state, current_left_position=config.SHIP_LEFT_BOUND + 1)
    assert vx == 0
    assert vy == config.PLAYER_SHIP_VERT

    input_state = DummyInput(down=True)
    vx, vy = logic.calculate_player_velocity(input_state, current_left_position=config.SHIP_LEFT_BOUND + 1)
    assert vx == 0
    assert vy == -config.PLAYER_SHIP_VERT


def test_calculate_player_velocity_idle_drifts_with_tunnel_velocity():
    from laser_gates import config, logic

    input_state = DummyInput()
    vx, vy = logic.calculate_player_velocity(input_state, current_left_position=config.SHIP_LEFT_BOUND + 10)
    assert (vx, vy) == (config.TUNNEL_VELOCITY, 0)

    # When exactly at left bound, no drift
    vx, vy = logic.calculate_player_velocity(input_state, current_left_position=config.SHIP_LEFT_BOUND)
    assert (vx, vy) == (0, 0)


@pytest.mark.parametrize(
    "sprite_cx,sprite_cy,sprite_w,sprite_h,coll_cx,coll_cy,coll_w,coll_h,expected_axis",
    [
        # Taller overlap than wide -> resolve on x
        (50, 50, 20, 20, 55, 50, 20, 40, "x"),
        # Wider overlap than tall -> resolve on y
        (50, 50, 20, 20, 50, 55, 40, 20, "y"),
    ],
)
def test_calculate_hill_collision_mtv_axis_choice(
    sprite_cx, sprite_cy, sprite_w, sprite_h, coll_cx, coll_cy, coll_w, coll_h, expected_axis
):
    from laser_gates import logic

    overlap, axis = logic.calculate_hill_collision_mtv(
        sprite_cx, sprite_cy, sprite_w, sprite_h, coll_cx, coll_cy, coll_w, coll_h
    )
    assert axis == expected_axis
    assert overlap > 0


def test_get_vertical_push_direction_top_vs_bottom():
    from laser_gates import config, logic

    # Bottom half -> push up (+1)
    assert logic.get_vertical_push_direction(sprite_center_y=config.WINDOW_HEIGHT / 4) == 1
    # Top half -> push down (-1)
    assert logic.get_vertical_push_direction(sprite_center_y=config.WINDOW_HEIGHT * 3 / 4) == -1


def test_calculate_shot_velocity_by_direction():
    from laser_gates import config, logic

    assert logic.calculate_shot_velocity(direction=1) == config.PLAYER_SHIP_FIRE_SPEED
    assert logic.calculate_shot_velocity(direction=-1) == -config.PLAYER_SHIP_FIRE_SPEED


def test_is_shot_off_screen_conditions():
    from laser_gates import config, logic

    # Left of screen
    assert logic.is_shot_off_screen(shot_left=-5, shot_right=-1) is True
    # Right of screen
    assert logic.is_shot_off_screen(shot_left=config.WINDOW_WIDTH + 1, shot_right=config.WINDOW_WIDTH + 5) is True
    # On screen
    assert logic.is_shot_off_screen(shot_left=10, shot_right=20) is False


def test_should_wave_cleanup_on_completion():
    from laser_gates import logic

    assert logic.should_wave_cleanup_on_completion(0) is True
    assert logic.should_wave_cleanup_on_completion(1) is False
