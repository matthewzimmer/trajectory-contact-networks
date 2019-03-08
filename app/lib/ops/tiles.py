import math
import itertools

import networkx as nx
import matplotlib.pyplot as plt

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
            for pt, plot in self.data_op.trajectories(uid):
                traj_pt = TrajectoryPoint(pt, uid)

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
    def __init__(self, hashed_tiles):
        PipelineOp.__init__(self)
        self.hashed_tiles = hashed_tiles
        # self.tile_hash = tile_hash
        # self.uids = uids

    def perform(self):
        png_filepath = 'user_contacts.png' #"{}.png".format(self.tile_hash)

        # tile_count = len(self.hashed_tiles.items())
        # op_count = 0
        graph = nx.Graph()

        for tile_hash, uids in self.hashed_tiles.items():
            if not tile_hash:
                graph_generated = False
                return self._apply_output({"png_filepath": png_filepath, "graph_generated": graph_generated})

            if len(uids) > 1:

                contact_pairs = itertools.combinations(uids, 2)
                for user_pair in contact_pairs:
                    if not graph.has_edge(*user_pair):
                        graph.add_edge(*user_pair, weight=1)
                        print(user_pair)

                # op_count += 1
                # print("Remaining Tiles: " + str(tile_count - op_count))
                
        nx.draw_circular(graph, with_labels=True)  # spectral circular random
        plt.savefig(png_filepath, bbox_inches='tight')
        nx.write_gexf(graph, 'graph.gexf')
        
        graph_generated = True
        return self._apply_output({"png_filepath": png_filepath, "graph_generated": graph_generated})

# nx.generate_graph(image_filepath=png_filepath, nodes=self.uids)
# graph_generated = True
# print("Number of Nodes: " + str(G.number_of_nodes()))
# print("Number of edges: " + str(G.number_of_edges()))
# print("Node degrees: " + str(G.degree()))
# largest_comp = find_largest_component(graph)
# avg_degree = find_average_degree(graph)
# print(find_average_degree(graph))
# print(find_largest_component(graph))

def find_largest_component(graph):
    component_size = [len(c) for c in sorted(nx.connected_components(graph), key=len, reverse=True)]
    return str(max(component_size))
    # print("Largest Component Size: " + str(max(component_size)))
    # print("Component List: " + str(max(nx.connected_components(Graph), key=len)))


def find_average_degree(graph):
    degree_list = []
    for n in graph.nodes():
        degree_list.append(graph.degree(n))
    return str(sum(degree_list) / graph.number_of_nodes())
    # print("Average degree of Nodes " + str(sum(listr)/Graph.number_of_nodes()))


def save_results(largest_comps, ave_degrees, deltas):
    if largest_comps or ave_degrees != 'NULL':
        plt.plot(deltas, largest_comps, label="Largest Component")
        plt.title("Size of Largest Connected Component")
        plt.ylabel("Largest Component Size")
        plt.xlabel("Delta settings")
        plt.savefig('app/viz/Largest_Component_Results.png', bbox_inches='tight')

        plt.plot(deltas, ave_degrees, label="Average Degree")
        plt.title("Average Degree of Nodes")
        plt.ylabel("Mean Degree")
        plt.xlabel("Delta settings")
        plt.savefig('app/viz/Avg_Degree_Results.png', bbox_inches='tight')

