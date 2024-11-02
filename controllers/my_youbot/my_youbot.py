from controller import Robot, GPS, Camera
import math
import random
import os
import sys
from graphs import compute_optimal_plan

# Create the Robot instance
robot = Robot()

# Get the timestep of the current world (in milliseconds)
timestep = int(robot.getBasicTimeStep())

# Get the predefined wheel motors
wheel_names = ['wheel1', 'wheel2', 'wheel3', 'wheel4']
wheels = []
for wheel_name in wheel_names:
    motor = robot.getDevice(wheel_name)
    motor.setPosition(float('inf'))  # Set to infinite rotation
    motor.setVelocity(0.0)  # Initially stop the wheels
    wheels.append(motor)
    
armMotors = []
armMotors.append(robot.getDevice("arm1"))
armMotors.append(robot.getDevice("arm2"))
armMotors.append(robot.getDevice("arm3"))
armMotors.append(robot.getDevice("arm4"))
armMotors.append(robot.getDevice("arm5"))
# Set maximum motor velocity
armMotors[0].setVelocity(1.5)
armMotors[1].setVelocity(1.5)
armMotors[2].setVelocity(1.5)
armMotors[3].setVelocity(0.5)
armMotors[4].setVelocity(1.5)

# Initialize gripper motors
finger1 = robot.getDevice("finger::left")
finger2 = robot.getDevice("finger::right")
# Set maximum motor velocity
finger1.setVelocity(0.5)
finger2.setVelocity(0.5)
# Read minimum and maximum position of the gripper motors
fingerMinPosition = finger1.getMinPosition()
fingerMaxPosition = finger1.getMaxPosition()

# Get the camera device and enable recognition
camera = robot.getDevice('camera')
camera.enable(timestep)
camera.recognitionEnable(timestep)

# Get the GPS device to track robot position
gps = robot.getDevice('gps')
gps.enable(timestep)

general_speed_rad = 8  # Speed in meters per second (m/s)
general_speed_m_s = general_speed_rad * 0.05

turning_speed = (math.pi / 4)  # make the robot turn in 2 sec

total_reward = 0

def move_forward(speed, steps):
    wheels[0].setVelocity(speed)
    wheels[1].setVelocity(speed)
    wheels[2].setVelocity(speed)
    wheels[3].setVelocity(speed)
    for _ in range(int(steps)):
        robot.step(timestep)


def move_backward(speed, steps):
    wheels[0].setVelocity(-speed)
    wheels[1].setVelocity(-speed)
    wheels[2].setVelocity(-speed)
    wheels[3].setVelocity(-speed)
    for _ in range(int(steps)):
        robot.step(timestep)


# Function to move left by a certain number of steps (calculated from time)
def move_right(speed, steps):
    wheels[0].setVelocity(-speed)
    wheels[1].setVelocity(speed)
    wheels[2].setVelocity(speed)
    wheels[3].setVelocity(-speed)
    for _ in range(int(steps)):
        robot.step(timestep)


def move_left(speed, steps):
    wheels[0].setVelocity(speed)
    wheels[1].setVelocity(-speed)
    wheels[2].setVelocity(-speed)
    wheels[3].setVelocity(speed)
    for _ in range(int(steps)):
        robot.step(timestep)

def stop():
    for motor in wheels:
        motor.setVelocity(0.0)

# Function to release the gripper
def release_object():
    # Open the gripper
    finger1.setPosition(fingerMaxPosition)  # Adjust to open the gripper
    finger2.setPosition(fingerMaxPosition)
    robot.step(1000)
    armMotors[1].setPosition(0)  # Adjust arm 2 to lower position
    armMotors[2].setPosition(0)  # Adjust arm 2 to lower position
    armMotors[3].setPosition(0) 
    move_forward(general_speed_rad, 2)
    stop()

