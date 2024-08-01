import carla
import math
import numpy as np

from shapely.geometry import LineString
from shapely import geometry
from shapely.geometry import Point

from enum import Enum
from config.agent.ppo.obs_configs.gaze_settings import GazeDirection, Gaze_Settings, driver

class ManeuverType(Enum):
    LANEFOLLOW = 1
    VEHICLE_FOLLOW = 2
    LANECHANGE_LEFT = 3
    LANECHANGE_RIGHT = 4

# class GazeDirection(Enum):
#     """
#     The gaze direction.
#     """
#     LEFTBLINDSPOT = 0       # 0.04
#     LEFTMIRROR = 1          # 0.08
#     LEFT = 2                # 0.1
#     CENTER = 3              # 0.5
#     RIGHT = 4               # 0.1
#     RIGHTMIRROR = 5         # 0.08
#     RIGHTBLINDSPOT = 6      # 0.04
#     BACK = 7                # 0.06
#     pass



# Gaze_Settings = {
#     GazeDirection.CENTER: (0, 30, 40, red),
#     GazeDirection.LEFT:  (70, 70, 35, green),
#     GazeDirection.RIGHT:  (-70, 70, 35, blue),
#     GazeDirection.LEFTBLINDSPOT:  (130, 5, 5, green),
#     GazeDirection.RIGHTBLINDSPOT:  (-130, 5, 5, blue),
#     GazeDirection.LEFTMIRROR:  (159.9, 20, 10, green),
#     GazeDirection.RIGHTMIRROR:  (-159.9, 20, 10, blue),
#     GazeDirection.BACK:  (179, 45, 20, red),
# }

