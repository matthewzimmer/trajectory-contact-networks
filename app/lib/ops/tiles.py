import math
from pyproj import Proj, transform
from app.lib.pipeline_ops import PipelineOp
from app.lib.points import TrajectoryPoint
def transform_geo(df):

    return df

class GenerateUserTilesOp(PipelineOp):
    def __init__(self, tiles, user_id, user_trajectory_pts, ds, dt, global_origin):
        PipelineOp.__init__(self)
        self.uid = user_id
        self.user_trajectories_pts = user_trajectory_pts
        self.ds = ds
        self.dt = dt
        self.global_origin = global_origin
        self.global_lat = global_origin[0]
        self.global_lon = global_origin[1]
        self.tiles = tiles

    def perform(self):
        for pt, plt in self.user_trajectories_pts:
            traj_pt = TrajectoryPoint(pt, self.uid)
            lat, lon = self.coordinate_conversion(traj_pt.lat, traj_pt.lon)
            # lon = self.coordinate_conversion(traj_pt.lon)
            t = traj_pt.t

            local_lat = math.floor(lat/self.ds) * self.ds
            local_lon = math.floor(lon/self.ds) * self.ds
            local_t = math.floor(t/self.dt) * self.dt

            tile_hash = "lat{}_lon{}_t{}".format(local_lat, local_lon, local_t)
            tile = self.hash_tile(tile_hash)
            # tile.append((traj_pt, self.global_lat + local_lat, self.global_lon + local_lon, local_t, self.ds, self.dt))
            tile.add(traj_pt.uid)

        return self._apply_output(self.tiles)

    def hash_tile(self, tile_hash):
        tile = self.tiles.get(tile_hash, None)
        if tile is None:
            tile = set()
            self.tiles[tile_hash] = tile
        return tile

    def coordinate_conversion(self, x, y):
        p1 = Proj(proj='latlong', datum='WGS84')
        # You can also search for UTM projections in the epsg reference website
        p3 = Proj(proj='utm', zone=49, datum='WGS84')
        # Call the tranform method and store the tranformed variables
        x, y = transform(p1, p3, x, y)
        return x, y
