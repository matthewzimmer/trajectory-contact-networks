import math
import numpy as np




from app.lib.pipeline_ops import PipelineOp
from app.lib.points import TrajectoryPoint



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

    def asRadians(self,degrees):
        return degrees * math.pi / 180

    def perform(self):
        for pt, plt in self.user_trajectories_pts:
            traj_pt = TrajectoryPoint(pt, self.uid)
            # lat = self.meters_for_lat_lon(traj_pt.lat)
            # lon = self.meters_for_lat_lon(traj_pt.lon)
            relativeNullPoint = {}
            relativeNullPoint['latitude'] = 39.75872
            relativeNullPoint['longitude'] = 116.04142



            lat,lon = self.meters_for_lat_lon(relativeNullPoint,traj_pt.lat,traj_pt.lon)
            t = traj_pt.t

            # local_lat = math.floor(lat/self.ds) * self.ds
            # local_lon = math.floor(lon/self.ds) * self.ds

            local_lat_meters = int(lat / self.ds) * self.ds
            local_lon_meters = int(lon / self.ds) * self.ds

            local_lat, local_lon = self.get_LatLng_from_meters(relativeNullPoint, local_lat_meters, local_lon_meters)
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

    #implementation for lat,lng to meters




    def meters_for_lat_lon(self,relativeNullPoint,lat,lon):

        """ Calculates X and Y distances in meters.
        """
        deltaLatitude =lat- relativeNullPoint['latitude']
        deltaLongitude = lon- relativeNullPoint['longitude']
        latitudeCircumference = 40075160 * math.cos(self.asRadians(relativeNullPoint['latitude']))
        resultX = deltaLongitude * latitudeCircumference / 360
        resultY = deltaLatitude * 40008000 / 360
        return resultX, resultY

    def get_LatLng_from_meters(self,relativeNullPoint, x, y):
        latitudeCircumference = 40075160 * math.cos(self.asRadians(relativeNullPoint['latitude']))
        deltaLatitude = y * 360 / 40008000
        deltaLongitude = x * 360 / latitudeCircumference

        resultLat = deltaLatitude + relativeNullPoint['latitude']
        resultLng = deltaLongitude + relativeNullPoint['longitude']

        return resultLat, resultLng




