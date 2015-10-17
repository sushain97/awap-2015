import networkx as nx
import random
from base_player import BasePlayer
from settings import *

class Player(BasePlayer):
    """
    You will implement this class for the competition. DO NOT change the class
    name or the base class.
    """

    # You can set up static state here
    has_built_station = False

    def __init__(self, state):
        """
        Initializes your Player. You can set up persistent state, do analysis
        on the input graph, engage in whatever pre-computation you need. This
        function must take less than Settings.INIT_TIMEOUT seconds.
        --- Parameters ---
        state : State
            The initial state of the game. See state.py for more information.
        """

        return

    # Checks if we can use a given path
    def path_is_valid(self, state, path):
        graph = state.get_graph()
        for i in range(0, len(path) - 1):
            if graph.edge[path[i]][path[i + 1]]['in_use']:
                return False
        return True

    def can_build_station(self, state):
        current = len([i for i, x in self.state.graph.node.iteritems() if x['is_station']])
        build_cost = INIT_BUILD_COST * (BUILD_FACTOR ** current)
        if state_get.money() >= build_cost:
            return True
        else:
            return False

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

        # We have implemented a naive bot for you that builds a single station
        # and tries to find the shortest path from it to first pending order.
        # We recommend making it a bit smarter ;-)

        graph = state.get_graph()
        station = graph.nodes()[0]

        commands = []
        if not self.has_built_station:
            commands.append(self.build_command(station))
            self.has_built_station = True

        pending_orders = state.get_pending_orders()
        if len(pending_orders) != 0:
            future_money = 0
            dest_order = pending_orders[0]

            for order in pending_orders:
                money = order.get_money()
                path_len = len(nx.shortest_path(graph, station, order.get_node()))
                if (money - DECAY_FACTOR * path_len) > future_money:
                    future_money = money - DECAY_FACTOR * path_len
                    dest_order = order
            #order = max(pending_orders, key=lambda x: x.get_money())

            path_list = nx.all_shortest_paths(graph, station, dest_order.get_node())
            for path in path_list:
                if self.path_is_valid(state, path):
                    commands.append(self.send_command(dest_order, path))
                    return commands
        return commands
