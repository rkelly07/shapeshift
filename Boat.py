"""
Boat Class for shapeshifting algorithm implementation
"""

class Boat:

    def __init__(self, boat_id, coordinator):
        self.boat_id = boat_id
        self.coordinator = coordinator
        self.latches = {"bow_male": None,
        "starboard_male_top": None,
        "starboard_male_bottom": None,
        "stern_female": None,
        "port_female_top": None,
        "port_female_bottom": None}


    def latch(self, latching_boat, latch_location):
        self.latches[latch_location] = latching_boat

    def unlatch(self, latch_location):
        self.latches[latch_location] = Noned