def turn_arm():
    armMotors[1].setPosition(1.57)  # Adjust arm 2 to lower position
    armMotors[2].setPosition(-0.3)
    armMotors[3].setPosition(0)
    robot.step(500)
    
def pick_up():
    # Lower the arm and open the gripper
    finger1.setPosition(fingerMaxPosition)  # Open gripper
    finger2.setPosition(fingerMaxPosition)
    armMotors[2].setPosition(-1)  # Adjust arm 2 to lower position
    armMotors[3].setPosition(-1.3)    # Adjust arm 3 for lowering the gripper
   
    # Wait for the arm to lower and the gripper to open
    robot.step(200 * timestep)

    # Close the gripper to grab the apple
    finger1.setPosition(0.001)  # Close gripper to grab
    finger2.setPosition(0.001)
    robot.step(100 * timestep)  # Wait for gripper to close

    # Lift the arm after grabbing the apple
    armMotors[1].setPosition(0)  # Raise arm 1 to lift the apple
    robot.step(200 * timestep)
    turn_arm()


def move_to_item(item_name):
    objects = camera.getRecognitionObjects()
    for obj in objects:
        obj_color = obj.getColors()[:3]
        obj_name = next((name for name, color in name_to_color.items() if color == obj_color), "Unknown")
        if item_name == obj_name:
            object_position = obj.getPosition()
            robot_position = gps.getValues()
            obj_x = object_position[1]
            obj_y = object_position[0]
            time_x = abs(obj_x) / general_speed_m_s  # Time in seconds to travel the distance (m/s)
            steps_x = (time_x * 1000) / timestep
            if obj_x >= 0:
                move_left(general_speed_rad, steps_x - 1)
            else:
                move_right(general_speed_rad, steps_x-1)

            time_y = obj_y / general_speed_m_s
            steps_y = ((time_y * 1000) / timestep) - 24  # Convert to number of simulation steps
            move_forward(general_speed_rad, steps_y)


def move_to_bin(bin_name):
    orange_bin_coordinates = [0, 1]
    purple_bin_coordinates = [-1, 1]
    blue_bin_coordinates = [-2, 1]
    green_bin_coordinates = [-3, 1]
    robot_position_bin = gps.getValues()
    if bin_name == "orange_bin":
        x_dist = robot_position_bin[0] - orange_bin_coordinates[0]
    elif bin_name == "blue_bin":
        x_dist = robot_position_bin[0] - blue_bin_coordinates[0]
    elif bin_name == "green_bin":
        x_dist = robot_position_bin[0] - green_bin_coordinates[0]
    elif bin_name == "purple_bin":
        x_dist = robot_position_bin[0] - purple_bin_coordinates[0]

    time_in_x = abs(x_dist) / general_speed_m_s
    steps_in_x = (time_in_x * 1000) / timestep
    if x_dist <= 0:
        move_left(general_speed_rad, steps_in_x)
    else:
        move_right(general_speed_rad, steps_in_x)
    stop()
    move_backward(general_speed_rad, 550)


recalculate_needed = False

def perform_plan(plan):
    global total_reward  # Declare total_reward as global
    global rewards
    global recalculate_needed  # Use the flag here

    initial_item_count = len(camera.getRecognitionObjects())
    for action in plan:
        parts = action.split(" ")
        action_name = parts[0].strip()
        item = parts[2].split(",")[0]
        bin = parts[4].split(",")[0]

        if action_name == 'start':
            continue
        elif action_name == 'move_to_item':
            print(f"Moving to item: {item}")
            move_to_item(item)
        elif action_name == 'pick_up':
            print(f"Picking up item: {item}")
            pick_up()
        elif action_name == 'move_to_bin':
            print(f"Moving {item} to bin: {bin}")
            move_to_bin(bin)
        elif action_name == 'place_in_bin':
            print(f"Placing {item} in bin: {bin}")
            total_reward += rewards[bin][item]
            rewards[bin][item] = []
            release_object()
            initial_item_count -= 1

            current_item_count = len(camera.getRecognitionObjects())
            if current_item_count != initial_item_count:
                print("New item detected! Recalculating plan.")
                recalculate_needed = True  # Set flag to recalculate plan in main loop
                break 
        stop()
        #check time


