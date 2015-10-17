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
    stations=[]
    builtStations = 0
    moneySpent = 0

    distanceWeight = 0.1
    stationCount = 4

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

    def nextBestNode(self, state):
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
        print("bestNode=",(bestScore,bestNode))

        #Factor in distance from each station
        for i in range(len(nodeScores)):
            if (i not in self.stations):
                distanceScore = 1.0 / self.closestStation(graph, i)[1]
                print("distanceScore=",distanceScore)
                nodeScores[i] -= distanceScore * self.distanceWeight

        #Get the node with the best score
        bestNode = 0
        bestScore = nodeScores[0]
        for i in range(len(nodeScores)):
            if (nodeScores[i] > bestScore and (i not in self.stations)):
                bestNode = i
                bestScore = nodeScores[i]
        print("bestNode=",(bestScore,bestNode))
        return bestNode

    def closestStation(self, graph, node):
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

        print("stations=",self.stations)
        print("money=", state.get_money())
        buildCost = INIT_BUILD_COST * BUILD_FACTOR ** len(self.stations)
        if (len(self.stations) == 0 or (len(self.stations) < self.stationCount and state.get_money() > buildCost)):
            self.stations.append(self.nextBestNode(state))
            self.moneySpent += buildCost
            #self.distanceWeight /= 1.5
        graph = state.get_graph()
        station = graph.nodes()[self.stations[len(self.stations)-1]]

        commands = []
        print("built", self.builtStations)
        if self.builtStations < len(self.stations):
            commands.append(self.build_command(station))
            self.builtStations += 1

        pending_orders = state.get_pending_orders()
        if len(pending_orders) != 0:
            order = random.choice(pending_orders)
            path = nx.shortest_path(graph, self.closestStation(graph,order.get_node())[0], order.get_node())
            if self.path_is_valid(state, path):
                commands.append(self.send_command(order, path)) #Go to this order with this path

        if (state.get_time() == 999):
            print("totalMoney=",state.get_money() + self.moneySpent)

        return commands
