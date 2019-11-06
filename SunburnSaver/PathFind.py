from graph import *
import math
import heapq

# Hyper-parameter, adjust as needed. SUN_WEIGHT=0 should find shortest path, large weight should find shadiest path
# TODO: Adjust
SUN_WEIGHT = 2

class ComparableNode:
    """Used for priority queue"""
    def __init__(self, id, value):
        self.id = id
        self.value = value

    def __lt__(self, other):
        return self.value < other.value

    def getID(self):
        return self.id

    def getValue(self):
        return self.value


def getPath(a, b, graph, sunWeight):
    """ What the user calls to get a good shady path from a->b
        a, b are (lat, long) tuples
        graph is a Graph object """
    # optional: replace graph with a smaller "region of interest"

    # populate the sun_score for each edge
    # getSunScores(graph)  # now graph should have sun_score={edge:score}

    # run our custom A* seach

    # a, b are latitude and longitude, we must convert these to nearest points
    start = graph.findClosestID(a[0], a[1])
    end = graph.findClosestID(b[0], b[1])

    assert(start in list(graph.node_df["id"]))
    assert(end in list(graph.node_df["id"]))
    path = getShadyPath(start, end, graph, euclideanDistance, sunWeight)
    return path


def euclideanDistance(a, b, graph):
    return math.sqrt((graph.getLon(b) - graph.getLon(a))**2 + (graph.getLat(b) - graph.getLat(a))**2)


def reconstructPath(cameFrom, cur):
    """Generates path from start to cur, called by getShadyPath"""
    total_path = [cur]
    while cur in cameFrom.keys():
        cur = cameFrom[cur]
        total_path = [cur] + total_path
    return total_path


def getShadyPath(start, end, graph, h, sunWeight):
    """Returns the best shady path from a->b
        start, end are ids"""
    discovered = [ComparableNode(start, h(start, end, graph))]  # NOTE: NODE OBJECTS MUST HAVE __lt__ method defined

    # for node n, cameFrom[n] is node immediately preceding it on path
    cameFrom = {}

    # for node n, gScore is cost of cheapest path from start to n currently known
    gScore = {k: float("inf") for k in graph.getIds()}
    gScore[start] = 0


    heapq.heapify(discovered)

    while len(discovered) > 0:
        curNode = heapq.heappop(discovered)
        curID = curNode.getID()
        if curID == end:
            return reconstructPath(cameFrom, curID)
        # discovered.remove(curNode)

        for neighbor in graph.getNeighbors(curID):
            edgeDist = graph.getDistance(curID, neighbor)
            score = gScore[curID] + edgeDist
            if score < gScore[neighbor]:
                cameFrom[neighbor] = curID
                gScore[neighbor] = score
                print("Calculating Sun Score!")
                new_score = gScore[neighbor] + h(neighbor, end, graph) + (graph.getSunScore(curID, neighbor) * sunWeight)
                print("calculated!")
                # new_score = gScore[neighbor] + h(neighbor)
                if neighbor not in discovered:
                    heapq.heappush(discovered, ComparableNode(neighbor, new_score))
    return "yikes error"


















# def dijkstra(graph, source, target):
#     """Returns shortest path from a to b """
#     distances = {vertex: float("inf") for vertex in graph.vertices}
#     previous_vertices = {
#         vertex: None for vertex in graph.vertices
#     }
#     distances[source] = 0
#     vertices = graph.vertices.copy()
#
#     while vertices:
#         # 3. Select the unvisited node with the smallest distance,
#         # it's current node now.
#         current_vertex = min(
#             vertices, key=lambda vertex: distances[vertex])
#
#         # 6. Stop, if the smallest distance
#         # among the unvisited nodes is infinity.
#         if distances[current_vertex] == float("inf"):
#             break
#
#         # 4. Find unvisited neighbors for the current node
#         # and calculate their distances through the current node.
#         for neighbour, cost in graph.neighbors[current_vertex]:
#             alternative_route = distances[current_vertex] + cost
#
#             # Compare the newly calculated distance to the assigned
#             # and save the smaller one.
#             if alternative_route < distances[neighbour]:
#                 distances[neighbour] = alternative_route
#                 previous_vertices[neighbour] = current_vertex
#
#         # 5. Mark the current node as visited
#         # and remove it from the unvisited set.
#         vertices.remove(current_vertex)
#
#     path, current_vertex = deque(), target
#     while previous_vertices[current_vertex] is not None:
#         path.appendleft(current_vertex)
#         current_vertex = previous_vertices[current_vertex]
#     if path:
#         path.appendleft(current_vertex)
#     return path
