from app.lib.datasets import GeolifeData
from app.lib.ops.tiles import GenerateUserTilesOp


def test_generate_user_tiles():
    data_op = GeolifeData()

    ds = 1000
    dt = 1200
    global_origin = (0, 0)

    tiles = {}

    for uid in data_op.users():
        user_tiles_op = GenerateUserTilesOp(tiles, uid, data_op.trajectories(uid), ds, dt, global_origin)
        updated_tiles = user_tiles_op.output()
        print(updated_tiles)
        