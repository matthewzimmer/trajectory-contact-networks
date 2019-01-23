import networkx as nx
import matplotlib.pyplot as plt


def grapher(combos):
    if not combos:
        print("NO NODES")
        return
    graph = nx.Graph()
    artificial_combos = [('003', '004', 40.007548, 116.32172650000001, 1224785351.0000029),
                         ('002', '005', 45.007548, 16.32172650000001, 14785351.0000029),
                         ('002', '001', 45.007548, 16.32172650000001, 14785351.0000029)]
    # for c in combos:
    for c in artificial_combos:
        graph.add_edge(c[0], c[1], weight=1)
    # print("Number of Nodes: " + str(G.number_of_nodes()))
    # print("Number of edges: " + str(G.number_of_edges()))
    # print("Node degrees: " + str(G.degree()))
    largest_comp = find_largest_component(graph)
    avg_degree = find_average_degree(graph)
    nx.draw_spectral(graph, with_labels=True)  # spectral circular random
    plt.savefig('con_components.png', bbox_inches='tight')
    plt.close()
    return largest_comp, avg_degree


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


def save_results(largest_comps, ave_degrees):
    if largest_comps or ave_degrees != 'NULL':
        deltas = ["100m 300s", "500m 600s", "1000m 1200s"]
        plt.plot(deltas, largest_comps, label="Largest Component")
        plt.title("Size of Largest Connected Component")
        plt.ylabel("Largest Component Size")
        plt.xlabel("Delta settings")
        plt.savefig('Largest_Component_Results.png', bbox_inches='tight')
        # plt.show()

        plt.plot(deltas, ave_degrees, label="Average Degree")
        plt.title("Average Degree of Nodes")
        plt.ylabel("Mean Degree")
        plt.xlabel("Delta settings")
        plt.savefig('Ave_Degree_Results.png', bbox_inches='tight')
