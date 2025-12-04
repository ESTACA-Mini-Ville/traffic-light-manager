import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))

from state_machine import TrafficLightManager, TrafficLightState
import time

def test_state_machine():
    manager = TrafficLightManager()
    print(f"Initial state: {manager.current_state}")
    
    # Simulate time passing
    # We can't easily mock time.time() without patching, but we can just call tick() and sleep or mock the time module if we want to be fancy.
    # For a quick check, let's just inspect the logic by overriding start_time.
    
    manager.state_start_time = time.time() - 100 # Force transition
    manager.tick()
    print(f"After 100s: {manager.current_state}")
    
    # Check schedule
    schedule = manager.get_schedule(horizon_seconds=10)
    print("Schedule:")
    for item in schedule:
        print(f"  State: {item.state}, Start: {item.start_time:.2f}, Duration: {item.duration}")

if __name__ == "__main__":
    test_state_machine()
