import heapq
from .structs import GameAction

class Node:
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position
        self.g = 0  # Cost from start to current node
        self.h = 0  # Heuristic (estimated cost from current to goal)
        self.f = 0  # Total cost

    def __eq__(self, other):
        return self.position == other.position
    
    def __lt__(self, other):
        return self.f < other.f

def heuristic(node_pos, goal_pos):
    # Manhattan distance for grid movement
    return abs(node_pos[0] - goal_pos[0]) + abs(node_pos[1] - goal_pos[1])

def get_neighbors(position, grid_size=64):
    """
    Returns valid adjacent coordinates (Up, Down, Left, Right).
    """
    (x, y) = position
    candidates = [
        ((x, y - 1), GameAction.UP),
        ((x, y + 1), GameAction.DOWN),
        ((x - 1, y), GameAction.LEFT),
        ((x + 1, y), GameAction.RIGHT)
    ]
    # Filter out of bounds
    valid = []
    for pos, action in candidates:
        if 0 <= pos[0] < grid_size and 0 <= pos[1] < grid_size:
            valid.append((pos, action))
    return valid

def a_star_search(start_pos, goal_pos, walls, hazards):
    """
    Returns a list of GameActions to get from Start to Goal, avoiding Walls.
    """
    start_node = Node(None, start_pos)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, goal_pos)
    end_node.g = end_node.h = end_node.f = 0

    open_list = []
    closed_list = set()

    heapq.heappush(open_list, start_node)

    # Safety break to prevent infinite loops in unreachable areas
    iterations = 0
    max_iterations = 5000 

    while len(open_list) > 0 and iterations < max_iterations:
        iterations += 1
        
        # Get the current node
        current_node = heapq.heappop(open_list)
        closed_list.add(current_node.position)

        # Found the goal
        if current_node == end_node:
            path = []
            current = current_node
            while current is not None and current.action is not None:
                path.append(current.action)
                current = current.parent
            return path[::-1] # Return reversed path

        # Generate children
        children = get_neighbors(current_node.position)

        for child_pos, action in children:
            if child_pos in closed_list:
                continue

            # CHECK THE WORLD MODEL (This is where System 1 informs System 2)
            # If BitNet says it's a wall, we treat cost as infinite
            if child_pos in walls:
                continue
            
            # Create the f, g, and h values
            child = Node(current_node, child_pos)
            child.action = action
            child.g = current_node.g + 1
            
            # Penalize hazards (like lava) but allow them if necessary
            if child_pos in hazards:
                child.g += 10 

            child.h = heuristic(child.position, end_node.position)
            child.f = child.g + child.h

            # Add the child to the open list
            # (In a production implementation, check if child is already in open_list with lower g)
            heapq.heappush(open_list, child)

    return [] # No path found
