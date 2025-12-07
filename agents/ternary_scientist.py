import random
import heapq
import math
from .agent import Agent
from .structs import FrameData, GameAction, GameState
from .pathfinder import a_star_search
# --- SYSTEM 1: INTUITION ENGINE (BitNet Stub) ---
class IntuitionEngine:
    def __init__(self):
        # In the future, load your quantized BitNet model here
        self.known_rules = {} 

    def analyze_frame_diff(self, prev_frame, curr_frame, action_taken):
        """
        BitNet looks at 'What changed?' to infer rules.
        """
        if prev_frame is None: return
        
        # Simple heuristic: If we moved but position didn't change, it's a wall.
        # Your BitNet model will eventually replace this with deep visual intuition.
        p_grid = prev_frame.state['grid'] # Pseudo-code access
        c_grid = curr_frame.state['grid']
        
        # Example Hypothesis Generation
        if p_grid == c_grid:
            return {"type": "collision", "tile_value": self._get_target_tile(prev_frame, action_taken)}
        return None

    def _get_target_tile(self, frame, action):
        # Helper to find what tile we tried to step on
        return 1 # Placeholder for 'Blue Tile'

# --- SYSTEM 2: VERIFICATION ENGINE (Planner) ---
class VerificationEngine:
    def plan_path(self, start_pos, goal_pos, world_model):
        """
        A* Pathfinding that uses the 'World Model' built by System 1.
        """
        # If System 1 says 'Blue is Lava', the planner avoids Blue.
        return [GameAction.RIGHT, GameAction.RIGHT, GameAction.UP] # Mock Plan

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
        # Update our mental model based on the result of the LAST action
        if len(frames) > 1:
            hypothesis = self.sys1.analyze_frame_diff(frames[-2], latest_frame, self.last_action)
            if hypothesis and hypothesis['type'] == 'collision':
                print(f"[Scientist] Hypothesis Confirmed: Tile {hypothesis['tile_value']} is a WALL.")
                self.world_model['walls'].append(hypothesis['tile_value'])

        # 2. PLANNING PHASE (System 2)
        # If we have a valid plan, execute it.
        if self.current_plan:
            action = self.current_plan.pop(0)
            self.last_action = action
            return action

        # 3. HYPOTHESIS PHASE (System 1)
        # If no plan, we need to formulate a new one.
        # "I want to reach the goal. Does my world model allow a path?"
        # For 'Locksmith', we define the Goal as the Lock.
        
        # If model is uncertain, EXPLORE (Random / BitNet suggestion)
        # If model is certain, EXPLOIT (A* Path to goal)
        if random.random() < 0.2: # 20% Curiosity rate
             print("[Scientist] Exploring to test physics...")
             action = random.choice([a for a in GameAction if a.value <= 4]) # Move actions
        else:
             print("[Scientist] Executing optimal path...")
             # Here we would call self.sys2.plan_path()
             action = random.choice([GameAction.RIGHT, GameAction.DOWN]) # Drift towards goal

        self.last_action = action
        return action
