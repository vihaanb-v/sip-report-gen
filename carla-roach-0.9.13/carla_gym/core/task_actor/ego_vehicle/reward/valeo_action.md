- **__ init__()**
  - **self._ego_vehicle** is the ego vehicle instance for which this class will calculate rewards.
  - **self.om_vehicle** is an [**ObsManager**](../../../obs_manager/object_finder/vehicle.py) that detects a maximum number of other vehicles that are in a range of certain distance of the ego vehicle.
  - **self.om_pedestrian** is an [**ObsManager**](../../../obs_manager/object_finder/pedestrian.py) that detects a maximum number of other pedestrians that are in a range of certain distance of the ego vehicle.
  - Both **self.om_vehicle** and **self.om_pedestrian** are attached to the **self._ego_vehicle**.
  - **self._maxium_speed**
  - **self._last_steer**
  - **self._tl_offset**
- **get()**
  - **terminal_reward** is a quantity that is calculated from the classes defined [**here**](../terminal/). For example, [**see**](../terminal/valeo_no_det_px.md).
  - **ev_transform** is ego vehicle carla transform.
  - **ev_control** ego vehicle controls.
  - **ev_vel** ego vehicle velocity.
  - **ev_speed** ego vehicle speed calculated from velocity.
  - **r_action** is a reward that is calculated when there is change in ego vehicle steering.
  - **obs_vehicle** is an observation dictionary. What the dictionary contains can be found [**here**](../../../obs_manager/object_finder/vehicle.md).
  - **obs_pedestrian** is an observation dictionary. What the dictionary contains can be found [**here**](../../../obs_manager/object_finder/pedestrian.md).
  - **hazard_vehicle_loc** is the nearest vehicle that may collide with the ego vehicle. **hazard_ped_loc** is the nearest pedestrian that may collide with the ego vehicle. Internal details of implementation of **lbc_hazard_vehicle()** and **lbc_hazard_walker()** can be found [here](../../../../utils/hazard_actor.md)
  - **light_state**, **light_loc** returns the state and location of traffic light that is nearest
  - **desired_spd_veh** **desired_spd_ped** **desired_spd_rl** **desired_spd_stop** **self._maxium_speed**
  - **dist_veh** is the distance between the ego vehicle and the hazardous vehicle having location **hazard_vehicle_loc**. **dist_veh** is calculated such that there is an 8.0 meter safety radius around the hazardous vehicle.
  - The desired speed **desired_spd_veh** is then calculated based on this distance, using a linear function that scales down the speed as the distance increases. The **np.clip** function ensures that the speed is between 0.0 and the maximum speed, and it scales the distance to a range of 0.0 to 5.0.
  - **dist_ped** is the distance between the ego vehicle and the hazardous pedestrian having location **hazard_ped_loc**. **dist_ped** is calculated such that there is an 6.0 meter safety radius around the hazardous vehicle.
  - The desired speed **desired_spd_ped** is then calculated based on this distance, using a linear function that scales down the speed as the distance increases. The **np.clip** function ensures that the speed is between 0.0 and the maximum speed, and it scales the distance to a range of 0.0 to 5.0. 
  - If **light_state** is red or yellow, it is also considered hazardous as if the ego vehicle may cross the traffic light in while it is red. **dist_rl** is the distance between the ego vehicle and the hazardous traffic light having location **light_loc**. **dist_rl** is calculated such that there is an 5.0 meter safety radius around the hazardous vehicle.
  - The desired speed **desired_spd_rl** is then calculated based on this distance, using a linear function that scales down the speed as the distance increases. The **np.clip** function ensures that the speed is between 0.0 and the maximum speed, and it scales the distance to a range of 0.0 to 5.0.
  - **stop_sign** is a stop sign that may effect the ego vehicle. It is calculated in the **tick()** method of [RunStopSign](../../common/criteria/run_stop_sign.py). 
  - In the **If** block,
    - If there is a stop sign and the ego vehicle did not stop encountering the stop sign, then **desired_spd_stop** is calculated which is the desired speed for the ego vehicle before encountering the stop sign.   
  - **desired_speed** is the final desired speed of the ego vehicle which is minimum among the all the desired speeds calculated above.
  -  The **if-else** block is redundant. Regardless of whether the condition is true or false, the block calculates the reward based on the absolute difference between the current speed **ev_speed** and the desired speed **desired_speed**. The result is normalized by dividing by the maximum allowable speed **self._maximum_speed**. The reward **r_speed** is then calculated as 1.0 minus this normalized difference. As you can see, if the ego vehicle speed is higher than the **desired_speed**, then **r_speed** is less. Otherwise, it is higher.
  - The next block annotated by the comment "r_position", calculates a reward **r_position** based on the lateral distance between the ego vehicle and a route waypoint transform **wp_transform**. This transform is associated with the first waypoint that is not reached by the ego vehicle.
  - **r_rotation** is calculated based on the angular difference between the yaw angles of the ego vehicle and a route waypoint **wp_transform**.
  - **reward** is calculated as a sum of **r_speed, r_position, r_rotation, terminal_reward and r_action**.
  - There are several **if-else** blocks from here on consecutively. They are  preparing textual representations of locations for different hazards (vehicle, pedestrian, traffic light, and stop sign) as strings. The locations are represented as 2D arrays, and these strings are used for logging or debugging purposes.   The code is useful for debugging or logging purposes, providing human-readable representations of hazard locations in a formatted way. The resulting strings **txt_hazard_veh, txt_hazard_ped, txt_light, txt_stop** can be printed or logged for inspection during the execution of the program.
  - All the important information calculated is stored in a list **debug_texts** which is initialized as below,

        [
            f'r:{reward:5.2f} rp:{r_position:5.2f} rr:{r_rotation:5.2f}',
            f'ds:{desired_speed:5.2f} rs:{r_speed:5.2f} ra:{r_action:5.2f}',
            f'veh_ds:{desired_spd_veh:5.2f} {txt_hazard_veh}',
            f'ped_ds:{desired_spd_ped:5.2f} {txt_hazard_ped}',
            f'tl_ds:{desired_spd_rl:5.2f} {light_state}{txt_light}',
            f'st_ds:{desired_spd_stop:5.2f} {txt_stop}',
            f'r_term:{terminal_reward:5.2f}'
        ]
  - **reward_debug** is a dictionary which stores the **debug_texts** with associated key string **debug_texts**.
  - **reward, reward_debug** is then returned.