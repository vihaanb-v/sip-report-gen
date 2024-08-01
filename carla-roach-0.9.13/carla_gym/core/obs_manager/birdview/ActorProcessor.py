from shapely.affinity import translate
import numpy as np
from .ActorTrackerUtils import ActorTrackerUtils
from .Memory import Memory
from shapely.geometry import Polygon
import carla

def lerp(start, end, t):
    return start + (end - start) * t

class ActorProcessor():
    def __init__(self, world, gaze, pedestrian_dict, vehicle_dict) -> None:
        self.world = world
        self.gaze = gaze
        
        self.pedestrian = pedestrian_dict
        self.movingVehicle = vehicle_dict
        
        self.vehicle_actors = self.world.get_actors().filter('vehicle.*')
        self.pedestrian_actors = self.world.get_actors().filter('walker.*')
        
        pass

    def get_actor_id_from_polygon(self, bbpoly):

        vehicle_actors_dict = ActorTrackerUtils.create_actor_id_to_2D_polygon_dict(self.vehicle_actors)
        pedestrian_actors_dict = ActorTrackerUtils.create_actor_id_to_2D_polygon_dict(self.pedestrian_actors)
        
        # Checking for intersections with vehicle and pedestrian polygons
        for actor_id, actor_polygon in {**vehicle_actors_dict, **pedestrian_actors_dict}.items():
            if actor_polygon.intersects(bbpoly):
                return actor_id
        
        # print("No actor found with the given polygon")
        # Raise an exception if no actor found
        return None

    def _update_bb(self, bbpoly, _dict, inside_gaze):
        actor_id = self.get_actor_id_from_polygon(bbpoly)
        
        if actor_id is None:
            return
        curTimestamp = self.world.get_snapshot().timestamp
        
        if inside_gaze:
            velocity_3D = self.world.get_actor(actor_id).get_velocity()
            memory = Memory(curTimestamp, bbpoly, velocity_3D, curTimestamp)
            _dict[actor_id] = memory
        else:
            memory = _dict.get(actor_id)
            if memory:   
                elapsed_time = (curTimestamp.elapsed_seconds - memory.timestamp.elapsed_seconds)
                prev_bbox = memory.bb_polygon
                t = np.random.uniform(0, 0.2)
                new_bbox = ActorTrackerUtils.interpolate_polygons(prev_bbox, bbpoly, t)
                memory.bb_polygon = new_bbox
                memory.timestamp = curTimestamp
                # velocity_3D = memory.velocity_3D
                # displacement = (
                #     memory.velocity_3D.x * elapsed_time,
                #     memory.velocity_3D.y * elapsed_time
                # )
                # new_bbpoly = translate(memory.bb_polygon, xoff=displacement[0], yoff=displacement[1])
                # memory.bb_polygon = new_bbpoly
                # memory.timestamp = curTimestamp    
        pass
   
    def process_pedestrians(self, pedestrian_polygons, gaze_direction):
        
        pedestrian_bbpoly_inside_gaze = self.gaze.filter_polygons_inside_gaze_direction(pedestrian_polygons, gaze_direction)
        pedestrian_bbpoly_outside_gaze = [bb for bb in pedestrian_polygons if bb not in pedestrian_bbpoly_inside_gaze]
        
        for pedestrian_bbpoly in pedestrian_bbpoly_inside_gaze:
            self._update_bb(pedestrian_bbpoly, self.pedestrian, True)
        for pedestrian_bbpoly in pedestrian_bbpoly_outside_gaze:
            self._update_bb(pedestrian_bbpoly, self.pedestrian, False)
        return pedestrian_bbpoly_inside_gaze,pedestrian_bbpoly_outside_gaze

    def process_vehicles(self, active_vehicle_polygons, gaze_direction):
        
        vehicle_bbpoly_inside_gaze = self.gaze.filter_polygons_inside_gaze_direction(active_vehicle_polygons, gaze_direction)
        vehicle_bbpoly_outside_gaze = [bb for bb in active_vehicle_polygons if bb not in vehicle_bbpoly_inside_gaze]
        
        for vehicle_bbpoly in vehicle_bbpoly_inside_gaze:
            self._update_bb(vehicle_bbpoly, self.movingVehicle, True)
        for vehicle_bbpoly in vehicle_bbpoly_outside_gaze:
            self._update_bb(vehicle_bbpoly, self.movingVehicle, False)
            
        return vehicle_bbpoly_inside_gaze,vehicle_bbpoly_outside_gaze
