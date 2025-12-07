import random
import heapq
import math
from .agent import Agent
from .structs import FrameData, GameAction, GameState
from .pathfinder import a_star_search

# --- SYSTEM 1: INTUITION ENGINE (BitNet Stub) ---
class IntuitionEngine:
    def __init__(self):
        # We will track 'known_rules' to build our world model
        self.known_rules = {} 

    def analyze_frame_diff(self, prev_frame, curr_frame, action_taken):
        """
        Compares two frames to deduce the effect of the last action.
        """
        if prev_frame is None: return None
        
        # 1. EXTRACT GRIDS
        p_grid = prev_frame.state.get('grid')
        c_grid = curr_frame.state.get('grid')
        
        # 2. DETECT COLLISION (Wall Logic)
        if p_grid == c_grid:
            target_pos = self._calculate_target_pos(prev_frame, action_taken)
            if target_pos:
                tile_val = self._get_tile_value(p_grid, target_pos)
                return {"type": "collision", "tile_value": tile_val, "pos": target_pos}
        return None

    def _get_player_pos(self, grid):
        """
        Scans the grid to find the player. 
        In Locksmith, the player is often the only unique non-background, non-wall entity.
        For now, we return (0,0) as a placeholder until we know the player's color ID.
        """
        return (0, 0) # Placeholder

    def _calculate_target_pos(self, frame, action):
        """
        Predicts where the player WANTED to go.
        """
        px, py = self._get_player_pos(frame.state.get('grid'))
        if action == GameAction.UP:    return (px, py - 1)
        if action == GameAction.DOWN:  return (px, py + 1)
        if action == GameAction.LEFT:  return (px - 1, py)
        if action == GameAction.RIGHT: return (px + 1, py)
        return (px, py)

    def _get_tile_value(self, grid, pos):
        x, y = pos
        if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
            return grid[y][x]
        return -1 # Out of bounds

# --- SYSTEM 2: VERIFICATION ENGINE (Planner) ---
class VerificationEngine:
    def plan_path(self, start_pos, goal_pos, world_model):
        """
        Uses A* to find the optimal path based on current beliefs.
        """
        print(f"[System 2] Planning path from {start_pos} to {goal_pos}...")
        
        # Extract constraints from World Model
        walls = set(world_model.get("walls", []))
        hazards = set(world_model.get("hazards", []))
        
        # Execute Search
        path = a_star_search(start_pos, goal_pos, walls, hazards)
        
        if path:
            print(f"[System 2] Path found! Length: {len(path)} steps.")
        else:
            print("[System 2] No path found. Target might be unreachable.")
            
        return path

# --- THE AGENT ---
class TernaryReasonerAgent(Agent):
    """
    The Scientist: Observes -> Hypothesizes -> Plans.
    """
    def __init__(self):
        super().__init__()
        self.sys1 = IntuitionEngine()
        self.sys2 = VerificationEngine()
        self.world_model = {"walls": [], "hazards": []}
        self.current_plan = []
        self.last_action = None

    def is_done(self, frames: list[FrameData], latest_frame: FrameData) -> bool:
        return latest_frame.state in [GameState.WIN, GameState.GAME_OVER]

    def choose_action(self, frames: list[FrameData], latest_frame: FrameData) -> GameAction:
        # 1. OBSERVATION PHASE
        if len(frames) > 1:
            hypothesis = self.sys1.analyze_frame_diff(frames[-2], latest_frame, self.last_action)
            if hypothesis and hypothesis['type'] == 'collision':
                print(f"[Scientist] Hypothesis Confirmed: Tile {hypothesis['tile_value']} is a WALL.")
                self.world_model['walls'].append(hypothesis['tile_value'])

        # 2. EXECUTION PHASE (Follow the Plan)
        if self.current_plan:
            return self.current_plan.pop(0)

        # 3. PLANNING PHASE (Formulate a Plan)
        grid = latest_frame.state.get('grid')
        
        # A. Find where we are
        start_pos = self.sys1._get_player_pos(grid) 
        
        # B. Find where the LOCK is (Scanning for the unique goal tile)
        goal_pos = None
        if grid:
            for y in range(len(grid)):
                for x in range(len(grid[0])):
                    val = grid[y][x]
                    # Heuristic: If it's not background(0) and not us, it might be the goal
                    if val != 0 and (x,y) != start_pos and val not in self.world_model['walls']:
                        goal_pos = (x, y)
                        break 
                if goal_pos: break

        # C. Generate Path
        if start_pos and goal_pos:
             print(f"[Scientist] Planning path from {start_pos} to {goal_pos}...")
             new_path = self.sys2.plan_path(start_pos, goal_pos, self.world_model)
             if new_path:
                 self.current_plan = new_path
                 return self.current_plan.pop(0)
                 
        # D. Fallback (If no plan found, explore randomly)
        return GameAction.RIGHT
