from app.lib.datasets import GeolifeData
from app.lib.ops.tiles import GenerateUserTilesOp


def test_generate_user_tiles():
    data_op = GeolifeData()

    ds = 0.01
    dt = 1200
    global_origin = (0, 0)

    for uid in data_op.users():
        user_tiles_op = GenerateUserTilesOp(uid, data_op.trajectories(uid), ds, dt, global_origin).output()
        print(uid, user_tiles_op)