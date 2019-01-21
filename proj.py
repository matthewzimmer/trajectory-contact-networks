
from math import radians, cos, sin, asin, sqrt
import numpy as np

from itertools import combinations
import ast

from app.lib.datasets import GeolifeTrajectories
from app.lib.graph import Graph, Vertex, Edge

import networkx as nx
import matplotlib.pyplot as plt

class Trajectory:
    def __init__(self, t, uid=None):
        self.lat = t[0]
        self.lon = t[1]
        self.alt = t[3]
        self.t = t[4]
        self.uid = uid

    def __str__(self):
        return '[lat: {}  lon: {}  alt: {}  time: {}]'.format(self.lat, self.lon, self.alt, self.t)


class ContactPoint(Trajectory):
    def __init__(self, t0, t1):
        Trajectory.__init__(self, [0, 0, 0, 0, 0])
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
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        # Radius of earth in kilometers is 6371
        km = 6371 * c #6373?
        return km * 1000

    def __str__(self):
        return '[user_i: {}  user_j: {}  dist: {}  time: {}  lat: {}  lon: {}  alt: {}]'.format(self.t0.uid, self.t1.uid, self.dist_apart(), self.t, self.lat, self.lon, self.alt)


def contact(user_i, user_j, data, delta):
    contacts = []
    ds, dt = delta
    for t0 in data.trajectories(user_i):
        for t1 in data.trajectories(user_j):
            tdelta = Trajectory(abs(t0-t1))
            cp = ContactPoint(Trajectory(t0, user_i), Trajectory(t1, user_j))
            if (cp.dist_apart() <= ds):
                if tdelta.t <= dt:
                    contacts.append(cp)
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
        c = ast.literal_eval(c) #convert to dict
        G.add_edge(c[user_i],c[user_j],c[dist])
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
    # combos = contact_combos(data, [0, 0])
    # if False:
    d0 = [100, 300]
    d1 = [500, 600]
    d2 = [1000, 1200]

    for d in [d0, d1, d2]:
        combos = contact_combos(data, d)
        for c in combos:
            print(c)
        print('\n\n\n')

if __name__ == "__main__":
    main()
