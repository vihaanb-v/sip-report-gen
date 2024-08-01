

import carla
from shapely.geometry import Polygon
import math
import numpy as np

class ActorTrackerUtils:
    
    @staticmethod
    def create_actor_id_to_2D_polygon_dict(actor_list):
        # returns a dictionary of actor id and its polygon bounding box
        actors_dict = {}
        for actor in actor_list:
            bbox_wrt_world_3D = actor.bounding_box.get_world_vertices(actor.get_transform())
            bbox_wrt_world_2D = [carla.Location(x=v.x, y=v.y, z=0) for v in bbox_wrt_world_3D]
            
            polygon = Polygon([(v.x, v.y) for v in bbox_wrt_world_2D])
            actors_dict[actor.id] = polygon
            
        return actors_dict
    
    @staticmethod
    def create_actor_polygon_list(actor_list):
        # returns a list of polygon bounding box
        actor_polygon_list = []
        for actor in actor_list:
            bbox_wrt_world_3D = actor.bounding_box.get_world_vertices(actor.get_transform())
            bbox_wrt_world_2D = [carla.Location(x=v.x, y=v.y, z=0) for v in bbox_wrt_world_3D]
            
            polygon = Polygon([(v.x, v.y) for v in bbox_wrt_world_2D])
            actor_polygon_list.append(polygon)
        return actor_polygon_list
    
    @staticmethod
    def convert_actor_tuple_to_shapely_polygons(actors, debug=False):
        polygons = []
        areas = []  # List to store the areas of the bounding boxes # actors = list of tuple (transform, loc, extent)
        for actor_transform, bb_loc, bb_ext in actors:
            corners = [carla.Location(x=-bb_ext.x, y=-bb_ext.y),
                       carla.Location(x=bb_ext.x, y=-bb_ext.y),
                       carla.Location(x=bb_ext.x, y=bb_ext.y),
                       carla.Location(x=-bb_ext.x, y=bb_ext.y)]
            corners = [bb_loc + corner for corner in corners]
            corners = [actor_transform.transform(corner) for corner in corners]                  
            # convert corners to tuples (x, y)
            corners = [(corner.x, corner.y) for corner in corners]
    
            polygon = Polygon(corners)
            polygons.append(polygon)
            areas.append((bb_ext.x * 2) * (bb_ext.y * 2))  # Calculate and store the area of the bounding box
        if debug:
            for polygon, area in zip(polygons, areas):
                print("BBox Area:", area, " Shapely Area:", polygon.area)
        return polygons

    @staticmethod
    def convert_shapely_polygons_to_actors_tuple(polygons):
        actors = []

        for polygon in polygons:
            exterior_coords = list(polygon.exterior.coords[:-1])  # Exclude duplicate last point
            centroid = polygon.centroid

            # Vectorized calculation of side lengths and directions
            diffs = [(exterior_coords[i+1][0] - exterior_coords[i][0], exterior_coords[i+1][1] - exterior_coords[i][1]) for i in range(len(exterior_coords)-1)]
            lengths = [math.sqrt(dx**2 + dy**2) for dx, dy in diffs]
            max_length_index = lengths.index(max(lengths))  # Index of the longest side
            yaw = math.degrees(math.atan2(diffs[max_length_index][1], diffs[max_length_index][0])) % 360

            width = min(lengths)
            length = max(lengths)

            loc = carla.Location(x=centroid.x, y=centroid.y)
            rot = carla.Rotation(pitch=0, yaw=yaw, roll=0)
            extent = carla.Vector3D(x=length / 2, y=width / 2)

            actors.append((carla.Transform(loc, rot), carla.Location(x=0, y=0), extent))

        return actors
    
    @staticmethod
    def carla_bbox_to_shapely_polygons(bbox_list):
        polygons = []
        for bbox in bbox_list:
            location, extent, rotation = bbox.location, bbox.extent, bbox.rotation
            yaw_rad = np.radians(rotation.yaw)
            # Calculate the corners of the bounding box
            corners = [(extent.x, extent.y), (-extent.x, extent.y), (-extent.x, -extent.y), (extent.x, -extent.y)]
            # Rotate the corners and translate them to the bounding box's location
            rotated_corners = []
            for x, y in corners:
                # Rotate each corner
                rotated_x = x * math.cos(yaw_rad) - y * math.sin(yaw_rad)
                rotated_y = x * math.sin(yaw_rad) + y * math.cos(yaw_rad)
                # Translate each corner
                translated_x = rotated_x + location.x
                translated_y = rotated_y + location.y
                rotated_corners.append((translated_x, translated_y))
            # Create a Shapely polygon from the rotated and translated corners
            polygon = Polygon(rotated_corners)
            polygons.append(polygon)
        return polygons
    
    
    def interpolate_polygons(poly1, poly2, t):
        
        if len(poly1.exterior.coords) != len(poly2.exterior.coords):
            raise ValueError("Polygons must have the same number of vertices.")
        
        # print("Poly1: ", list(poly1.exterior.coords))
        # print("Poly2: ", list(poly2.exterior.coords))
        # Extract coordinates
        coords1 = np.array(poly1.exterior.coords)
        coords2 = np.array(poly2.exterior.coords)
        # Linear interpolation
        interpolated_coords = (1 - t) * coords1 + t * coords2
        
        # Create a new interpolated polygon
        return Polygon(interpolated_coords)
    
    
    @staticmethod
    def convert_bb_to_actor_tuple(bbox_list, scale=None):
        actors = []
        for bbox in bbox_list:
            bb_loc = carla.Location()
            bb_ext = carla.Vector3D(bbox.extent)
            if scale is not None:
                bb_ext = bb_ext * scale
                bb_ext.x = max(bb_ext.x, 0.8)
                bb_ext.y = max(bb_ext.y, 0.8)
            actors.append((carla.Transform(bbox.location, bbox.rotation), bb_loc, bb_ext))
        return actors