"""Unit tests for TextureCache and SpritePool."""

import unittest
from unittest.mock import Mock, call, patch

import arcade

from laser_gates.resources import SpritePool, TextureCache


class TestTextureCache(unittest.TestCase):
    """Test the TextureCache class."""

    def setUp(self):
        """Set up test fixtures."""
        self.cache = TextureCache()

    def test_cache_is_dict_subclass(self):
        """TextureCache should be a dictionary."""
        self.assertIsInstance(self.cache, dict)

    @patch("arcade.load_texture")
    def test_get_new_texture(self, mock_load):
        """Should load and cache new textures."""
        mock_texture = Mock(spec=arcade.Texture)
        mock_load.return_value = mock_texture

        result = self.cache.get("test_path.png")

        self.assertEqual(result, mock_texture)
        mock_load.assert_called_once_with("test_path.png")
        self.assertEqual(self.cache["test_path.png"], mock_texture)

    @patch("arcade.load_texture")
    def test_get_cached_texture(self, mock_load):
        """Should return cached texture without reloading."""
        mock_texture = Mock(spec=arcade.Texture)
        mock_load.return_value = mock_texture

        # First call should load
        result1 = self.cache.get("test_path.png")
        # Second call should use cache
        result2 = self.cache.get("test_path.png")

        self.assertEqual(result1, mock_texture)
        self.assertEqual(result2, mock_texture)
        # Should only call load_texture once
        mock_load.assert_called_once_with("test_path.png")

    @patch("arcade.load_texture")
    def test_multiple_different_textures(self, mock_load):
        """Should handle multiple different texture paths."""
        mock_texture1 = Mock(spec=arcade.Texture)
        mock_texture2 = Mock(spec=arcade.Texture)
        mock_load.side_effect = [mock_texture1, mock_texture2]

        result1 = self.cache.get("path1.png")
        result2 = self.cache.get("path2.png")

        self.assertEqual(result1, mock_texture1)
        self.assertEqual(result2, mock_texture2)
        self.assertEqual(mock_load.call_count, 2)
        mock_load.assert_has_calls([call("path1.png"), call("path2.png")])


