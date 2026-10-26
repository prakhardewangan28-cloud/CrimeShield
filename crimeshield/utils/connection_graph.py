"""
Connection graph traversal utility for CRIMESHIELD.
Demonstrates: Recursive traversal with cycle detection and maximum depth.
"""

from typing import Dict, List, Set, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class ConnectionGraph:
    """
    In-memory graph for connection traversal.
    Demonstrates: Graph data structure and recursive traversal with safeguards.
    
    IMPORTANT: This operates on a small in-memory subset, NOT the entire database.
    """
    
    def __init__(self) -> None:
        """Initialize empty connection graph."""
        # Adjacency list: case_id -> set of connected case_ids
        self.adjacency: Dict[int, Set[int]] = {}
        # Connection details: (case_id_1, case_id_2) -> connection info
        self.connections: Dict[Tuple[int, int], List[Dict]] = {}
    
    def add_connection(
        self,
        case_id_1: int,
        case_id_2: int,
        connection_info: Dict
    ) -> None:
        """
        Add a connection to the graph.
        
        Args:
            case_id_1: First case ID
            case_id_2: Second case ID
            connection_info: Connection details
        """
        # Ensure both cases are in adjacency list
        if case_id_1 not in self.adjacency:
            self.adjacency[case_id_1] = set()
        if case_id_2 not in self.adjacency:
            self.adjacency[case_id_2] = set()
        
        # Add bidirectional connection
        self.adjacency[case_id_1].add(case_id_2)
        self.adjacency[case_id_2].add(case_id_1)
        
        # Store connection details (normalized pair)
        pair = tuple(sorted([case_id_1, case_id_2]))
        if pair not in self.connections:
            self.connections[pair] = []
        self.connections[pair].append(connection_info)
    
    def find_path(
        self,
        start_case: int,
        end_case: int,
        max_depth: int = 5
    ) -> Optional[List[int]]:
        """
        Find a path between two cases using recursive DFS.
        Demonstrates: Recursive algorithm with cycle detection and depth limit.
        
        Args:
            start_case: Starting case ID
            end_case: Target case ID
            max_depth: Maximum path length (prevents unbounded recursion)
            
        Returns:
            List of case IDs forming path, or None if no path exists
        """
        visited: Set[int] = set()
        
        def _dfs_recursive(current: int, target: int, depth: int, path: List[int]) -> Optional[List[int]]:
            """
            Recursive DFS with cycle detection and depth limit.
            Demonstrates: Recursion, base cases, and safeguards.
            """
            # Base case 1: Found target
            if current == target:
                return path + [current]
            
            # Base case 2: Exceeded maximum depth
            if depth >= max_depth:
                logger.debug(f"Max depth {max_depth} reached at case {current}")
                return None
            
            # Base case 3: Already visited (cycle detection)
            if current in visited:
                return None
            
            # Mark as visited (cycle prevention)
            visited.add(current)
            
            # Recursive case: Explore neighbors
            if current in self.adjacency:
                for neighbor in self.adjacency[current]:
                    result = _dfs_recursive(neighbor, target, depth + 1, path + [current])
                    if result is not None:
                        return result
            
            # Backtrack: Remove from visited if no path found
            visited.discard(current)
            return None
        
        return _dfs_recursive(start_case, end_case, 0, [])
    
    def get_connected_cases(
        self,
        case_id: int,
        max_depth: int = 2
    ) -> Set[int]:
        """
        Get all cases connected within a maximum depth.
        Demonstrates: Recursive traversal with depth limit.
        
        Args:
            case_id: Starting case ID
            max_depth: Maximum traversal depth
            
        Returns:
            Set of connected case IDs
        """
        visited: Set[int] = set()
        
        def _traverse_recursive(current: int, depth: int) -> None:
            """
            Recursively traverse connections up to max depth.
            Demonstrates: Recursive traversal with safeguards.
            """
            # Base case 1: Exceeded maximum depth
            if depth > max_depth:
                return
            
            # Base case 2: Already visited (cycle prevention)
            if current in visited:
                return
            
            # Mark as visited
            visited.add(current)
            
            # Recursive case: Traverse neighbors
            if current in self.adjacency:
                for neighbor in self.adjacency[current]:
                    _traverse_recursive(neighbor, depth + 1)
        
        _traverse_recursive(case_id, 0)
        visited.discard(case_id)  # Remove starting case from result
        return visited
    
    def get_connection_details(
        self,
        case_id_1: int,
        case_id_2: int
    ) -> List[Dict]:
        """
        Get all connection details between two cases.
        
        Args:
            case_id_1: First case ID
            case_id_2: Second case ID
            
        Returns:
            List of connection detail dictionaries
        """
        pair = tuple(sorted([case_id_1, case_id_2]))
        return self.connections.get(pair, [])
    
    def count_connections(self, case_id: int) -> int:
        """
        Count direct connections for a case.
        
        Args:
            case_id: Case ID
            
        Returns:
            Number of direct connections
        """
        return len(self.adjacency.get(case_id, set()))
    
    def detect_cycle(self, start_case: int, max_length: int = 10) -> Optional[List[int]]:
        """
        Detect if a case is part of any cycle.
        Demonstrates: Cycle detection in graphs.
        
        Args:
            start_case: Starting case ID
            max_length: Maximum cycle length to detect
            
        Returns:
            Cycle path if found, None otherwise
        """
        visited: Set[int] = set()
        
        def _detect_cycle_recursive(
            current: int,
            parent: Optional[int],
            path: List[int]
        ) -> Optional[List[int]]:
            """Recursive cycle detection."""
            # If we've seen this node and it's in our current path, we found a cycle
            if current in path:
                cycle_start = path.index(current)
                return path[cycle_start:] + [current]
            
            # Stop if path is too long
            if len(path) >= max_length:
                return None
            
            # Mark as visited
            visited.add(current)
            
            # Explore neighbors
            if current in self.adjacency:
                for neighbor in self.adjacency[current]:
                    # Don't go back to parent (would be a false cycle)
                    if neighbor != parent:
                        result = _detect_cycle_recursive(neighbor, current, path + [current])
                        if result is not None:
                            return result
            
            return None
        
        return _detect_cycle_recursive(start_case, None, [])


def build_graph_from_connections(connections: List[Dict]) -> ConnectionGraph:
    """
    Build an in-memory graph from a list of connections.
    Demonstrates: Factory function for graph construction.
    
    Args:
        connections: List of connection dictionaries
        
    Returns:
        ConnectionGraph instance
    """
    graph = ConnectionGraph()
    
    for conn in connections:
        graph.add_connection(
            conn['case_id_1'],
            conn['case_id_2'],
            {
                'type': conn.get('connection_type'),
                'value': conn.get('connection_value'),
                'explanation': conn.get('explanation')
            }
        )
    
    return graph
