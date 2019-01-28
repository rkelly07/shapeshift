# Given intial boat configurations and a goal configuration
# return the intermediate configurations in order to reach the goal
def shapeshift(init_configs, goal_config):
    current_config = None
    while init_configs != goal_config:
        if current_config == None:
            current_goal = goal_config
        else current_goal = goal_config - current_config
        current_size = 0
        current_isomorph_config = None
        current_index = None
        for i in range(len(init_configs)):
            boat_config = init_configs[i]
            isomorph_config, size = find_isomorphism(boat_config, current_goal)
            if size > old_size:
                current_isomorph_config = isomorph_config
                current_size = size
                current_index = i
        for i in range(len(init_configs)):
            if i != current_index:
                smart_melt(init_configs[i], init_configs[current_index], current_isomorph_config)
                del init_configs[current_index]
                break
        if current_config != None:
            current_config += current_isomorph_config
        else:
            current_config = current_isomorph_config

# Implement tree isomorphism alg from paper
def find_isomorphism(G, H):
    return

def smart_melt(base_config, meltable_config, persistent_config):
    return

        





