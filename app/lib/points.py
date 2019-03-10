import datetime
from math import radians, cos, sin, asin, sqrt

import numpy as np
import pytz


class TrajectoryPoint:
    def __init__(self, pnt, uid=None):
        self.pnt = pnt
        self.uid = uid
        self.lat = pnt[0]
        self.lon = pnt[1]
        self.alt = pnt[3]
        self.days = pnt[4]
        self.datetime = (datetime.datetime(1899, 12, 30, tzinfo=pytz.utc) + datetime.timedelta(days=self.days))
        self.t = self.datetime.timestamp()
        self.t2 = (self.days * 24 * 60 * 60)

    def __str__(self):
        return '[lat: {}  lon: {}  alt: {}  time: {}]'.format(self.lat, self.lon, self.alt, self.t)


class ContactPoint(TrajectoryPoint):
    def __init__(self, p1, p2, traj_plt_p1, traj_plt_p2):
        TrajectoryPoint.__init__(self, [0, 0, 0, 0, 0])
        self.p1 = p1
        self.p2 = p2
        self.traj_plt_p1 = traj_plt_p1
        self.traj_plt_p2 = traj_plt_p2
        self.lat = np.mean([p1.lat, p2.lat])
        self.lon = np.mean([p1.lon, p2.lon])
        self.alt = np.mean([p1.alt, p2.alt])
        self.t = np.mean([p1.t, p2.t])
        self.__dist_apart = None

    def dist_apart(self):
        if self.__dist_apart is None:
            # convert decimal degrees to radians
            lon1, lat1, lon2, lat2 = map(radians, [self.p1.lon, self.p1.lat, self.p2.lon, self.p2.lat])
            # haversine formula
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
            c = 2 * asin(sqrt(a))
            # Radius of earth in kilometers is 6371
            km = 6371 * c
            self.__dist_apart = km * 1000
        return self.__dist_apart

    def tuplize(self):
        return self.p1.uid, self.p2.uid, self.lat, self.lon, self.alt

    def __str__(self):
        return '[user_i: {}  user_j: {}  dist: {}  tdelta: {}  avg_time: {}  avg_lat: {}  avg_lon: {}  avg_alt: {}  ' \
               'traj_i: {}  traj_j: {}]'.format(
                self.p1.uid,
                self.p2.uid,
                self.dist_apart(),
                abs(self.p1.t - self.p2.t),
                self.t,
                self.lat,
                self.lon,
                self.alt,
                self.traj_plt_p1,
                self.traj_plt_p2
        )
