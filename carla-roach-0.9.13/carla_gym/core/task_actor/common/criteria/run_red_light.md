- **__ init__()**:
  - **self._map** contains carla map instance.
  - **self._last_red_light_id**
  - **self._distance_light** 
- **tick()**:
  - **ev_tra** is ego vehicle carla transformation.
  - **ev_loc** is ego vehicle location
  - **ev_dir** is the forward vector or the direction the ego vehicle is heading.
  - **ev_extent** contains x axis extent of the bounding box representing the geometry information of the ego vehicle. This is relative to the ego vehicle center.
  - **tail_close_pt** is a carla transformation which is 80 percent behind the center of the vehicle along the x axis.
  - **tail_far_pt** is same as **tail_close_pt**, but it is more behind than **tail_close_pt**. Note that, **tail_close_pt** is inside the ego vehicle but **tail_far_pt** is one meter behind outside the ego vehicle along the x axis.
  - **tail_wp** contains the waypoint related to **tail_far_pt**.
  - I will be describing this script later time along with [**TrafficLightHandler**](../../../../utils/traffic_light.py)
  - But this method returns information dictionary about if the ego vehicle has crossed a red light. Example of such dictionary is below,
   
        {
            'step': timestamp['step'],
            'simulation_time': timestamp['relative_simulation_time'],
            'id': traffic_light.id,
            'tl_loc': [tl_loc.x, tl_loc.y, tl_loc.z],
            'ev_loc': [ev_loc.x, ev_loc.y, ev_loc.z]
        }

  - So, this contains several timing information and location information.
