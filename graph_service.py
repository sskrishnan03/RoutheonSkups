import heapq

class GraphService:
    def __init__(self):
        # Dictionary to store graph: {node: {neighbor: distance}}
        self.graph = {
            "Delhi": {"Manali": 530, "Jaipur": 280, "Rishikesh": 240, "Agra": 230, "Chandigarh": 245},
            "Manali": {"Delhi": 530, "Leh": 473, "Chandigarh": 305, "Kasol": 75},
            "Jaipur": {"Delhi": 280, "Mumbai": 1150, "Udaipur": 390, "Agra": 240, "Jodhpur": 330},
            "Rishikesh": {"Delhi": 240, "Dehradun": 45, "Haridwar": 20},
            "Mumbai": {"Goa": 590, "Jaipur": 1150, "Pune": 150, "Nashik": 165},
            "Goa": {"Mumbai": 590, "Bangalore": 560, "Mangalore": 360, "Gokarna": 145},
            "Bangalore": {"Goa": 560, "Ooty": 270, "Mysore": 145, "Chennai": 345, "Coorg": 240},
            "Ooty": {"Bangalore": 270, "Mysore": 125, "Coimbatore": 85, "Kodaikanal": 250},
            "Chennai": {"Bangalore": 345, "Pondicherry": 150, "Tirupati": 135},
            "Kolkata": {"Darjeeling": 615, "Puri": 500},
            "Darjeeling": {"Kolkata": 615, "Gangtok": 95},
            "Agra": {"Delhi": 230, "Jaipur": 240, "Lucknow": 335},
            "Udaipur": {"Jaipur": 390, "Ahmedabad": 260},
            "Chandigarh": {"Delhi": 245, "Manali": 305, "Amritsar": 225},
            "Leh": {"Manali": 473, "Srinagar": 420},
            "Kasol": {"Manali": 75},
            "Dehradun": {"Rishikesh": 45, "Mussoorie": 35},
            "Haridwar": {"Rishikesh": 20},
            "Pune": {"Mumbai": 150, "Mahabaleshwar": 120},
            "Nashik": {"Mumbai": 165, "Shirdi": 85},
            "Mangalore": {"Goa": 360, "Coorg": 140},
            "Gokarna": {"Goa": 145},
            "Mysore": {"Bangalore": 145, "Ooty": 125, "Coorg": 120},
            "Coorg": {"Bangalore": 240, "Mysore": 120, "Mangalore": 140},
            "Coimbatore": {"Ooty": 85},
            "Kodaikanal": {"Ooty": 250, "Madurai": 115},
            "Pondicherry": {"Chennai": 150},
            "Tirupati": {"Chennai": 135},
            "Puri": {"Kolkata": 500},
            "Gangtok": {"Darjeeling": 95},
            "Lucknow": {"Agra": 335, "Varanasi": 320},
            "Jodhpur": {"Jaipur": 330, "Jaisalmer": 280},
            "Amritsar": {"Chandigarh": 225},
            "Srinagar": {"Leh": 420, "Gulmarg": 50},
            "Mussoorie": {"Dehradun": 35},
            "Mahabaleshwar": {"Pune": 120},
            "Shirdi": {"Nashik": 85},
            "Madurai": {"Kodaikanal": 115, "Rameswaram": 170},
            "Varanasi": {"Lucknow": 320},
            "Jaisalmer": {"Jodhpur": 280},
            "Gulmarg": {"Srinagar": 50},
            "Rameswaram": {"Madurai": 170},
             "Ahmedabad": {"Udaipur": 260}
        }

    def get_locations(self):
        """Returns a sorted list of all locations in the graph."""
        return sorted(list(self.graph.keys()))

    def get_shortest_path(self, start_node, end_node):
        """
        Calculates the shortest path using Dijkstra's algorithm.
        Returns: (path_list, total_distance)
        """
        if start_node not in self.graph or end_node not in self.graph:
            return None, -1

        # Priority queue to store (distance, current_node, path)
        queue = [(0, start_node, [start_node])]
        visited = set()

        while queue:
            current_distance, current_node, path = heapq.heappop(queue)

            if current_node in visited:
                continue
            visited.add(current_node)

            if current_node == end_node:
                return path, current_distance

            if current_node in self.graph:
                for neighbor, weight in self.graph[current_node].items():
                    if neighbor not in visited:
                        new_distance = current_distance + weight
                        new_path = path + [neighbor]
                        heapq.heappush(queue, (new_distance, neighbor, new_path))
        
        return None, -1 # No path found

# Singleton instance
graph_service = GraphService()
