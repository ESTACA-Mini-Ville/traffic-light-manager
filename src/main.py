import time
import logging
import signal
import sys
import os

from state_machine import TrafficLightManager
from udp_sender import UdpSender
from dds_publisher import DDSPublisher

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    logging.info("Starting Traffic Light Manager...")

    # Initialize components
    manager = TrafficLightManager()
    
    udp_host = os.environ.get("UDP_HOST", "127.0.0.1")
    udp_port = int(os.environ.get("UDP_PORT", "5005"))
    udp_sender = UdpSender(host=udp_host, port=udp_port)
    
    try:
        dds_publisher = DDSPublisher()
        logging.info("DDS Publisher initialized.")
    except Exception as e:
        logging.error(f"Failed to initialize DDS Publisher: {e}")
        dds_publisher = None

    running = True

    def signal_handler(sig, frame):
        nonlocal running
        logging.info("Shutting down...")
        running = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    previous_state = None

    while running:
        # Update state
        manager.tick()
        
        current_state = manager.current_state
        schedule = manager.get_schedule()
        
        # Prepare data
        state_data = {
            "current_state": int(current_state),
            "timestamp": time.time(),
            "schedule": [
                {"state": int(item.state), "start_time": item.start_time, "duration": item.duration}
                for item in schedule
            ]
        }
        
        # Send UDP only on state change
        if current_state != previous_state:
            udp_sender.send_state(state_data)
            previous_state = current_state
        
        # Publish DDS
        if dds_publisher:
            try:
                dds_publisher.publish(int(current_state), schedule)
            except Exception as e:
                logging.error(f"Error publishing DDS: {e}")

        time.sleep(0.5)

    if dds_publisher:
        dds_publisher.close()

if __name__ == "__main__":
    main()
