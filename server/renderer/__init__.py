from common.enum import TileType
from renderer import tunnel_v2, cavern_v1


def get_renderer(tile_type: TileType):
    if tile_type == TileType.TUNNEL:
        return tunnel_v2
    if tile_type == TileType.CAVERN:
        return cavern_v1
    raise ValueError(f"Invalid tile_type: {tile_type}")
