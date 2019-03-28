from math import radians, cos, sin, asin, pi, sqrt
import itertools
import networkx as nx
import numpy as np


from app.lib.datasets import GeolifeData
from app.lib.pipeline_ops import PipelineOp
from app.lib.points import TrajectoryPoint


class GenerateTilesOp(PipelineOp):
    EARTH_CIRCUMFERENCE_AT_EQUATOR_METERS = 40075160
    EARTH_CIRCUMFERENCE_THROUGH_POLES_METERS = 40008000

    """
    Generates a dictionary of tiles where the key is a hash
    of lat/lon/time and the value is a set of unique user
    ids that have points within that encoded
    spaciotemporal tile (cube).
    """
    def __init__(self, users, ds, dt, relative_null_point=(39.75872, 116.04142)):
        PipelineOp.__init__(self)
        self.tiles = {}
        self.data_op = GeolifeData()
        self.users = np.array(users)
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
                # extract first column (uid)
                users = [sub_list[0] for sub_list in tile]
                if traj_pt.uid not in users:
                    tile.append([traj_pt.uid, traj_pt.lat, traj_pt.lon, t, self.ds, self.dt])
        return self._apply_output(self.tiles)

    def hash_tile(self, tile_hash):
        """
        Returns an existing tile based on tile hash if already generated.
        Otherwise, generates and returns a new list for the given tile_hash.
        """
        tile = self.tiles.get(tile_hash, None)
        if tile is None:
            tile = []
            self.tiles[tile_hash] = tile
        return tile

    def meters_for_lat_lon(self, lat, lon):
        """
        Calculates X and Y distances in meters.

        https://stackoverflow.com/a/3024728
        """
        delta_latitude = lat - self.relative_null_lat
        delta_longitude = lon - self.relative_null_lon
        latitude_circumference = self.EARTH_CIRCUMFERENCE_AT_EQUATOR_METERS * cos(self.deg_to_rad(self.relative_null_lat))
        result_x = delta_longitude * latitude_circumference / 360
        result_y = delta_latitude * self.EARTH_CIRCUMFERENCE_THROUGH_POLES_METERS / 360
        return result_x, result_y

    def get_lat_lng_from_meters(self, lat, lon):
        latitude_circumference = self.EARTH_CIRCUMFERENCE_AT_EQUATOR_METERS * cos(self.deg_to_rad(self.relative_null_lat))
        delta_latitude = lon * 360 / self.EARTH_CIRCUMFERENCE_THROUGH_POLES_METERS
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
        assert(weight in ['dist_weight', 'count_weight'])

    def perform(self):
        contact_points = [['uid1', 'uid2', 'ds', 'dt', 'tile_hash', 'dist_apart', 'time_diff', 'lat1', 'lat2', 'lon1', 'lon2', 't1', 't2']]
        tiles = self.hashed_tiles.items()
        tile_count = len(tiles)
        op_count = 0
        graph = nx.Graph()
        delta = (None, None)
        for tile_hash, uids in tiles:
            if not tile_hash:
                graph_filepath = 'app/data/graphs/no_tiles_from_data.png'
                return self._apply_output({"graph_filepath": graph_filepath, "graph_generated": False})
            if not delta:
                delta = (uids[0][4], uids[0][5])
            if len(uids) > 1:
                contact_pairs = itertools.combinations(uids, 2)
                for user_pair in contact_pairs:
                    user1, user2 = user_pair
                    u1_uid, u1_lat, u1_lon, u1_t, u1_ds, u1_dt = user1
                    u2_uid, u2_lat, u2_lon, u2_t, u2_ds, u2_dt = user2
                    u1_lat_lon = (u1_lat, u1_lon)
                    u2_lat_lon = (u2_lat, u2_lon)
                    distance = dist_apart(u1_lat_lon, u2_lat_lon)
                    time_difference = abs(u1_t - u2_t)
                    contact_points.append([u1_uid, u2_uid, u1_ds, u1_dt, tile_hash, distance, time_difference, u1_lat, u2_lat, u1_lon, u2_lon, u1_t, u2_t])

                    if self.weight == 'dist_weight':
                        graph = weight_by_distance(graph, user1, user2)
                    elif self.weight == 'count_weight':
                        graph = weight_by_count(graph, user1, user1)

            op_count += 1
            print("Remaining Tiles: {}".format(tile_count - op_count))

        # graph_filepath = 'app/data/graphs/{}.png'.format(str(delta[0]) + 'ds_' + str(delta[1]) + 'dt')
        # nx.draw_circular(graph, with_labels=True)  # spectral circular random
        # plt.savefig(graph_filepath, bbox_inches='tight')
        ds, dt = delta
        gml_filepath = 'app/data/graphs/{}.gml'.format(str(ds) + 'ds_' + str(dt) + 'dt_' + str(self.weight))
        nx.write_gml(graph, gml_filepath)

        # largest_comp = find_largest_component(graph)
        # avg_degree = find_average_degree(graph)
        # graph_results(largest_comp, avg_degree, deltas)
        return self._apply_output({"contact_points": np.asarray(contact_points), "graph_filepath": gml_filepath, "graph_generated": True})


