import graph_tool.all as gt

# This function will return a list of latch and unlatch steps in order to transform the initial configuration
# to the goal configuration
def shapeshift(initial_configuration, goal_configuration):
    planner_steps = []

    # This vertex property is created to keep track of what boats have already been accounted for in the shapeshift
    # this is necessary for setting the vertex filter so that we update the graph accordingly
    used_initial_nodes = initial_configuration.new_vertex_property('bool')
    for node in initial_configuration.vertices():
        used_initial_nodes[node] = 1
    used_goal_nodes = goal_configuration.new_vertex_property('bool')
    for node in goal_configuration.vertices():
        used_goal_nodes[node] = 1

    # This loop will construct the actual plan
    while True:
        initial_configuration.set_vertex_filter(used_initial_nodes)
        goal_configuration.set_vertex_filter(used_goal_nodes)
        # If there is only one vertex left in the initial config we are done
        # as that vertex is the coordinator and it is apart of both structures
        if len(list(initial_configuration.vertices())) == 1:
            break
        # find_overlap is the greedy algorithm that finds the maximum overlap between the init and goal
        current_steps = find_overlap(initial_configuration, goal_configuration)
        planner_steps.append(current_steps)
        # We now will update the nodes in the graph that have been used in the step so that we can update the filter
        for step in current_steps:
            used_initial_nodes[step[0]] = 0
            used_goal_nodes[step[1]] = 0

    return planner_steps
        
# This method performs all of the greedy overlap calculation and is the core of the algorithm
def find_overlap(current_configuration, goal_configuration):
    # Create Children and parent properties for their respective graphs
    current_children = current_configuration.new_vertex_property("vector<int>")
    goal_children = goal_configuration.new_vertex_property("vector<int>")
    
    current_parent = current_configuration.new_vertex_property("int")
    goal_parent = goal_configuration.new_vertex_property("int")
    
    #Perform a bfs to populate the children and parent fields
    gt.bfs_search(current_configuration, current_configuration.vertex(0), 
               VisitorDistance("current", current_parent, current_children))
    gt.bfs_search(goal_configuration, goal_configuration.vertex(0), 
               VisitorDistance("goal", goal_parent, goal_children))
    
    # Initialize an empty list of overlapping boats. This list will contain tuples where the first element 
    matching = []
    max_overlap_size = 10000
    while len(matching) == 0:
        # Iterate through the leaf nodes in the current_configuration
        for potential_leaf in current_configuration.vertices():

            # Make sure we are only examining LEAFS from the breadth first search
            if len(current_children[potential_leaf]) > 0 or potential_leaf == 0:
                continue
            # Now iterate through all of the roots in the goal (direct connection to coordinator)
            for potential_root in goal_configuration.vertices():
                #construct grid data structure to also check for valid overlaps
                grid_locations = {}
                grid_locations[potential_leaf] = ((0,0),(0,1))
                # Make sure we are only examining ROOTS
                if goal_parent[potential_root] != 0 or potential_root == 0:
                    continue
                stack_current = [potential_leaf]
                stack_goal = [potential_root]
                current_visited = set([potential_leaf])
                goal_visited = set([potential_root])
                current_overlap = []
                while len(stack_current) != 0:
                    current_node = stack_current.pop()
                    current_node_edges = [x for x in current_node.out_edges() if x.target() != 0 and x.target() not in current_visited]
                    current_goal = stack_goal.pop()
                    current_goal_edges = [x for x in current_goal.out_edges() if x.target() != 0 and x.target() not in goal_visited]
                    current_overlap.append((current_node, current_goal))
                    for current_node_edge in current_node_edges:
                        for current_goal_edge in current_goal_edges:
                            if (current_configuration.edge_properties["connection_type"][current_node_edge] == 
                            goal_configuration.edge_properties["connection_type"][current_goal_edge]):
                                print(max_overlap_size)
                                if len(current_overlap) < max_overlap_size-2:
                                    stack_current.append(current_node_edge.target())
                                    stack_goal.append(current_goal_edge.target())
                                    current_visited.add(current_node_edge.target())
                                    goal_visited.add(current_goal_edge.target())
                                    new_grid_location = determine_new_grid_location(
                                        current_configuration.edge_properties["connection_type"][current_node_edge], grid_locations[current_node])
                                    grid_locations[current_node_edge.target()] = new_grid_location
                if len(current_overlap) > len(matching):
                    if len(current_overlap) <= 2:
                        matching = current_overlap
                    elif valid_overlap(grid_locations):
                        matching = current_overlap
                    else:
                        max_overlap_size = len(current_overlap)
    return matching

# return the new grid location for the current boat based on the geometry from the edge type
def determine_new_grid_location(edge_type, parent_location):
    point1,point2 = parent_location
    x0,y0 = point1
    x1,y1 = point2
    if edge_type == 1:
        return ((x0+1,y0),(x1+1,y1))
    if edge_type == 2:
        return ((x0,y0+2),(x1,y1+2))
    if edge_type == 3:
        return ((x0-1,y0),(x1-1,y1))
    if edge_type == 4:
        return ((x0,y0-2),(x1,y1-2))

# This method determines if the current overlapped vertices are valid with respect to the geometric constraints
def valid_overlap(grid_locations):
    num_boats = len(grid_locations)
    grid = [[0 for _ in range(2*num_boats)] for _ in range(2*num_boats)]
    # build the mapping grid of where the boats occupy
    for boat in grid_locations:
        grid[grid_locations[boat][0][0]][grid_locations[boat][0][1]] = boat
        grid[grid_locations[boat][1][0]][grid_locations[boat][1][1]] = boat

    for i in range(2*num_boats):
        vertical_checker = False
        horizontal_checker = False
        for j in range(2*num_boats):
            if j != 2*num_boats:
                if grid[i][j] != 0 and grid[i][j+1] != 0:
                    vertical_checker = True
                elif vertical_checker == True:
                    return False
            if i != 2*num_boats:
                if grid[i][j] != 0 and grid[i+1][j] != 0:
                    horizontal_checker = True
                elif horizontal_checker == True:
                    return False
    return True


# This class handles building the parent and children property maps
class VisitorDistance(gt.BFSVisitor):

    def __init__(self, name, parent, children):
        self.name = name
        self.parent = parent
        self.children = children

    def tree_edge(self, e):
        self.parent[e.target()] = e.source()
        self.children[e.source()].append(e.target())
    