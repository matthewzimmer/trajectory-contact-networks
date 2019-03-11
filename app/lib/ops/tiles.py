from math import radians, cos, sin, asin, pi, sqrt
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
                local_t = int(t / self.dt) * self.dt

                tile_hash = "lat{}_lon{}_t{}".format(local_lat, local_lon, local_t)
                tile = self.hash_tile(tile_hash)
                users = [sub_list[0] for sub_list in tile]
                if traj_pt.uid not in users:
                    tile.append([traj_pt.uid, (traj_pt.lat, traj_pt.lon), t, (self.ds, self.dt)])
        return self._apply_output(self.tiles)

    def hash_tile(self, tile_hash):
        """
        Returns an existing tile based on tile hash if already generated.
        Otherwise, generates and returns a new set for the given tile_hash.
        """
        tile = self.tiles.get(tile_hash, None)
        if tile is None:
            tile = []
            self.tiles[tile_hash] = tile
        return tile

    def meters_for_lat_lon(self, lat, lon):
        """ Calculates X and Y distances in meters.
        """
        delta_latitude = lat - self.relative_null_lat
        delta_longitude = lon - self.relative_null_lon
        latitude_circumference = 40075160 * cos(self.deg_to_rad(self.relative_null_lat))
        result_x = delta_longitude * latitude_circumference / 360
        result_y = delta_latitude * 40008000 / 360
        return result_x, result_y

    def get_lat_lng_from_meters(self, lat, lon):
        latitude_circumference = 40075160 * cos(self.deg_to_rad(self.relative_null_lat))
        delta_latitude = lon * 360 / 40008000
        delta_longitude = lat * 360 / latitude_circumference

        result_lat = delta_latitude + self.relative_null_lat
        result_lng = delta_longitude + self.relative_null_lon

        return result_lat, result_lng

    @staticmethod
    def deg_to_rad(degrees):
        return degrees * pi / 180


class GraphContactPointsOp(PipelineOp):
    def __init__(self, hashed_tiles, weight):
        PipelineOp.__init__(self)
        self.hashed_tiles = hashed_tiles
        self.weight = weight

    def perform(self):
        tiles = self.hashed_tiles.items()
        tile_count = len(tiles)
        op_count = 0
        graph = nx.Graph()
        delta = []
        for tile_hash, uids in tiles:
            if not tile_hash:
                graph_generated = False
                png_filepath = 'app/data/graphs/no_tiles_from_data.png'
                return self._apply_output({"png_filepath": png_filepath, "graph_generated": graph_generated})
            if not delta:
                delta = uids[0][3]
            if len(uids) > 1:
                contact_pairs = itertools.combinations(uids, 2)
                for user_pair in contact_pairs:
                    if self.weight == 'dist_weight':
                        graph = weight_by_count(graph, user_pair[0][0], user_pair[1][0])
                    elif self.weight == 'count_weight':
                        graph = weight_by_distance(graph, user_pair[0], user_pair[1])

            op_count += 1
            print("Remaining Tiles: {}".format(tile_count - op_count))

        # png_filepath = 'app/data/graphs/{}.png'.format(str(delta[0]) + 'ds_' + str(delta[1]) + 'dt')
        # nx.draw_circular(graph, with_labels=True)  # spectral circular random
        # plt.savefig(png_filepath, bbox_inches='tight')
        png_filepath = 'app/data/graphs/{}.gml'.format(str(delta[0]) + 'ds_' + str(delta[1]) + 'dt_' + str(self.weight))
        nx.write_gml(graph, png_filepath)
        
        graph_generated = True
        # largest_comp = find_largest_component(graph)
        # avg_degree = find_average_degree(graph)
        # graph_results(largest_comp, avg_degree, deltas)
        return self._apply_output({"png_filepath": png_filepath, "graph_generated": graph_generated})


