"""Context classes for passing read-only bundles of objects."""

from collections.abc import Callable
from typing import TYPE_CHECKING

import arcade

if TYPE_CHECKING:
    from .waves import EnemyWave


class WaveContext:
    """
    Read-only bundle of objects a wave may need.

    Nothing here is specific to any particular wave pattern.
    """

    __slots__ = ("shot_list", "player_ship", "register_damage", "on_cleanup")

    def __init__(
        self,
        *,
        shot_list: arcade.SpriteList,
        player_ship: arcade.Sprite,
        register_damage: Callable[[float], None],
        on_cleanup: Callable[["EnemyWave"], None],
    ):
        self.shot_list = shot_list
        self.player_ship = player_ship
        self.register_damage = register_damage
        self.on_cleanup = on_cleanup


class PlayerContext:
    """
    Read-only bundle of objects a PlayerShip may need.

    Nothing here is specific to any particular player behavior.
    """

    __slots__ = ("shot_list", "hill_tops", "hill_bottoms", "tunnel_walls", "set_tunnel_velocity", "register_damage")

    def __init__(
        self,
        *,
        shot_list: arcade.SpriteList,
        hill_tops: arcade.SpriteList,
        hill_bottoms: arcade.SpriteList,
        tunnel_walls: arcade.SpriteList,
        set_tunnel_velocity: Callable[[float], None],
        register_damage: Callable[[float], None],
    ):
        self.shot_list = shot_list
        self.hill_tops = hill_tops
        self.hill_bottoms = hill_bottoms
        self.tunnel_walls = tunnel_walls
        self.set_tunnel_velocity = set_tunnel_velocity
        self.register_damage = register_damage
