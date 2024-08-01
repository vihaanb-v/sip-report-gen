
import random
import carla
import numpy as np
import cv2 as cv
import pandas as pd
from carla_gym.core.obs_manager.birdview.Gaze import Gaze
from carla_gym.utils.traffic_light import TrafficLightHandler
from carla_gym.core.obs_manager.birdview.chauffeurnet import ObsManager_Base
from carla_gym.core.obs_manager.birdview.chauffeurnet import tint, COLOR_ALUMINIUM_5, COLOR_ALUMINIUM_3, COLOR_MAGENTA, COLOR_MAGENTA_2, COLOR_YELLOW_2, COLOR_GREEN, COLOR_YELLOW, COLOR_RED, COLOR_BLUE, COLOR_CYAN, COLOR_WHITE
from .ActorTracker import ActorTracker
from collections import deque

from utils.error_measures import measure_detection_error, measure_perception_error, measure_image_difference


class ObsManager(ObsManager_Base):
    def __init__(self, obs_configs):
        super(ObsManager, self).__init__(obs_configs)
        self.gt_history_queue = deque(maxlen=20)
        self.gt_history_idx = self._history_idx.copy()
        
        if 'driver' in obs_configs:
            self.driver_type = obs_configs['driver']
    
    def _define_obs_space(self):
        return super()._define_obs_space()
    
    def attach_ego_vehicle(self, parent_actor):
        self.gaze = Gaze(parent_actor.vehicle, self.driver_type)
        self._tracker = ActorTracker(parent_actor.vehicle, self.gaze)
        return super().attach_ego_vehicle(parent_actor)
    
    def _get_history_masks(self, M_warp):
        return super()._get_history_masks(M_warp)
    
    def _get_gt_history_masks(self, M_warp):
        qsize = len(self.gt_history_queue)
        vehicle_masks, walker_masks, tl_green_masks, tl_yellow_masks, tl_red_masks, stop_masks = [], [], [], [], [], []
        for idx in self.gt_history_idx:
            idx = max(idx, -1 * qsize)

            vehicles, walkers, tl_green, tl_yellow, tl_red, stops = self.gt_history_queue[idx]

            vehicle_masks.append(self._get_mask_from_actor_list(vehicles, M_warp))
            walker_masks.append(self._get_mask_from_actor_list(walkers, M_warp))
            tl_green_masks.append(self._get_mask_from_stopline_vtx(tl_green, M_warp))
            tl_yellow_masks.append(self._get_mask_from_stopline_vtx(tl_yellow, M_warp))
            tl_red_masks.append(self._get_mask_from_stopline_vtx(tl_red, M_warp))
            stop_masks.append(self._get_mask_from_actor_list(stops, M_warp))

        return vehicle_masks, walker_masks, tl_green_masks, tl_yellow_masks, tl_red_masks, stop_masks
    
    def _get_mask_from_stopline_vtx(self, stopline_vtx, M_warp):
        return super()._get_mask_from_stopline_vtx(stopline_vtx, M_warp)
    
    def _get_mask_from_actor_list(self, actor_list, M_warp):
        return super()._get_mask_from_actor_list(actor_list, M_warp)
    
    def _get_warp_transform(self, ev_loc, ev_rot):
        return super()._get_warp_transform(ev_loc, ev_rot)
    
    def _world_to_pixel(self, location, projective=False):
        return super()._world_to_pixel(location, projective)
    
    def _world_to_pixel_width(self, width):
        return super()._world_to_pixel_width(width)
    
    def clean(self):
        return super().clean()
    
    
    # def set_spectator(self, carla_vehicle):
    #     spec_location = carla_vehicle.get_location()
    #     spec_location.z += 80
    #     spec_rotation = carla_vehicle.get_transform().rotation
    #     spec_rotation.pitch = -90
    #     spec_rotation.roll = 0
    #     spec_rotation.yaw = spec_rotation.yaw
    #     self.spectator.set_transform(carla.Transform(spec_location, spec_rotation))
    #     return 
    
    def get_observation(self):
        
        ev_transform = self._parent_actor.vehicle.get_transform()
        ev_loc = ev_transform.location
        ev_rot = ev_transform.rotation
        ev_bbox = self._parent_actor.vehicle.bounding_box
        snap_shot = self._world.get_snapshot()
        
        self.set_spectator(self._parent_actor.vehicle)

        def is_within_distance(w):
            c_distance = abs(ev_loc.x - w.location.x) < self._distance_threshold \
                and abs(ev_loc.y - w.location.y) < self._distance_threshold \
                and abs(ev_loc.z - w.location.z) < 8.0
            c_ev = abs(ev_loc.x - w.location.x) < 1.0 and abs(ev_loc.y - w.location.y) < 1.0
            return c_distance and (not c_ev)

        vehicle_bbox_list = self._world.get_level_bbs(carla.CityObjectLabel.Vehicles)
        walker_bbox_list = self._world.get_level_bbs(carla.CityObjectLabel.Pedestrians)
        
        if self._scale_bbox:
            gt_vehicles = self._get_surrounding_actors(vehicle_bbox_list, is_within_distance, 1.0)
            gt_walkers = self._get_surrounding_actors(walker_bbox_list, is_within_distance, 2.0)
        else:
            gt_vehicles = self._get_surrounding_actors(vehicle_bbox_list, is_within_distance)
            gt_walkers = self._get_surrounding_actors(walker_bbox_list, is_within_distance)

        tl_green = TrafficLightHandler.get_stopline_vtx(ev_loc, 0)
        tl_yellow = TrafficLightHandler.get_stopline_vtx(ev_loc, 1)
        tl_red = TrafficLightHandler.get_stopline_vtx(ev_loc, 2)
        stops = self._get_stops(self._parent_actor.criteria_stop)
        
        M_warp = self._get_warp_transform(ev_loc, ev_rot)

        self.gt_history_queue.append((gt_vehicles, gt_walkers, tl_green, tl_yellow, tl_red, stops)) # ground truth simulation
        gt_vehicle_masks, gt_walker_masks, gt_tl_green_masks, gt_tl_yellow_masks, gt_tl_red_masks, gt_stop_masks \
            = self._get_gt_history_masks(M_warp)
        
        gaze_direction = self.gaze.gaze_direction_tick()
        mod_vehicles, mod_walkers = self._tracker.track(gt_vehicles, gt_walkers, gaze_direction)
        
        self._history_queue.append((mod_vehicles, mod_walkers, tl_green, tl_yellow, tl_red, stops))
        
        vehicle_masks, walker_masks, tl_green_masks, tl_yellow_masks, tl_red_masks, stop_masks \
            = self._get_history_masks(M_warp)

        # road_mask, lane_mask
        road_mask = cv.warpAffine(self._road, M_warp, (self._width, self._width)).astype(np.bool)
        lane_mask_all = cv.warpAffine(self._lane_marking_all, M_warp, (self._width, self._width)).astype(np.bool)
        lane_mask_broken = cv.warpAffine(self._lane_marking_white_broken, M_warp,
                                         (self._width, self._width)).astype(np.bool)

        # route_mask
        route_mask = np.zeros([self._width, self._width], dtype=np.uint8)
        route_in_pixel = np.array([[self._world_to_pixel(wp.transform.location)]
                                   for wp, _ in self._parent_actor.route_plan[0:80]])
        route_warped = cv.transform(route_in_pixel, M_warp)
        cv.polylines(route_mask, [np.round(route_warped).astype(np.int32)], False, 1, thickness=16)
        route_mask = route_mask.astype(np.bool)

        # ev_mask
        ev_mask = self._get_mask_from_actor_list([(ev_transform, ev_bbox.location, ev_bbox.extent)], M_warp)
        ev_mask_col = self._get_mask_from_actor_list([(ev_transform, ev_bbox.location,
                                                       ev_bbox.extent*self._scale_mask_col)], M_warp)

        # render
        image = self.create_rendered_image(vehicle_masks, walker_masks, 
                                           tl_green_masks, tl_yellow_masks, tl_red_masks, 
                                           stop_masks, road_mask, lane_mask_all, lane_mask_broken, 
                                           route_mask, ev_mask)
        image_org = self.create_rendered_image(gt_vehicle_masks, gt_walker_masks,
                                               gt_tl_green_masks, gt_tl_yellow_masks, gt_tl_red_masks,
                                               gt_stop_masks, road_mask, lane_mask_all, lane_mask_broken,
                                               route_mask, ev_mask)

        # masks
        c_road = road_mask * 255
        c_route = route_mask * 255
        c_lane = lane_mask_all * 255
        c_lane[lane_mask_broken] = 120

        # masks with history
        c_tl_history = []
        for i in range(len(self._history_idx)):
            c_tl = np.zeros([self._width, self._width], dtype=np.uint8)
            c_tl[tl_green_masks[i]] = 80
            c_tl[tl_yellow_masks[i]] = 170
            c_tl[tl_red_masks[i]] = 255
            c_tl[stop_masks[i]] = 255
            c_tl_history.append(c_tl)

        c_vehicle_history = [m*255 for m in vehicle_masks]
        c_walker_history = [m*255 for m in walker_masks]

        masks = np.stack((c_road, c_route, c_lane, *c_vehicle_history, *c_walker_history, *c_tl_history), axis=2)
        masks = np.transpose(masks, [2, 0, 1])

        # error measures
        detection_error =  measure_detection_error(gt_vehicles, gt_walkers, mod_vehicles, mod_walkers) # ratio of the number of detected vehicles and walkers with the ground truth
        approximation_error = measure_perception_error(gt_vehicles, gt_walkers, mod_vehicles, mod_walkers) # compare the displacement error of detected vehicles and walkers with the ground truth
        
        image_diff = measure_image_difference(image_org, image)
        # print('detection error: ', detection_error, ' approximation error: ', approximation_error, ' image difference: ', image_diff)


        obs_dict = {'rendered': image, 'image_original': image_org, 'masks': masks, 
                    'gaze_direction': gaze_direction, 'detection_error': detection_error, 'approximation_error': approximation_error, 'image_difference': image_diff}

        self._parent_actor.collision_px = np.any(ev_mask_col & (walker_masks[-1] | vehicle_masks[-1]))
        if self._parent_actor.collision_px:
            print('collision detected')
        return obs_dict

    def update_history_idx(self, nAgent, base_nAgent):
        if nAgent > base_nAgent:
            subtract = nAgent - base_nAgent
            self._history_idx =  - subtract + np.array(self.gt_history_idx)
        pass


    def create_rendered_image(self, vehicle_masks, walker_masks, 
                              tl_green_masks, tl_yellow_masks, tl_red_masks, 
                              stop_masks, road_mask, lane_mask_all, lane_mask_broken, 
                              route_mask, ev_mask, len_history_idx=4):
        image = np.zeros([self._width, self._width, 3], dtype=np.uint8)
        image[road_mask] = COLOR_ALUMINIUM_5
        image[route_mask] = COLOR_ALUMINIUM_3
        image[lane_mask_all] = COLOR_MAGENTA
        image[lane_mask_broken] = COLOR_MAGENTA_2

        h_len = len_history_idx - 1
        for i, mask in enumerate(stop_masks):
            image[mask] = tint(COLOR_YELLOW_2, (h_len-i)*0.2)
        for i, mask in enumerate(tl_green_masks):
            image[mask] = tint(COLOR_GREEN, (h_len-i)*0.2)
        for i, mask in enumerate(tl_yellow_masks):
            image[mask] = tint(COLOR_YELLOW, (h_len-i)*0.2)
        for i, mask in enumerate(tl_red_masks):
            image[mask] = tint(COLOR_RED, (h_len-i)*0.2)

        for i, mask in enumerate(vehicle_masks):
            image[mask] = tint(COLOR_BLUE, (h_len-i)*0.2)
        for i, mask in enumerate(walker_masks):
            image[mask] = tint(COLOR_CYAN, (h_len-i)*0.2)

        image[ev_mask] = COLOR_WHITE
        return image
    
    