class Gaze():
    def __init__(self, vehicle, driver_type='normal'):
        
        self.driver_type = driver_type
        self.name = 'Gaze Module'
        self.tick_counter = 0
        self.tick_frequency = 10

        self.vehicle = vehicle
        self.gaze_settings = Gaze_Settings

        self.gaze_direction_list = list(GazeDirection)
        self.gaze_direction = GazeDirection.CENTER
        self.gaze_probability = driver[driver_type][0]
        self.gaze_frequency = driver[driver_type][1]
        pass
    

    def filter_polygons_inside_gaze_direction(self, box_polygons, gaze_direction):

        # print('gaze direction ', gaze_direction)
        if gaze_direction not in self.gaze_settings.keys():
            raise ValueError('need to have gaze direction')
        self.gaze_direction = gaze_direction

        gaze_settings = self.gaze_settings[self.gaze_direction]
        triangle_corners = self.find_gaze_triangle_corners(self.vehicle, gaze_settings)
        gaze_triangle_polygon = geometry.Polygon([[p.x, p.y] for p in triangle_corners])

        # check if gaze triangle intersects with bounding box
        bb_polygon_inside_gaze = []
        for bbox in box_polygons:
            if gaze_triangle_polygon.intersects(bbox):
                # print('gaze triangle intersects with bounding box')
                bb_polygon_inside_gaze.append(bbox)
        return bb_polygon_inside_gaze

    def gaze_direction_tick(self, maneuver_type=ManeuverType.LANEFOLLOW):
        self.tick_counter += 1
        gaze_direction = None
        if self.tick_counter == self.tick_frequency:
            self.tick_counter = 0
            self.tick_frequency = np.random.randint(self.gaze_frequency[0], self.gaze_frequency[1])
            val = self.get_gaze_distribution(maneuver_type)
            gaze_direction = self.gaze_direction_list[val]
        else:
            gaze_direction = self.gaze_direction
        self.draw_gaze_triangle()
        return gaze_direction

    def get_gaze_direction(self):
        return self.gaze_direction

    # x = np.random.normal(3.5, 0.9, 100000) # lane follow
    # y = np.random.normal(3.5, 0.4, 100000) # vehicle follow

    def get_gaze_distribution(self, maneuver_type):
        # print('maneuver type ', maneuver_type, ' driver type ', self.driver_type)
        if maneuver_type == ManeuverType.LANEFOLLOW:
            # val = np.random.normal(3.5, 2, 1)
            val = np.random.choice(len(GazeDirection), 1, p = self.gaze_probability)[0]
            val = int(val)
            if self.check_valid_direction(val):
                return val
            else:
                return 3
        
        elif maneuver_type == ManeuverType.VEHICLE_FOLLOW:
            val = np.random.normal(3.5, 0.5, 1)
            val = int(val)
            if self.check_valid_direction(val):
                return val
            else:
                return 3
        
        elif maneuver_type == ManeuverType.LANECHANGE_RIGHT:
            val = np.random.lognormal(1, 1, 1)
            val = int(val)
            if self.check_valid_direction(val):
                return val
            else:
                return 1
        
        elif maneuver_type == ManeuverType.LANECHANGE_LEFT:
            val = np.random.lognormal(1, 1, 1)
            val = 6 - int(val)
            if self.check_valid_direction(val):
                return val
            else:
                return 5

        pass

    def check_valid_direction(self, val):
        if val < 0 or val > 6:
            return False
        return True


    def draw_gaze_triangle(self):
        # print('gaze direction ', self.gaze_direction)
        # print('gaze settings ', self.gaze_settings.keys())
        if self.gaze_direction not in self.gaze_settings.keys():
            raise ValueError('need to have gaze direction')
            return
        gaze_settings = self.gaze_settings[self.gaze_direction]
        
        debug = self.vehicle.get_world().debug
        
        triangle_corners = self.find_gaze_triangle_corners(self.vehicle, gaze_settings)

        # draw an arrow from the vehicle to the gaze direction point draw_hud_arrow(self, begin, end, thickness=0.1, arrow_size=0.1, color=(255,0,0), life_time=-1.0)
        # end = (triangle_corners[0] + triangle_corners[1])/2
        # debug.draw_arrow(begin=triangle_corners[2], end=triangle_corners[1], thickness=1, arrow_size=0.1, color=(0,0,255), life_time=0.2) 

        # for i in range(len(triangle_corners)):
        #     # print('triangle corners ', triangle_corners[i])
        #     debug.draw_line(begin=triangle_corners[i], 
        #                     end=triangle_corners[(i+1)%3],
        #                     thickness=0.2,
        #                     color=gaze_settings[3],
        #                     life_time=0.2)
        
        return triangle_corners

    def find_gaze_triangle_corners(self, vehicle, gaze_settings, height = 1):
        gaze_direction, view_angle, length, _ = gaze_settings
        view_angle = math.radians(view_angle)   # convert to radians
        # print(gaze_direction, view_angle, length, color)   

        vehicle_transform = vehicle.get_transform()
        vehicle_center = vehicle_transform.location
        vehicle_forward = vehicle_transform.get_forward_vector()

        cos = math.cos(gaze_direction)
        sin = math.sin(gaze_direction)
        newX = vehicle_forward.x * cos - vehicle_forward.y * sin
        newY = vehicle_forward.x * sin + vehicle_forward.y * cos

        direction_vector = carla.Vector3D(newX*length, newY*length, height)

        normalized_direction_vector = direction_vector.make_unit_vector()

        left_point = self.find_corner_point_of_triangle(height, view_angle, length, normalized_direction_vector)
        right_point = self.find_corner_point_of_triangle(height, -view_angle, length, normalized_direction_vector)

        left_point = vehicle_center + left_point
        right_point = vehicle_center + right_point
        end_point = vehicle_center + direction_vector

        return [right_point, left_point, vehicle_center]
    

    
    def find_corner_point_of_triangle(self, height, view_angle, length, normalized_direction_vector):
        cos_left = math.cos(view_angle/2)
        sin_left = math.sin(view_angle/2)
        left_point_x =  normalized_direction_vector.x * cos_left - normalized_direction_vector.y * sin_left
        left_point_y =  normalized_direction_vector.x * sin_left + normalized_direction_vector.y * cos_left
        left_point = carla.Vector3D(left_point_x*length, left_point_y*length, height)
        return left_point
    