class GraphHottestPointsOp(PipelineOp):
    def __init__(self, hashed_tiles, weight):
        PipelineOp.__init__(self)
        self.hashed_tiles = hashed_tiles
        self.weight = weight

    def perform(self):
        user_count_in_tiles = [len(uids) for tile_hash, uids in self.hashed_tiles.items()]
        hot_zone_count = max(user_count_in_tiles)
        graph = nx.Graph()
        delta = []
        for tile_hash, uids in self.hashed_tiles.items():
            if not delta:
                delta = uids[0][3]
            if len(uids) == hot_zone_count:
                contact_pairs = itertools.combinations(uids, 2)
                for user_pair in contact_pairs:
                    if self.weight == 'dist_weight':
                        graph = weight_by_count(graph, user_pair[0][0], user_pair[1][0])
                    elif self.weight == 'count_weight':
                        graph = weight_by_distance(graph, user_pair[0], user_pair[1])

        png_filepath = 'app/data/graphs/{}.gml'.format(str(delta[0]) + 'ds_' + str(delta[1]) + 'dt_hot_zones')
        nx.write_gml(graph, png_filepath)
        graph_generated = True
        return self._apply_output({"png_filepath": png_filepath, "graph_generated": graph_generated})


def weight_by_count(graph, user1, user2):
    distance = dist_apart(user1[1], user2[1])
    time_difference = abs(user1[2] - user2[2])

    if not graph.has_edge(user1, user2):
        graph.add_edge(user1, user2, weight=1, ds=time_difference, distance=distance)
    else:
        graph[user1][user2]['weight'] += 1
        graph[user1[0]][user2[0]]['ds'] = time_difference
        graph[user1[0]][user2[0]]['dt'] = distance
    return graph


def weight_by_distance(graph, user1, user2):
    distance = dist_apart(user1[1], user2[1])
    delta = user1[3]
    weight = delta[1] - dist_apart(user1[1], user2[1])
    time_difference = abs(user1[2] - user2[2])
    if not graph.has_edge(user1[0], user2[0]):
        graph.add_edge(user1[0], user2[0], weight=weight, distance=distance, ds=time_difference, dt=distance)
    else:
        if graph[user1[0]][user2[0]]['weight'] > weight:
            graph[user1[0]][user2[0]]['weight'] = weight
            graph[user1[0]][user2[0]]['ds'] = time_difference
            graph[user1[0]][user2[0]]['dt'] = distance
    return graph


def dist_apart(p1, p2):
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [p1[1], p1[0], p2[1], p2[0]])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    # Radius of earth in kilometers is 6371
    km = 6371 * c
    dist_apart = km * 1000
    return dist_apart

# def find_largest_component(graph):
#     component_size = [len(c) for c in sorted(nx.connected_components(graph), key=len, reverse=True)]
#     return str(max(component_size))
#     # print("Largest Component Size: " + str(max(component_size)))
#     # print("Component List: " + str(max(nx.connected_components(Graph), key=len)))
#
#
# def find_average_degree(graph):
#     degree_list = []
#     for n in graph.nodes():
#         degree_list.append(graph.degree(n))
#     return str(sum(degree_list) / graph.number_of_nodes())
#     # print("Average degree of Nodes " + str(sum(listr)/Graph.number_of_nodes()))
#
#
# def graph_results(largest_comps, avg_degrees, deltas):
#     if largest_comps or avg_degrees != 'NULL':
#         plt.plot(deltas, largest_comps, label="Largest Component")
#         plt.title("Size of Largest Connected Component")
#         plt.ylabel("Largest Component Size")
#         plt.xlabel("Delta settings")
#         plt.savefig('app/viz/Largest_Component_Results.png', bbox_inches='tight')
#
#         plt.plot(deltas, avg_degrees, label="Average Degree")
#         plt.title("Average Degree of Nodes")
#         plt.ylabel("Mean Degree")
#         plt.xlabel("Delta settings")
#         plt.savefig('app/viz/Avg_Degree_Results.png', bbox_inches='tight')

