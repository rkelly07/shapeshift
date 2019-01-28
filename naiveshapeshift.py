import graph_tool.all as gt

# This function will return a list of latch and unlatch steps in order to transform the initial configuration
# to the goal configuration
def shapeshift(initial_configuration, goal_configuration):
    planner_steps = []
    used_initial_nodes = initial_configuration.new_vertex_property('bool')
    for node in initial_configuration.vertices():
        used_initial_nodes[node] = 1
    used_goal_nodes = goal_configuration.new_vertex_property('bool')
    for node in goal_configuration.vertices():
        used_goal_nodes[node] = 1

    while True:
        initial_configuration.set_vertex_filter(used_initial_nodes)
        goal_configuration.set_vertex_filter(used_goal_nodes)

        if len(list(initial_configuration.vertices())) == 1:
            break
            
        current_steps = find_overlap(initial_configuration, goal_configuration)
        planner_steps.append(current_steps)
        
        for step in current_steps:
            used_initial_nodes[step[0]] = 0
            used_goal_nodes[step[1]] = 0

    return planner_steps
        
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
    # Iterate through the leaf nodes in the current_configuration
    for potential_leaf in current_configuration.vertices():
        # Make sure we are only examining leafs from the breadth first search
        if len(current_children[potential_leaf]) > 0 or potential_leaf == 0:
            continue
        # Now iterate through all of the roots in the goal (direct connection to coordinator)
        for potential_root in goal_configuration.vertices():
            # Make sure we are only examining roots
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
                            stack_current.append(current_node_edge.target())
                            stack_goal.append(current_goal_edge.target())
                            current_visited.add(current_node_edge.target())
                            goal_visited.add(current_goal_edge.target())
            if len(current_overlap) > len(matching):
                matching = current_overlap
    return matching

# This class handles building the parent and children property maps
class VisitorDistance(gt.BFSVisitor):

    def __init__(self, name, parent, children):
        self.name = name
        self.parent = parent
        self.children = children

    def tree_edge(self, e):
        self.parent[e.target()] = e.source()
        self.children[e.source()].append(e.target())
    