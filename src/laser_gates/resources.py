"""Resource management for textures and sprite pools."""

from collections.abc import Callable, Iterable

import arcade


class TextureCache(dict):
    """A cache for arcade textures that loads them only once per path."""

    def get(self, path: str) -> arcade.Texture:
        """Get a texture from the cache, loading it if necessary.

        Args:
            path: Path to the texture file

        Returns:
            The cached or newly loaded texture
        """
        texture = super().get(path)
        if texture is None:
            texture = arcade.load_texture(path)
            self[path] = texture
        return texture


class SpritePool:
    """A pool of sprites that can be acquired and released to avoid allocation during gameplay."""

    def __init__(self, factory: Callable[[], arcade.Sprite], size: int):
        """Initialize the sprite pool.

        Args:
            factory: Function that creates a new sprite
            size: Number of sprites to pre-allocate
        """
        self._factory = factory
        self.active = arcade.SpriteList(use_spatial_hash=True)
        self.inactive = arcade.SpriteList()

        # Pre-allocate all sprites
        for _ in range(size):
            sprite = factory()
            self.inactive.append(sprite)

    def acquire(self, n: int) -> list[arcade.Sprite]:
        """Acquire n sprites from the pool.

        Args:
            n: Number of sprites to acquire

        Returns:
            List of acquired sprites

        Raises:
            RuntimeError: If there aren't enough sprites available
        """
        if n > len(self.inactive):
            raise RuntimeError(f"pool exhausted: requested {n}, available {len(self.inactive)}")

        # Move sprites from inactive to active
        sprites = []
        for _ in range(n):
            sprite = self.inactive.pop(0)
            self.active.append(sprite)
            sprites.append(sprite)

        return sprites

    def release(self, sprites: Iterable[arcade.Sprite]) -> None:
        """Release sprites back to the pool.

        Args:
            sprites: Iterable of sprites to release
        """
        sprites_to_release = list(sprites) if sprites is self.active else sprites

        for sprite in sprites_to_release:
            sprite.visible = False
            # Remove from active list first, then from all sprite lists
            if sprite in self.active:
                self.active.remove(sprite)
            sprite.remove_from_sprite_lists()
            self.inactive.append(sprite)

    def release_all(self) -> None:
        """Release all active sprites back to the pool."""
        # Move all sprites from active to inactive efficiently
        while self.active:
            sprite = self.active.pop()
            sprite.visible = False
            sprite.remove_from_sprite_lists()
            self.inactive.append(sprite)


# Global texture cache
TEXTURES = TextureCache()


def create_forcefield_textures(path: str) -> list[arcade.Texture]:
    """Create forcefield textures with left/right variations.

    Args:
        path: Path to the base forcefield texture

    Returns:
        List containing the base texture and its horizontally flipped version
    """
    base = TEXTURES.get(path)
    return [base, base.flip_horizontally()]


# Global sprite pools - these will be initialized when needed
shield_blocks: SpritePool | None = None
forcefield_sprites: SpritePool | None = None


def initialize_pools() -> None:
    """Initialize all sprite pools. Call this once at game startup."""
    global shield_blocks, forcefield_sprites

    def make_shield_block() -> arcade.Sprite:
        """Factory that creates a single shield block sprite."""
        return arcade.SpriteSolidColor(10, 12, color=arcade.color.GRAY)

    def make_forcefield_sprite() -> arcade.Sprite:
        """Factory that creates a forcefield sprite."""
        from .config import FORCEFIELD

        texture = TEXTURES.get(FORCEFIELD)
        return arcade.Sprite(texture=texture)
