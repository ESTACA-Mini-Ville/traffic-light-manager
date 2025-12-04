import time
from enum import IntEnum
from dataclasses import dataclass
from typing import List, Tuple

class TrafficLightState(IntEnum):
    A_GREEN = 1
    A_ORANGE = 2
    ALL_RED = 3
    B_GREEN = 4
    B_ORANGE = 5

@dataclass
class ScheduleItem:
    state: int
    start_time: float
    duration: float

class TrafficLightManager:
    def __init__(self):
        self.current_state = TrafficLightState.ALL_RED
        self.state_start_time = time.time()
        # Initial transition direction: from All Red to A Green
        self._next_from_all_red = TrafficLightState.A_GREEN
        
        # Durations in seconds
        self.durations = {
            TrafficLightState.A_GREEN: 5.0,
            TrafficLightState.A_ORANGE: 2.0,
            TrafficLightState.ALL_RED: 1.0,
            TrafficLightState.B_GREEN: 5.0,
            TrafficLightState.B_ORANGE: 2.0,
        }

    def get_next_state(self, current: TrafficLightState) -> TrafficLightState:
        if current == TrafficLightState.A_GREEN:
            return TrafficLightState.A_ORANGE
        elif current == TrafficLightState.A_ORANGE:
            self._next_from_all_red = TrafficLightState.B_GREEN
            return TrafficLightState.ALL_RED
        elif current == TrafficLightState.ALL_RED:
            return self._next_from_all_red
        elif current == TrafficLightState.B_GREEN:
            return TrafficLightState.B_ORANGE
        elif current == TrafficLightState.B_ORANGE:
            self._next_from_all_red = TrafficLightState.A_GREEN
            return TrafficLightState.ALL_RED
        return TrafficLightState.ALL_RED

    def tick(self):
        now = time.time()
        elapsed = now - self.state_start_time
        current_duration = self.durations[self.current_state]

        if elapsed >= current_duration:
            self.current_state = self.get_next_state(self.current_state)
            self.state_start_time = now

    def get_schedule(self, horizon_seconds: float = 20.0) -> List[ScheduleItem]:
        """
        Returns a list of upcoming states and their start times.
        """
        schedule = []
        
        # Current state remaining time
        now = time.time()
        current_elapsed = now - self.state_start_time
        current_remaining = max(0, self.durations[self.current_state] - current_elapsed)
        
        # Add current state (conceptually it started in the past, but we report it)
        # Or should we only report future? The requirement says "upcoming states".
        # Let's include current state as the first item with its actual start time.
        
        sim_state = self.current_state
        sim_start_time = self.state_start_time
        # We need to simulate the internal state of _next_from_all_red too
        sim_next_from_all_red = self._next_from_all_red
        
        schedule.append(ScheduleItem(int(sim_state), sim_start_time, self.durations[sim_state]))
        
        sim_time = sim_start_time + self.durations[sim_state]
        
        while sim_time < now + horizon_seconds:
            # Simulate next transition
            if sim_state == TrafficLightState.A_GREEN:
                sim_state = TrafficLightState.A_ORANGE
            elif sim_state == TrafficLightState.A_ORANGE:
                sim_next_from_all_red = TrafficLightState.B_GREEN
                sim_state = TrafficLightState.ALL_RED
            elif sim_state == TrafficLightState.ALL_RED:
                sim_state = sim_next_from_all_red
            elif sim_state == TrafficLightState.B_GREEN:
                sim_state = TrafficLightState.B_ORANGE
            elif sim_state == TrafficLightState.B_ORANGE:
                sim_next_from_all_red = TrafficLightState.A_GREEN
                sim_state = TrafficLightState.ALL_RED
            
            schedule.append(ScheduleItem(int(sim_state), sim_time, self.durations[sim_state]))
            sim_time += self.durations[sim_state]
            
        return schedule
