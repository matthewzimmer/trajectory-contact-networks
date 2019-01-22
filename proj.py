import datetime
from math import radians, cos, sin, asin, sqrt
import numpy as np

from itertools import combinations
import ast

import pytz

from app.lib.data_serializer import DataSerializer
from app.lib.datasets import GeolifeTrajectories
from app.lib.graph import Graph, Vertex, Edge

import networkx as nx
import matplotlib.pyplot as plt


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

    def __str__(self):
        return '[user_i: {}  user_j: {}  dist: {}  tdelta: {}  avg_time: {}  avg_lat: {}  avg_lon: {}  avg_alt: {}  traj_i: {}  traj_j: {}]'.format(
            self.p1.uid,
            self.p2.uid,
            self.dist_apart(),
            abs(self.p1.t - self.p2.t),
            self.t,
            self.lat,
            self.lon,
            self.alt,
            self.traj_plt_p1,
            self.traj_plt_p2)


def contact(user_i, user_j, data, delta):
    contacts = []
    ds, dt = delta
    total_count = 0
    for traj_plt_i in data.load_user_trajectory_plts(user_i):
        for traj_plt_j in data.load_user_trajectory_plts(user_j):
            pnt_i_count = 0
            next_j_plt = False
            for pnt_i in data.load_trajectory_plt_points(traj_plt_i):
                if next_j_plt:
                    break

                pnt_i = TrajectoryPoint(pnt_i, user_i)
                pnt_i_count = pnt_i_count + 1
                pnt_j_count = 0
                for pnt_j in data.load_trajectory_plt_points(traj_plt_j):
                    pnt_j = TrajectoryPoint(pnt_j, user_j)
                    pnt_j_count = pnt_j_count + 1
                    total_count = total_count + 1

                    tdelta = abs(pnt_i.t - pnt_j.t)
                    cp = ContactPoint(pnt_i, pnt_j, traj_plt_i, traj_plt_j)
                    print('t: {}    dist: {}    ui: {}    uj: {}    tot: {}    plt_i: {}    plt_j: {}'.format(tdelta,
                                                                                                              cp.dist_apart(),
                                                                                                              user_i,
                                                                                                              user_j,
                                                                                                              total_count,
                                                                                                              traj_plt_i,
                                                                                                              traj_plt_j))
                    if tdelta <= dt:
                        if cp.dist_apart() <= ds:
                            print('    CONTACT!')
                            contacts.append(cp)
                            if len(contacts) % 1000 == 0:
                                save_contacts(ds, dt, contacts)
                    else:
                        if pnt_j_count == 1:
                            # The first point in user j's trajectory is not within dt seconds so we
                            # signal to move to the next trajectory for user j.
                            next_j_plt = True
                            break  # Move to the next PLT for user j
    save_contacts(ds, dt, contacts)
    return contacts


def save_contacts(ds, dt, contacts):
    DataSerializer.save_data({'ds': ds, 'dt': dt, 'total': len(contacts), 'contacts': contacts},
                             'app/data/contacts/ContactPoints_ds{}_dt{}.pickle'.format(ds, dt))


def load_contacts(ds, dt):
    return DataSerializer.reload_data('app/data/contacts/ContactPoints_ds{}_dt{}.pickle'.format(ds, dt))


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

    ignore_cache = False
    for d in deltas:
        ds, dt = d
        contact_point_data = load_contacts(ds, dt)
        if ignore_cache or contact_point_data is None:
            contact_points = contact_combos(data, d)
        else:
            contact_points = contact_point_data['contacts']
            total = contact_point_data['total']
            print('Loaded {} pickled contact points for ds={}, dt={}\n\n'.format(total, ds, dt))
        for cp in contact_points:
            print(cp)
        print('\n\n\n')


if __name__ == "__main__":
    main()
