import socket
import json
import logging

class UdpSender:
    def __init__(self, host: str = "127.0.0.1", port: int = 5005):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        logging.info(f"UDP Sender initialized for {self.host}:{self.port}")

    def send_state(self, state_data: dict):
        try:
            message = json.dumps(state_data).encode('utf-8')
            self.sock.sendto(message, (self.host, self.port))
        except Exception as e:
            logging.error(f"Failed to send UDP message: {e}")
