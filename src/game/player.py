import networkx as nx
import random
from base_player import BasePlayer
from settings import *
import operator

class Player(BasePlayer):
    """
    You will implement this class for the competition. DO NOT change the class
    name or the base class.
    """

    has_built_station = False
    stations = []

    def __init__(self, state):
        """
        Initializes your Player. You can set up persistent state, do analysis
        on the input graph, engage in whatever pre-computation you need. This
        function must take less than Settings.INIT_TIMEOUT seconds.
        --- Parameters ---
        state : State
            The initial state of the game. See state.py for more information.
        """

        graph = state.get_graph()
        #e_dict = nx.eccentricity(graph)
        station = nx.center(graph)[0] if nx.center(graph) else graph.nodes()[len(graph.nodes()) / 2] #max(e_dict, key=lambda i: x[i])
        self.stations.append(station)

    # Checks if we can use a given path
    def path_is_valid(self, state, path):
        graph = state.get_graph()
        for i in range(0, len(path) - 1):
            if graph.edge[path[i]][path[i + 1]]['in_use']:
                return False
        return True

    def can_build_station(self, state):
        current = len([i for i, x in state.graph.node.iteritems() if x['is_station']])
        build_cost = INIT_BUILD_COST * (BUILD_FACTOR ** current)
        if state.get_money() >= build_cost:
            return True
        else:
            return False

    def path_to_edges(self, path):
        return [(path[i], path[i + 1]) for i in range(0, len(path) - 1)]

    def step(self, state):
        """
        Determine actions based on the current state of the city. Called every
        time step. This function must take less than Settings.STEP_TIMEOUT
        seconds.
        --- Parameters ---
        state : State
            The state of the game. See state.py for more information.
        --- Returns ---
        commands : dict list
            Each command should be generated via self.send_command or
            self.build_command. The commands are evaluated in order.
        """

        graph = state.get_graph()
        
        commands = []
        if not self.has_built_station:
            commands.append(self.build_command(self.stations[0]))
            state.money -= INIT_BUILD_COST
            self.has_built_station = True

        pending_orders = state.get_pending_orders()

        if len(self.stations) < HUBS and pending_orders and self.can_build_station(state):
            subgraph = graph.subgraph(list(map(lambda x: x.get_node(), pending_orders)))
            if nx.is_connected(subgraph):
                centers = nx.center(subgraph)
                if centers:
                    for center in centers:
                        too_close = False

                        for station in self.stations:
                            if len(nx.shortest_path(graph, center, station)) - 1 < ORDER_VAR:
                                too_close = True

                        if not too_close:
                            self.stations.append(center)
                            commands.append(self.build_command(center))

        while len(pending_orders) != 0:
            future_money = 0
            dest_order = pending_orders[0]
            dest_station = self.stations[0]

            for order in pending_orders:
                money = order.get_money()
                for station in self.stations:
                    path_len = len(nx.shortest_path(graph, station, order.get_node()))
                    if money - DECAY_FACTOR * path_len > future_money:
                        future_money = money - DECAY_FACTOR * path_len
                        dest_order = order
                        dest_station = station

            path_list = nx.all_shortest_paths(graph, dest_station, dest_order.get_node())
            for path in path_list:
                if self.path_is_valid(state, path):
                    commands.append(self.send_command(dest_order, path))
                    for (u, v) in self.path_to_edges(path):
                        graph.edge[u][v]['in_use'] = True
                        graph.edge[v][u]['in_use'] = True
                    break

            pending_orders.remove(dest_order)

        return commands
