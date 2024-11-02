import heapq

def compute_optimal_plan(locations, rewards):
    general_speed_m_s = 8 * 0.05  # Speed in m/s

    bin_locations = {
        'orange_bin': [0, 0.4],
        'purple_bin': [-1, 0.4],
        'blue_bin': [-2, 0.4],
        'green_bin': [-3, 0.4]
    }
    locations.update(bin_locations)
    # Function to calculate travel duration between two locations
    def calculate_duration(loc1, loc2):
        return (abs(loc1[0] - loc2[0]) + abs(loc1[1] - loc2[1])) / general_speed_m_s

    # Graph node to represent each action
    class ActionNode:
        def __init__(self, action_type, location, item=None, bin=None, parent=None, cost=0, reward=0, duration=0,
                     items_collected=None):
            self.action_type = action_type  # Action type
            self.location = location  # Current location
            self.item = item  # Item associated with this action
            self.bin = bin  # Bin associated with this action
            self.parent = parent  # Parent node to trace back path
            self.cost = cost  # Total duration cost up to this action
            self.reward = reward  # Total reward collected up to this action
            self.duration = duration  # Duration of this action
            # Track items already recycled to avoid duplicate recycling
            self.items_collected = items_collected or set()

        def __lt__(self, other):
            # Prioritize nodes by cost-reward tradeoff
            return (self.cost - self.reward) < (other.cost - other.reward)

    # Initialize the starting node
    start_node = ActionNode('start', location='green_bin', cost=0)

    # Priority queue for A* search
    pq = []
    heapq.heappush(pq, (0, start_node))  # (priority, node)

    visited = set()
    max_duration = 100  # Duration limit for the entire plan
    best_plan = None
    best_reward = 0

    # A* search through action nodes
    while pq:
        _, current = heapq.heappop(pq)

        # Stop if we've exceeded the duration limit
        if current.cost > max_duration:
            continue

        # Mark this node as visited
        state = (current.action_type, current.location, current.item, frozenset(current.items_collected))
        visited.add(state)

        # Update the best plan if current reward is the highest
        if current.reward > best_reward:
            best_reward = current.reward
            best_plan = current

        # Generate next actions based on current action type
        if current.action_type == 'start' or current.action_type == 'place_in_bin':
            # Move to item actions for all available items
            for item, item_loc in locations.items():
                if item not in current.items_collected and item not in bin_locations:
                    duration = calculate_duration(locations[current.location], item_loc)
                    next_node = ActionNode('move_to_item', item, item=item, parent=current,
                                           cost=current.cost + duration, reward=current.reward,
                                           duration=duration, items_collected=current.items_collected)
                    if (next_node.action_type, next_node.location, next_node.item,
                        frozenset(next_node.items_collected)) not in visited:
                        heapq.heappush(pq, (next_node.cost, next_node))

        elif current.action_type == 'move_to_item':
            # Pick up action
            next_node = ActionNode('pick_up', current.location, item=current.item, parent=current,
                                   cost=current.cost + 5, reward=current.reward, duration=5,
                                   items_collected=current.items_collected)
            if (next_node.action_type, next_node.location, next_node.item,
                frozenset(next_node.items_collected)) not in visited:
                heapq.heappush(pq, (next_node.cost, next_node))

        elif current.action_type == 'pick_up':
            # Move to bin actions
            for bin_name, bin_loc in bin_locations.items():
                if current.item in rewards.get(bin_name, {}):  # Item must match bin
                    duration = calculate_duration(locations[current.location], bin_loc)
                    next_node = ActionNode('move_to_bin', bin_name, item=current.item, bin=bin_name,
                                           parent=current, cost=current.cost + duration, reward=current.reward,
                                           duration=duration, items_collected=current.items_collected)
                    if (next_node.action_type, next_node.location, next_node.item,
                        frozenset(next_node.items_collected)) not in visited:
                        heapq.heappush(pq, (next_node.cost, next_node))

        elif current.action_type == 'move_to_bin':
            # Place in bin action and collect reward
            reward = rewards[current.bin].get(current.item, 0)
            next_items_collected = current.items_collected | {current.item}  # Add item to collected items
            next_node = ActionNode('place_in_bin', current.location, item=current.item, bin=current.bin, parent=current,
                                   cost=current.cost + 1, reward=current.reward + reward,
                                   duration=1, items_collected=next_items_collected)
            if (next_node.action_type, next_node.location, next_node.item, frozenset(next_node.items_collected)) not in visited:
                heapq.heappush(pq, (next_node.cost, next_node))

    # Reconstruct the best path
    def reconstruct_path(node):
        path = []
        total_duration = 0
        while node:
            path.append(f"{node.action_type} (item: {node.item}, bin: {node.bin}, duration: {node.duration} sec)")
            total_duration += node.duration
            node = node.parent
        return path[::-1], total_duration

    # Output the best path, reward, and total duration
    if best_plan:
        print("Best Path:")
        path, total_duration = reconstruct_path(best_plan)
        for action in path:
            print(action)
        #print(f"Total Reward: {best_reward}")
        #print(f"Total Duration: {total_duration} sec")
    else:
        print("No valid plan found within the duration limit.")

    return path


# plan = compute_optimal_plan(locations, rewards)
# print(plan)