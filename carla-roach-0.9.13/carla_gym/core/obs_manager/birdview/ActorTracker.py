import carla
import numpy as np
from .ActorProcessor import ActorProcessor
from .ActorTrackerUtils import ActorTrackerUtils

red = carla.Color(255, 0, 0)
green = carla.Color(0, 255, 0)
blue = carla.Color(47, 210, 231)
cyan = carla.Color(0, 255, 255)
yellow = carla.Color(255, 255, 0)
orange = carla.Color(255, 162, 0)
white = carla.Color(255, 255, 255)


class ActorTracker:
    def __init__(self, egoVehicle, gaze, forget_time=1.0):

        self.egoVehicle = egoVehicle
        self.forgetting_threshold = forget_time
        self.world = self.egoVehicle.get_world()
        
        self.movingVehicle = {} # key - actor id, value - latest memory of the vehicle both for exact update and approximate update
        self.pedestrian = {} # key - actor id, value - latest memory of the pedestrian both for exact update and approximate update
        self.actor_processor = ActorProcessor(self.world, gaze, self.pedestrian, self.movingVehicle)
        self.staticVehiclePolygons = self.get_static_vehicle_polygons_list()
        pass
    
    def get_static_vehicle_polygons_list(self):
        vehicle_bbox_list = self.world.get_level_bbs(carla.CityObjectLabel.Vehicles)
        moving_vehicle_actors = self.world.get_actors().filter('vehicle.*')
        vehicle_actors_list = ActorTrackerUtils.create_actor_polygon_list(moving_vehicle_actors)  # dictionary of vehicle id and its polygon (shapely)
        vehicle_polygons = ActorTrackerUtils.carla_bbox_to_shapely_polygons(vehicle_bbox_list)  # converts the bbox to shapely polygons

        static_vehicle_polygons = []

        for poly in vehicle_polygons:
            is_static = True  # Assume the vehicle is static initially
            for vehicle_polygon in vehicle_actors_list:
                if poly.intersects(vehicle_polygon):
                    is_static = False  # The vehicle is not static since it intersects with a moving vehicle
                    break
            if is_static:
                static_vehicle_polygons.append(poly)
        return static_vehicle_polygons
    
    def filter_active_vehicle_bbpoly_list(self, bb_list):
        active_bb_list = []
        for bb in bb_list:
            is_static = False
            for static_poly in self.staticVehiclePolygons:
                if bb.intersects(static_poly):
                    is_static = True
                    break
            if not is_static:
                active_bb_list.append(bb)
        return active_bb_list

    
    # actors are a list of tuples (transform, loc, extent) this actors are inside the birdeve view limit
    # loc is always 0, 0, 0 for some reason
    def track(self, vehicles, walkers, gaze_direction):
        curTimestamp = self.world.get_snapshot().timestamp
        
        vehicle_polygons = ActorTrackerUtils.convert_actor_tuple_to_shapely_polygons(vehicles)
        active_vehicle_polygons = self.filter_active_vehicle_bbpoly_list(vehicle_polygons)
        
        pedestrian_polygons = ActorTrackerUtils.convert_actor_tuple_to_shapely_polygons(walkers)
        
        vehicle_bbpoly_inside_gaze, vehicle_bbpoly_outside_gaze = self.actor_processor.process_vehicles(active_vehicle_polygons, gaze_direction)
        pedestrian_bbpoly_inside_gaze, pedestrian_bbpoly_outside_gaze = self.actor_processor.process_pedestrians(pedestrian_polygons, gaze_direction)
        
        # self.draw_list_of_polygons(vehicle_bbpoly_inside_gaze + pedestrian_bbpoly_inside_gaze, color=green)
        # self.draw_list_of_polygons(vehicle_bbpoly_outside_gaze + pedestrian_bbpoly_outside_gaze, color=red)
        
        # self.forget_actor_after_time(self.forgetting_threshold)
        
        vehicle_shapely_polygons = self.get_all_polygons_from_dict(self.movingVehicle)
        pedestrian_shapely_polygons = self.get_all_polygons_from_dict(self.pedestrian)
        
        # remove out of the scope actors 
        gt_vehicle_ids = []
        for polygon in vehicle_polygons:
            actor_id = self.actor_processor.get_actor_id_from_polygon(polygon)
            if actor_id is not None:
                gt_vehicle_ids.append(actor_id)
        
        gt_pedesrian_ids = []
        for polygon in pedestrian_polygons:
            actor_id = self.actor_processor.get_actor_id_from_polygon(polygon)
            if actor_id is not None:
                gt_pedesrian_ids.append(actor_id)
        
        # out of scope actors
        out_of_scope_vehicles = set(self.movingVehicle.keys()) - set(gt_vehicle_ids)
        out_of_scope_pedestrians = set(self.pedestrian.keys()) - set(gt_pedesrian_ids)
        
        # print('gt_vehicle_ids ', gt_vehicle_ids, ' gt_pedesrian_ids ', gt_pedesrian_ids)
        # print('out_of_scope_vehicles ', out_of_scope_vehicles, ' out_of_scope_pedestrians ', out_of_scope_pedestrians)

        # delete the out of scope actors
        for vehicle_id in out_of_scope_vehicles:
            self.movingVehicle.pop(vehicle_id)
        for pedestrian_id in out_of_scope_pedestrians:
            self.pedestrian.pop(pedestrian_id)

        updated_vehicle = ActorTrackerUtils.convert_shapely_polygons_to_actors_tuple(vehicle_shapely_polygons)
        updated_pedestrian = ActorTrackerUtils.convert_shapely_polygons_to_actors_tuple(pedestrian_shapely_polygons)
        
        # updated_vehicle = vehicles
        # updated_pedestrian = walkers
        
        # updated_vehicle = self.convert_shapely_polygons_to_actors_tuple(vehicle_polygons)
        # updated_pedestrian = self.convert_shapely_polygons_to_actors_tuple(pedestrian_polygons)
        
        # self.compare_bounding_boxes_list(vehicles, updated_vehicle)
        
        return updated_vehicle, updated_pedestrian
    

    def get_all_polygons_from_dict(self, actors_dict):
        polygons = []
        for actor_id, memory in actors_dict.items():
            polygons.append(memory.bb_polygon)
        return polygons

    def draw_list_of_polygons(self, polygons, color=carla.Color(255, 0, 0)):
        for poly in polygons:
            self.visualize_bb(poly, color)
        pass
    
    def visualize_bb(self, bbpoly, color):
        debug = self.world.debug
        # Extract polygon exterior coordinates
        exterior_coords = list(bbpoly.exterior.coords)

        # CARLA requires carla.Location objects to draw lines. Assuming z is constant for this example.
        z = 1  # Adjust the Z coordinate as needed for your application
        carla_locations = [carla.Location(x=coord[0], y=coord[1], z=z) for coord in exterior_coords]

        # Draw lines between consecutive points and also close the polygon by connecting the last and first points
        for i in range(len(carla_locations)):
            start_point = carla_locations[i]
            end_point = carla_locations[(i + 1) % len(carla_locations)]  # Wrap around to the first point
            debug.draw_line(begin=start_point, 
                            end=end_point,
                            thickness=0.5,  # Adjust thickness as needed
                            color=color,  # RGBA color, here set to red
                            life_time=0.2)  # Time in seconds for how long the line should be visible
        pass
    
    
    def forget_actor_after_time(self, threshold=5.0):
        remove_vehicle = []
        remove_pedestrian = []
        curTimestamp = self.world.get_snapshot().timestamp
        
        for vehicle_id, memory in self.movingVehicle.items():
            # print('how old ', memory.how_old)
            elapsed_time = (curTimestamp.elapsed_seconds - memory.last_update.elapsed_seconds)
            if elapsed_time > threshold:
                remove_vehicle.append(vehicle_id)
        
        for pedestrian_id, memory in self.pedestrian.items():
            # print('how old ', memory.how_old)
            elapsed_time = (curTimestamp.elapsed_seconds - memory.last_update.elapsed_seconds)
            if elapsed_time > threshold:
                remove_pedestrian.append(pedestrian_id)
        
        for vehicle_id in remove_vehicle:
            self.movingVehicle.pop(vehicle_id)
        
        for pedestrian_id in remove_pedestrian:
            self.pedestrian.pop(pedestrian_id)
        pass
    
    

    
    def compare_bounding_boxes_list(self, actors_list1, actors_list2):
        # this function checks the differences between the bounding boxes of the actors
        # length needs to be the same for both lists
        if len(actors_list1) != len(actors_list2):
            raise ValueError("The lists must have the same length.")

        differences = []

        for i in range(len(actors_list1)):
            actor1 = actors_list1[i]
            actor2 = actors_list2[i]

            transform1, loc1, extent1 = actor1
            transform2, loc2, extent2 = actor2

            # Calculate the difference in location
            location_diff = np.sqrt((loc1.x - loc2.x)**2 + (loc1.y - loc2.y)**2 + (loc1.z - loc2.z)**2)

            # Calculate the differences in extents
            extent_diff_x = abs(extent1.x - extent2.x)
            extent_diff_y = abs(extent1.y - extent2.y)
            extent_diff_z = abs(extent1.z - extent2.z)

            # Calculate the differences in rotation (yaw, pitch, roll)
            yaw_diff = abs(transform1.rotation.yaw - transform2.rotation.yaw)
            pitch_diff = abs(transform1.rotation.pitch - transform2.rotation.pitch)
            roll_diff = abs(transform1.rotation.roll - transform2.rotation.roll)

            differences.append({
                'location_diff': location_diff,
                'extent_diff_x': extent_diff_x,
                'extent_diff_y': extent_diff_y,
                'extent_diff_z': extent_diff_z,
                'yaw_diff': yaw_diff,
                'pitch_diff': pitch_diff,
                'roll_diff': roll_diff,
            })

            print(f"Actor Pair {i+1}:")
            print(f"  Location Difference: {location_diff}")
            print(f"  Extent Differences: X={extent_diff_x}, Y={extent_diff_y}, Z={extent_diff_z}")
            print(f"  Rotation Differences: Yaw={yaw_diff}, Pitch={pitch_diff}, Roll={roll_diff}")
            print("")

        return differences







