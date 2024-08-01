

- **__init __()**:
  - **self.vehicle** : A vehicle that spawned in carla world.
  - **world** : Carla world.
  - **self._map** : Map that is currently loaded in **world**.
  - **self._world** : **world** is reassigned to it. 
  - **self.criteria_blocked** : [**Blocked**](criteria/blocked.py)
  - **self.criteria_collision** : [**Collision**](criteria/collision.py)
  - **self.criteria_light** : [**RunRedLight**](criteria/run_red_light.py)
  - **self.criteria_encounter_light** : [**EncounterLight**](criteria/encounter_light.py)
  - **self.criteria_stop** : [**RunStopSign**](criteria/run_stop_sign.py)
  - **self.criteria_outside_route_lane** : [**OutsideRouteLane**](criteria/outside_route_lane.py)
  - **self.criteria_route_deviation** : [**RouteDeviation**](criteria/route_deviation.py)
  - **self._route_completed** : Route that is completed by the ego vehicle.
  - **self._route_length** : Total length of the planned route.
  - **self._target_transforms** : It is list of carla transforms along the route the ego vehicle must follow.
  - **self._planner** : It contains the instance of [**GlobalRoutePlanner**](navigation/global_route_planner.py)
  - **self._global_route** : It is a list of carla waypoint and [**RoadOption**](./navigation/map_utils.py). It tells the ego vehicle which decision to take based on the waypoint it is in.
  - **self._global_plan_gps** :
  - **self._global_plan_world_coord** :
  - **self._trace_route_to_global_target()** : In the for loop, **self._target_transforms** list is iterated and the transforms are converted to carla locations. Then, **trace_route()** method of **GlobalRoutePlanner** class is used to trace the route between consecutive locations converted from **self._target_transforms** list. But at first, route is traced between the current location of carla car and the first converted location item of **self._target_transforms**. **self._global_route** contains the complete traced route. **self._route_length** contains the length of the traced route in meter. This method is not for endless environment. I will add more later.
  - **self._spawn_transforms** : It contains carla transforms where a vehicle can be spawned. Every element is a pair of road id and carla transform. 
  - **self._endless** : It is a boolean variable that is true if the gym environment is [**EndlessEnv**](../../../envs/suites/endless_env.py).
  - If there is no carla transform in **self._target_transforms**, then it populated with **_add_random_target()** method until **self._route_length** is less than some predefined constant in meter. 
  - **self._last_route_location** contains current location of the carla vehicle.
  - **self.collision_px** :
- **_add_random_target()**:
  - In this method, we need to calculate two variables **last_target_loc** and **new_target_transform** in order to calculate the global route of the ego vehicle. 
  - If **self._target_transforms** is empty, then **last_target_loc** is the current location of the ego vehicle and **new_target_transform** is a carla transform, which is six meter ahead of **last_target_loc**. 
  - If **self._target_transforms** is not empty, then **last_target_loc** is carla location which is acquired from the last element of **self._target_transforms**. **last_road_id** contains the road id of waypoint which contains **last_target_loc**. **new_target_transform** contains a random carla transform from **self._spawn_transforms** where the road id is not same as **last_road_id**. 
  - **route_trace** is calculated from **last_target_loc** and **new_target_transform**'s location using the **trace_route()** method of [**GlobalRoutePlanner**](navigation/global_route_planner.py). You can think **route_trace** as a google map. **self._global_route** is appended with **route_trace**. **new_target_transform** is added to the **self._target_transforms**. **self._route_length** is updated as well. **self._update_leaderboard_plan()** method is called. 
- **_truncate_global_route_till_local_target()**
  
  - This method will check the first **windows_size** + 1 number of elements in the **self._global_route** list.
  - Then it will find out the element that has the waypoint closest to the ego vehicle.
  - It will remove the elements before the element that has the closest waypoint to the ego vehicle.
- **_is_route_completed()**:
  
  -  This checks if the ego vehicle completed the route by checking if percentage of route completion is greater than **percentage_threshold** and distance between ego vehicle location and target location is less than **distance_threshold**.
- **tick()**:
 
  - **timestamp** contains several step, frame and time related information about simulation. This dictionary variable is initialized as below,
 
        self._timestamp = {
            'step': 0,
            'frame': snap_shot.timestamp.frame,
            'relative_wall_time': 0.0,
            'wall_time': snap_shot.timestamp.platform_timestamp,
            'relative_simulation_time': 0.0,
            'simulation_time': snap_shot.timestamp.elapsed_seconds,
            'start_frame': snap_shot.timestamp.frame,
            'start_wall_time': snap_shot.timestamp.platform_timestamp,
            'start_simulation_time': snap_shot.timestamp.elapsed_seconds
        }
  - **_truncate_global_route_till_local_target()** method is called. **distance_traveled** is a truncated list of **self._global_route**.
  - **route_completed** is a boolean variable that checks if the ego vehicle has completed the route.
  - If the environment is **endless** and the length of **self.global_route** is less than 10 meter or route is completed, then additional route is added using **self._add_random_target()** and **route_completed** becomes false.
  - **info_blocked** is a dictionary containing information where and when the ego vehicle is blocked. **self.criteria_blocked.tick()** method is described [**here**](./criteria/blocked.md)
  - **info_collision** is a dictionary that contains information of last occurred collision. How this dictionary is built can be found [here](../common/criteria/collision.md)
  - **info_light** is a dictionary that contains information of crossing red light by the ego vehicle. Example of the dictionary can be found [here](../common/criteria/run_red_light.md)
  - **info_encounter_light** is a dictionary that contains information about the last encountered traffic light by the ego vehicle. Example of the dictionary can be found [here](../common/criteria/encounter_light.md)
  - **info_stop** is a dictionary containing information about encountering or running through a stop sign. Example of the dictionary can be found [here](../common/criteria/run_stop_sign.md)
  - **info_route_deviation** is a dictionary containing information about if the ego vehicle has deviated from its predetermined route. Example of the dictionary can be found [here](../common/criteria/route_deviation.md)
  - **info_route_completion** is a dictionary which describes route related information of the ego vehicle, built from the variables described in the start of the method. Example of this is below,
  - 
        {
            "step": timestamp["step"],
            "simulation_time": timestamp["relative_simulation_time"],
            "route_completed_in_m": self._route_completed,
            "route_length_in_m": self._route_length,
            "is_route_completed": route_completed,
        }
  - **self._info_criteria** is dictionary built from several above described dictionaries. Here how it is initialized,
  
        {
            "route_completion": info_route_completion,
            "outside_route_lane": info_outside_route_lane,
            "route_deviation": info_route_deviation,
            "blocked": info_blocked,
            "collision": info_collision,
            "run_red_light": info_light,
            "encounter_light": info_encounter_light,
            "run_stop_sign": info_stop,
        }

    By doing this, all the criteria based information is now associated with a particular ego vehicle for the current **timestamp**.
  - Based on the sun's altitude information, the light of the ego vehicle is turned on.
  - **self._info_criteria** is then returned.
