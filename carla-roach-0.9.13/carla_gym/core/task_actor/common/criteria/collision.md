- Should read about [Collision detector](https://carla.readthedocs.io/en/latest/ref_sensors/#collision-detector) before starting this doc.
- **__ init__()**
  - Firstly, a collision sensor is created and attached to the ego vehicle. The sensor is configured to have **_on_collision()** callback method that will be called when an collision event has occurred.
  - **self._collision_info** is a dictionary that contains several collision related information.
  - **self.registered_collisions** is list of ego vehicle's location where collision occurred.
  - **self.last_id** is the id of last thing (can be vehicle, pedestrian etc) that collided with the ego vehicle.
  - **self.collision_time** simulation time when the collision occurred.
  - The remaining variables' information are described in the code. Refer to it.
- **_on_collision()**
  - This method is well commented in the code and so I am not going to describe it.
- **tick()**
  - **ev_loc** contains the location of the ego vehicle.
  - **new_registered_collisions** is a list that is calculated in the next **for loop**. 
  - The **for loop** is well described and so I will not write about it. Basically it populates the **new_registered_collisions** with collision location that did not happen far away from the ego vehicle.
  - **self.registered_collisions** is assigned the values of **new_registered_collisions**.
  - In the **if** block it is checked if **self.last_id** exists and if it exists then the ego vehicle collided with the object having this id. If the collision happened much time before then, it is ignored by making **self.last_id** to **None**
  - **info** contains the last collision information which is collected in **_on_collision()** callback function. Example of info is given below,
        
        {
            'step': event.frame,
            'simulation_time': event.timestamp,
            'collision_type': collision_type,
            'other_actor_id': event.other_actor.id,
            'other_actor_type_id': event.other_actor.type_id,
            'intensity': intensity,
            'normal_impulse': [impulse.x, impulse.y, impulse.z],
            'event_loc': [event_loc.x, event_loc.y, event_loc.z],
            'event_rot': [event_rot.roll, event_rot.pitch, event_rot.yaw],
            'ev_loc': [ev_loc.x, ev_loc.y, ev_loc.z],
            'ev_rot': [ev_rot.roll, ev_rot.pitch, ev_rot.yaw],
            'ev_vel': [ev_vel.x, ev_vel.y, ev_vel.z],
            'oa_loc': [oa_loc.x, oa_loc.y, oa_loc.z],
            'oa_rot': [oa_rot.roll, oa_rot.pitch, oa_rot.yaw],
            'oa_vel': [oa_vel.x, oa_vel.y, oa_vel.z]
        }
  - In the **if** statement some adjustments are made as the episode may start in a later time than the simulation start time.
  - **info** is then returned.