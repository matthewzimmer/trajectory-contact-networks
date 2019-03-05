import math
import numpy as np

from app.lib.pipeline_ops import PipelineOp
from app.lib.points import TrajectoryPoint


class GenerateUserTilesOp(PipelineOp):
    def __init__(self, user_id, user_trajectory_pts, ds, dt, global_origin):
        PipelineOp.__init__(self)
        self.uid = user_id
        self.user_trajectories_pts = user_trajectory_pts
        self.ds = ds
        self.dt = dt
        self.global_origin = global_origin
        self.global_lat = global_origin[0]
        self.global_lon = global_origin[1]
        self.tiles = {}

    def perform(self):
        for pt, plt in self.user_trajectories_pts:
            traj_pt = TrajectoryPoint(pt, self.uid)
            lat = traj_pt.lat
            lon = traj_pt.lon
            t = traj_pt.t

            local_lat = round(math.floor(lat/self.ds) * self.ds, 1)
            local_lon = round(math.floor(lon/self.ds) * self.ds, 1)
            local_t = round(math.floor(t/self.dt) * self.dt, 1)

            tile_hash = "lat{}_lon{}".format(local_lat, local_lon)
            tile = self.hash_tile(tile_hash)
            tile.append((pt, local_lat, local_lon, local_t, self.ds, self.dt))

        return self._apply_output(self.tiles)

    def hash_tile(self, tile_hash):
        tile = self.tiles.get(tile_hash, None)
        if tile is None:
            tile = []
            self.tiles[tile_hash] = tile
        return tile
