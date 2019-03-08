import math
import numpy as np

from app.lib.datasets import GeolifeData
from app.lib.pipeline_ops import PipelineOp
from app.lib.points import TrajectoryPoint


class GenerateTilesOp(PipelineOp):
    """
    Generates a dictionary of tiles where the key is a hash
    of lat/lon/time and the value is a set of unique user
    ids that have points within that encoded
    spaciotemporal tile (cube).
    """
    def __init__(self, ds, dt, relative_null_point=(39.75872, 116.04142)):
        PipelineOp.__init__(self)
        self.tiles = {}
        self.data_op = GeolifeData()
        self.users = self.data_op.users()
        self.ds = ds
        self.dt = dt
        self.relative_null_lat = relative_null_point[0]
        self.relative_null_lon = relative_null_point[1]

    def perform(self):
        for uid in self.users:
            for pt, plt in self.geolife_data_op.trajectories(uid):
                traj_pt = TrajectoryPoint(pt, self.uid)

                lat, lon = self.meters_for_lat_lon(traj_pt.lat, traj_pt.lon)
                t = traj_pt.t

                local_lat_meters = int(lat / self.ds) * self.ds
                local_lon_meters = int(lon / self.ds) * self.ds

                local_lat, local_lon = self.get_lat_lng_from_meters(local_lat_meters, local_lon_meters)
                local_t = math.floor(t / self.dt) * self.dt

                tile_hash = "lat{}_lon{}_t{}".format(local_lat, local_lon, local_t)
                tile = self.hash_tile(tile_hash)
                tile.add(traj_pt.uid)

        return self._apply_output(self.tiles)

    def hash_tile(self, tile_hash):
        """
        Returns an existing tile based on tile hash if already generated.
        Otherwise, generates and returns a new set for the given tile_hash.
        """
        tile = self.tiles.get(tile_hash, None)
        if tile is None:
            tile = set()
            self.tiles[tile_hash] = tile
        return tile

    def meters_for_lat_lon(self, lat, lon):
        """ Calculates X and Y distances in meters.
        """
        delta_latitude = lat - self.relative_null_lat
        delta_longitude = lon - self.relative_null_lon
        latitude_circumference = 40075160 * math.cos(self.deg_to_rad(self.relative_null_lat))
        result_x = delta_longitude * latitude_circumference / 360
        result_y = delta_latitude * 40008000 / 360
        return result_x, result_y

    def get_lat_lng_from_meters(self, lat, lon):
        latitude_circumference = 40075160 * math.cos(self.deg_to_rad(self.relative_null_lat))
        delta_latitude = lon * 360 / 40008000
        delta_longitude = lat * 360 / latitude_circumference

        result_lat = delta_latitude + self.relative_null_lat
        result_lng = delta_longitude + self.relative_null_lon

        return result_lat, result_lng

    @staticmethod
    def deg_to_rad(degrees):
        return degrees * math.pi / 180


class GraphContactPointsOp(PipelineOp):
    def __init__(self, tile_hash, uids):
        PipelineOp.__init__(self)
        self.tile_hash = tile_hash
        self.uids = uids

    def perform(self):
        png_filepath = "{}.png".format(self.tile_hash)
        graph_generated = False

        if len(self.uids) > 1:
            # TODO: Generate PNG of graph using networkx API.
            #       Name of PNG should be the value of self.tile_hash.
            #
            #   Pseudocode:
            #
            #       networkx.generate_graph(image_filepath=png_path, nodes=self.uids)
            #       graph_generated = True
            pass

        return self._apply_output({"png_filepath": png_filepath, "graph_generated": graph_generated})
