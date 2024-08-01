- **__ init__()**
  - **self._ego_vehicle** contains the ego vehicle for which **done, timeout, terminal_reward, terminal_debug** is going to be calculated using **get()** method.
  - **self._exploration_suggest**
  - **self._last_lat_dist**
  - **self._min_thresh_lat_dist**
  - **self._eval_mode**
  - **self._eval_time**
- **get()**
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
  - How **self._ego_vehicle.info_criteria** is calculated can be found in the **tick()** method of [**TaskVehicle**](../../common/task_vehicle.py)
  - At first, six conditions are checked. If one of them is **true**, then **done** is true. Therefore, in such case the episode has ended. As the conditions are well commented in the code and self-explanatory I am not going to describe all of them. I will write about **Condition 2** in a later time.
  - **timeout** is calculated in evaluation mode. Otherwise, it is false.
  - **terminal_reward** is initiated with 0. If **done** is true, it is converted to -1. If the ego vehicle ran a red light or experienced collision or ran a stop sign or [do not know what **self._ego_vehicle.collision_px** is], then the reward is reduced by the speed of the ego vehicle.
  - This is an assumption. **exploration_suggest** contains in which step the ego vehicle agent should explore and what type action it may take while exploring. Based on **self._exploration_suggest** and several conditions' truth value, **exploration_suggest** is calculated differently.
  - **debug_texts** is built based on several variables' value calculated above.
  - **terminal_debug** is built based on **exploration_suggest** and **debug_texts**. Why use **exploration_suggest** in **terminal_debug**?
  - **done, timeout, terminal_reward, terminal_debug** are then returned.