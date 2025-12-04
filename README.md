# Traffic Light Manager

A Dockerized Python application that manages a traffic light state machine, broadcasts the state via UDP, and publishes state and future schedules to a DDS topic.

## Features

- **State Machine**: Manages traffic light states (Green, Orange, Red) with configurable timings.
- **UDP Broadcast**: Sends the current state and schedule via UDP to a specified host/port (default: `localhost:5005`).
- **DDS Publisher**: Publishes state and schedule to a DDS topic (`TrafficLightStatus`) using eProsima Fast DDS.
- **DDS Subscriber**: Includes a debug subscriber to verify DDS communication.
- **Dockerized**: Fully containerized environment with Fast DDS and Python bindings built from source.

## Prerequisites

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

## Getting Started

### 1. Clone the Repository

```bash
git clone <repository-url>
cd traffic-light-manager
```

### 2. Build and Run

Use Docker Compose to build the image and start the services (Manager and Subscriber).

```bash
docker compose up --build
```

> **Note**: The initial build may take several minutes as it compiles Fast DDS and its Python bindings from source.

### 3. Verify Output

You should see output from the `traffic-light-subscriber` service showing the received states:

```
traffic-light-subscriber-1  | Received State: 1
traffic-light-subscriber-1  | Timestamp: 1701600000.0
traffic-light-subscriber-1  | Schedule:
traffic-light-subscriber-1  |   - State: 1, Start: 1701600000.00, Duration: 5.0
traffic-light-subscriber-1  |   - State: 2, Start: 1701600005.00, Duration: 2.0
...
```

To verify UDP output, you can listen on port 5005 (if mapped to host) or check the logs.

## Configuration

Environment variables can be set in `docker-compose.yml`:

- `UDP_HOST`: Destination host for UDP messages (default: `127.0.0.1`).
- `UDP_PORT`: Destination port for UDP messages (default: `5005`).

## Project Structure

- `src/main.py`: Application entry point.
- `src/state_machine.py`: Traffic light logic.
- `src/udp_sender.py`: UDP communication.
- `src/dds_publisher.py`: DDS publisher implementation.
- `src/dds_subscriber.py`: DDS subscriber for debugging.
- `src/TrafficLight.idl`: IDL definition for DDS topics.
- `Dockerfile`: Multi-stage build for Fast DDS and Python environment.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
