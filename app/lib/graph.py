import numpy as np


class Graph:
    def __init__(self, vertices=[]):
        self.vertices = vertices

    def total_weight(self):
        return np.sum([v.total_weight() for v in self.vertices])


class Vertex:
    def __init__(self, edges=[]):
        self.edges = edges

    def total_weight(self):
        return np.sum([e.weight for e in self.edges])


class Edge:
    def __init(self, vertex1, vertex2, weight):
        self.v1 = vertex1
        self.v2 = vertex2
        self.weight = weight
