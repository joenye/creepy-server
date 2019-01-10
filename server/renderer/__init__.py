from common.enum import TileType
from renderer import tunnel, cavern


def get_renderer(tile_type: TileType):
    if tile_type == TileType.TUNNEL:
        return tunnel
    if tile_type == TileType.CAVERN:
        return cavern
    raise ValueError(f"Invalid tile_type: {tile_type}")
