from Boat import *
from utils import *

latch_names = ["bow_male", "starboard_male_top", "starboard_male_bottom",
            "stern_female", "port_female_top", "port_female_bottom"]

def latch_boats(boat1, latch1, boat2, latch2):
    if (boat1.latches[latch1] != None) or (boat2.latches[latch2] != None):
        print("Both latches must currently be empty in order to latch")
        return False

    if ("_male" in latch1 and "_male" in latch2) or ("_female" in latch1 and "_female" in latch2):
        print("Invalid latch, must have one female and one male latching mechanisms")
        return False

    boat1.latch(boat2, latch1)
    boat2.latch(boat1, latch2)
    return True

def unlatch_boats(boat1, latch1, boat2, latch2):
    boat1.unlatch(latch1)
    boat2.unlatch(latch2)
    return True

# Determines if given boat configuration is valid (i.e. no overlaps), assumes that there 
# are only male to female connections and no two boats are attached to the same latch
def is_valid_configuration(boats):
    visited_boats = set([])
    for parent_boat in boats:
        grid = {}
        boat_locations = {}
        visited_coordinator = False
        if parent_boat.boat_id in visited_boats:
            continue
        boat_queue = [parent_boat]
        while len(boat_queue) > 0:
            boat = boat_queue.pop(0)
            if boat.coordinator:
                visited_coordinator = True
            if len(grid.keys()) == 0:
                grid[(0,0)] = boat.boat_id
                grid[(0,1)] = boat.boat_id
                boat_locations[boat.boat_id] = ((0,0),(0,1))

            for latch_name in latch_names:
                child_boat = boat.latches[latch_name]
                if child_boat == None: 
                    continue
                if child_boat.boat_id in visited_boats:
                    continue
                boat_queue.append(child_boat)
                for k, v in child_boat.latches.iteritems():
                    if v != None:
                        if v.boat_id == boat.boat_id:
                            child_latch_name = k
                child_boat_cell1, child_boat_cell2, is_valid = boat_cells_from_parent(boat_locations[boat.boat_id], latch_name, child_latch_name)
                if not is_valid:
                    return False
                if child_boat_cell1 in grid:
                    print("Invalid boat configuration, boat:", grid[child_boat_cell1], "already occupies cell", child_boat_cell1)
                if child_boat_cell2 in grid:
                    print("Invalid boat configuration, boat:", grid[child_boat_cell2], "already occupies cell", child_boat_cell2)
                if child_boat_cell1 in grid or child_boat_cell2 in grid:
                    return False
                else:
                    grid[child_boat_cell1] = child_boat.boat_id
                    grid[child_boat_cell2] = child_boat.boat_id
                    boat_locations[child_boat.boat_id] = (child_boat_cell1, child_boat_cell2)
            visited_boats.add(boat.boat_id)
        if not visited_coordinator:
            print("Invalid boat configuration, there is no coordinator in this current set of attached boats")
            return False

    return True







        
