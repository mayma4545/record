"""
A* Pathfinding Algorithm for Campus Navigation

This module implements A* pathfinding that considers:
- Edge distances (actual cost)
- Compass angles for directional awareness
- Staircase detection (is_staircase flag)
- Active/inactive edges (is_active flag)
"""

import heapq
from typing import List, Dict, Tuple, Optional
from .models import Nodes, Edges


class PathFinder:
    """A* pathfinding with compass direction awareness."""
    
    def __init__(self):
        self.nodes_cache = {}
        self.edges_cache = {}
        self._build_graph()
    
    def _build_graph(self):
        """Build adjacency list from database edges."""
        self.graph = {}  # {node_id: [(neighbor_id, distance, compass_angle, is_staircase), ...]}
        
        # Cache all nodes
        for node in Nodes.objects.all():
            self.nodes_cache[node.node_id] = node
            self.graph[node.node_id] = []
        
        # Build adjacency list from active edges
        for edge in Edges.objects.filter(is_active=True).select_related('from_node', 'to_node'):
            from_id = edge.from_node.node_id
            to_id = edge.to_node.node_id
            
            self.graph[from_id].append({
                'to': to_id,
                'distance': edge.distance,
                'compass_angle': edge.compass_angle,
                'is_staircase': edge.is_staircase,
                'edge_id': edge.edge_id
            })
            
            # Add reverse edge (bidirectional)
            reverse_angle = (edge.compass_angle + 180) % 360
            self.graph[to_id].append({
                'to': from_id,
                'distance': edge.distance,
                'compass_angle': reverse_angle,
                'is_staircase': edge.is_staircase,
                'edge_id': edge.edge_id
            })
    
    def heuristic(self, node_a_id: int, node_b_id: int) -> float:
        """
        Heuristic for A*: Estimate distance using floor difference.
        Assumes ~4 meters per floor level.
        """
        node_a = self.nodes_cache.get(node_a_id)
        node_b = self.nodes_cache.get(node_b_id)
        
        if not node_a or not node_b:
            return 0.0
        
        # Floor difference as heuristic (admissible since actual path >= floor difference)
        floor_diff = abs(node_a.floor_level - node_b.floor_level)
        return floor_diff * 4.0  # Assume 4 meters per floor
    
    def find_path(self, start_code: str, goal_code: str, 
                  avoid_stairs: bool = False) -> Dict:
        """
        Find shortest path using A* algorithm.
        
        Args:
            start_code: Starting node code
            goal_code: Destination node code
            avoid_stairs: If True, avoid edges with is_staircase=True
        
        Returns:
            Dictionary with path details or error message
        """
        # Find start and goal nodes
        try:
            start_node = Nodes.objects.get(node_code=start_code)
            goal_node = Nodes.objects.get(node_code=goal_code)
        except Nodes.DoesNotExist as e:
            return {'error': f'Node not found: {str(e)}'}
        
        start_id = start_node.node_id
        goal_id = goal_node.node_id
        
        # A* data structures
        open_set = []  # Priority queue: (f_score, node_id)
        heapq.heappush(open_set, (0, start_id))
        
        came_from = {}  # {node_id: (previous_node_id, edge_info)}
        g_score = {start_id: 0}  # Cost from start to node
        f_score = {start_id: self.heuristic(start_id, goal_id)}  # Estimated total cost
        
        visited = set()
        
        while open_set:
            current_f, current_id = heapq.heappop(open_set)
            
            if current_id in visited:
                continue
            
            visited.add(current_id)
            
            # Goal reached
            if current_id == goal_id:
                return self._reconstruct_path(came_from, start_id, goal_id, g_score[goal_id])
            
            # Explore neighbors
            for edge_info in self.graph.get(current_id, []):
                neighbor_id = edge_info['to']
                
                # Skip stairs if requested
                if avoid_stairs and edge_info['is_staircase']:
                    continue
                
                # Calculate tentative g_score
                tentative_g = g_score[current_id] + edge_info['distance']
                
                if neighbor_id not in g_score or tentative_g < g_score[neighbor_id]:
                    # Better path found
                    came_from[neighbor_id] = (current_id, edge_info)
                    g_score[neighbor_id] = tentative_g
                    f = tentative_g + self.heuristic(neighbor_id, goal_id)
                    f_score[neighbor_id] = f
                    heapq.heappush(open_set, (f, neighbor_id))
        
        return {'error': 'No path found between the specified nodes'}
    
    def _reconstruct_path(self, came_from: Dict, start_id: int, goal_id: int, 
                          total_distance: float) -> Dict:
        """Reconstruct path from came_from dictionary."""
        path = []
        current_id = goal_id
        
        while current_id != start_id:
            if current_id not in came_from:
                break
            
            prev_id, edge_info = came_from[current_id]
            node = self.nodes_cache[current_id]
            
            path.append({
                'node_id': node.node_id,
                'node_code': node.node_code,
                'name': node.name,
                'building': node.building,
                'floor_level': node.floor_level,
                'type': node.type_of_node,
                'image360': node.image360.url if node.image360 else None,
                'map_x': float(node.map_x) if node.map_x is not None else None,
                'map_y': float(node.map_y) if node.map_y is not None else None,
                'distance_from_prev': edge_info['distance'],
                'compass_angle': edge_info['compass_angle'],
                'is_staircase': edge_info['is_staircase']
            })
            
            current_id = prev_id
        
        # Add start node
        start_node = self.nodes_cache[start_id]
        path.append({
            'node_id': start_node.node_id,
            'node_code': start_node.node_code,
            'name': start_node.name,
            'building': start_node.building,
            'floor_level': start_node.floor_level,
            'type': start_node.type_of_node,
            'image360': start_node.image360.url if start_node.image360 else None,
            'map_x': float(start_node.map_x) if start_node.map_x is not None else None,
            'map_y': float(start_node.map_y) if start_node.map_y is not None else None,
            'distance_from_prev': 0,
            'compass_angle': None,
            'is_staircase': False
        })
        
        path.reverse()
        
        return {
            'success': True,
            'path': path,
            'total_distance': round(total_distance, 2),
            'num_nodes': len(path),
            'start': path[0],
            'goal': path[-1]
        }
    
    def get_directions(self, start_code: str, goal_code: str, 
                       avoid_stairs: bool = False) -> Dict:
        """
        Get turn-by-turn directions with compass headings.
        
        Returns path with human-readable directions.
        """
        result = self.find_path(start_code, goal_code, avoid_stairs)
        
        if 'error' in result:
            return result
        
        # Add human-readable directions
        path = result['path']
        directions = []
        
        for i, step in enumerate(path):
            if i == 0:
                directions.append(f"Start at {step['name']} ({step['building']}, Floor {step['floor_level']})")
            else:
                compass = step['compass_angle']
                compass_dir = self._compass_to_direction(compass) if compass else "forward"
                stair_info = " via stairs" if step['is_staircase'] else ""
                
                directions.append(
                    f"Go {compass_dir} ({compass:.0f}°) for {step['distance_from_prev']:.1f}m{stair_info} "
                    f"to {step['name']}"
                )
        
        result['directions'] = directions
        return result
    
    def _compass_to_direction(self, angle: float) -> str:
        """Convert compass angle to human-readable direction."""
        directions = [
            "North", "North-Northeast", "Northeast", "East-Northeast",
            "East", "East-Southeast", "Southeast", "South-Southeast",
            "South", "South-Southwest", "Southwest", "West-Southwest",
            "West", "West-Northwest", "Northwest", "North-Northwest"
        ]
        index = int((angle + 11.25) / 22.5) % 16
        return directions[index]


# Global instance (singleton pattern)
_pathfinder_instance = None

def get_pathfinder() -> PathFinder:
    """Get or create global PathFinder instance."""
    global _pathfinder_instance
    if _pathfinder_instance is None:
        _pathfinder_instance = PathFinder()
    return _pathfinder_instance

def reset_pathfinder():
    """Reset pathfinder (useful after database changes)."""
    global _pathfinder_instance
    _pathfinder_instance = None
