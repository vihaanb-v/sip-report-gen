## carla_gym/carla_multi_agent_env.py

As I have said before, there are several environments that are implemented here. The environments can be found in **carla_gym/envs/suites/** folder. As you can see all the environments have inherited from **CarlaMultiAgentEnv** class. 

Below, I will describes several parts of the class and their purposes. Be tuned.
- **__ init__()** : 
  - **self._all_tasks** : This is a list of dictionary. Here is one example task that is represented as dictionary and stored in **self._all_tasks** list. 
    
        {
            'weather': 'ClearNoon',
            'description_folder': 'None',
            'route_id': 0,
            'num_zombie_vehicles': 10,
            'num_zombie_walkers': 15,
            'ego_vehicles': {
                'routes': {'hero': []},
                'actors': {'hero': {'model': 'vehicle.lincoln.mkz_2017'}},
                'endless': {'hero': True}
            },
            'scenario_actors': {},
        }
  - **self._obs_configs** : This contains observation settings of the agent. How the agent is going to perceive the environment is described here. An example of this represented as **yaml** file is given below.
    
        hero:
            obs_configs:
                birdview:
                    module: birdview.chauffeurnet
                    width_in_pixels: 192
                    pixels_ev_to_bottom: 40
                    pixels_per_meter: 5.0
                    history_idx:
                    - -16
                    - -11
                    - -6
                    - -1
                    scale_bbox: true
                    scale_mask_col: 1.0
                speed:
                    module: actor_state.speed
                control:
                    module: actor_state.control
                velocity:
                    module: actor_state.velocity
  - **self._carla_map** : This contains the carla map, specifically which map to load after client is connected to server.
  - **self._seed** : This is for result reproducibility.
  - **self.name** : This is name of the class which implemented a specific environment.
  - **_init_client()** method is called.
  - **self._om_handler** : It contains the observation manager handler instance. More about this in [here](core/obs_manager/obs_manager_handler.md)
  - **self._ev_handler** : It contains ego vehicle handler instance.  More about this in [here](core/task_actor/ego_vehicle/ego_vehicle_handler.md)
  - **self._zw_handler** : It contains the zombie walker handler instance. More about this in [here](core/zombie_vehicle/zombie_vehicle_handler.md).
  - **self._sa_handler** : This contains the scenario actor handler instance. More about this in [here](core/task_actor/scenario_actor/scenario_actor_handler.md)
  - **self._wt_handler** : This contains the weather handler instance. More about this in [here](utils/dynamic_weather.md)
  - **self.observation_space** : Every gym environment must define observation space and action space. This variable contains the observation space of the **CarlaMultiAgentEnv** class and the classes that extend it. **self._om_handler.observation_space** is call to the property method of **ObsManagerHandler** class.  How observation space is obtained from observation manager handler is described [here](core/obs_manager/obs_manager_handler.md).
  - **self.action_space** : This contains the action space for the gym environment. This contains a gym dictionary which is a key-value pair between ego vehicle id and three dimensional Box space. The dimensions are throttle, steer and brake.
  - **self._task_idx** : The task contains weather settings, ego vehicle ids, the routes the ego vehicles follow etc. The task are defined in the **__ init __** method of the concrete classes that inherit the **CarlaMultiAgentEnv** class. You can see the **build_all_tasks()** method of the below classes to see how a task list is built. Each element of the list is a individual task. **self._task_idx** variable defines an index to the list and during initialization the first task is by default chosen.

    - [CoRL2017Env](envs/suites/corl2017_env.py)
    - [EndlessEnv](envs/suites/endless_env.py)
    - [LeaderboardEnv](envs/suites/leaderboard_env.py)
    - [NoCrashEnv](envs/suites/nocrash_env.py)
  - **self._shuffle_task** : As said above, the first task is chosen to be done by default. So, to make the choice of the tasks nondeterministic, this variable is used. When **reset()** method is called on the environment, this variable is used to randomly choose different index for the task to be chosen.
  - **self._task** : This is the real task instance that is chosen by using **self._task_idx**. As you can see the **copy()** method is used as the task is not fully built yet. There are changes that need to be done before using the task instance.
- **set_task_idx()** : This method is used to choose a specific task.
- **num_tasks()** : This is a property method to get the number of tasks in the task list.
- **task()** : This property method returns the task that is being used in the gym environment.
- **reset()** : 
  - This one of the two methods that a custom gym environment must implement, the other being **step()**. 
  - Firstly, if **self._shuffle_task** is **true**, then a random task is chosen from the task list. 
  - After that, the **clean** method is called. The inner working of **clean** method is described below on a separate paragraph. 
  - [**reset()**](utils/dynamic_weather.md) is called on weather handler instance. 
  - Then [**reset()**](core/task_actor/ego_vehicle/ego_vehicle_handler.md) is called on ego vehicle handler instance. This spawns ego vehicles and returns their spwan points. 
  - After that [**reset()**](core/task_actor/scenario_actor/scenario_actor_handler.md) method of scenario actor handler is called. 
  - Then, the [**reset()**](core/zombie_vehicle/zombie_vehicle_handler.md) method is called with arguments **self._task['num_zombie_vehicles']** and **ev_spawn_locations**. 
  - After that, the [**reset()**](core/obs_manager/obs_manager_handler.md) method of observation manager is summoned. 
  - **self._world.tick()** is used to calculate the next frame as the simulation is in synchronous mode. 
  - **snap_shot** is used to initialize **self._timestamp**.
  - **self._timestamp** contains several information regarding simulation such as the number of step, the number of frame and several time related information.
  - The **tick()** method of ego vehicle handler is called. What this returns can be found [here](./core/task_actor/ego_vehicle/ego_vehicle_handler.md)
  - **obs_dict** is dictionary where the values are observations found by the [**observation managers**](./core/obs_manager/) associated with two keys that are ego vehicle id and observation manager id. It is then returned.
- **step()**
  - Controls are applied to all the ego vehicles according to **control_dict** dictionary.
  - Next frame of the carla world is calculated by calling the **tick()** method of carla world object.
  - **self._timestamp** is then updated.
  - [**tick()**](./core/task_actor/ego_vehicle/ego_vehicle_handler.md) method of [**EgoVehicleHandler**](./core/task_actor/ego_vehicle/ego_vehicle_handler.py) is then called which subsequently returns three specific dictionaries which contain reward information, episode completion information and several other information stored in **info_dict**.
  - **obs_dict** is dictionary where the values are observations found by the [**observation managers**](./core/obs_manager/) associated with two keys that are ego vehicle id and observation manager id. It is then returned.
  - [**tick()**](./utils/dynamic_weather.md) method of [**WeatherHandler**](./utils/dynamic_weather.py) is called which changes the weather if it is defined as dynamic.
  - **obs_dict, reward_dict, done_dict and info_dict** is then returned.
- **clean()** : The **clean()** methods of scenario handler, zombie walker handler, zombie vehicle handler, observation manager handler, ego vehicle handler and weather handler is called. The **world.tick()** is called because the server is in synchronous mode. 
- **self._init_client()** : This method is used to initialize the carla client. First the **client** variable is set to **None**. Then, in a while loop it tries to connect to server until the connection is established. 
  - **self._client** : It contains the carla client instance.
  - **self._world** : It contains the carla world instance. More about carla client and world can be found [here](https://carla.readthedocs.io/en/0.9.13/core_world/).
  - **self._tm** : It contains the carla traffic manager instance. More about carla traffic manager can be found [here](https://carla.readthedocs.io/en/0.9.13/adv_traffic_manager/).
  - **self.set_sync_mode()** : It is used to turn off and on synchronous mode. It is an important concept in carla. More about it can be found [here](https://carla.readthedocs.io/en/0.9.13/adv_synchrony_timestep/).
  - **self.set_no_rendering_mode()** : It is used to disable and unable rendering in carla server. More about it can be found [here](https://carla.readthedocs.io/en/0.9.13/adv_rendering_options/#no-rendering-mode).
  - **set_random_seed()** : It is used to seed the random number generator.
  - **self._tm.set_random_device_seed()** : It makes the traffic manager deterministic.
  - **self._world.tick()** : In synchronous mode the server will calculate the next frame if this method is called. The traffic manager properly works in synchronous mode.
  - **TrafficLightHandler.reset()** : It is used to register traffic lights in carla world.