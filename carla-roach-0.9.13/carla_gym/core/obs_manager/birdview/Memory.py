




class Memory:
    def __init__(self, timestamp, bb_poly, velocity, last_update):
        self.timestamp = timestamp
        self.bb_polygon = bb_poly
        self.velocity_3D = velocity
        self.last_update = last_update
    
    @property
    def how_old(self):
        return self.timestamp.elapsed_seconds - self.last_update.elapsed_seconds

