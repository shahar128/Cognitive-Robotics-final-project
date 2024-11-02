import random
from controller import Supervisor

supervisor = Supervisor()
timestep = int(supervisor.getBasicTimeStep())
simulation_start_time = supervisor.getTime()

# Define full node strings for each complex item
complex_nodes = {
    'orange': """
Solid {
  translation -1.3 -3.55 0.339327343517186
  rotation 0.8944271909999159 -0.4472135954999579 0 1.4238000900283822e-15
  children [
    Shape {
      appearance PBRAppearance {
        baseColor 1 0.5 0
      }
      geometry Sphere {
        radius 0.03
      }
    }
  ]
  name "orange"
  boundingObject Sphere {
    radius 0.03
  }
  physics Physics {
  }
  recognitionColors [
    1 0.5 0
  ]
}
""",
    'glass': """
Solid {
  translation -1.7 -3.58 0.30
  rotation -0.9066295000453348 -0.4219276591535275 -9.421841043019257e-06 9.989992496035105e-18
  children [
    Glass {
      rotation 0 0 1 1.5708
    }
  ]
  name "glass"
  physics Physics {
  }
  boundingObject Box {
    size 0.02 0.01 0.06
  }

  recognitionColors [
    0.5 0 0
  ]
}
""",
    # Add more items here as needed
}


# Define the appearance order and goals
item_appearance_order = ['orange','glass','orange','glass']
goals = {'orange': 'green_bin','glass': 'purple_bin'}

# Main loop to manage the addition of items over time
while supervisor.step(timestep) != -1:
    current_time = supervisor.getTime()
    time_elapsed = current_time - simulation_start_time

    if time_elapsed > 161:
        supervisor.simulationSetMode(Supervisor.SIMULATION_MODE_PAUSE)
        break

    if time_elapsed >= 50 and item_appearance_order:
        # Get the next item to add from the predefined order

        next_item = item_appearance_order.pop(0)

        # Add the complex node using the full string
        if next_item in complex_nodes:
            supervisor.getRoot().getField("children").importMFNodeFromString(-1, complex_nodes[next_item])

            # Set a random reward for the newly added item
            bin_name = goals[next_item]
            print(f"Added {next_item} for goal in bin {bin_name}")

        # Reset the timer for the next item addition
        simulation_start_time = current_time


