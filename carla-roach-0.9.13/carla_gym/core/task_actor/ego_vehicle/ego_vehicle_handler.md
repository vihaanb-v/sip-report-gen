# carla_gym/core/task_actor/ego_vehicle/ego_vehicle_handler.py

Below, I describe several parts of **EgoVehicleHandler** class.
- **__init__()** :
  - **self.ego_vehicles** : This a dictionary containing ego vehicle id as key and [**TaskVehicle**](../common/task_vehicle.py) as value.
  - **self.info_buffers** : It is a dictionary where key is the ego vehicle id and it stores several dictionaries associated with a given ego vehicle. They are information related to collision, running a red light, encountering a traffic light, running a stop sign, deviating from the given route, being blocked and being outside the route lane etc.
  - **self.reward_buffers** : It is a dictionary where key is the ego vehicle id and the value is a list of rewards earned by the associated ego vehicle during an episode. 
  - **self.reward_handlers** :
  - **self.terminal_handlers** :
  - **self._reward_configs** : This contains the reward configuration of an agent. It is a dictionary. An example represented as yaml is given below : 
  
          reward:
              entry_point: reward.valeo_action:ValeoAction
              kwargs: {}

  - **self._terminal_configs** : This contains the terminal condition configuration of an agent. An example is given below :
  
          terminal:
              entry_point: terminal.valeo_no_det_px:ValeoNoDetPx
              kwargs: {}

  - **self._world** : Carla world instance.
  - **self._map** : Carla map instance.
  - **self._spawn_transforms** : It has specific spawn points returned by **_get_spawn_points()**.
- **_get_spawn_points()** : It generates list of pairs of carla road id and transform where the vehicle can be spawned. This method excludes junctions from the list and handles test case regarding **Town03**.
- **reset()** : The **task_config** variable contains actor configuration, such as which vehicle model to use, the route the actor is going to use and wether this is an endless environment described in **carla_gym/envs/suites/endless_env.py**. Example of **task_config** is following :
    
        {
        'routes':{
                    'hero': []},
        'actors':{
                    'hero': {'model': 'vehicle.lincoln.mkz_2017'}
                },
        'endless':{
                    'hero': True
                }
        }

    In the above example the **'hero'** is ego vehicle id. According to the above example,
    
    - **actor_config** contains **{'hero': {'model': 'vehicle.lincoln.mkz_2017'}}**, **route_config** contains **{'hero': []}** and **endless_config** contains **{'hero': True}**. **ev_spawn_locations** contains the locations where different ego vehicles are spawned.
    - Note that, **endless_config** can contain **None**, as a result **'endless'** may be absent from **task_config**. But the remaining two keys must be present. Now, I am going to explain the for loop based on the above example. 
    - **actor_config** is iterated and the ego vehicle id **'hero'** is stored in **ev_id** variable. 
    - **bp_filter** contains **'vehicle.lincoln.mkz_2017'**. **blueprint** contains the blueprint of **vehicle.lincoln.mkz_2017** where the attribute **'role_name'** is set to **'hero'**. 
    - if **route_config['hero']** is an empty list, then no route information is generated yet. As a result, a random transform is chosen from **self._spawn_transforms**. If **route_config[ev_id]** is not empty, then as a natural choice, the first point in the route is chosen as spawn point. 
    - **wp** contains the waypoint which contains **spawn_transform**. **spawn_transform.location.z** is increased by some amount to avoid Z-collisions. 
    - **carla_vehicle** is spawned in the carla world but it is not rendered yet as the carla gym environment is synchronous. As a result, **self._world.tick()** is needed to render the vehicle to the scene. 
    - If **endless_config** is **None**, **endless** variable is set to **False**. Otherwise, **endless** is according to **endless_config[ev_id]**. For the above example, it is **True**. 
    - **target_transforms** contains the target carla transform of the carla map where the the ego vehicle should go. If **route_config[ev_id]** is empty, then **target_transforms** is an empty list. 
    - **self.ego_vehicles[ev_id]** contains instance of **TaskVehicle** class. **_build_instance()** method builds a class's instance using the **config** argument. It also uses the **ego_vehicle** argument. If we follow the example given above for **self._reward_configs** and **self._terminal_configs**, then **self.reward_handlers[ev_id]** contains [**ValeoAction**](reward/valeo_action.py) class instance and **self.terminal_handlers[ev_id]** contains [**ValeoNoDetPx**](terminal/valeo_no_det_px.py) class instance. 
    - **self.reward_buffers[ev_id]** is initialized as empty list and a dictionary of empty lists **self.info_buffers[ev_id]** is created. 
    - **reset()** returns the **ev_spawn_locations** which is a list locations where ego vehicles are spawned.
- **apply_control()**:
  - **control_dict** is iterated and controls are applied to specific ego vehicles.
- **tick()** : 
  
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
  - **reward_dict, done_dict, info_dict** are initialized as empty dictionary. 
  - **self.ego_vehicles** is dictionary of ego vehicle id and [**TaskVehicle](../common/task_vehicle.py) 
  - In the **for loop**, **self.ego_vehicles** is iterated,
  
    - [**tick()**](../common/task_vehicle.py) method of [**TaskVehicle**](../common/task_vehicle.py) class is called. This returns several criteria related information that can be found in the [**tick()**](../common/task_vehicle.md) method description. For example, if the ego vehicle crosses a red light, then it will return the when it happened, location of the ego vehicle and red light when the event occurred etc. Such information is stored in **info_criteria**.
    - **info** contains a shallow copy of **info_criteria**.
    - I am assuming that for a particular ego vehicle, a terminal handler [**ValeoNoDetPx**](./terminal/valeo_no_det_px.py) is used. How **done, timeout, terminal_reward, terminal_debug** is calculated can be found [here](./terminal/valeo_no_det_px.md).
    - I am assuming that for a particular ego vehicle, a reward handler [**ValeoNoDetPx**](./reward/valeo_action.py) is used. How **reward, reward_debug** is calculated can be found [here](./reward/valeo_action.md). **reward** calculated based on position, rotation, speed, steering and **terminal_reward**. **reward_debug** is a dictionary that is used for debugging purpose.
    - The next block of code populates several dictionary that has **ev_id** as key and the values are calculated above. **reward_dict** stores rewards, **done_dict** stores a boolean of the information that if the episode has ended, **info_dict** is a dictionary that contains several criteria, timeout and debug information.
    - **self.reward_buffers[ev_id]** is appended with **reward**.
    - Based on the type of collision **self.info_buffers** associated with an ego vehicle is populated with collision information.
    - If an ego vehicle ran a red light, then **self.info_buffers** is populated with this information.
    - If an ego vehicle encountered a traffic light, then **self.info_buffers** is populated with this information.
    - If an ego vehicle encountered or ran a stop sign , then **self.info_buffers** is populated with this information.
    - If an ego vehicle deviated from its route, then **self.info_buffers** is populated with this information.
    - If an ego vehicle is blocked, then **self.info_buffers** is populated with this information.
    - If an ego vehicle deviated from its route's lane, then **self.info_buffers** is populated with this information.
    - If the ego vehicle completed the episode, 
      - **info_dict** is again populated. Most of the code is self-explanatory. Some important variables that are calculated are **score_route**, **score_penalty** and **is_route_completed_nocrash**. They are used to score the route taken by ego vehicle, penalty for not following criteria and for completing the route without collisions respectively.
    - **done_dict** contains information if all the ego vehicles completed the episode.
    - How **info_dict** is initiated cannot be shown as it is built incrementally and huge. Must see from the code.
    - **reward_dict, done_dict, info_dict** are then returned.