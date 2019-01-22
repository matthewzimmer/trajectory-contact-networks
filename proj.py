import datetime
from math import radians, cos, sin, asin, sqrt
import numpy as np

from itertools import combinations
import ast

import pytz

from app.lib.datasets import GeolifeTrajectories
from app.lib.graph import Graph, Vertex, Edge

import networkx as nx
import matplotlib.pyplot as plt


class TrajectoryPoint:
    def __init__(self, t, uid=None):
        self.lat = t[0]
        self.lon = t[1]
        self.alt = t[3]
        self.days = t[4]
        self.datetime = (datetime.datetime(1899, 12, 30, tzinfo=pytz.utc) + datetime.timedelta(days=self.days))
        self.t = self.datetime.timestamp()
        self.t2 = (self.days * 24 * 60 * 60)
        self.uid = uid

    def __str__(self):
        return '[lat: {}  lon: {}  alt: {}  time: {}]'.format(self.lat, self.lon, self.alt, self.t)


class ContactPoint(TrajectoryPoint):
    def __init__(self, t0, t1):
        TrajectoryPoint.__init__(self, [0, 0, 0, 0, 0])
        self.t0 = t0
        self.t1 = t1
        self.lat = np.mean([t0.lat, t1.lat])
        self.lon = np.mean([t0.lon, t1.lon])
        self.t = np.mean([t0.t, t1.t])

    def dist_apart(self):
        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [self.t0.lon, self.t0.lat, self.t1.lon, self.t1.lat])
        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        # Radius of earth in kilometers is 6371
        km = 6371 * c  # 6373?
        return km * 1000

    def __str__(self):
        return '[user_i: {}  user_j: {}  dist: {}  time: {}  lat: {}  lon: {}  alt: {}]'.format(self.t0.uid,
                                                                                                self.t1.uid,
                                                                                                self.dist_apart(),
                                                                                                self.t, self.lat,
                                                                                                self.lon, self.alt)


def contact(user_i, user_j, data, delta):
    contacts = []
    ds, dt = delta
    total_count = 0
    counter = 0
    # for pnt_i, traj_plt_i in data.trajectories(user_i):
    for traj_plt_i in data.load_user_trajectory_plts(user_i):
        next_i_plt = False
        for pnt_i in data.load_trajectory_plt_points(traj_plt_i):
            if next_i_plt:
                break

            pnt_i = TrajectoryPoint(pnt_i, user_i)

            for traj_plt_j in data.load_user_trajectory_plts(user_j):
                counter = 0
                for pnt_j in data.load_trajectory_plt_points(traj_plt_j):
                    counter = counter + 1
                    total_count = total_count + 1

                    pnt_j = TrajectoryPoint(pnt_j, user_j)
                    tdelta = abs(pnt_i.t - pnt_j.t)
                    cp = ContactPoint(pnt_i, pnt_j)
                    if tdelta <= dt:
                        if cp.dist_apart() <= ds:
                            print('CONTACT:  t: {}    dist: {}    ui: {}    uj: {}    tot: {}    plt_i: {}    plt_j: {}'.format(tdelta, cp.dist_apart(), user_i, user_j, total_count, traj_plt_i, traj_plt_j))
                            contacts.append(cp)
                    else:
                        if counter == 1:
                            next_i_plt = True
                            break
    return contacts


def contact_combos(data, delta):
    combos = set()
    users = data.users()
    user_combos = combinations(users, 2)
    for i, j in user_combos:
        contacts = contact(i, j, data, delta)
        for c in contacts:
            combos.add((i, j, c.lat, c.lon, c.t))
    return combos


def grapher(combos):
    G = nx.Graph()
    for c in combos:
        c = ast.literal_eval(c)  # convert to dict
        G.add_edge(c[user_i], c[user_j], c[dist])
    # G.add_node(c[0])
    # G.add_node(c[1])
    # G.add_edge(c[0], c[1], weight = c[2])
    G.number_of_nodes()
    G.number_of_edges()
    nx.draw(G)
    plt.show()

    # edges, vertices = [],[]
    # E = Edge(Vertex(c[0]),Vertex(c[1]))
    # edges.append(E)
    # for V in verts:
    #     vertices.append(Vertex(Vertex(c[0],edges)))
    # Gr = Graph(vertices)
    # print(Gr.total_weight())


def main():
    data = GeolifeTrajectories().load()

    # [ds, dt] ==> [meters from each other,  seconds apart]
    deltas = []
    # deltas.append([100, 300])
    # deltas.append([500, 600])
    deltas.append([1000, 1200])
    # deltas.append([1000, 1200])

    for d in deltas:
        combos = contact_combos(data, d)
        for c in combos:
            print(c)
        print('\n\n\n')


if __name__ == "__main__":
    main()
