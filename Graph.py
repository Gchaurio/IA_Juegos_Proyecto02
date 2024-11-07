import pygame
import heapq

class Connection:
    def __init__(self, fromNode, toNode, cost):
        self.fromNode = fromNode
        self.toNode = toNode
        self.cost = cost

    def getCost(self):
        return self.cost

    def getFromNode(self):
        return self.fromNode

    def getToNode(self):
        return self.toNode


class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.connections = []

    def add_connection(self, toNode, cost):
        connection = Connection(self, toNode, cost)
        self.connections.append(connection)

    def distance_to(self, other_node):
        return ((self.x - other_node.x) ** 2 + (self.y - other_node.y) ** 2) ** 0.5


class Graph:
    def __init__(self, tile_size, screen_size, obstacles_group):
        self.nodes = []
        self.tile_size = tile_size
        self.grid_width = screen_size[0] // tile_size
        self.grid_height = screen_size[1] // tile_size
        self.obstacles_group = obstacles_group
        self.create_tiles()

    def getConnections(self, fromNode):
        return fromNode.connections

    def get_closest_node(self, pos):
        closest_node = None
        min_distance = float('inf')
        for node in self.nodes:
            distance = ((node.x - pos[0]) ** 2 + (node.y - pos[1]) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                closest_node = node
        return closest_node
    
    def get_farthest_node(self, pos):

        farthest_node = None
        max_distance = float('-inf')

        for node in self.nodes:
            distance = ((node.x - pos[0]) ** 2 + (node.y - pos[1]) ** 2) ** 0.5
            if distance > max_distance:
                max_distance = distance
                farthest_node = node

        return farthest_node

    def create_tiles(self):
        node_grid = [[None for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                x = col * self.tile_size + self.tile_size // 2
                y = row * self.tile_size + self.tile_size // 2
                node_rect = pygame.Rect(x - self.tile_size // 2, y - self.tile_size // 2, self.tile_size, self.tile_size)


                if not any(obstacle.rect.colliderect(node_rect) for obstacle in self.obstacles_group):
                    node = Node(x, y)
                    node_grid[row][col] = node 
                    self.nodes.append(node)

        for row in range(self.grid_height):
            for col in range(self.grid_width):
                current_node = node_grid[row][col]
                if current_node is not None:
                    neighbors_offsets = [
                        (-1, 0), (1, 0), (0, -1), (0, 1), 
                        (-1, -1), (-1, 1), (1, -1), (1, 1) 
                    ]

                    for d_row, d_col in neighbors_offsets:
                        n_row, n_col = row + d_row, col + d_col
                        if 0 <= n_row < self.grid_height and 0 <= n_col < self.grid_width:
                            neighbor_node = node_grid[n_row][n_col]
                            if neighbor_node is not None:
                                distance = current_node.distance_to(neighbor_node)
                                current_node.add_connection(neighbor_node, distance)


class NodeRecord:
    def __init__(self, node, connection=None, costSoFar=0, estimatedTotalCost=0):
        self.node = node
        self.connection = connection
        self.costSoFar = costSoFar
        self.estimatedTotalCost = estimatedTotalCost

    def __lt__(self, other):
        return self.estimatedTotalCost < other.estimatedTotalCost


class Heuristic:
    def __init__(self, goalNode):
        self.goalNode = goalNode

    def estimate(self, fromNode):
        return fromNode.distance_to(self.goalNode)


def pathfindAStar(graph, start, end, heuristic):
    open_list = []
    closed_dict = {}

    startRecord = NodeRecord(start)
    startRecord.estimatedTotalCost = heuristic.estimate(start)
    heapq.heappush(open_list, startRecord)

    while open_list:
        currentRecord = heapq.heappop(open_list)

        if currentRecord.node == end:
            path = []
            while currentRecord.node != start:
                path.append(currentRecord.node)
                if currentRecord.connection is not None:
                    currentRecord = closed_dict[currentRecord.connection.getFromNode()]
                else:
                    break
            path.reverse()
            return path

        connections = graph.getConnections(currentRecord.node)
        for connection in connections:
            endNode = connection.getToNode()
            endNodeCost = currentRecord.costSoFar + connection.getCost()

            if endNode in closed_dict and closed_dict[endNode].costSoFar <= endNodeCost:
                continue

            endNodeRecord = next((record for record in open_list if record.node == endNode), None)
            if endNodeRecord and endNodeRecord.costSoFar <= endNodeCost:
                continue

            if not endNodeRecord:
                endNodeRecord = NodeRecord(endNode)

            endNodeRecord.costSoFar = endNodeCost
            endNodeRecord.connection = connection
            endNodeRecord.estimatedTotalCost = endNodeCost + heuristic.estimate(endNode)

            if endNodeRecord not in open_list:
                heapq.heappush(open_list, endNodeRecord)

        closed_dict[currentRecord.node] = currentRecord

    return None
