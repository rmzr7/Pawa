import networkx as nx
import random
from base_player import BasePlayer
from settings import *
# from copy import deepcopy

class Player(BasePlayer):
    """
    You will implement this class for the competition. DO NOT change the class
    name or the base class.
    """


    # You can set up static state here
    has_built_station = False
    stations=[]
    builtStations = 0
    moneySpent = 0

    distanceWeight = 0.2
    stationCount = int(GRAPH_SIZE / 25)
    if stationCount < 2:
        stationCount = 2
    elif stationCount > 4:
        stationCount = 5

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

    def nextBestNode(self, state): #Finds the next best spot for a station
        graph = state.get_graph()
        nodeScores = []
        centrality = nx.degree_centrality(graph)
        for i in centrality:
            nodeScores.append(centrality[i])

        bestNode = 0
        bestScore = nodeScores[0]
        for i in range(len(nodeScores)):
            if (nodeScores[i] > bestScore and (i not in self.stations)):
                bestNode = i
                bestScore = nodeScores[i]
        #print("bestNode=",(bestScore,bestNode))

        #Factor in distance from each station
        for i in range(len(nodeScores)):
            if (i not in self.stations):
                distanceScore = 1.0 / self.closestStation(graph, i)[1]
                #print("distanceScore=",distanceScore)
                nodeScores[i] -= distanceScore * self.distanceWeight

        #Get the node with the best score
        bestNode = 0
        bestScore = nodeScores[0]
        for i in range(len(nodeScores)):
            if (nodeScores[i] > bestScore and (i not in self.stations)):
                bestNode = i
                bestScore = nodeScores[i]
        #print("bestNode=",(bestScore,bestNode))
        return bestNode

    def closestStation(self, graph, node): #Returns the closest station and the distance from it
        if (len(self.stations) == 0): return 0,999999
        bestDistance = 99999999
        bestStation = self.stations[0]
        for station in self.stations:
            dist = nx.astar_path_length(graph,station,node)
            if (dist == 0): return node, 1
            if (dist < bestDistance):
                bestDistance = dist
                bestStation = station
        return bestStation, bestDistance

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

    def get_graph_without_orders(self, state, graph):
        new_graph = graph.copy()
        for order_with_path in state.get_active_orders():
            path = order_with_path[1]
            for index in range(len(path) - 1):
                new_graph.remove_edge(path[index], path[index + 1])

        return new_graph

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

        buildCost = INIT_BUILD_COST * BUILD_FACTOR ** len(self.stations)
        if (len(self.stations) == 0 or (len(self.stations) < self.stationCount and state.get_money() > buildCost)):
            self.stations.append(self.nextBestNode(state))
            self.moneySpent += buildCost
            #self.distanceWeight /= 1.5
        graph = state.get_graph()
        station = graph.nodes()[self.stations[len(self.stations)-1]]

        commands = []
        if self.builtStations < len(self.stations):
            commands.append(self.build_command(station))
            self.builtStations += 1

        pending_orders = state.get_pending_orders()
        selections = {} # {int:order}
        if len(pending_orders) != 0:
            try:
                for order in pending_orders:
                    new_graph = self.get_graph_without_orders(state, graph)
                    path = nx.shortest_path(new_graph, self.closestStation(new_graph,order.get_node())[0],
                     order.get_node())

                    selections[self.get_actual_gain(state, order, path)] = order
                opt_order = selections[self.key_with_max_val(selections)]

                #order = random.choice(pending_orders)
                path = nx.shortest_path(self.get_graph_without_orders(state, graph),
                 self.closestStation(graph,order.get_node())[0], opt_order.get_node())
                if self.path_is_valid(state, path):
                    commands.append(self.send_command(opt_order, path))
            except:
                pass

        return commands
