"""Pytest configuration and fixtures for wave tests."""

import sys
import types
import pytest


@pytest.fixture(autouse=True)
def stub_arcade_if_needed(monkeypatch):
    """Stub arcade module if it's not available (e.g., in CI without graphics)."""
    try:
        import arcade  # noqa: F401
        # Arcade is available, don't stub
        yield
    except ImportError:
        # Arcade not available, create a stub
        arcade_stub = types.SimpleNamespace()

        # SpriteList stub
        class StubSpriteList(list):
            def __init__(self, *args, **kwargs):
                super().__init__()
                self.visible = False
                if kwargs.get("use_spatial_hash"):
                    pass  # Ignore spatial hash parameter

            def update(self):
                pass

            def draw(self):
                pass

            def append(self, item):
                super().append(item)

            def remove(self, item):
                if item in self:
                    super().remove(item)

            def pop(self, index=0):
                if self:
                    return super().pop(index)
                raise IndexError("pop from empty list")

        # Sprite stub
        class StubSprite:
            def __init__(self, *args, **kwargs):
                self.visible = False
                self.left = 0
                self.bottom = 0
                self.center_x = 0
                self.center_y = 0
                self.color = (128, 128, 128)

            def remove_from_sprite_lists(self):
                self._removed = True

        # SpriteSolidColor factory
        def stub_sprite_solid_color(width, height, color):
            sprite = StubSprite()
            sprite.color = color
            return sprite

        # Assign to stub
        arcade_stub.SpriteList = StubSpriteList
        arcade_stub.Sprite = StubSprite
        arcade_stub.SpriteSolidColor = stub_sprite_solid_color
        arcade_stub.color = types.SimpleNamespace(
            GRAY=(128, 128, 128),
            BLACK=(0, 0, 0),
            RED=(255, 0, 0),
        )
        arcade_stub.check_for_collision_with_list = lambda *args, **kwargs: []

        # Patch the module
        sys.modules["arcade"] = arcade_stub
        monkeypatch.setitem(sys.modules, "arcade", arcade_stub)

        yield

        # Cleanup
        if "arcade" in sys.modules and not hasattr(sys.modules["arcade"], "load_texture"):
            # Only remove if it's our stub
            del sys.modules["arcade"]


@pytest.fixture(autouse=True)
def stub_actions_if_needed(monkeypatch):
    """Stub actions module if it's not available."""
    try:
        import actions  # noqa: F401
        # Actions module is available, don't stub
        yield
    except ImportError:
        # Actions not available, create a stub
        actions_stub = types.SimpleNamespace()

        # Action base class stub
        class StubAction:
            def __init__(self, *args, **kwargs):
                self.done = False
                self._sprites = None

            def stop(self):
                self.done = True

            def apply(self, sprites):
                self._sprites = sprites

            def set_current_velocity(self, velocity):
                self._velocity = velocity

        # move_until function stub
        def stub_move_until(*args, **kwargs):
            action = StubAction()
            if "velocity" in kwargs:
                action._velocity = kwargs["velocity"]
            return action

        # arrange_grid function stub
        def stub_arrange_grid(*args, **kwargs):
            # Just a no-op for testing
            pass

        # infinite condition stub
        def stub_infinite(*args, **kwargs):
            return False  # Never true, so action never completes

        # Assign to stub
        actions_stub.Action = StubAction
        actions_stub.move_until = stub_move_until
        actions_stub.arrange_grid = stub_arrange_grid
        actions_stub.infinite = stub_infinite

        # Patch the module
        sys.modules["actions"] = actions_stub
        monkeypatch.setitem(sys.modules, "actions", actions_stub)

        yield

        # Cleanup
        if "actions" in sys.modules and not hasattr(sys.modules["actions"], "__file__"):
            # Only remove if it's our stub (real modules have __file__)
            del sys.modules["actions"]

