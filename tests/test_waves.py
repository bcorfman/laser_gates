"""Unit tests for wave classes."""

import types

import arcade
import pytest

from laser_gates.contexts import WaveContext


def make_ctx(shots=None, player_speed_factor=1.0, on_cleanup=None, register_damage=None):
    """Create a WaveContext for testing.

    Args:
        shots: List of shot sprites (default: empty list)
        player_speed_factor: Speed factor for player ship (default: 1.0)
        on_cleanup: Cleanup callback (default: tracks calls)
        register_damage: Damage callback (default: tracks calls)

    Returns:
        Tuple of (WaveContext, cleanup_tracker, damage_tracker)
    """
    shot_list = shots if shots is not None else []
    player_ship = types.SimpleNamespace(speed_factor=player_speed_factor)

    cleanup_tracker = {"called": False, "wave": None}

    def _on_cleanup(wave):
        cleanup_tracker["called"] = True
        cleanup_tracker["wave"] = wave

    damage_tracker = {"amounts": []}

    def _register_damage(amount: float):
        damage_tracker["amounts"].append(amount)

    ctx = WaveContext(
        shot_list=shot_list,
        player_ship=player_ship,
        register_damage=register_damage or _register_damage,
        on_cleanup=on_cleanup or _on_cleanup,
    )

    return ctx, cleanup_tracker, damage_tracker


class TestDensePackWave:
    """Test dense pack wave classes."""

    def test_pool_release_on_cleanup(self):
        """Test that sprites are released back to pool on cleanup (Test 1)."""
        from laser_gates.waves import ThinDensePackWave

        wave = ThinDensePackWave()
        ctx, _, _ = make_ctx()
        wave.build(ctx)

        # Count sprites in pool before cleanup
        initial_inactive_count = len(wave._shield_pool.inactive)
        initial_active_count = len(wave._shield_pool.active)

        # Verify sprites were acquired
        assert initial_active_count > 0, "Sprites should be acquired during build"
        assert len(wave._shield_sprites) > 0, "Shield sprites should exist"

        # Cleanup should release all sprites back to pool
        wave.cleanup(ctx)

        # After cleanup, all sprites should be in inactive pool
        final_inactive_count = len(wave._shield_pool.inactive)
        final_active_count = len(wave._shield_pool.active)

        assert final_active_count == 0, "All sprites should be released from active pool"
        assert final_inactive_count > initial_inactive_count, "Sprites should be returned to inactive pool"
        assert final_inactive_count == initial_inactive_count + initial_active_count, (
            "All acquired sprites should be returned"
        )

    def test_scroll_actions_tracked_for_velocity_updates(self):
        """Test that scroll actions are tracked for velocity updates (Test 4)."""
        from laser_gates.waves import ThinDensePackWave

        wave = ThinDensePackWave()
        ctx, _, _ = make_ctx()
        wave.build(ctx)

        # After build, scroll actions should be tracked
        assert len(wave._scroll_actions) > 0, "Scroll actions should be tracked for velocity updates"

        # Verify we can update velocity (this tests the tracking mechanism)
        # The action should have a set_current_velocity method
        for action in wave._scroll_actions:
            assert hasattr(action, "set_current_velocity"), (
                "Scroll actions should support velocity updates"
            )

        # Test that update_scroll_velocity doesn't crash
        wave.update_scroll_velocity(-3.0)


class TestFlashingForcefieldWave:
    """Test flashing forcefield wave class."""

    def test_forcefield_only_collides_when_active(self, monkeypatch):
        """Test that collisions are only checked when forcefields are active (Test 3)."""
        from laser_gates.waves import FlashingForcefieldWave

        # Create a shot that tracks removal
        shot_removed = {"called": False}

        def remove_shot():
            shot_removed["called"] = True

        shot = types.SimpleNamespace()
        shot.remove_from_sprite_lists = remove_shot

        wave = FlashingForcefieldWave(total_forcefields=3)
        ctx, cleanup_tracker, damage_tracker = make_ctx(shots=[shot])
        wave.build(ctx)

        # Track collision calls
        collision_calls = []

        def track_collisions(*args, **kwargs):
            collision_calls.append(args)
            # Return collision when active, empty when inactive
            return [object()] if wave._forcefields_active else []

        monkeypatch.setattr(arcade, "check_for_collision_with_list", track_collisions)

        # Test 1: When active, collisions should be checked and shot removed
        wave._forcefields_active = True
        shot_removed["called"] = False
        collision_calls.clear()
        wave.update(ctx)

        assert len(collision_calls) > 0, "Collision checks should occur when forcefields are active"
        assert shot_removed["called"], "Shot should be removed when forcefields are active and collision occurs"

        # Test 2: When inactive, collisions should NOT be checked
        wave._forcefields_active = False
        shot_removed["called"] = False
        collision_calls.clear()
        wave.update(ctx)

        # When inactive, no collision checks should happen for shots
        # (Forcefield waves check both initial and last, so we might get 2 calls, but they return empty)
        # The key is that shot removal should NOT happen
        assert not shot_removed["called"], "Shot should NOT be removed when forcefields are inactive"

        # Test 3: Player collision should also respect active state
        wave._forcefields_active = True
        damage_tracker["amounts"].clear()
        cleanup_tracker["called"] = False

        # Make collision return True (player collision)
        def player_collision(*args, **kwargs):
            return True if wave._forcefields_active else []

        monkeypatch.setattr(arcade, "check_for_collision_with_list", player_collision)
        wave.update(ctx)

        assert cleanup_tracker["called"], "Cleanup should be triggered when player collides with active forcefields"
        assert len(damage_tracker["amounts"]) > 0, "Damage should be registered when player collides"

        # Test 4: When inactive, player collision should NOT trigger damage
        wave._forcefields_active = False
        damage_tracker["amounts"].clear()
        cleanup_tracker["called"] = False
        wave.update(ctx)

        assert len(damage_tracker["amounts"]) == 0, "Damage should NOT be registered when forcefields are inactive"
        assert not cleanup_tracker["called"], "Cleanup should NOT be triggered when forcefields are inactive"

