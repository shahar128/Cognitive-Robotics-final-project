from unified_planning.shortcuts import *
from unified_planning.io import PDDLWriter



def main():
    # Create the planning problem
    problem = Problem()

    general_speed_rad = 8  # Speed in meters per second (m/s)
    general_speed_m_s = general_speed_rad * 0.05

    duck_loc = [-3.4, -3.52]
    cerealBox_loc = [-3.1, -3.58]
    cardboardBox_loc = [-2.5, -3.57]
    longGlass_loc = [-2.18,-3.57]
    board_loc = [-2.0,-3.6]
    orange_loc = [-1.3,-3.55]
    apple_loc = [-0.97,-3.53]
    glass_loc = [-0.7, -3,53]

    orange_bin_loc = [0,0.4]
    purple_bin_loc = [-1, 0.4]
    blue_bin_loc = [-2, 0.4]
    green_bin_loc = [-3, 0.4]

    robot_init_loc = [-3, 0.4]
    # Define the objects and their locations
    item_locations = {
        'duck': duck_loc,
        'cerealBox': cerealBox_loc,
        'cardboardBox': cardboardBox_loc,
        'longGlass': longGlass_loc,
        'board': board_loc,
        'orange': orange_loc,
        'apple': apple_loc,
        'glass': glass_loc
    }

    bin_locations = {
        'orange_bin': orange_bin_loc,
        'purple_bin': purple_bin_loc,
        'blue_bin': blue_bin_loc,
        'green_bin': green_bin_loc
    }

    # Precompute all durations and store in a dictionary
    def calculate_duration(item_loc, bin_loc):
        return int((abs(item_loc[0] - bin_loc[0]) + abs(item_loc[1] - bin_loc[1])) / general_speed_m_s)

    durations = {}
    for item_name, item_loc in item_locations.items():
        for bin_name, bin_loc in bin_locations.items():
            durations[(item_name, bin_name)] = calculate_duration(item_loc, bin_loc)
    #print(durations)
    # Define the types
    Item = UserType('item')
    Bin = UserType('bin')
    Robot = UserType('robot')

    InBin = Fluent('InBin', BoolType(), item=Item, bin=Bin)
    Holding = Fluent('Holding', BoolType(), robot=Robot, item=Item)
    TimeRemaining = Fluent('TimeRemaining', RealType())
    Destination = Fluent('Destination', BoolType(), item=Item, bin=Bin)
    robot_at_bin = Fluent('robot_at_bin', BoolType(), robot=Robot, bin=Bin)
    robot_at_item = Fluent('robot_at_item', BoolType(), robot=Robot, item=Item)
    robot_empty = Fluent('robot_empty', BoolType(), robot=Robot)
    Reward = Fluent('Reward', IntType(), item=Item, bin=Bin)
    Reward_robot = Fluent('Reward_robot', IntType())
    Duration = Fluent('Duration', RealType(), item=Item, bin=Bin)

    # Define the actions
    move_to_item = InstantaneousAction("move_to_item", r=Robot, i=Item, b =Bin)
    r = move_to_item.parameter("r")
    i = move_to_item.parameter("i")
    b = move_to_item.parameter("b")

    move_to_item.add_precondition(robot_at_bin(r,b))

    move_to_item.add_effect(robot_at_bin(r,b),False)
    move_to_item.add_effect(robot_at_item(r,i),True)
    move_to_item.add_effect(TimeRemaining(), TimeRemaining() - Duration(i,b))

    #move to bin
    move_to_bin = InstantaneousAction("move_to_bin", r=Robot, i=Item, b=Bin)
    r = move_to_item.parameter("r")
    i = move_to_item.parameter("i")
    b = move_to_item.parameter("b")

    move_to_bin.add_precondition(robot_at_item(r, i))

    move_to_bin.add_effect(robot_at_bin(r, b), True)
    move_to_bin.add_effect(robot_at_item(r,i), False)
    move_to_bin.add_effect(TimeRemaining(), TimeRemaining() - Duration(i, b))

    pick_up = InstantaneousAction("pick_up", r=Robot, i=Item)
    r = pick_up.parameter("r")
    i = pick_up.parameter("i")

    pick_up.add_precondition(robot_at_item(r,i))
    pick_up.add_precondition(robot_empty(r))

    pick_up.add_effect(Holding(r, i), True)
    pick_up.add_effect(robot_empty(r), False)
    pick_up.add_effect(TimeRemaining(), TimeRemaining() - 7)

    # Define the place_in_bin action
    place_in_bin = InstantaneousAction("place_in_bin", r=Robot, i=Item, b=Bin)
    r = place_in_bin.parameter("r")
    i = place_in_bin.parameter("i")
    b = place_in_bin.parameter("b")

    place_in_bin.add_precondition(Holding(r, i))
    place_in_bin.add_precondition(robot_at_bin(r,b))
    place_in_bin.add_precondition(Destination(i, b))

    place_in_bin.add_effect(InBin(i, b), True)
    place_in_bin.add_effect(Holding(r, i), False)
    place_in_bin.add_effect(Reward_robot(), Reward_robot() + Reward(i, b))
    place_in_bin.add_effect(TimeRemaining(), TimeRemaining() - 1)  # Example time decrement for placing

    # Define the objects
    duck = Object('duck', Item)
    apple = Object('apple', Item)
    cerealBox = Object('cerealBox', Item)
    cardboardBox = Object('cardboardBox', Item)
    orange = Object('orange', Item)
    glass = Object('glass', Item)
    longGlass = Object('longGlass', Item)
    board = Object('board', Item)

    orange_bin = Object('orange_bin', Bin)
    blue_bin = Object('blue_bin', Bin)
    purple_bin = Object('purple_bin', Bin)
    green_bin = Object('green_bin', Bin)

    robot = Object('Robot', Robot)

    problem.add_objects(
        [duck, apple, cerealBox, cardboardBox, orange, glass, longGlass, board, orange_bin, blue_bin, purple_bin,
         green_bin, robot])

    # Add fluents to the problem
    problem.add_fluent(InBin, default_initial_value=False)
    problem.add_fluent(Holding, default_initial_value=False)
    problem.add_fluent(TimeRemaining, default_initial_value=20000)
    problem.add_fluent(Destination, default_initial_value=False)
    problem.add_fluent(robot_at_bin, default_initial_value=False)
    problem.add_fluent(robot_at_item, default_initial_value=False)
    problem.add_fluent(robot_empty, default_initial_value=True)
    problem.add_fluent(Reward, default_initial_value=0)
    problem.add_fluent(Reward_robot, default_initial_value=0)
    problem.add_fluent(Duration, default_initial_value=100)


    # Define the initial state

    problem.set_initial_value(Duration(duck, orange_bin), durations['duck', 'orange_bin'])
    problem.set_initial_value(Duration(board, orange_bin), durations['board', 'orange_bin'])
    problem.set_initial_value(Duration(cardboardBox, blue_bin), durations['cardboardBox', 'blue_bin'])
    problem.set_initial_value(Duration(cerealBox, blue_bin), durations['cerealBox', 'blue_bin'])
    problem.set_initial_value(Duration(apple, green_bin), durations['apple', 'green_bin'])
    problem.set_initial_value(Duration(orange, green_bin), durations['orange', 'green_bin'])
    problem.set_initial_value(Duration(longGlass, purple_bin), durations['longGlass', 'purple_bin'])
    problem.set_initial_value(Duration(glass, purple_bin), durations['glass', 'purple_bin'])

    # Add actions to the problem
    problem.add_action(move_to_item)
    problem.add_action(move_to_bin)
    problem.add_action(pick_up)
    problem.add_action(place_in_bin)

    # Define the initial state
    problem.set_initial_value(Destination(duck, orange_bin), True)
    problem.set_initial_value(Destination(board, orange_bin), True)
    problem.set_initial_value(Destination(cardboardBox, blue_bin), True)
    problem.set_initial_value(Destination(cerealBox, blue_bin), True)
    problem.set_initial_value(Destination(apple, green_bin), True)
    problem.set_initial_value(Destination(orange, green_bin), True)
    problem.set_initial_value(Destination(longGlass, purple_bin), True)
    problem.set_initial_value(Destination(glass, purple_bin), True)


    # need to define rewards for each recycling
    problem.set_initial_value(Reward(duck, orange_bin), 10)
    problem.set_initial_value(Reward(board, orange_bin), 90)
    problem.set_initial_value(Reward(cardboardBox, blue_bin), 12)
    problem.set_initial_value(Reward(cerealBox, blue_bin), 33)
    problem.set_initial_value(Reward(apple, green_bin), 1)
    problem.set_initial_value(Reward(orange, green_bin), 2)
    problem.set_initial_value(Reward(longGlass, purple_bin), 32)
    problem.set_initial_value(Reward(glass, purple_bin), 27)

    problem.set_initial_value(robot_at_item(robot, duck), True)
    #problem.add_goal(InBin(duck, orange_bin))


    print(problem.goals)

    problem.add_quality_metric(up.model.metrics.MaximizeExpressionOnFinalState(Reward_robot()))

    # Solve the problem with TAMER
    with OneshotPlanner(name='aries') as planner:
        result = planner.solve(problem)
        plan = result.plan
        if plan is not None:
            print(f"{planner.name} returned:")
            print(plan)
        else:
            print("No plan found.")

    # Write the PDDL files
    writer = PDDLWriter(problem)
    writer.write_domain('domain_recycling.pddl')
    writer.write_problem('problem_recycling.pddl')


if __name__ == '__main__':
    main()