def recalculate_plan():
    objects = camera.getRecognitionObjects()
    robot_position = gps.getValues()
    global rewards

    # Calculate locations and rewards
    locations = {}
    for obj in objects:
        obj_color = obj.getColors()[:3]
        obj_name = next((name for name, color in name_to_color.items() if color == obj_color), "Unknown")
        object_position = obj.getPosition()
        obj_location_x = robot_position[0] + object_position[1]
        obj_location_y = robot_position[1] - object_position[0] - 0.3
        locations[obj_name] = [obj_location_x, obj_location_y]
        bin_name = goals[obj_name]
        if obj_name not in rewards[bin_name]:
            rewards[bin_name][obj_name] = random.randint(1, 50)
    print(rewards)
    # Generate a new plan
    new_plan = compute_optimal_plan(locations, rewards)
    return new_plan




name_to_color = {

    'duck': [0.87451, 0.756863, 0.113725],
    'cerealBox': [1,1,0],
    'cardboardBox': [1,1,1],
    'longGlass': [0,1,0],
    'board': [0,1,1],
    'orange': [1,0.5,0],
    'apple': [0.59, 0.75, 0.28],
    'glass': [0.5,0,0],
}

goals = {

    'duck': 'orange_bin',
    'cerealBox': 'blue_bin',
    'cardboardBox': 'blue_bin',
    'longGlass': 'purple_bin',
    'board': 'orange_bin',
    'orange': 'green_bin',
    'apple': 'green_bin',
    'glass': 'purple_bin',
}

rewards = {
    'orange_bin': {},
    'blue_bin': {},
    'green_bin': {},
    'purple_bin': {}
}
simulation_start_time = robot.getTime()

# Main loop: move the robot to the apple
while robot.step(timestep) != -1:
    current_time = robot.getTime()
    time_elapsed = current_time - simulation_start_time

    if time_elapsed > 160:
        print(f"Finished 160 sec of recycling. Total reward: {total_reward}")
        stop()  # Stop all robot motors
        break

    # Check if we need to recalculate the plan due to new items
    if recalculate_needed:
        plan = recalculate_plan()
        recalculate_needed = False  # Reset the flag
    else:
        plan = recalculate_plan()  # Get initial plan if no recalculation is pending

    if time_elapsed > 160:
        print(f"Finished 160 sec of recycling. Total reward: {total_reward}")
        stop()  # Stop all robot motors
        break

    #perform_plan(plan)
    initial_item_count = len(camera.getRecognitionObjects())
    for action in plan:
        parts = action.split(" ")
        action_name = parts[0].strip()
        item = parts[2].split(",")[0]
        bin = parts[4].split(",")[0]

        if action_name == 'start':
            continue
        elif action_name == 'move_to_item':
            print(f"Moving to item: {item}")
            move_to_item(item)
        elif action_name == 'pick_up':
            print(f"Picking up item: {item}")
            pick_up()
        elif action_name == 'move_to_bin':
            print(f"Moving {item} to bin: {bin}")
            move_to_bin(bin)
        elif action_name == 'place_in_bin':
            print(f"Placing {item} in bin: {bin}")
            total_reward += rewards[bin][item]
            rewards[bin][item] = []
            release_object()
            initial_item_count -= 1

            current_item_count = len(camera.getRecognitionObjects())
            if current_item_count != initial_item_count:
                print("New item detected! Recalculating plan.")
                recalculate_needed = True  # Set flag to recalculate plan in main loop
                break
        stop()
        if time_elapsed > 160:
            print(f"Finished 160 sec of recycling. Total reward: {total_reward}")
            stop()  # Stop all robot motors
            break
        # check time

    
    
    

