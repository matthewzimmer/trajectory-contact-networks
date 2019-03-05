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
            lat = self.meters_for_lat_lon(traj_pt.lat)
            lon = self.meters_for_lat_lon(traj_pt.lon)
            t = traj_pt.t

            local_lat = math.floor(lat/self.ds) * self.ds
            local_lon = math.floor(lon/self.ds) * self.ds
            local_t = math.floor(t/self.dt) * self.dt

            tile_hash = "lat{}_lon{}_t{}".format(local_lat, local_lon, local_t)
            tile = self.hash_tile(tile_hash)
            tile.append((traj_pt, self.global_lat + local_lat, self.global_lon + local_lon, local_t, self.ds, self.dt))

        return self._apply_output(self.tiles)

    def hash_tile(self, tile_hash):
        tile = self.tiles.get(tile_hash, None)
        if tile is None:
            tile = []
            self.tiles[tile_hash] = tile
        return tile

    def meters_for_lat_lon(self, lat_lon):
        return lat_lon