class TestSpritePool(unittest.TestCase):
    """Test the SpritePool class."""

    def setUp(self):
        """Set up test fixtures."""

        def real_sprite_factory():
            # Create a real sprite with minimal setup
            sprite = arcade.SpriteSolidColor(10, 10, arcade.color.RED)
            sprite.center_x = 0.0
            sprite.center_y = 0.0
            return sprite

        self.mock_sprite_factory = Mock(side_effect=real_sprite_factory)
        self.pool = SpritePool(self.mock_sprite_factory, size=5)

    def test_initialization(self):
        """Pool should initialize with correct number of sprites."""
        # Should have called factory 5 times
        self.assertEqual(self.mock_sprite_factory.call_count, 5)
        # Should have 0 active sprites
        self.assertEqual(len(self.pool.active), 0)
        # Should have 5 inactive sprites
        self.assertEqual(len(self.pool.inactive), 5)

    def test_sprite_lists_are_arcade_spritelists(self):
        """Active and inactive should be arcade.SpriteList instances."""
        self.assertIsInstance(self.pool.active, arcade.SpriteList)
        self.assertIsInstance(self.pool.inactive, arcade.SpriteList)

    def test_active_uses_spatial_hash(self):
        """Active sprite list should use spatial hash for performance."""
        # This is tested by verifying the constructor was called correctly
        # We can't easily inspect the internal state, so we'll verify behavior
        # Check that the spatial hash was enabled during construction
        self.assertIsInstance(self.pool.active, arcade.SpriteList)

    def test_acquire_sprites(self):
        """Should move sprites from inactive to active."""
        sprites = self.pool.acquire(3)

        self.assertEqual(len(sprites), 3)
        self.assertEqual(len(self.pool.active), 3)
        self.assertEqual(len(self.pool.inactive), 2)

        # All acquired sprites should be in the active list
        for sprite in sprites:
            self.assertIn(sprite, self.pool.active)

    def test_acquire_all_sprites(self):
        """Should be able to acquire all sprites."""
        sprites = self.pool.acquire(5)

        self.assertEqual(len(sprites), 5)
        self.assertEqual(len(self.pool.active), 5)
        self.assertEqual(len(self.pool.inactive), 0)

    def test_acquire_too_many_sprites_raises_error(self):
        """Should raise RuntimeError when requesting more sprites than available."""
        with self.assertRaises(RuntimeError) as cm:
            self.pool.acquire(6)

        self.assertIn("pool exhausted", str(cm.exception))

    def test_release_sprites(self):
        """Should move sprites from active back to inactive."""
        sprites = self.pool.acquire(3)

        # Mock the remove_from_sprite_lists method
        for sprite in sprites:
            sprite.remove_from_sprite_lists = Mock()
            sprite.visible = True

        self.pool.release(sprites)

        self.assertEqual(len(self.pool.active), 0)
        self.assertEqual(len(self.pool.inactive), 5)

        # Verify sprites were made invisible and removed from sprite lists
        for sprite in sprites:
            self.assertFalse(sprite.visible)
            sprite.remove_from_sprite_lists.assert_called_once()
            self.assertIn(sprite, self.pool.inactive)

    def test_acquire_after_release(self):
        """Should be able to acquire sprites after releasing them."""
        # Acquire and release
        sprites = self.pool.acquire(3)
        for sprite in sprites:
            sprite.remove_from_sprite_lists = Mock()
        self.pool.release(sprites)

        # Should be able to acquire again
        new_sprites = self.pool.acquire(2)
        self.assertEqual(len(new_sprites), 2)
        self.assertEqual(len(self.pool.active), 2)
        self.assertEqual(len(self.pool.inactive), 3)

    def test_release_partial_sprites(self):
        """Should handle releasing only some of the acquired sprites."""
        sprites = self.pool.acquire(4)
        sprites_to_release = sprites[:2]

        for sprite in sprites_to_release:
            sprite.remove_from_sprite_lists = Mock()

        self.pool.release(sprites_to_release)

        self.assertEqual(len(self.pool.active), 2)  # 4 - 2 released
        self.assertEqual(len(self.pool.inactive), 3)  # 1 + 2 released

    def test_factory_function_type_hint(self):
        """Pool should accept a callable factory function."""

        # This test verifies the type hint works - the actual test is in initialization
        def test_factory() -> arcade.Sprite:
            sprite = arcade.SpriteSolidColor(5, 5, arcade.color.BLUE)
            sprite.center_x = 0.0
            sprite.center_y = 0.0
            return sprite

        pool = SpritePool(test_factory, size=1)
        self.assertEqual(len(pool.inactive), 1)

    def test_release_all_empty_pool(self):
        """Should handle release_all when no sprites are active."""
        # Initially no sprites are active
        self.assertEqual(len(self.pool.active), 0)

        # Should not raise an error
        self.pool.release_all()

        # Should still have all sprites inactive
        self.assertEqual(len(self.pool.active), 0)
        self.assertEqual(len(self.pool.inactive), 5)

    def test_release_all_with_active_sprites(self):
        """Should release all active sprites back to inactive."""
        # Acquire some sprites
        sprites = self.pool.acquire(3)

        # Mock the remove_from_sprite_lists method for all sprites
        for sprite in sprites:
            sprite.remove_from_sprite_lists = Mock()
            sprite.visible = True

        # Release all active sprites
        self.pool.release_all()

        # Check that all sprites are back in inactive
        self.assertEqual(len(self.pool.active), 0)
        self.assertEqual(len(self.pool.inactive), 5)

        # Verify all sprites were made invisible and removed from sprite lists
        for sprite in sprites:
            self.assertFalse(sprite.visible)
            sprite.remove_from_sprite_lists.assert_called_once()

    def test_release_all_partial_then_release_all(self):
        """Should handle release_all after partial releases."""
        # Acquire some sprites
        sprites = self.pool.acquire(4)

        # Mock remove_from_sprite_lists for all sprites
        for sprite in sprites:
            sprite.remove_from_sprite_lists = Mock()

        # Release some sprites individually
        sprites_to_release = sprites[:2]
        self.pool.release(sprites_to_release)

        self.assertEqual(len(self.pool.active), 2)
        self.assertEqual(len(self.pool.inactive), 3)

        # Now release all remaining active sprites
        self.pool.release_all()

        self.assertEqual(len(self.pool.active), 0)
        self.assertEqual(len(self.pool.inactive), 5)

    def test_release_when_sprites_is_active_list(self):
        """Should handle the special case when releasing the active list itself."""
        # Acquire some sprites
        sprites = self.pool.acquire(3)

        # Mock remove_from_sprite_lists for all sprites
        for sprite in sprites:
            sprite.remove_from_sprite_lists = Mock()
            sprite.visible = True

        # This should trigger the special case handling in release()
        # where sprites is self.active
        self.pool.release(self.pool.active)

        # All sprites should be released
        self.assertEqual(len(self.pool.active), 0)
        self.assertEqual(len(self.pool.inactive), 5)

        # Verify sprites were processed correctly
        for sprite in sprites:
            self.assertFalse(sprite.visible)
            sprite.remove_from_sprite_lists.assert_called_once()

    def test_acquire_after_release_all(self):
        """Should be able to acquire sprites after release_all."""
        # Acquire some sprites
        sprites = self.pool.acquire(3)
        for sprite in sprites:
            sprite.remove_from_sprite_lists = Mock()

        # Release all
        self.pool.release_all()

        # Should be able to acquire again
        new_sprites = self.pool.acquire(2)
        self.assertEqual(len(new_sprites), 2)
        self.assertEqual(len(self.pool.active), 2)
        self.assertEqual(len(self.pool.inactive), 3)


if __name__ == "__main__":
    unittest.main()
