import heapq
import math


class GraphService:
    """Global route graph service using Haversine distance between any two coordinates."""

    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    @staticmethod
    def dijkstra(graph, start):
        distances = {node: float('inf') for node in graph}
        distances[start] = 0
        priority_queue = [(0, start)]
        path = {}

        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)

            if current_distance > distances[current_node]:
                continue

            for neighbor, weight in graph[current_node].items():
                distance = current_distance + weight
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    path[neighbor] = current_node
                    heapq.heappush(priority_queue, (distance, neighbor))

        return distances, path

    @staticmethod
    def get_shortest_path(graph, start, end):
        distances, predecessors = GraphService.dijkstra(graph, start)
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = predecessors.get(current)
        return path[::-1] if distances[end] != float('inf') else None

    @staticmethod
    def optimize_route(locations):
        """Simple Nearest Neighbor TSP for route optimization.
        locations: list of dicts with 'lat', 'lng'
        """
        if not locations or len(locations) <= 1:
            return locations

        unvisited = list(locations)
        optimized = [unvisited.pop(0)]

        while unvisited:
            current = optimized[-1]
            next_idx = 0
            min_dist = float('inf')

            for i, loc in enumerate(unvisited):
                d = GraphService.haversine(
                    float(current.get('lat', 0)), float(current.get('lng', 0)),
                    float(loc.get('lat', 0)), float(loc.get('lng', 0))
                )
                if d < min_dist:
                    min_dist = d
                    next_idx = i

            optimized.append(unvisited.pop(next_idx))

        return optimized

    @staticmethod
    def get_locations():
        return []

    @staticmethod
    def get_shortest_path_static(start_node, end_node):
        return None, -1


graph_service = GraphService()
