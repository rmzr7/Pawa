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

    def get_actual_gain(self, state, order, path):
        total = order.get_money() - \
            (state.get_time() - order.get_time_created()) * \
            DECAY_FACTOR

        amortized = total - (len(path) -1) * DECAY_FACTOR
        return max(amortized, 0)

    def find_best_max_decay(self, graph):
        pass

    def determine_fufill_order(self, path):
        pass

    def key_with_max_val(self, d):
        """ a) create a list of the dict's keys and values;
            b) return the key with the max value"""
        v=list(d.values())
        k=list(d.keys())
        return k[v.index(max(v))]

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
        station = graph.nodes()[35]

        commands = []
        if not self.has_built_station:
            commands.append(self.build_command(station))
            self.has_built_station = True

        pending_orders = state.get_pending_orders()
        selections = {} # {int:order}
        if len(pending_orders) != 0:
            for order in pending_orders:
                path = nx.shortest_path(graph, station, order.get_node())
                selections[self.get_actual_gain(state, order, path)] = order
            opt_order = selections[self.key_with_max_val(selections)]

            #order = random.choice(pending_orders)
            path = nx.shortest_path(graph, station, opt_order.get_node())
            if self.path_is_valid(state, path) and self.get_actual_gain(state, order, path) <= 100000000:
                commands.append(self.send_command(opt_order, path))

        return commands