class GraphHottestPointsOp(PipelineOp):
    def __init__(self, hashed_tiles, weight):
        PipelineOp.__init__(self)
        self.hashed_tiles = hashed_tiles
        self.weight = weight

    def perform(self):
        contact_points = [['uid1', 'uid2', 'ds', 'dt', 'tile_hash', 'dist_apart', 'time_diff', 'lat1', 'lat2', 'lon1', 'lon2', 't1', 't2']]
        user_count_in_tiles = [len(uids) for tile_hash, uids in self.hashed_tiles.items()]
        hot_zone_count = max(user_count_in_tiles)
        graph = nx.Graph()
        delta = (None, None)
        for tile_hash, uids in self.hashed_tiles.items():
            if not delta:
                delta = (uids[0][4], uids[0][5])
            if len(uids) == hot_zone_count:
                contact_pairs = itertools.combinations(uids, 2)
                for user_pair in contact_pairs:
                    user1, user2 = user_pair
                    u1_uid, u1_lat, u1_lon, u1_t, u1_ds, u1_dt = user1
                    u2_uid, u2_lat, u2_lon, u2_t, u2_ds, u2_dt = user2
                    u1_lat_lon = (u1_lat, u1_lon)
                    u2_lat_lon = (u2_lat, u2_lon)
                    distance = dist_apart(u1_lat_lon, u2_lat_lon)
                    time_difference = abs(u1_t - u2_t)
                    contact_points.append([u1_uid, u2_uid, u1_ds, u1_dt, tile_hash, distance, time_difference, u1_lat, u2_lat, u1_lon, u2_lon, u1_t, u2_t])

                    if self.weight == 'dist_weight':
                        graph = weight_by_distance(graph, user_pair[0], user_pair[1])
                    elif self.weight == 'count_weight':
                        graph = weight_by_count(graph, user_pair[0], user_pair[1])

        ds, dt = delta
        gml_filepath = 'app/data/graphs/{}.gml'.format(str(ds) + 'ds_' + str(dt) + 'dt_hot_zones')
        nx.write_gml(graph, gml_filepath)

        return self._apply_output({"contact_points": np.asarray(contact_points), "gml_filepath": gml_filepath, "graph_generated": True})


def weight_by_count(graph, user1, user2):
    u1_uid, u1_lat, u1_lon, u1_t, u1_ds, u1_dt = user1
    u2_uid, u2_lat, u2_lon, u2_t, u2_ds, u2_dt = user2
    u1_lat_lon = (u1_lat, u1_lon)
    u2_lat_lon = (u2_lat, u2_lon)
    distance = dist_apart(u1_lat_lon, u2_lat_lon)
    time_difference = abs(u1_t - u2_t)

    if not graph.has_edge(u1_uid, u2_uid):
        graph.add_edge(u1_uid, u2_uid, weight=1, ds=time_difference, distance=distance)
    else:
        graph[u1_uid][u2_uid]['weight'] += 1
        graph[u1_uid][u2_uid]['ds'] = time_difference
        graph[u1_uid][u2_uid]['dt'] = distance
    return graph


def weight_by_distance(graph, user1, user2):
    u1_uid, u1_lat, u1_lon, u1_t, u1_ds, u1_dt = user1
    u2_uid, u2_lat, u2_lon, u2_t, u2_ds, u2_dt = user2
    u1_lat_lon = (u1_lat, u1_lon)
    u2_lat_lon = (u2_lat, u2_lon)
    distance = dist_apart(u1_lat_lon, u2_lat_lon)
    time_difference = abs(u1_t - u2_t)
    delta = (u1_ds, u1_dt)
    ds, dt = delta
    weight = dt - distance
    if not graph.has_edge(u1_uid, u2_uid):
        graph.add_edge(u1_uid, u2_uid, weight=weight, distance=distance, ds=time_difference, dt=distance)
    else:
        if graph[u1_uid][u2_uid]['weight'] > weight:
            graph[u1_uid][u2_uid]['weight'] = weight
            graph[u1_uid][u2_uid]['ds'] = time_difference
            graph[u1_uid][u2_uid]['dt'] = distance
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
    return km * 1000

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

