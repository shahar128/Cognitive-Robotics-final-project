# Cognitive-Robotics-final-project

This project leverages the KUKA YouBot robot in Webots to address a real-world challenge in recycling through intelligent sorting. The robot detects and places recyclable items into designated bins, using a reward-based A* algorithm that maximizes both recycling efficiency and rewards.

## Setup and Installation
To run this project:
1. Install Webots for simulation.
2. Clone the repository: git clone https://github.com/shahar128/Cognitive-Robotics-final-project.git
3. Open the worlds file in Webots to load the project environment.
4. Run the simulation through the Webots interface.

## Folders explantion
contollers: 
  - my_youbot:
      - graphs.py: have the A* palnning implementation that outputs a plan
      - my_youbot.py: Main control file responsible for handling robot movements, item detection, and interactions with bins.
      - pddl.py: the initial pddl file which was not used in the final project but gave us the direction to go to A*.
  - supervisor:
      - supervisor.py: Supervisor script to introduce random items during the simulation.
worlds:
  - factory.wbt: Main world file where the KUKA YouBot, bins, and items are placed for the simulation. It defines the layout, object positions, and environmental properties.
protos: contains custom PROTO files used to define reusable and customizable objects in Webots.

## Implementation Details
- Robot Design: KUKA YouBot with omnidirectional Mecanum wheels allowing for flexible movement.
Camera and GPS: The robot uses camera recognition for item detection and a GPS for navigation accuracy.
- A Algorithm*: Implemented for optimal planning to sort items into bins based on time and reward constraints.
How It Works
- Item Detection: The robot’s camera detects items on the table with unique colors representing each recyclable type.
- Path Planning: The A* algorithm computes paths based on the closest item and bin locations, maximizing rewards.
- Recycling: Upon successful item placement in the bin, rewards are accumulated, and new items appear periodically to keep the task dynamic.

## youtube video
https://youtu.be/xwkPleRuofk


